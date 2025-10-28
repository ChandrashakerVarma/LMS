<<<<<<< HEAD

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

=======
from fastapi import FastAPI
from app.routes import auth_routes, course_routes, progress_routes, enrollment_routes
from app.routes.admin_dashboard import user_routes
from app.routes import video_routes, quiz_checkpoint_routes, quiz_history_routes, branch_routes, organization_routes
from app.routes import categorys_routes, formula_routes
from app.database import engine, Base
from app.models import user_m, role_m, course_m, video_m, QuizCheckpoint_m, Progress_m, QuizHistory_m, enrollment_m,shift_m, department_m, leavemaster_m
from app.models import organization, branch_m, category_m, salary_structure_m, payroll_m, formula_m
from app.seeders.role_seeder import seed_roles
from app.routes import shift_routes,department_routes
from app.routes import leavemaster_routes, salary_structure_routes, payroll_routes

 
app = FastAPI()

# Base.metadata.create_all(bind=engine)

>>>>>>> origin/main
@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI is running"}

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(organization_routes.router)
app.include_router(branch_routes.router)
app.include_router(enrollment_routes.router)
<<<<<<< HEAD
app.include_router(category_routes.router)
=======
app.include_router(categorys_routes.router)
>>>>>>> origin/main
app.include_router(course_routes.router)
app.include_router(video_routes.router)
app.include_router(quiz_checkpoint_routes.router)
app.include_router(quiz_history_routes.router)
app.include_router(progress_routes.router)
app.include_router(shift_routes.router)
app.include_router(department_routes.router)
app.include_router(leavemaster_routes.router)
<<<<<<< HEAD
app.include_router(jobposting_routes.router)
app.include_router(workflow_routes.router)
app.include_router(jobrole_routes.router)
app.include_router(candidate_routes.router)
app.include_router(candidate_document_routes.router)
# ✅ Create tables at startup if necessary
Base.metadata.create_all(bind=engine)



# Seed roles at startup
=======
app.include_router(salary_structure_routes.router)
app.include_router(formula_routes.router)
app.include_router(payroll_routes.router)
# ✅ Create tables at startup if necessary
Base.metadata.create_all(bind=engine)

>>>>>>> origin/main
seed_roles()
