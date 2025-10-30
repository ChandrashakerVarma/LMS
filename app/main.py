from fastapi import FastAPI
from app.routes import auth_routes, course_routes, progress_routes, enrollment_routes
from app.routes.admin_dashboard import user_routes
from app.routes import video_routes, quiz_checkpoint_routes, quiz_history_routes, branch_routes, organization_routes
from app.routes import categorys_routes
from app.database import engine, Base
from app.models import user_m, role_m, course_m, video_m, QuizCheckpoint_m, Progress_m, QuizHistory_m, enrollment_m, department_m
from app.models import branch_m, category_m,leavemaster_m
from app.seeders.role_seeder import seed_roles
from app.routes import shift_routes,department_routes
from app.routes import leavemaster_routes,job_posting_routes,jobrole_routes,workflow_routes,attendance_routes
from app.models import organization_m,job_posting_m
from app.models import jobrole_m,workflow_m,candidate_m,candidate_documents_m,shift_change_request_m,user_shifts_m,shift_m
from app.routes import candidate_routes,candidates_documents_routes,shift_change_request_routes,shift_routes,user_shifts_routes
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
app.include_router(department_routes.router)

app.include_router(job_posting_routes.router)
app.include_router(jobrole_routes.router)
app.include_router(workflow_routes.router)
app.include_router(candidate_routes.router)
app.include_router(candidates_documents_routes.router)

app.include_router(shift_routes.router)
app.include_router(user_shifts_routes.router)
app.include_router(shift_change_request_routes.router)
app.include_router(attendance_routes.router)
app.include_router(leavemaster_routes.router)

# ✅ Create tables at startup if necessary
Base.metadata.create_all(bind=engine)

seed_roles()
