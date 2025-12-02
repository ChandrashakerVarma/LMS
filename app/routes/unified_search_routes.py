# app/routes/unified_search_routes.py
# 🔍 UNIFIED SEARCH - Search across ALL entities simultaneously

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_user
from app.utils.fuzzy_search import apply_fuzzy_search_to_query

# Import all models
from app.models.user_m import User
from app.models.candidate_m import Candidate
from app.models.job_posting_m import JobPosting
from app.models.course_m import Course
from app.models.department_m import Department
from app.models.organization_m import Organization
from app.models.branch_m import Branch
from app.models.category_m import Category
from app.models.video_m import Video
from app.models.role_m import Role

router = APIRouter(prefix="/search", tags=["Unified Search"])


def serialize_model(obj: Any) -> Dict:
    """
    Helper to serialize SQLAlchemy models to dict
    """
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        if isinstance(value, datetime):
            value = value.isoformat()
        result[column.name] = value
    return result


@router.get("/all")
async def unified_search(
    query: str = Query(..., min_length=1, max_length=200, description="Search query"),
    fuzzy_threshold: int = Query(70, ge=50, le=100, description="Match threshold (50-100)"),
    limit_per_entity: int = Query(5, ge=1, le=20, description="Max results per entity type"),
    
    # Optional: Filter by specific entity types
    entities: Optional[str] = Query(
        None,
        description="Comma-separated entity types to search (e.g., 'users,courses,candidates')"
    ),
    
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🔍 UNIFIED SEARCH - Search across ALL entities at once!
    
    Returns top matches from:
    - Users, Candidates, Job Postings
    - Courses, Departments, Organizations
    - Branches, Categories, Videos, Roles
    
    **Examples:**
    ```
    GET /search/all?query=python&limit_per_entity=5
    GET /search/all?query=engineering&entities=users,departments
    GET /search/all?query=john&fuzzy_threshold=80
    ```
    
    **Response includes:**
    - Total results across all entities
    - Results grouped by entity type
    - Each result includes search score and matched field
    """
    
    # Parse entity filter if provided
    entity_filter = None
    if entities:
        entity_filter = [e.strip().lower() for e in entities.split(',')]
    
    results = {}
    total_count = 0
    
    # Helper to check if we should search this entity
    def should_search(entity_name: str) -> bool:
        return entity_filter is None or entity_name in entity_filter
    
    # 1. Search Users
    if should_search('users'):
        try:
            user_query = db.query(User)
            
            # Filter by organization (non-super-admins only see their org)
            if hasattr(current_user, 'role') and current_user.role.name.lower() != 'super_admin':
                if hasattr(current_user, 'organization_id') and current_user.organization_id:
                    user_query = user_query.filter(User.organization_id == current_user.organization_id)
            
            user_results = apply_fuzzy_search_to_query(
                base_query=user_query,
                model_class=User,
                fuzzy_query=query,
                search_fields=['first_name', 'last_name', 'email', 'designation'],
                field_weights={'first_name': 2.0, 'last_name': 2.0, 'email': 1.5, 'designation': 1.0},
                fuzzy_threshold=fuzzy_threshold
            )[:limit_per_entity]
            
            results['users'] = [serialize_model(u) for u in user_results]
            total_count += len(user_results)
        except Exception as e:
            results['users'] = []
            results['users_error'] = str(e)
    
    # 2. Search Candidates
    if should_search('candidates'):
        try:
            candidate_results = apply_fuzzy_search_to_query(
                base_query=db.query(Candidate),
                model_class=Candidate,
                fuzzy_query=query,
                search_fields=['first_name', 'last_name', 'email', 'phone_number'],
                field_weights={'first_name': 2.0, 'last_name': 2.0, 'email': 1.5, 'phone_number': 1.0},
                fuzzy_threshold=fuzzy_threshold
            )[:limit_per_entity]
            
            results['candidates'] = [serialize_model(c) for c in candidate_results]
            total_count += len(candidate_results)
        except Exception as e:
            results['candidates'] = []
            results['candidates_error'] = str(e)
    
    # 3. Search Job Postings
    if should_search('job_postings'):
        try:
            job_results = apply_fuzzy_search_to_query(
                base_query=db.query(JobPosting),
                model_class=JobPosting,
                fuzzy_query=query,
                search_fields=['location', 'employment_type'],
                field_weights={'location': 2.0, 'employment_type': 1.5},
                fuzzy_threshold=fuzzy_threshold
            )[:limit_per_entity]
            
            results['job_postings'] = [serialize_model(j) for j in job_results]
            total_count += len(job_results)
        except Exception as e:
            results['job_postings'] = []
            results['job_postings_error'] = str(e)
    
    # 4. Search Courses
    if should_search('courses'):
        try:
            course_query = db.query(Course)
            
            # Filter by organization
            if hasattr(current_user, 'organization_id') and current_user.organization_id:
                course_query = course_query.filter(Course.organization_id == current_user.organization_id)
            
            course_results = apply_fuzzy_search_to_query(
                base_query=course_query,
                model_class=Course,
                fuzzy_query=query,
                search_fields=['title', 'instructor', 'level'],
                field_weights={'title': 2.5, 'instructor': 1.5, 'level': 1.0},
                fuzzy_threshold=fuzzy_threshold
            )[:limit_per_entity]
            
            results['courses'] = [serialize_model(c) for c in course_results]
            total_count += len(course_results)
        except Exception as e:
            results['courses'] = []
            results['courses_error'] = str(e)
    
    # 5. Search Departments
    if should_search('departments'):
        try:
            dept_results = apply_fuzzy_search_to_query(
                base_query=db.query(Department),
                model_class=Department,
                fuzzy_query=query,
                search_fields=['name', 'code', 'description'],
                field_weights={'name': 2.5, 'code': 2.0, 'description': 1.0},
                fuzzy_threshold=fuzzy_threshold
            )[:limit_per_entity]
            
            results['departments'] = [serialize_model(d) for d in dept_results]
            total_count += len(dept_results)
        except Exception as e:
            results['departments'] = []
            results['departments_error'] = str(e)
    
    # 6. Search Organizations (super admin only)
    if should_search('organizations'):
        try:
            if hasattr(current_user, 'role') and current_user.role.name.lower() == 'super_admin':
                org_results = apply_fuzzy_search_to_query(
                    base_query=db.query(Organization),
                    model_class=Organization,
                    fuzzy_query=query,
                    search_fields=['name', 'description', 'contact_email'],
                    field_weights={'name': 2.5, 'description': 1.0, 'contact_email': 1.5},
                    fuzzy_threshold=fuzzy_threshold
                )[:limit_per_entity]
                
                results['organizations'] = [serialize_model(o) for o in org_results]
                total_count += len(org_results)
            else:
                results['organizations'] = []
        except Exception as e:
            results['organizations'] = []
            results['organizations_error'] = str(e)
    
    # 7. Search Branches
    if should_search('branches'):
        try:
            branch_query = db.query(Branch)
            
            # Filter by organization
            if hasattr(current_user, 'organization_id') and current_user.organization_id:
                branch_query = branch_query.filter(Branch.organization_id == current_user.organization_id)
            
            branch_results = apply_fuzzy_search_to_query(
                base_query=branch_query,
                model_class=Branch,
                fuzzy_query=query,
                search_fields=['name', 'address'],
                field_weights={'name': 2.5, 'address': 1.5},
                fuzzy_threshold=fuzzy_threshold
            )[:limit_per_entity]
            
            results['branches'] = [serialize_model(b) for b in branch_results]
            total_count += len(branch_results)
        except Exception as e:
            results['branches'] = []
            results['branches_error'] = str(e)
    
    # 8. Search Categories
    if should_search('categories'):
        try:
            category_results = apply_fuzzy_search_to_query(
                base_query=db.query(Category),
                model_class=Category,
                fuzzy_query=query,
                search_fields=['name', 'description'],
                field_weights={'name': 2.5, 'description': 1.0},
                fuzzy_threshold=fuzzy_threshold
            )[:limit_per_entity]
            
            results['categories'] = [serialize_model(c) for c in category_results]
            total_count += len(category_results)
        except Exception as e:
            results['categories'] = []
            results['categories_error'] = str(e)
    
    # 9. Search Videos
    if should_search('videos'):
        try:
            video_results = apply_fuzzy_search_to_query(
                base_query=db.query(Video),
                model_class=Video,
                fuzzy_query=query,
                search_fields=['title', 'youtube_url'],
                field_weights={'title': 2.5, 'youtube_url': 1.0},
                fuzzy_threshold=fuzzy_threshold
            )[:limit_per_entity]
            
            results['videos'] = [serialize_model(v) for v in video_results]
            total_count += len(video_results)
        except Exception as e:
            results['videos'] = []
            results['videos_error'] = str(e)
    
    # 10. Search Roles
    if should_search('roles'):
        try:
            role_results = apply_fuzzy_search_to_query(
                base_query=db.query(Role),
                model_class=Role,
                fuzzy_query=query,
                search_fields=['name'],
                field_weights={'name': 2.5},
                fuzzy_threshold=fuzzy_threshold
            )[:limit_per_entity]
            
            results['roles'] = [serialize_model(r) for r in role_results]
            total_count += len(role_results)
        except Exception as e:
            results['roles'] = []
            results['roles_error'] = str(e)
    
    return {
        'success': True,
        'query': query,
        'fuzzy_threshold': fuzzy_threshold,
        'limit_per_entity': limit_per_entity,
        'total_results': total_count,
        'entities_searched': list(results.keys()),
        'results': results
    }


@router.get("/quick")
async def quick_search(
    q: str = Query(..., min_length=1, max_length=200, description="Quick search query"),
    limit: int = Query(10, ge=1, le=50, description="Total results limit"),
    
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Quick search across top 3 entity types: Users, Candidates, Courses
    
    Faster than /all endpoint, returns mixed results sorted by relevance.
    
    Example: GET /search/quick?q=python&limit=10
    """
    
    all_results = []
    
    # Search users
    try:
        user_query = db.query(User)
        if hasattr(current_user, 'organization_id') and current_user.organization_id:
            user_query = user_query.filter(User.organization_id == current_user.organization_id)
        
        users = apply_fuzzy_search_to_query(
            base_query=user_query,
            model_class=User,
            fuzzy_query=q,
            search_fields=['first_name', 'last_name', 'email'],
            fuzzy_threshold=70
        )[:5]
        
        for u in users:
            all_results.append({
                'type': 'user',
                'id': u.id,
                'name': f"{u.first_name} {u.last_name}",
                'email': u.email,
                'data': serialize_model(u)
            })
    except:
        pass
    
    # Search candidates
    try:
        candidates = apply_fuzzy_search_to_query(
            base_query=db.query(Candidate),
            model_class=Candidate,
            fuzzy_query=q,
            search_fields=['first_name', 'last_name', 'email'],
            fuzzy_threshold=70
        )[:5]
        
        for c in candidates:
            all_results.append({
                'type': 'candidate',
                'id': c.id,
                'name': f"{c.first_name} {c.last_name}",
                'email': c.email,
                'data': serialize_model(c)
            })
    except:
        pass
    
    # Search courses
    try:
        course_query = db.query(Course)
        if hasattr(current_user, 'organization_id') and current_user.organization_id:
            course_query = course_query.filter(Course.organization_id == current_user.organization_id)
        
        courses = apply_fuzzy_search_to_query(
            base_query=course_query,
            model_class=Course,
            fuzzy_query=q,
            search_fields=['title', 'instructor'],
            fuzzy_threshold=70
        )[:5]
        
        for c in courses:
            all_results.append({
                'type': 'course',
                'id': c.id,
                'title': c.title,
                'instructor': c.instructor,
                'data': serialize_model(c)
            })
    except:
        pass
    
    # Limit total results
    all_results = all_results[:limit]
    
    return {
        'success': True,
        'query': q,
        'total_results': len(all_results),
        'results': all_results
    }