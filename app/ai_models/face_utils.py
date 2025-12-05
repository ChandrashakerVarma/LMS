import numpy as np
import cv2
from sqlalchemy.orm import Session
from sklearn.metrics.pairwise import cosine_similarity

from app.models.user_face_m import UserFace
from app.ai_models.anti_spoof import is_live_face
from app.ai_models.insight_model import get_face_model


# ---------------------------------------------------------
# FACE QUALITY CHECK
# ---------------------------------------------------------
def is_quality_face(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clarity = cv2.Laplacian(gray, cv2.CV_64F).var()
    return clarity >= 50


# ---------------------------------------------------------
# EXTRACT EMBEDDING USING INSIGHTFACE
# ---------------------------------------------------------
def extract_embedding(frame):
    face_app = get_face_model()          # 👈 lazy load here
    faces = face_app.get(frame)

    if len(faces) == 0:
        return None

    best_face = max(faces, key=lambda x: x.det_score)
    return best_face.embedding


# ---------------------------------------------------------
# REGISTER FACE → DB
# ---------------------------------------------------------
def register_user_face(db: Session, user_id: int, image_bytes: bytes):
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if img is None:
        raise Exception("Invalid image format.")

    if not is_quality_face(img):
        raise Exception("Face too blurry or low quality.")

    if not is_live_face(img):
        raise Exception("Spoof detected! Show a real face.")

    embedding = extract_embedding(img)
    if embedding is None:
        raise Exception("Unable to detect face.")

    emb_bytes = embedding.astype("float32").tobytes()

    rec = UserFace(
        user_id=user_id,
        embedding=emb_bytes
    )

    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


# ---------------------------------------------------------
# LOAD EMBEDDINGS FROM DB
# ---------------------------------------------------------
def load_all_embeddings(db: Session):
    faces = db.query(UserFace).all()
    items = []

    for face in faces:
        emb = np.frombuffer(face.embedding, dtype=np.float32)
        items.append((face.user_id, emb))

    return items


# ---------------------------------------------------------
# RECOGNIZE USER (strict match for attendance)
# ---------------------------------------------------------
def recognize_user(db: Session, frame, threshold=0.48):
    emb = extract_embedding(frame)
    if emb is None:
        return None

    emb = emb / np.linalg.norm(emb)

    items = load_all_embeddings(db)
    if len(items) == 0:
        return None

    best_score = -1
    best_user = None

    for (uid, db_emb) in items:
        db_emb = db_emb / np.linalg.norm(db_emb)
        score = np.dot(emb, db_emb)

        if score > best_score:
            best_score = score
            best_user = uid

    return best_user if best_score >= threshold else None


# ---------------------------------------------------------
# FUZZY FACE SEARCH (Top K similar users)
# ---------------------------------------------------------
def fuzzy_face_search(db: Session, frame, top_k=5):
    emb = extract_embedding(frame)
    if emb is None:
        return []

    emb = emb.reshape(1, -1)

    items = load_all_embeddings(db)
    if len(items) == 0:
        return []

    results = []
    for (uid, db_emb) in items:
        score = cosine_similarity(emb, db_emb.reshape(1, -1))[0][0]
        results.append((uid, float(score)))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]
