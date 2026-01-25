"""
Central seeder runner.
Do NOT change individual seeder files.
"""

def run_all_seeders():
    print("🌱 Running seeders...")

    # Import inside function to avoid circular imports
    from app.seeders.menu_seeder import seed_menus
    from app.seeders.week_day_seeders import seed_weekdays
    from app.seeders.role_seeder import seed_roles
    from app.seeders.role_right_seeder import seed_role_rights
    from app.seeders.super_admin import seed_super_admin

    # IMPORTANT ORDER
    seed_roles()          # Roles first
    seed_menus()          # Menus next
    seed_weekdays()       # Week master
    seed_role_rights()    # Depends on roles + menus
    seed_super_admin()    # Depends on roles

    print("✅ All seeders executed successfully")
