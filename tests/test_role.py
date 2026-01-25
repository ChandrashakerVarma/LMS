import pytest

from app.models.role_m import Role
from app.models.user_m import User


# --------------------------------------------------
# CREATE ROLE (BASIC)
# --------------------------------------------------
def test_create_role_basic(db):
    role = Role(
        name="hr_manager"
    )

    db.add(role)
    db.commit()
    db.refresh(role)

    assert role.id is not None
    assert role.name == "hr_manager"


# --------------------------------------------------
# UNIQUE ROLE NAME CONSTRAINT
# --------------------------------------------------
def test_role_unique_name(db):
    role1 = Role(name="unique_role")
    db.add(role1)
    db.commit()

    role2 = Role(name="unique_role")
    db.add(role2)

    with pytest.raises(Exception):
        db.commit()


# --------------------------------------------------
# MULTIPLE ROLES
# --------------------------------------------------
def test_multiple_roles(db):
    roles = [
        Role(name="admin_role"),
        Role(name="employee_role"),
        Role(name="manager_role")
    ]

    db.add_all(roles)
    db.commit()

    stored_roles = db.query(Role).filter(
        Role.name.in_(["admin_role", "employee_role", "manager_role"])
    ).all()

    assert len(stored_roles) == 3


# --------------------------------------------------
# UPDATE ROLE
# --------------------------------------------------
def test_update_role(db):
    role = Role(name="old_role")
    db.add(role)
    db.commit()
    db.refresh(role)

    role.name = "updated_role"
    db.commit()
    db.refresh(role)

    assert role.name == "updated_role"


# --------------------------------------------------
# DELETE ROLE (NO USERS ATTACHED)
# --------------------------------------------------
def test_delete_role(db):
    role = Role(name="delete_role")
    db.add(role)
    db.commit()

    role_id = role.id

    db.delete(role)
    db.commit()

    deleted = db.query(Role).filter(Role.id == role_id).first()
    assert deleted is None


# --------------------------------------------------
# ROLE ↔ USERS RELATIONSHIP
# --------------------------------------------------
def test_role_user_relationship(db):
    role = Role(name="role_with_users")
    db.add(role)
    db.commit()
    db.refresh(role)

    user = User(
        first_name="Test",
        last_name="User",
        email="roleuser@example.com",
        hashed_password="dummy",
        role_id=role.id
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.role_id == role.id
    assert user.role.name == "role_with_users"
