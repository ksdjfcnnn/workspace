from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.models.employee import Employee
from app.schemas.project import Project as ProjectSchema
from app.services.project_service import ProjectService

router = APIRouter()


@router.get("/", response_model=List[ProjectSchema])
async def get_user_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get projects assigned to current user"""
    project_service = ProjectService(db)
    projects = project_service.get_user_projects(
        employee_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return projects


@router.get("/{project_id}", response_model=ProjectSchema)
async def get_user_project(
    project_id: str,
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific project if user is assigned to it"""
    project_service = ProjectService(db)
    project = project_service.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user is assigned to this project
    user_project_ids = [p.id for p in current_user.projects]
    if project_id not in user_project_ids:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project