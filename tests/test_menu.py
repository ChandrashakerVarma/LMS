import pytest

from app.models.menu_m import Menu


# --------------------------------------------------
# CREATE MENU (BASIC)
# --------------------------------------------------
def test_create_menu_basic(db):
    menu = Menu(
        name="attendance",
        display_name="Attendance",
        route="/attendance",
        icon="calendar",
        created_by="TestUser"
    )

    db.add(menu)
    db.commit()
    db.refresh(menu)

    assert menu.id is not None
    assert menu.name == "attendance"
    assert menu.display_name == "Attendance"
    assert menu.is_active is True


# --------------------------------------------------
# CREATE MENU WITHOUT OPTIONAL FIELDS
# --------------------------------------------------
def test_create_menu_minimal(db):
    menu = Menu(
        name="dashboard",
        display_name="Dashboard"
    )

    db.add(menu)
    db.commit()
    db.refresh(menu)

    assert menu.id is not None
    assert menu.route is None
    assert menu.icon is None


# --------------------------------------------------
# PARENT → CHILD MENU RELATIONSHIP
# --------------------------------------------------
def test_menu_parent_child_relationship(db):
    parent = Menu(
        name="leave",
        display_name="Leave Management"
    )

    db.add(parent)
    db.commit()
    db.refresh(parent)

    child = Menu(
        name="leave_apply",
        display_name="Apply Leave",
        parent_id=parent.id
    )

    db.add(child)
    db.commit()
    db.refresh(child)

    assert child.parent_id == parent.id
    assert child.parent.id == parent.id
    assert child in parent.children


# --------------------------------------------------
# UPDATE MENU
# --------------------------------------------------
def test_update_menu(db):
    menu = Menu(
        name="reports",
        display_name="Reports"
    )

    db.add(menu)
    db.commit()
    db.refresh(menu)

    menu.display_name = "Reports & Analytics"
    menu.modified_by = "AdminUser"
    menu.is_active = False

    db.commit()
    db.refresh(menu)

    assert menu.display_name == "Reports & Analytics"
    assert menu.modified_by == "AdminUser"
    assert menu.is_active is False


# --------------------------------------------------
# DELETE MENU (CASCADE SAFE)
# --------------------------------------------------
def test_delete_menu(db):
    menu = Menu(
        name="settings",
        display_name="Settings"
    )

    db.add(menu)
    db.commit()

    menu_id = menu.id

    db.delete(menu)
    db.commit()

    deleted = db.query(Menu).filter(
        Menu.id == menu_id
    ).first()

    assert deleted is None


# --------------------------------------------------
# MENU ORDER DEFAULT
# --------------------------------------------------
def test_menu_order_default(db):
    menu = Menu(
        name="profile",
        display_name="Profile"
    )

    db.add(menu)
    db.commit()
    db.refresh(menu)

    assert menu.menu_order == 0
