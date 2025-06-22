from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.core.deps import get_current_admin_user
from app.models.employee import Employee
from app.schemas.project import Project as ProjectSchema, ProjectCreate, ProjectUpdate, ProjectStats
from app.services.project_service import ProjectService

router = APIRouter()


@router.post("/", response_model=ProjectSchema)
async def create_project(
    project_data: ProjectCreate,
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new project"""
    project_service = ProjectService(db)
    
    # Use admin's organization
    project_data.organizationId = current_admin.organizationId
    
    try:
        project = project_service.create_project(project_data, current_admin.id)
        return project
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ProjectSchema])
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all projects in the organization"""
    project_service = ProjectService(db)
    projects = project_service.get_projects(
        organization_id=current_admin.organizationId,
        skip=skip,
        limit=limit
    )
    return projects


@router.get("/{project_id}", response_model=ProjectSchema)
async def get_project(
    project_id: str,
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get project by ID"""
    project_service = ProjectService(db)
    project = project_service.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if project belongs to same organization
    if project.organizationId != current_admin.organizationId:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project


@router.put("/{project_id}", response_model=ProjectSchema)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update project by ID"""
    project_service = ProjectService(db)
    
    # Check if project exists and belongs to same organization
    project = project_service.get_project(project_id)
    if not project or project.organizationId != current_admin.organizationId:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        updated_project = project_service.update_project(project_id, project_data)
        if not updated_project:
            raise HTTPException(status_code=404, detail="Project not found")
        return updated_project
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{project_id}", response_model=ProjectSchema)
async def delete_project(
    project_id: str,
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete project by ID"""
    project_service = ProjectService(db)
    
    # Check if project exists and belongs to same organization
    project = project_service.get_project(project_id)
    if not project or project.organizationId != current_admin.organizationId:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        deleted_project = project_service.delete_project(project_id)
        if not deleted_project:
            raise HTTPException(status_code=404, detail="Project not found")
        return deleted_project
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}/stats", response_model=ProjectStats)
async def get_project_stats(
    project_id: str,
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get project statistics"""
    project_service = ProjectService(db)
    
    # Check if project exists and belongs to same organization
    project = project_service.get_project(project_id)
    if not project or project.organizationId != current_admin.organizationId:
        raise HTTPException(status_code=404, detail="Project not found")
    
    stats = project_service.get_project_stats(project_id)
    return stats