from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from app.database import get_db
from app.schema.user_schema import UserCreate, UserResponse, UserUpdate
from app.models.user_m import User
from app.utils.utils import hash_password
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/users", tags=["Users"])

# ⭐ IMPORTANT: MENU ID FOR USERS MODULE
USERS_MENU_ID = 2


# =====================================================
# CREATE USER
# =====================================================
@router.post("/", response_model=UserResponse)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_create_permission(USERS_MENU_ID))
):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        **payload.dict(exclude={"password"}),
        hashed_password=hash_password(payload.password),
        created_by=current_user["first_name"]
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse.model_validate(new_user)


# =====================================================
# GET ALL USERS
# =====================================================
@router.get("/", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_view_permission(USERS_MENU_ID))
):
    users = db.query(User).options(
        selectinload(User.role),
        selectinload(User.branch),
        selectinload(User.organization)
    ).all()

    return [UserResponse.model_validate(u) for u in users]


# =====================================================
# GET SINGLE USER
# =====================================================
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_view_permission(USERS_MENU_ID))
):
    user = db.query(User).options(
        selectinload(User.role),
        selectinload(User.branch),
        selectinload(User.organization)
    ).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, detail="User not found")

    return UserResponse.model_validate(user)


# =====================================================
# UPDATE USER
# =====================================================
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    updated_user: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_edit_permission(USERS_MENU_ID))
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, detail="User not found")

    update_data = updated_user.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    user.modified_by = current_user["first_name"]
    db.commit()
    db.refresh(user)

    return UserResponse.model_validate(user)


# =====================================================
# DELETE USER
# =====================================================
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_delete_permission(USERS_MENU_ID))
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}


# =====================================================
# ASSIGN SHIFT ROSTER → ALL USERS OF ROLE
# =====================================================
@router.put("/assign-shift/{role_id}/{shift_roster_id}")
def assign_shift_to_role(
    role_id: int,
    shift_roster_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_edit_permission(USERS_MENU_ID))
):
    users = db.query(User).filter(User.role_id == role_id).all()

    if not users:
        raise HTTPException(404, detail="No users found with this role")

    for user in users:
        user.shift_roster_id = shift_roster_id
        user.modified_by = current_user["first_name"]

    db.commit()

    return {
        "message": "Shift roster assigned to all users of the role",
        "role_id": role_id,
        "shift_roster_id": shift_roster_id,
        "total_updated_users": len(users)
    }


# =====================================================
# ASSIGN SHIFT ROSTER → SINGLE USER
# =====================================================
@router.patch("/update-shift/{user_id}/{shift_roster_id}")
def update_user_shift_roster(
    user_id: int,
    shift_roster_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_edit_permission(USERS_MENU_ID))
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, detail="User not found")

    user.shift_roster_id = shift_roster_id
    user.modified_by = current_user["first_name"]

    db.commit()
    db.refresh(user)

    return {
        "message": "Shift roster updated for the user",
        "user_id": user_id,
        "shift_roster_id": shift_roster_id
    }
