# app/ai_models/face_service.py

import numpy as np
import cv2
from functools import lru_cache
from insightface.app import FaceAnalysis
from sqlalchemy.orm import Session

from app.models.user_face_m import UserFace


# ==========================================================
# LAZY LOAD INSIGHTFACE (loads only when needed)
# ==========================================================
@lru_cache(maxsize=1)
def get_face_app():
    print("⚡ Loading InsightFace model (lazy)...")
    app = FaceAnalysis(name="buffalo_l")
    app.prepare(ctx_id=0, det_size=(640, 640))
    print("✅ InsightFace model ready!")
    return app


# ==========================================================
# REGISTER USER FACE → SAVE EMBEDDING IN DB
# ==========================================================
def register_face(image_bytes: bytes, user_id: int, db: Session):

    face_app = get_face_app()   # load when used the first time

    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    faces = face_app.get(img)

    if len(faces) == 0:
        return False, "No face detected"

    if len(faces) > 1:
        return False, "Multiple faces detected. Only one face allowed."

    face = faces[0]
    embedding = face['embedding']

    db_face = UserFace(
        user_id=user_id,
        embedding=embedding.tobytes(),
        model_name="insightface_arcface"
    )

    db.add(db_face)
    db.commit()
    db.refresh(db_face)

    return True, "Face registered successfully"


# ==========================================================
# RECOGNIZE FACE + DRAW BOX
# ==========================================================
def recognize_face_with_box(image_bytes: bytes, db: Session):

    face_app = get_face_app()   # lazy load

    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    faces = face_app.get(img)

    if len(faces) == 0:
        return None, img, "No face detected"

    if len(faces) > 1:
        return None, img, "Multiple faces detected"

    face = faces[0]
    embedding = face['embedding']

    # ---------------- DRAW BOUNDING BOX ----------------
    x1, y1, x2, y2 = face['bbox'].astype(int)
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # ---------------- FETCH KNOWN EMBEDDINGS -----------
    all_faces = db.query(UserFace).all()
    if not all_faces:
        return None, img, "No registered faces in DB"

    best_user_id = None
    best_score = -1

    for rec in all_faces:
        saved_embedding = np.frombuffer(rec.embedding, dtype=np.float32)

        # Cosine similarity
        score = float(
            np.dot(embedding, saved_embedding)
            / (np.linalg.norm(embedding) * np.linalg.norm(saved_embedding))
        )

        if score > best_score:
            best_score = score
            best_user_id = rec.user_id

    # ----------- VALIDATE MATCH -----------------
    THRESHOLD = 0.48  # production threshold

    if best_score < THRESHOLD:
        return None, img, f"Unknown face (score={best_score:.2f})"

    return best_user_id, img, None
