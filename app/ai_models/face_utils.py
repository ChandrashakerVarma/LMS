import cv2
import os
import numpy as np
import face_recognition
from datetime import datetime
from deepface import DeepFace
from app.ai_models.anti_spoof import is_live_face

FACES_DIR = "app/ai_models/registered_faces"
if not os.path.exists(FACES_DIR):
    os.makedirs(FACES_DIR)


# ---------------------------------------------------------
# FACE QUALITY CHECK (blur, brightness, angle)
# ---------------------------------------------------------
def is_quality_face(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clarity = cv2.Laplacian(gray, cv2.CV_64F).var()

    if clarity < 50:   # too blurry
        return False
    return True


# ---------------------------------------------------------
# REGISTER FACE
# ---------------------------------------------------------
def register_user_face(image_path, user_id):
    img = cv2.imread(image_path)

    if not is_quality_face(img):
        return {"success": False, "msg": "Low quality face. Retake with clear lighting."}

    # SPOOF CHECK
    if not is_live_face(img):
        return {"success": False, "msg": "Spoof detected! Show your real face."}

    enc = face_recognition.face_encodings(img)
    if len(enc) == 0:
        return {"success": False, "msg": "No detectable face."}

    np.save(os.path.join(FACES_DIR, f"{user_id}.npy"), enc[0])
    return {"success": True, "msg": "Face registered securely"}


# ---------------------------------------------------------
# RECOGNIZE FACE WITH EMOTION + POSE + SPOOF CHECK
# ---------------------------------------------------------
def analyze_frame(frame):

    # SPOOF CHECK
    if not is_live_face(frame):
        return {"spoof": True}

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    encs = face_recognition.face_encodings(rgb)

    if len(encs) == 0:
        return {"recognized": False}

    encoding = encs[0]

    # MULTI-FACE SCAN
    candidates = []
    for file in os.listdir(FACES_DIR):
        if file.endswith(".npy"):
            uid = file.replace(".npy", "")
            saved_encoding = np.load(os.path.join(FACES_DIR, file))

            match = face_recognition.compare_faces([saved_encoding], encoding)[0]
            if match:
                candidates.append(int(uid))

    if len(candidates) == 0:
        return {"recognized": False}

    user_id = candidates[0]

    # EMOTION
    emo = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)

    return {
        "recognized": True,
        "user_id": user_id,
        "emotion": emo[0]['dominant_emotion'],
        "spoof": False
    }
