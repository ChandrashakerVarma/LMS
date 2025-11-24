from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.menu_m import Menu

def seed_menus():
    """Seed initial menu structure with main menus, submenus, and inner menus"""

    menus = [
        # ------------------------------
        # BASE SYSTEM MENUS (Your Old Menus)
        # ------------------------------
        {"id": 1, "name": "dashboard", "display_name": "Dashboard", "route": "/dashboard", "icon": "dashboard", "parent_id": None, "menu_order": 1},

        # USER MANAGEMENT
        {"id": 2, "name": "user_management", "display_name": "User Management", "route": None, "icon": "people", "parent_id": None, "menu_order": 2},
        {"id": 3, "name": "users", "display_name": "Users", "route": "/users", "icon": "person", "parent_id": 2, "menu_order": 1},
        {"id": 4, "name": "roles", "display_name": "Roles", "route": "/roles", "icon": "security", "parent_id": 2, "menu_order": 2},
        {"id": 5, "name": "permissions", "display_name": "Permissions", "route": "/permissions", "icon": "lock", "parent_id": 2, "menu_order": 3},

        # ORGANIZATION
        {"id": 6, "name": "organization", "display_name": "Organization", "route": None, "icon": "business", "parent_id": None, "menu_order": 3},
        {"id": 7, "name": "organizations", "display_name": "Organizations", "route": "/organizations", "icon": "domain", "parent_id": 6, "menu_order": 1},
        {"id": 8, "name": "branches", "display_name": "Branches", "route": "/branches", "icon": "store", "parent_id": 6, "menu_order": 2},
        {"id": 9, "name": "departments", "display_name": "Departments", "route": "/departments", "icon": "corporate_fare", "parent_id": 6, "menu_order": 3},

        # MENU MANAGEMENT
        {"id": 10, "name": "menu_management", "display_name": "Menu Management", "route": None, "icon": "menu", "parent_id": None, "menu_order": 4},
        {"id": 11, "name": "menus", "display_name": "Menus", "route": "/menus", "icon": "list", "parent_id": 10, "menu_order": 1},
        {"id": 12, "name": "role_rights", "display_name": "Role Rights", "route": "/role-rights", "icon": "admin_panel_settings", "parent_id": 10, "menu_order": 2},

        # SETTINGS
        {"id": 13, "name": "settings", "display_name": "Settings", "route": None, "icon": "settings", "parent_id": None, "menu_order": 5},
        {"id": 14, "name": "general_settings", "display_name": "General Settings", "route": "/settings/general", "icon": "tune", "parent_id": 13, "menu_order": 1},
        {"id": 15, "name": "system_settings", "display_name": "System Settings", "route": "/settings/system", "icon": "settings_applications", "parent_id": 13, "menu_order": 2},

        # REPORTS
        {"id": 16, "name": "reports", "display_name": "Reports", "route": None, "icon": "assessment", "parent_id": None, "menu_order": 6},
        {"id": 17, "name": "user_reports", "display_name": "User Reports", "route": None, "icon": "people_outline", "parent_id": 16, "menu_order": 1},
        {"id": 18, "name": "active_users_report", "display_name": "Active Users", "route": "/reports/users/active", "icon": "check_circle", "parent_id": 17, "menu_order": 1},
        {"id": 19, "name": "inactive_users_report", "display_name": "Inactive Users", "route": "/reports/users/inactive", "icon": "cancel", "parent_id": 17, "menu_order": 2},
        {"id": 20, "name": "attendance_reports", "display_name": "Attendance Reports", "route": None, "icon": "event_available", "parent_id": 16, "menu_order": 2},
        {"id": 21, "name": "daily_attendance", "display_name": "Daily Attendance", "route": "/reports/attendance/daily", "icon": "today", "parent_id": 20, "menu_order": 1},
        {"id": 22, "name": "monthly_attendance", "display_name": "Monthly Attendance", "route": "/reports/attendance/monthly", "icon": "calendar_month", "parent_id": 20, "menu_order": 2},

        # ----------------------------------------
        # LMS MODULE MENUS (Courses, Videos, Quiz)
        # ----------------------------------------
        {"id": 30, "name": "lms", "display_name": "LMS", "route": None, "icon": "school", "parent_id": None, "menu_order": 7},

        {"id": 31, "name": "courses", "display_name": "Courses", "route": "/courses", "icon": "menu_book", "parent_id": 30, "menu_order": 1},
        {"id": 32, "name": "videos", "display_name": "Videos", "route": "/videos", "icon": "video_library", "parent_id": 30, "menu_order": 2},
        {"id": 33, "name": "categories", "display_name": "Categories", "route": "/categories", "icon": "category", "parent_id": 30, "menu_order": 3},
        {"id": 34, "name": "enrollments", "display_name": "Enrollments", "route": "/enrollments", "icon": "how_to_reg", "parent_id": 30, "menu_order": 4},
        {"id": 35, "name": "quiz_checkpoints", "display_name": "Quiz Checkpoints", "route": "/quiz-checkpoints", "icon": "question_answer", "parent_id": 30, "menu_order": 5},
        {"id": 36, "name": "quiz_history", "display_name": "Quiz History", "route": "/quiz-history", "icon": "history", "parent_id": 30, "menu_order": 6},
        {"id": 37, "name": "progress", "display_name": "Progress", "route": "/progress", "icon": "trending_up", "parent_id": 30, "menu_order": 7},

        # ----------------------------------------
        # HRMS MODULE MENUS (Attendance, Shifts, Payroll)
        # ----------------------------------------
        {"id": 40, "name": "hrms", "display_name": "HRMS", "route": None, "icon": "badge", "parent_id": None, "menu_order": 8},

        {"id": 41, "name": "shifts", "display_name": "Shifts", "route": "/shifts", "icon": "schedule", "parent_id": 40, "menu_order": 1},
        {"id": 42, "name": "user_shifts", "display_name": "User Shifts", "route": "/user-shifts", "icon": "supervisor_account", "parent_id": 40, "menu_order": 2},
        {"id": 43, "name": "shift_change_requests", "display_name": "Shift Change Requests", "route": "/shift-change-requests", "icon": "swap_horiz", "parent_id": 40, "menu_order": 3},

        {"id": 44, "name": "attendance", "display_name": "Attendance", "route": "/attendance", "icon": "event", "parent_id": 40, "menu_order": 4},
        {"id": 45, "name": "leave_master", "display_name": "Leave Master", "route": "/leave-master", "icon": "beach_access", "parent_id": 40, "menu_order": 5},
        {"id": 46, "name": "permissions_module", "display_name": "Permissions", "route": "/hrms-permissions", "icon": "vpn_key", "parent_id": 40, "menu_order": 6},

        {"id": 47, "name": "salary_structure", "display_name": "Salary Structure", "route": "/salary-structure", "icon": "account_balance_wallet", "parent_id": 40, "menu_order": 7},
        {"id": 48, "name": "formulas", "display_name": "Formulas", "route": "/formulas", "icon": "functions", "parent_id": 40, "menu_order": 8},
        {"id": 49, "name": "payroll", "display_name": "Payroll", "route": "/payroll", "icon": "monetization_on", "parent_id": 40, "menu_order": 9},
        {"id": 50, "name": "payroll_attendance", "display_name": "Payroll Attendance", "route": "/payroll-attendance", "icon": "fact_check", "parent_id": 40, "menu_order": 10},

        # ----------------------------------------
        # HIRING MODULE (Job Posting, Workflow, Candidates)
        # ----------------------------------------
        {"id": 60, "name": "hiring", "display_name": "Hiring", "route": None, "icon": "work", "parent_id": None, "menu_order": 9},

        {"id": 61, "name": "job_postings", "display_name": "Job Postings", "route": "/job-postings", "icon": "work_outline", "parent_id": 60, "menu_order": 1},
        {"id": 62, "name": "job_roles", "display_name": "Job Roles", "route": "/job-roles", "icon": "badge", "parent_id": 60, "menu_order": 2},
        {"id": 63, "name": "workflows", "display_name": "Workflows", "route": "/workflows", "icon": "timeline", "parent_id": 60, "menu_order": 3},
        {"id": 64, "name": "candidates", "display_name": "Candidates", "route": "/candidates", "icon": "person_search", "parent_id": 60, "menu_order": 4},
        {"id": 65, "name": "candidate_documents", "display_name": "Candidate Documents", "route": "/candidate-documents", "icon": "folder", "parent_id": 60, "menu_order": 5},
    ]

    db: Session = SessionLocal()

    try:
        for menu_data in menus:
            existing = db.query(Menu).filter_by(id=menu_data["id"]).first()
            if not existing:
                db.add(Menu(**menu_data))

        db.commit()
        print("✅ Menus seeded successfully")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding menus: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_menus()
