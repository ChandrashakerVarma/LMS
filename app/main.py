from fastapi import FastAPI
from app.routes import auth_routes, course_routes
from app.routes.admin_dashboard import user_routes
from app.database import engine, Base
from app.models import user_m, role_m  # ✅ import models so tables are registered
from app.seeders.role_seeder import  seed_roles


app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI is running"}

# Admin dashboard
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(course_routes.router)

# ✅ Create tables at startup
# Base.metadata.create_all(bind=engine)

seed_roles()
