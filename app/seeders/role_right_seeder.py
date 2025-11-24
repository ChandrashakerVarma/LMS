from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.role_right_m import RoleRight
from app.models.role_m import Role
from app.models.menu_m import Menu

def seed_role_rights():
    """Seed role rights based on updated LMS + HRMS menu structure"""

    db: Session = SessionLocal()

    try:
        # ---------------------------------------------------------
        # 1️⃣ Admin Role -> Full Access
        # ---------------------------------------------------------
        admin_role = db.query(Role).filter_by(name="admin").first()

        if not admin_role:
            print("❌ Admin role not found. Run role_seeder first.")
            return

        all_menus = db.query(Menu).all()

        if not all_menus:
            print("❌ No menus found. Run menu_seeder first.")
            return

        for menu in all_menus:
            exists = db.query(RoleRight).filter_by(
                role_id=admin_role.id,
                menu_id=menu.id
            ).first()

            if not exists:
                db.add(RoleRight(
                    role_id=admin_role.id,
                    menu_id=menu.id,
                    can_view=True,
                    can_create=True,
                    can_edit=True,
                    can_delete=True
                ))

        # ---------------------------------------------------------
        # 2️⃣ User Role -> Very Limited Access
        # ---------------------------------------------------------
        user_role = db.query(Role).filter_by(name="user").first()
        if user_role:
            # Basic user can view dashboard only
            user_view_only_menus = [1]  # Dashboard

            for menu_id in user_view_only_menus:
                exists = db.query(RoleRight).filter_by(
                    role_id=user_role.id,
                    menu_id=menu_id
                ).first()

                if not exists:
                    db.add(RoleRight(
                        role_id=user_role.id,
                        menu_id=menu_id,
                        can_view=True,
                        can_create=False,
                        can_edit=False,
                        can_delete=False
                    ))

        # ---------------------------------------------------------
        # 3️⃣ Manager Role -> Moderate Access
        # ---------------------------------------------------------
        manager_role = db.query(Role).filter_by(name="manager").first()
        if manager_role:
            # Manager accesses updated menus in LMS + HRMS
            manager_permissions = [
                # Dashboard
                (1, True, False, False, False),

                # User Management
                (3, True, True, True, False),  # Users
                (17, True, False, False, False),  # User Reports
                (18, True, False, False, False),  # Active Users
                (19, True, False, False, False),  # Inactive Users

                # Attendance Reports
                (21, True, False, False, False),
                (22, True, False, False, False),
            ]

            for menu_id, can_view, can_create, can_edit, can_delete in manager_permissions:
                exists = db.query(RoleRight).filter_by(
                    role_id=manager_role.id,
                    menu_id=menu_id
                ).first()

                if not exists:
                    db.add(RoleRight(
                        role_id=manager_role.id,
                        menu_id=menu_id,
                        can_view=can_view,
                        can_create=can_create,
                        can_edit=can_edit,
                        can_delete=can_delete
                    ))

        # ---------------------------------------------------------
        # Commit All Changes
        # ---------------------------------------------------------
        db.commit()
        print("✅ Role rights seeded successfully")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding role rights: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_role_rights()
