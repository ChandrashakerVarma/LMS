import pytest
from sqlalchemy.orm import Session

from app.models.leaveconfig_m import LeaveConfig
from app.models.leavetype_m import LeaveType
from tests.test_database import TestingSessionLocal

def test_create_leave_config_basic():
    """
    Create a basic leave config for a leave type
    """
    db: Session = TestingSessionLocal()

    config = LeaveConfig(
        leave_type_id=1,   # Casual Leave (seeded in conftest)
        per_month=1,
        no_of_leaves=12,
        carry_forward=False,
        created_by="test-system"
    )

    db.add(config)
    db.commit()
    db.refresh(config)

    assert config.id is not None
    assert config.leave_type_id == 1
    assert config.per_month == 1
    assert config.no_of_leaves == 12
    assert config.carry_forward is False

    db.close()


def test_leave_config_with_carry_forward():
    """
    Leave config with carry forward enabled
    """
    db: Session = TestingSessionLocal()

    config = LeaveConfig(
        leave_type_id=2,   # Sick Leave (seeded)
        per_month=1,
        no_of_leaves=10,
        carry_forward=True,
        created_by="test-system"
    )

    db.add(config)
    db.commit()
    db.refresh(config)

    assert config.carry_forward is True
    assert config.no_of_leaves == 10

    db.close()


def test_fetch_leave_config_by_leave_type():
    """
    Fetch leave config using leave_type_id
    """
    db: Session = TestingSessionLocal()

    config = (
        db.query(LeaveConfig)
        .filter(LeaveConfig.leave_type_id == 1)
        .first()
    )

    assert config is not None
    assert config.leave_type_id == 1

    db.close()


def test_update_leave_config():
    """
    Update existing leave config values
    """
    db: Session = TestingSessionLocal()

    config = (
        db.query(LeaveConfig)
        .filter(LeaveConfig.leave_type_id == 1)
        .first()
    )

    assert config is not None

    config.no_of_leaves = 15
    config.modified_by = "test-admin"

    db.commit()
    db.refresh(config)

    assert config.no_of_leaves == 15
    assert config.modified_by == "test-admin"

    db.close()


def test_multiple_leave_configs():
    """
    Multiple leave configs for different leave types
    """
    db: Session = TestingSessionLocal()

    configs = db.query(LeaveConfig).all()

    assert len(configs) >= 2

    leave_type_ids = {cfg.leave_type_id for cfg in configs}
    assert 1 in leave_type_ids
    assert 2 in leave_type_ids

    db.close()


def test_leave_config_invalid_leave_type():
    """
    Leave config with invalid leave_type_id should fail
    """
    db: Session = TestingSessionLocal()

    invalid_config = LeaveConfig(
        leave_type_id=9999,   # ❌ does not exist
        per_month=1,
        no_of_leaves=5,
        carry_forward=False,
        created_by="test-system"
    )

    db.add(invalid_config)

    with pytest.raises(Exception):
        db.commit()

    db.rollback()
    db.close()
