from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.models.employee import Employee
from app.schemas.task import Task as TaskSchema
from app.services.task_service import TaskService

router = APIRouter()


@router.get("/", response_model=List[TaskSchema])
async def get_user_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get tasks assigned to current user"""
    task_service = TaskService(db)
    tasks = task_service.get_user_tasks(
        employee_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return tasks


@router.get("/{task_id}", response_model=TaskSchema)
async def get_user_task(
    task_id: str,
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific task if user is assigned to it"""
    task_service = TaskService(db)
    task = task_service.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if user is assigned to this task
    user_task_ids = [t.id for t in current_user.tasks]
    if task_id not in user_task_ids:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task