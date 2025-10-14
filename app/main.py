
from fastapi import FastAPI
from app.routes import auth_routes, course_routes, progress_routes, enrollment_routes, organization_routes, branch_routes, category_routes
from app.routes import user_routes
from app.routes import video_routes, quiz_checkpoint_routes, quiz_history_routes
from app.database import engine, Base
from app.models import user_m, role_m, course_m, video_m, QuizCheckpoint_m, Progress_m, QuizHistory_m, enrollment_m,shift_m, department_m, leavemaster_m
from app.routes import shift_routes,department_routes
from app.routes import leavemaster_routes
from app.models import user_m, role_m, course_m, video_m, QuizCheckpoint_m, Progress_m, QuizHistory_m, enrollment_m, Organization, branch_m, category_m,jobposting_m
from app.seeders.seed_roles import seed_roles
from app.routes import jobposting_routes
from app.routes import workflow_routes
from app.models import workflow_m, jobrole_m,candidate_m, candidate_document_m
from app.routes import jobrole_routes
from app.routes import candidate_routes 
from app.routes import candidate_document_routes
 
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
app.include_router(shift_routes.router)
app.include_router(department_routes.router)
app.include_router(leavemaster_routes.router)
app.include_router(jobposting_routes.router)
app.include_router(workflow_routes.router)
app.include_router(jobrole_routes.router)
app.include_router(candidate_routes.router)
app.include_router(candidate_document_routes.router)
# ✅ Create tables at startup if necessary
Base.metadata.create_all(bind=engine)



# Seed roles at startup
seed_roles()
