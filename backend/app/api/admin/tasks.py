from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.core.deps import get_current_admin_user
from app.models.employee import Employee
from app.schemas.task import Task as TaskSchema, TaskCreate, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter()


@router.post("/", response_model=TaskSchema)
async def create_task(
    task_data: TaskCreate,
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new task"""
    task_service = TaskService(db)
    
    try:
        task = task_service.create_task(
            task_data, 
            current_admin.id, 
            current_admin.organizationId
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[TaskSchema])
async def get_tasks(
    project_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all tasks in the organization, optionally filtered by project"""
    task_service = TaskService(db)
    tasks = task_service.get_tasks(
        organization_id=current_admin.organizationId,
        project_id=project_id,
        skip=skip,
        limit=limit
    )
    return tasks


@router.get("/{task_id}", response_model=TaskSchema)
async def get_task(
    task_id: str,
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get task by ID"""
    task_service = TaskService(db)
    task = task_service.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if task belongs to same organization
    if task.organizationId != current_admin.organizationId:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.put("/{task_id}", response_model=TaskSchema)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update task by ID"""
    task_service = TaskService(db)
    
    # Check if task exists and belongs to same organization
    task = task_service.get_task(task_id)
    if not task or task.organizationId != current_admin.organizationId:
        raise HTTPException(status_code=404, detail="Task not found")
    
    try:
        updated_task = task_service.update_task(task_id, task_data)
        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")
        return updated_task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{task_id}", response_model=TaskSchema)
async def delete_task(
    task_id: str,
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete task by ID"""
    task_service = TaskService(db)
    
    # Check if task exists and belongs to same organization
    task = task_service.get_task(task_id)
    if not task or task.organizationId != current_admin.organizationId:
        raise HTTPException(status_code=404, detail="Task not found")
    
    try:
        deleted_task = task_service.delete_task(task_id)
        if not deleted_task:
            raise HTTPException(status_code=404, detail="Task not found")
        return deleted_task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))