from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.menu_m import Menu
<<<<<<< HEAD
from app.schemas.menu_schema import MenuCreate, MenuUpdate, MenuResponse, MenuTreeResponse
=======
from app.schema.menu_schema import MenuCreate, MenuUpdate, MenuResponse, MenuTreeResponse
>>>>>>> origin/main
from app.dependencies import require_org_admin, get_current_user
from app.models.user_m import User

router = APIRouter(prefix="/menus", tags=["Menus"])


# ---------------- CREATE MENU ----------------
@router.post("/", response_model=MenuResponse, status_code=status.HTTP_201_CREATED)
def create_menu(
    payload: MenuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org_admin)
):
    if payload.parent_id:
        parent_menu = db.query(Menu).filter(Menu.id == payload.parent_id).first()
        if not parent_menu:
            raise HTTPException(status_code=404, detail="Parent menu not found")

    new_menu = Menu(
        name=payload.name,
        display_name=payload.display_name,
        route=payload.route,
        icon=payload.icon,
        parent_id=payload.parent_id,
        menu_order=payload.menu_order,
        is_active=payload.is_active,
        created_by=current_user.email,
        modified_by=current_user.email
    )

    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)
    return new_menu


# ---------------- GET ALL MENUS (FLAT) ----------------
@router.get("/", response_model=List[MenuResponse])
def get_all_menus(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    menus = db.query(Menu).order_by(Menu.menu_order).all()
    return menus


# ---------------- GET MENU TREE ----------------
@router.get("/tree", response_model=List[MenuTreeResponse])
def get_menu_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    all_menus = (
        db.query(Menu)
        .filter(Menu.is_active == True)
        .order_by(Menu.menu_order)
        .all()
    )

    # Build dict for quick lookup
    menu_dict = {menu.id: MenuTreeResponse.from_orm(menu) for menu in all_menus}

    # Add children
    for menu in all_menus:
        node = menu_dict[menu.id]
        node.children = [
            menu_dict[m.id] for m in all_menus if m.parent_id == menu.id
        ]

    # Return root menus only
    return [menu_dict[m.id] for m in all_menus if m.parent_id is None]


# ---------------- GET USER MENUS (ROLE-BASED) ----------------
@router.get("/user-menus", response_model=List[MenuTreeResponse])
def get_user_menus(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.role_right_m import RoleRight

    accessible_menu_ids = (
        db.query(RoleRight.menu_id)
        .filter(
            RoleRight.role_id == current_user.role_id,
            RoleRight.can_view == True
        )
        .all()
    )

    menu_ids = [m[0] for m in accessible_menu_ids]

    if not menu_ids:
        return []

    accessible_menus = (
        db.query(Menu)
        .filter(Menu.id.in_(menu_ids), Menu.is_active == True)
        .order_by(Menu.menu_order)
        .all()
    )

    menu_dict = {menu.id: MenuTreeResponse.from_orm(menu) for menu in accessible_menus}

    for menu_id, menu_data in menu_dict.items():
        menu_data.children = [
            child for child in menu_dict.values()
            if child.parent_id == menu_id
        ]

    return [menu for menu in menu_dict.values() if menu.parent_id is None]


# ---------------- GET MENU BY ID ----------------
@router.get("/{menu_id}", response_model=MenuResponse)
def get_menu_by_id(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return menu


# ---------------- UPDATE MENU ----------------
@router.put("/{menu_id}", response_model=MenuResponse)
def update_menu(
    menu_id: int,
    payload: MenuUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org_admin)
):
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    update_data = payload.dict(exclude_unset=True)

    # Validate parent
    if "parent_id" in update_data and update_data["parent_id"]:
        if update_data["parent_id"] == menu_id:
            raise HTTPException(status_code=400, detail="Menu cannot be its own parent")

        parent = db.query(Menu).filter(Menu.id == update_data["parent_id"]).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent menu not found")

    for key, value in update_data.items():
        setattr(menu, key, value)

    menu.modified_by = current_user.email

    db.commit()
    db.refresh(menu)
    return menu


# ---------------- DELETE MENU ----------------
@router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org_admin)
):
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    children = db.query(Menu).filter(Menu.parent_id == menu_id).first()
    if children:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete menu with children. Delete children first."
        )

    db.delete(menu)
    db.commit()
    return None
