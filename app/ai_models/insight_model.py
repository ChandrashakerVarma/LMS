import insightface
from functools import lru_cache

print("🟡 InsightFace lazy-loader ready…")

@lru_cache(maxsize=1)
def get_face_model():
    print("🔵 Loading InsightFace model (first-time only)…")
    app = insightface.app.FaceAnalysis(name="buffalo_l")
    app.prepare(ctx_id=0, det_size=(640, 640))
    print("✅ InsightFace model loaded!")
    return app
