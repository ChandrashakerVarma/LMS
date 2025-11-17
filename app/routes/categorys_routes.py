from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app.models.category_m import Category
from app.schema.category_schema import CategoryResponse, CategoryCreate, CategoryUpdate
from app.schema.course_schema import CourseResponse
from app.dependencies import require_admin, get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])

# ----------------------
# Create a category
# ----------------------
@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    new_category = Category(**category.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    cat_data = CategoryResponse.from_orm(new_category)
    cat_data.courses = []  # no courses yet
    return cat_data

# ----------------------
# List all categories with courses
# ----------------------
@router.get("/", response_model=List[CategoryResponse])
def categories_list(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    categories = db.query(Category).options(joinedload(Category.courses)).all()
    
    result = []
    for cat in categories:
        cat_data = CategoryResponse.from_orm(cat)
        cat_data.courses = [CourseResponse.from_orm(course) for course in cat.courses]
        result.append(cat_data)
    return result

# ----------------------
# Get a single category
# ----------------------
@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).options(joinedload(Category.courses)).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    cat_data = CategoryResponse.from_orm(category)
    cat_data.courses = [CourseResponse.from_orm(course) for course in category.courses]
    return cat_data

# ----------------------
# Update a category
# ----------------------
@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    
    db.commit()
    db.refresh(category)

    cat_data = CategoryResponse.from_orm(category)
    cat_data.courses = [CourseResponse.from_orm(course) for course in category.courses]
    return cat_data

# ----------------------
# Delete a category
# ----------------------
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}
