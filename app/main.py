# ==========================================================
# main.py (FINAL MERGED VERSION)
# ==========================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# DB
from app.database import engine, Base
<<<<<<< HEAD

# MODELS (Required for SQLAlchemy)
from app.models import (
    user_m, role_m, course_m, video_m, QuizCheckpoint_m, Progress_m,
    QuizHistory_m, enrollment_m, shift_m, department_m, leavemaster_m,
    organization_m, branch_m, category_m, salary_structure_m, payroll_m,
    formula_m, permission_m, attendance_m, payroll_attendance_m,
    job_posting_m, candidate_m, candidate_documents_m, menu_m,
    role_right_m, shift_roster_detail_m, shift_roster_m,
    user_shifts_m, shift_change_request_m, job_description_m, notification_m
)

# ROUTERS
from app.routes.auth_routes import router as auth_router
from app.routes.user_routes import router as user_router
from app.routes.role_routes import router as role_router
from app.routes.organization_routes import router as organization_router
from app.routes.branch_routes import router as branch_router
from app.routes.menu_routes import router as menu_router
from app.routes.role_right_routes import router as role_right_router
from app.routes.enrollment_routes import router as enrollment_router
from app.routes.categorys_routes import router as category_router
from app.routes.course_routes import router as course_router
from app.routes.video_routes import router as video_router
from app.routes.quiz_checkpoint_routes import router as quiz_checkpoint_router
from app.routes.quiz_history_routes import router as quiz_history_router
from app.routes.progress_routes import router as progress_router

# HRMS
from app.routes.department_routes import router as department_router
from app.routes.leavemaster_routes import router as leavemaster_router
from app.routes.shift_routes import router as shift_router
from app.routes.user_shifts_routes import router as user_shift_router
from app.routes.shift_change_request_routes import router as shift_change_router
from app.routes.shift_roster_routes import router as roster_router
from app.routes.shift_roster_detail_routes import router as roster_detail_router
from app.routes.salary_structure_routes import router as salary_router
from app.routes.formula_routes import router as formula_router
from app.routes.payroll_routes import router as payroll_router
from app.routes.payroll_attendance_routes import router as payroll_attendance_router
from app.routes.shift_summery_routes import router as shift_summary_router

# Job Portal
from app.routes.job_posting_routes import router as job_posting_router
from app.routes.candidate_routes import router as candidate_router
from app.routes.candidates_documents_routes import router as candidate_docs_router
from app.routes.job_description_routes import router as job_description_router
from app.routes.notification_routes import router as notification_router

# AI
from app.routes.face_routes import router as face_router
from app.routes.attendance_routes import router as attendance_router
from app.routes.ai_attendance_routes import router as ai_attendance_router

# SEEDERS
=======
from app.models import user_m, role_m, course_m, video_m, QuizCheckpoint_m, Progress_m, QuizHistory_m, enrollment_m,shift_m, department_m, leavemaster_m, user_shifts_m, shift_change_request_m
from app.models import organization_m, branch_m, category_m, salary_structure_m, payroll_m, formula_m, permission_m, attendance_m, payroll_attendance_m, shift_roster_detail_m, shift_roster_m
from app.models import job_posting_m, candidate_m, candidate_documents_m,menu_m, role_right_m, holiday_m, notification_m, job_description_m, shift_roster_m, user_shifts_m, shift_change_request_m, attendance_punch_m
>>>>>>> origin/main
from app.seeders.role_seeder import seed_roles
from app.seeders.menu_seeder import seed_menus
from app.seeders.role_right_seeder import seed_role_rights
from app.seeders.week_day_seeders import seed_weekdays
from app.seeders.super_admin import seed_super_admin
<<<<<<< HEAD
=======
from app.routes import shift_routes,department_routes
from app.routes import leavemaster_routes, salary_structure_routes, payroll_routes, payroll_attendance_routes, user_shifts_routes, shift_change_request_routes
from app.routes import job_posting_routes,candidate_routes,candidates_documents_routes,shift_roster_detail_routes,shift_roster_routes
from app.models import job_description_m, notification_m
from app.routes import job_description_routes,notification_routes
from app.routes import shift_routes,department_routes, enrollment_routes, shift_summery_routes, attendance_routes, attendance_punch_routes, permission_routes, formula_routes, shift_change_request_routes, user_shifts_routes, holiday_routes
from app.routes import leavemaster_routes, salary_structure_routes, payroll_routes, payroll_attendance_routes, user_shifts_routes, shift_change_request_routes, shift_routes, attendance_routes, department_routes, branch_routes, organization_routes
from app.routes import job_posting_routes, candidate_routes, candidates_documents_routes,shift_roster_detail_routes,shift_roster_routes, notification_routes, job_description_routes, leavemaster_routes, salary_structure_routes, payroll_routes
from app.routes import holiday_routes, attendance_punch_routes

