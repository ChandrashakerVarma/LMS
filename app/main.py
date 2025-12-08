# ==========================================================
# main.py (FINAL MERGED VERSION)
# ==========================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# DB
from app.database import engine, Base

# MODELS
from app.models import (
    user_m, role_m, course_m, video_m, QuizCheckpoint_m, Progress_m,
    QuizHistory_m, enrollment_m, shift_m, department_m, leavemaster_m,
    organization_m, branch_m, category_m, salary_structure_m, payroll_m,
    formula_m, permission_m, attendance_m, payroll_attendance_m,
    job_posting_m, candidate_m, candidate_documents_m, menu_m,
    role_right_m, shift_roster_detail_m, shift_roster_m,
    user_shifts_m, shift_change_request_m, job_description_m,
    notification_m, week_day_m, subscription_plans_m, add_on_m,
    organization_add_on_m, payment_m, attendance_punch_m
)

# ROUTERS (your clean imports kept)
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

# NEW (added from origin/main)
from app.routes.attendance_punch_routes import router as attendance_punch_router
from app.routes.holiday_routes import router as holiday_router

# Job Portal
from app.routes.job_posting_routes import router as job_posting_router
from app.routes.candidate_routes import router as candidate_router
from app.routes.candidates_documents_routes import router as candidate_docs_router
from app.routes.job_description_routes import router as job_description_router
from app.routes.notification_routes import router as notification_router

# AI (manual + ai)
from app.routes.face_routes import router as face_router
from app.routes.attendance_routes import router as attendance_router
from app.routes.ai_attendance_routes import router as ai_attendance_router

# SEEDERS
from app.seeders.role_seeder import seed_roles
from app.seeders.menu_seeder import seed_menus
from app.seeders.role_right_seeder import seed_role_rights
from app.seeders.week_day_seeders import seed_weekdays
from app.seeders.super_admin import seed_super_admin

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
# REGISTER ROUTERS (ORDER CLEAN)
# ==========================================================

# Auth & Users
app.include_router(auth_router)
app.include_router(user_router)

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
app.include_router(attendance_punch_router)
app.include_router(holiday_router)

# Job Portal
app.include_router(job_posting_router)
app.include_router(candidate_router)
app.include_router(candidate_docs_router)
app.include_router(job_description_router)
app.include_router(notification_router)

# Attendance (Manual + AI)
app.include_router(attendance_router)
app.include_router(ai_attendance_router)

# AI Face Registration
app.include_router(face_router)

# ==========================================================
# DB INIT + SEEDERS
# ==========================================================
Base.metadata.create_all(bind=engine)

seed_roles()
seed_menus()
seed_role_rights()
seed_super_admin()
seed_weekdays()
