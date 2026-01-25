import pytest

from app.models.branch_m import Branch
from app.models.organization_m import Organization


# --------------------------------------------------
# CREATE BRANCH (BASIC)
# --------------------------------------------------
def test_create_branch_basic(db):
    branch = Branch(
        name="Main Branch",
        address="Hyderabad",
        organization_id=1
    )

    db.add(branch)
    db.commit()
    db.refresh(branch)

    assert branch.id is not None
    assert branch.name == "Main Branch"
    assert branch.organization_id == 1


# --------------------------------------------------
# BRANCH MUST BELONG TO ORGANIZATION
# --------------------------------------------------
def test_branch_requires_organization(db):
    branch = Branch(
        name="Invalid Branch",
        address="No Org",
        organization_id=9999   # non-existing org
    )

    db.add(branch)

    with pytest.raises(Exception):
        db.commit()


# --------------------------------------------------
# MULTIPLE BRANCHES SAME ORG
# --------------------------------------------------
def test_multiple_branches_same_org(db):
    branch1 = Branch(
        name="Branch A",
        organization_id=1
    )

    branch2 = Branch(
        name="Branch B",
        organization_id=1
    )

    db.add_all([branch1, branch2])
    db.commit()

    branches = db.query(Branch).filter(
        Branch.organization_id == 1
    ).all()

    assert len(branches) >= 2


# --------------------------------------------------
# UPDATE BRANCH
# --------------------------------------------------
def test_update_branch(db):
    branch = Branch(
        name="Old Name",
        address="Old Address",
        organization_id=1
    )

    db.add(branch)
    db.commit()
    db.refresh(branch)

    branch.name = "New Branch Name"
    branch.address = "New Address"

    db.commit()
    db.refresh(branch)

    assert branch.name == "New Branch Name"
    assert branch.address == "New Address"


# --------------------------------------------------
# DELETE BRANCH
# --------------------------------------------------
def test_delete_branch(db):
    branch = Branch(
        name="Delete Branch",
        organization_id=1
    )

    db.add(branch)
    db.commit()

    branch_id = branch.id

    db.delete(branch)
    db.commit()

    deleted = db.query(Branch).filter(
        Branch.id == branch_id
    ).first()

    assert deleted is None


# --------------------------------------------------
# CASCADE: DELETE ORG → DELETE BRANCH
# --------------------------------------------------
def test_branch_deleted_on_org_delete(db):
    org = Organization(
        name="Temp Org"
    )
    db.add(org)
    db.commit()
    db.refresh(org)

    branch = Branch(
        name="Org Branch",
        organization_id=org.id
    )
    db.add(branch)
    db.commit()

    branch_id = branch.id

    # delete organization
    db.delete(org)
    db.commit()

    deleted_branch = db.query(Branch).filter(
        Branch.id == branch_id
    ).first()

    assert deleted_branch is None
