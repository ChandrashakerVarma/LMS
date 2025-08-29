from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.models.role_m import Role
from app.database import SessionLocal  # Make sure this points to your session creator


def seed_roles():
    print("🔄 Starting role seeding...")   # LOG
    db = SessionLocal()
    try:
        existing_roles = db.query(Role).all()
        existing_role_names = {r.name.lower() for r in existing_roles}
        print(f"✅ Existing roles in DB: {existing_role_names}")  # LOG

        role_names = ["Admin", "User"]  # add more roles if needed
        new_roles = []
        for role_name in role_names:
            if role_name.lower() not in existing_role_names:
                db.add(Role(name=role_name))
                new_roles.append(role_name)
        
        db.commit()
        if new_roles:
            print(f"✅ Added new roles: {new_roles}")
        else:
            print("ℹ️ No new roles to add, already present.")
        print("🎉 Roles seeding completed.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding roles: {e}")
    finally:
        db.close()
        print("🔒 Database session closed.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("🚀 App starting up...")
    seed_roles()  # automatically runs when app starts
    yield  # The app runs here
    # Shutdown logic (optional)
    print("🛑 App shutting down...")


# attach lifespan to FastAPI
app = FastAPI(lifespan=lifespan)


# Allow standalone execution
if __name__ == "__main__":
    print("▶️ Running as script...")
    seed_roles()
