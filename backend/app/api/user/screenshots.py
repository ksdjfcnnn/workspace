from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.models.employee import Employee
from app.schemas.screenshot import Screenshot as ScreenshotSchema, ScreenshotCreate
from app.services.screenshot_service import ScreenshotService

router = APIRouter()


@router.post("/", response_model=ScreenshotSchema)
async def create_screenshot(
    screenshot_data: ScreenshotCreate,
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new screenshot record"""
    screenshot_service = ScreenshotService(db)
    
    # Validate project and task assignment if provided
    if screenshot_data.projectId:
        user_project_ids = [p.id for p in current_user.projects]
        if screenshot_data.projectId not in user_project_ids:
            raise HTTPException(status_code=400, detail="You are not assigned to this project")
    
    if screenshot_data.taskId:
        user_task_ids = [t.id for t in current_user.tasks]
        if screenshot_data.taskId not in user_task_ids:
            raise HTTPException(status_code=400, detail="You are not assigned to this task")
    
    screenshot = screenshot_service.create_screenshot(
        screenshot_data,
        current_user.id,
        current_user.organizationId
    )
    
    return screenshot


@router.get("/", response_model=List[ScreenshotSchema])
async def get_user_screenshots(
    start_time: int = Query(..., description="Start time in milliseconds"),
    end_time: int = Query(..., description="End time in milliseconds"),
    project_id: Optional[str] = Query(None),
    task_id: Optional[str] = Query(None),
    shift_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get screenshots for current user"""
    screenshot_service = ScreenshotService(db)
    
    screenshots = screenshot_service.get_screenshots(
        organization_id=current_user.organizationId,
        start_time=start_time,
        end_time=end_time,
        employee_id=current_user.id,
        project_id=project_id,
        task_id=task_id,
        shift_id=shift_id,
        limit=limit
    )
    
    return screenshots