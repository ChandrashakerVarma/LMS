
from fastapi import FastAPI
from app.routes import auth_routes, course_routes, progress_routes, enrollment_routes, organization_routes, branch_routes, category_routes
from app.routes.admin_dashboard import user_routes
from app.routes import video_routes, quiz_checkpoint_routes, quiz_history_routes
from app.database import engine, Base
from app.models import user_m, role_m, course_m, video_m, QuizCheckpoint_m, Progress_m, QuizHistory_m, enrollment_m, Organization, branch_m, category_m
from app.seeders.seed_roles import seed_roles  # <- this should now work

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI is running"}

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(organization_routes.router)
app.include_router(branch_routes.router)
app.include_router(enrollment_routes.router)
app.include_router(category_routes.router)
app.include_router(course_routes.router)
app.include_router(video_routes.router)
app.include_router(quiz_checkpoint_routes.router)
app.include_router(quiz_history_routes.router)
app.include_router(progress_routes.router)

# Seed roles at startup
seed_roles()
