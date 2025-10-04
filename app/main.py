from fastapi import FastAPI
from app.routes import auth_routes, course_routes, progress_routes, enrollment_routes
from app.routes.admin_dashboard import user_routes
from app.routes import video_routes, quiz_checkpoint_routes, quiz_history_routes, branch_routes, organization_routes
from app.routes import categorys_routes
from app.database import engine, Base
from app.models import user_m, role_m, course_m, video_m, QuizCheckpoint_m, Progress_m, QuizHistory_m, enrollment_m,shift_m, department_m, leavemaster_m
from app.models import organization, branch_m, category_m
from app.seeders.role_seeder import seed_roles
from app.routes import shift_routes,department_routes
from app.routes import leavemaster_routes

 
app = FastAPI()

# Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI is running"}

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(organization_routes.router)
app.include_router(branch_routes.router)
app.include_router(enrollment_routes.router)
app.include_router(categorys_routes.router)
app.include_router(course_routes.router)
app.include_router(video_routes.router)
app.include_router(quiz_checkpoint_routes.router)
app.include_router(quiz_history_routes.router)
app.include_router(progress_routes.router)
app.include_router(shift_routes.router)
app.include_router(department_routes.router)
app.include_router(leavemaster_routes.router)
# ✅ Create tables at startup if necessary
Base.metadata.create_all(bind=engine)

seed_roles()
