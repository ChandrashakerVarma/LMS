import pytest
from datetime import date

from app.models.organization_m import Organization
from app.models.subscription_plans_m import SubscriptionPlan


# --------------------------------------------------
# CREATE ORGANIZATION (BASIC)
# --------------------------------------------------
def test_create_organization_basic(db):
    org = Organization(
        name="Test Organization A",
        description="Test org description",
        created_by="TestUser"
    )

    db.add(org)
    db.commit()
    db.refresh(org)

    assert org.id is not None
    assert org.is_active is True
    assert org.branch_limit == 2
    assert org.user_limit == 10


# --------------------------------------------------
# UNIQUE NAME CONSTRAINT
# --------------------------------------------------
def test_organization_unique_name(db):
    db.add(Organization(name="Unique Org", created_by="TestUser"))
    db.commit()

    db.add(Organization(name="Unique Org", created_by="TestUser"))
    with pytest.raises(Exception):
        db.commit()


# --------------------------------------------------
# SUBSCRIPTION FIELDS (USE SEEDED PLAN)
# --------------------------------------------------
def test_organization_subscription_fields(db):
    plan = db.query(SubscriptionPlan).filter_by(id=1).first()
    assert plan is not None

    org = Organization(
        name="Subscription Org",
        plan_id=plan.id,
        subscription_status="active",
        subscription_start_date=date(2025, 1, 1),
        subscription_end_date=date(2025, 12, 31),
        created_by="TestUser"
    )

    db.add(org)
    db.commit()
    db.refresh(org)

    assert org.plan_id == plan.id
    assert org.subscription_status == "active"


# --------------------------------------------------
# USAGE TRACKING DEFAULTS
# --------------------------------------------------
def test_organization_usage_defaults(db):
    org = Organization(name="Usage Org", created_by="TestUser")
    db.add(org)
    db.commit()
    db.refresh(org)

    assert org.current_branches == 0
    assert org.current_users == 0
    assert org.current_storage_mb == 0


# --------------------------------------------------
# BILLING FIELDS
# --------------------------------------------------
def test_organization_billing_fields(db):
    org = Organization(
        name="Billing Org",
        last_payment_date=date(2025, 2, 1),
        next_billing_date=date(2025, 3, 1),
        total_amount_paid=5000.00,
        created_by="TestUser"
    )

    db.add(org)
    db.commit()
    db.refresh(org)

    assert float(org.total_amount_paid) == 5000.00


# --------------------------------------------------
# UPDATE ORGANIZATION
# --------------------------------------------------
def test_update_organization(db):
    org = Organization(name="Update Org", created_by="TestUser")
    db.add(org)
    db.commit()

    org.name = "Updated Org Name"
    org.modified_by = "AdminUser"
    org.is_active = False
    db.commit()
    db.refresh(org)

    assert org.is_active is False
    assert org.modified_by == "AdminUser"


# --------------------------------------------------
# DELETE ORGANIZATION
# --------------------------------------------------
def test_delete_organization(db):
    org = Organization(name="Delete Org", created_by="TestUser")
    db.add(org)
    db.commit()

    org_id = org.id
    db.delete(org)
    db.commit()

    assert db.query(Organization).filter_by(id=org_id).first() is None
