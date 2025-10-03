from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.role_m import Role


def seed_roles(db: Session):
    """Seed default roles into the database."""
    try:
        existing_roles = db.query(Role).all()
        existing_role_names = {r.name.lower() for r in existing_roles}

        roles_to_seed = ["admin", "user"]
        for role_name in roles_to_seed:
            if role_name.lower() not in existing_role_names:
                db.add(Role(name=role_name))
        
        db.commit()
        print("✅ Roles seeding completed.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding roles: {e}")
        raise


def run_seeder(seeder_func, db: Session, seeder_name: str):
    """Run a single seeder function and handle errors."""
    print(f"Executing seeder: {seeder_name}")
    try:
        seeder_func(db)
        print(f"Successfully executed {seeder_name}")
    except Exception as e:
        print(f"Error executing {seeder_name}: {str(e)}")
        raise


def main():
    """Run all seeders."""
    db = SessionLocal()
    try:
        run_seeder(seed_roles, db, "seed_roles")
    finally:
        db.close()
        print("Database session closed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Seeding failed. Check the error messages above: {str(e)}")
