from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.database import get_db
from app.models.category_m import Category
from app.schema.category_schema import CategoryResponse, CategoryCreate, CategoryUpdate
from app.schema.course_schema import CourseResponse

from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])

MENU_ID = 33   # Category Module ID


# ----------------------
# Create a category
# ----------------------
@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_create_permission(MENU_ID))
):
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    new_category = Category(**category.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    cat_data = CategoryResponse.from_orm(new_category)
    cat_data.courses = []
    return cat_data


# ----------------------
# List all categories (Read)
# ----------------------
@router.get("/", response_model=List[CategoryResponse])
async def get_all_categories(
    # ✅ NEW: Fuzzy search parameters
    use_fuzzy_search: bool = Query(False, description="Enable fuzzy search"),
    fuzzy_query: Optional[str] = Query(None, description="Fuzzy search query"),
    fuzzy_threshold: int = Query(70, ge=50, le=100),
    
    # Your existing parameters
    skip: int = 0,
    limit: int = 100,
    
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all categories with OPTIONAL fuzzy search
    
    Searches across: name, description
    """
    
    query = db.query(Category)
    
    # Your existing filters here
    
    if use_fuzzy_search and fuzzy_query:
        from app.utils.fuzzy_search import apply_fuzzy_search_to_query
        
        search_fields = ['name', 'description']
        field_weights = {
            'name': 2.5,
            'description': 1.0
        }
        
        categories = apply_fuzzy_search_to_query(
            base_query=query,
            model_class=Category,
            fuzzy_query=fuzzy_query,
            search_fields=search_fields,
            field_weights=field_weights,
            fuzzy_threshold=fuzzy_threshold
        )
        
        categories = categories[skip:skip + limit]
    else:
        categories = query.offset(skip).limit(limit).all()
    
    return categories
# ----------------------
# Get a single category (Read)
# ----------------------
@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_view_permission(MENU_ID))
):
    category = db.query(Category).options(joinedload(Category.courses)).filter(
        Category.id == category_id
    ).first()

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
    current_user = Depends(require_edit_permission(MENU_ID))
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
    current_user = Depends(require_delete_permission(MENU_ID))
):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()

    return {"message": "Category deleted successfully"}
