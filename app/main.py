from fastapi import FastAPI
from app.routes import auth_routes, course_routes, progress_routes
from app.routes.admin_dashboard import user_routes
from app.routes import video_routes, quiz_checkpoint_routes, quiz_history_routes
from app.database import engine, Base
from app.models import user_m, role_m, course_m, video_m, QuizCheckpoint_m, Progress_m, QuizHistory_m
from app.seeders.role_seeder import seed_roles

app = FastAPI()

# Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI is running"}

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(course_routes.router)
app.include_router(video_routes.router)
app.include_router(quiz_checkpoint_routes.router)
app.include_router(quiz_history_routes.router)
app.include_router(progress_routes.router)


# ✅ Create tables at startup if necessary
# Base.metadata.create_all(bind=engine)

seed_roles()
