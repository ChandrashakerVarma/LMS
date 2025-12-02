# CORRECTED app/main.py
# ✅ Fixed: unified_search_routes now registered AFTER app creation

from fastapi import FastAPI
from app.routes import auth_routes, course_routes, progress_routes, enrollment_routes, role_routes
from app.routes.admin_dashboard import user_routes
from app.routes import video_routes, quiz_checkpoint_routes, quiz_history_routes, branch_routes, organization_routes
from app.routes import categorys_routes, formula_routes, permission_routes, attendance_routes, menu_routes, role_right_routes, shift_summery_routes
from app.database import engine, Base
from app.models import user_m, role_m, course_m, video_m, QuizCheckpoint_m, Progress_m, QuizHistory_m, enrollment_m, shift_m, department_m, leavemaster_m
from app.models import organization_m, branch_m, category_m, salary_structure_m, payroll_m, formula_m, permission_m, attendance_m, payroll_attendance_m
from app.models import job_posting_m, candidate_m, candidate_documents_m, menu_m, role_right_m
from app.seeders.role_seeder import seed_roles
from app.seeders.menu_seeder import seed_menus
from app.seeders.role_right_seeder import seed_role_rights
from app.seeders.week_day_seeders import seed_weekdays
from app.seeders.super_admin import seed_super_admin
from app.routes import shift_routes, department_routes
from app.routes import leavemaster_routes, salary_structure_routes, payroll_routes, payroll_attendance_routes, user_shifts_routes, shift_change_request_routes
from app.routes import job_posting_routes, candidate_routes, candidates_documents_routes, shift_roster_detail_routes, shift_roster_routes
from app.models import job_description_m, notification_m
from app.routes import job_description_routes, notification_routes

# ✅ NEW: Import unified search routes
from app.routes import unified_search_routes

# ✅ CRITICAL: Create FastAPI app FIRST
app = FastAPI()

# Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI is running"}

# ✅ Register all routers AFTER app creation
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(role_routes.router)
app.include_router(organization_routes.router)
app.include_router(branch_routes.router)
app.include_router(menu_routes.router)
app.include_router(role_right_routes.router)
app.include_router(enrollment_routes.router)
app.include_router(categorys_routes.router)
app.include_router(course_routes.router)
app.include_router(video_routes.router)
app.include_router(quiz_checkpoint_routes.router)
app.include_router(quiz_history_routes.router)
app.include_router(progress_routes.router)
app.include_router(department_routes.router)

app.include_router(job_posting_routes.router)
app.include_router(job_description_routes.router)
app.include_router(candidate_routes.router)
app.include_router(candidates_documents_routes.router)
app.include_router(notification_routes.router)

app.include_router(shift_routes.router)
app.include_router(user_shifts_routes.router)
app.include_router(shift_change_request_routes.router)
app.include_router(attendance_routes.router)
app.include_router(leavemaster_routes.router)
app.include_router(shift_roster_routes.router)
app.include_router(shift_roster_detail_routes.router)
app.include_router(permission_routes.router)
app.include_router(salary_structure_routes.router)
app.include_router(formula_routes.router)
app.include_router(payroll_routes.router)
app.include_router(payroll_attendance_routes.router)
app.include_router(shift_summery_routes.router)

# ✅ NEW: Register unified search router (searches ALL entities at once!)
app.include_router(unified_search_routes.router)

# ✅ Create tables at startup if necessary
Base.metadata.create_all(bind=engine)

seed_roles()
seed_menus()
seed_role_rights()
seed_super_admin()
seed_weekdays()