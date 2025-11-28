import os
import cv2
import numpy as np
from datetime import datetime

# Load only when needed to prevent server crash
def load_deepface():
    from deepface import DeepFace
    return DeepFace


FACES_DIR = "app/ai_models/registered_faces"

if not os.path.exists(FACES_DIR):
    os.makedirs(FACES_DIR)


# -------------------------------
# Generate embedding (ArcFace + opencv detector)
# -------------------------------
def get_embedding(img_path):
    DeepFace = load_deepface()

    embedding = DeepFace.represent(
        img_path=img_path,
        model_name="ArcFace",
        detector_backend="opencv",     # <<< NO RETINAFACE
        enforce_detection=False
    )
    return np.array(embedding[0]["embedding"])


# -------------------------------
# Register user face
# -------------------------------
def register_user_face(image_path: str, user_id: int):
    try:
        embedding = get_embedding(image_path)
        np.save(os.path.join(FACES_DIR, f"{user_id}.npy"), embedding)
        return {"success": True, "msg": "Face registered successfully"}
    except Exception as e:
        return {"success": False, "msg": str(e)}


# -------------------------------
# Recognize face
# -------------------------------
def recognize_face(frame_bgr):
    try:
        temp_path = "temp_frame.jpg"
        cv2.imwrite(temp_path, frame_bgr)

        frame_emb = get_embedding(temp_path)

        best_user = None
        best_distance = 999

        for file in os.listdir(FACES_DIR):
            if file.endswith(".npy"):
                saved_id = file.replace(".npy", "")
                saved_emb = np.load(os.path.join(FACES_DIR, file))

                distance = np.linalg.norm(frame_emb - saved_emb)

                if distance < best_distance:
                    best_distance = distance
                    best_user = saved_id

        if best_distance < 0.65:
            return int(best_user)
        return None

    except Exception as e:
        print("Recognition error:", e)
        return None