>>>>>>> origin/main

# ==========================================================
# APP INITIALIZATION
# ==========================================================
app = FastAPI(title="LMS + HRMS + AI Attendance Backend")

# ==========================================================
# CORS
# ==========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# ROOT
# ==========================================================
@app.get("/")
def root():
    return {"status": "ok", "message": "LMS + HRMS + AI Attendance Running 🚀"}

# ==========================================================
# REGISTER ROUTERS (CLEAN ORDER)
# ==========================================================

# Auth & Users
app.include_router(auth_router)
app.include_router(user_router)

<<<<<<< HEAD
# Core Admin
app.include_router(role_router)
app.include_router(organization_router)
app.include_router(branch_router)
app.include_router(menu_router)
app.include_router(role_right_router)

# LMS
app.include_router(category_router)
app.include_router(course_router)
app.include_router(video_router)
app.include_router(enrollment_router)
app.include_router(progress_router)
app.include_router(quiz_checkpoint_router)
app.include_router(quiz_history_router)

# HRMS
app.include_router(department_router)
app.include_router(leavemaster_router)
app.include_router(shift_router)
app.include_router(shift_summary_router)
app.include_router(user_shift_router)
app.include_router(shift_change_router)
app.include_router(roster_router)
app.include_router(roster_detail_router)
app.include_router(salary_router)
app.include_router(formula_router)
app.include_router(payroll_router)
app.include_router(payroll_attendance_router)

# Job Portal
app.include_router(job_posting_router)
app.include_router(candidate_router)
app.include_router(candidate_docs_router)
app.include_router(job_description_router)
app.include_router(notification_router)

# Attendance (Manual + AI)
app.include_router(attendance_router)         # /attendance/
app.include_router(ai_attendance_router)      # /attendance/ai-checkin

# AI Face Registration
app.include_router(face_router)

# ==========================================================
# DB INIT + SEEDERS
# ==========================================================
=======
app.include_router(shift_routes.router)
app.include_router(shift_change_request_routes.router)
app.include_router(attendance_punch_routes.router)
app.include_router(attendance_routes.router)
app.include_router(leavemaster_routes.router)
app.include_router(holiday_routes.router)
app.include_router(permission_routes.router)

app.include_router(user_shifts_routes.router)
app.include_router(shift_roster_routes.router)
app.include_router(shift_roster_detail_routes.router)
app.include_router(shift_summery_routes.router)

app.include_router(salary_structure_routes.router)
app.include_router(formula_routes.router)
app.include_router(payroll_routes.router)
app.include_router(payroll_attendance_routes.router)

# ✅ Create tables at startup if necessary
>>>>>>> origin/main
Base.metadata.create_all(bind=engine)

# Seed core data
seed_roles()
seed_menus()
seed_role_rights()
seed_super_admin()
<<<<<<< HEAD
seed_weekdays()
=======
seed_weekdays()
>>>>>>> origin/main
