import pytest

from app.models.role_right_m import RoleRight
from app.models.role_m import Role
from app.models.menu_m import Menu


# --------------------------------------------------
# Helper: create valid menu (NO NULL columns)
# --------------------------------------------------
def create_menu(name: str):
    return Menu(
        name=name,
        display_name=name,   # 🔥 REQUIRED
        is_active=True
    )


# --------------------------------------------------
# CREATE ROLE RIGHT (BASIC)
# --------------------------------------------------
def test_create_role_right_basic(db):
    role = Role(name="rr_basic_role")
    menu = create_menu("Dashboard")

    db.add_all([role, menu])
    db.commit()
    db.refresh(role)
    db.refresh(menu)

    rr = RoleRight(
        role_id=role.id,
        menu_id=menu.id,
        can_view=True,
        can_create=True,
        created_by="TestUser"
    )

    db.add(rr)
    db.commit()
    db.refresh(rr)

    assert rr.id is not None
    assert rr.role_id == role.id
    assert rr.menu_id == menu.id
    assert rr.can_view is True
    assert rr.can_create is True


# --------------------------------------------------
# UNIQUE CONSTRAINT (role_id + menu_id)
# --------------------------------------------------
def test_role_right_unique_constraint(db):
    role = Role(name="rr_unique_role")
    menu = create_menu("Users")

    db.add_all([role, menu])
    db.commit()
    db.refresh(role)
    db.refresh(menu)

    rr1 = RoleRight(
        role_id=role.id,
        menu_id=menu.id,
        can_view=True
    )
    db.add(rr1)
    db.commit()

    rr2 = RoleRight(
        role_id=role.id,
        menu_id=menu.id,
        can_edit=True
    )
    db.add(rr2)

    with pytest.raises(Exception):
        db.commit()


# --------------------------------------------------
# UPDATE ROLE RIGHT
# --------------------------------------------------
def test_update_role_right(db):
    role = Role(name="rr_update_role")
    menu = create_menu("Settings")

    db.add_all([role, menu])
    db.commit()
    db.refresh(role)
    db.refresh(menu)

    rr = RoleRight(
        role_id=role.id,
        menu_id=menu.id,
        can_view=True
    )
    db.add(rr)
    db.commit()
    db.refresh(rr)

    rr.can_edit = True
    rr.can_delete = True
    rr.modified_by = "AdminUser"

    db.commit()
    db.refresh(rr)

    assert rr.can_edit is True
    assert rr.can_delete is True
    assert rr.modified_by == "AdminUser"


# --------------------------------------------------
# DELETE ROLE RIGHT
# --------------------------------------------------
def test_delete_role_right(db):
    role = Role(name="rr_delete_role")
    menu = create_menu("Reports")

    db.add_all([role, menu])
    db.commit()
    db.refresh(role)
    db.refresh(menu)

    rr = RoleRight(
        role_id=role.id,
        menu_id=menu.id
    )

    db.add(rr)
    db.commit()

    rr_id = rr.id

    db.delete(rr)
    db.commit()

    deleted = db.query(RoleRight).filter(
        RoleRight.id == rr_id
    ).first()

    assert deleted is None


# --------------------------------------------------
# CASCADE DELETE (ROLE → ROLE RIGHTS)
# --------------------------------------------------
def test_role_right_deleted_on_role_delete(db):
    role = Role(name="rr_cascade_role")
    menu = create_menu("Leaves")

    db.add_all([role, menu])
    db.commit()
    db.refresh(role)
    db.refresh(menu)

    rr = RoleRight(
        role_id=role.id,
        menu_id=menu.id,
        can_view=True
    )

    db.add(rr)
    db.commit()

    rr_id = rr.id

    db.delete(role)
    db.commit()

    deleted_rr = db.query(RoleRight).filter(
        RoleRight.id == rr_id
    ).first()

    assert deleted_rr is None


# --------------------------------------------------
# RELATIONSHIP VALIDATION
# --------------------------------------------------
def test_role_right_relationships(db):
    role = Role(name="rr_relation_role")
    menu = create_menu("Attendance")

    db.add_all([role, menu])
    db.commit()
    db.refresh(role)
    db.refresh(menu)

    rr = RoleRight(
        role_id=role.id,
        menu_id=menu.id,
        can_view=True
    )

    db.add(rr)
    db.commit()
    db.refresh(rr)

    assert rr.role.name == "rr_relation_role"
    assert rr.menu.display_name == "Attendance"
