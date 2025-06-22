from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.db.database import get_db
from app.core.deps import get_current_admin_user
from app.models.employee import Employee
from app.services.shift_service import ShiftService
from app.services.screenshot_service import ScreenshotService
from app.schemas.screenshot import ScreenshotResponse

router = APIRouter()


@router.get("/project-time")
async def get_project_time_analytics(
    start: int = Query(..., description="Start time in milliseconds"),
    end: int = Query(..., description="End time in milliseconds"),
    timezone: Optional[str] = Query(None),
    employeeId: Optional[str] = Query(None),
    teamId: Optional[str] = Query(None),
    projectId: Optional[str] = Query(None),
    taskId: Optional[str] = Query(None),
    shiftId: Optional[str] = Query(None),
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get project time analytics"""
    shift_service = ShiftService(db)
    
    analytics = shift_service.get_project_time_analytics(
        organization_id=current_admin.organizationId,
        start_time=start,
        end_time=end,
        employee_id=employeeId,
        team_id=teamId,
        project_id=projectId,
        task_id=taskId,
        shift_id=shiftId
    )
    
    return analytics


@router.get("/screenshot")
async def get_screenshots(
    start: int = Query(..., description="Start time in milliseconds"),
    end: int = Query(..., description="End time in milliseconds"),
    limit: int = Query(15, ge=1, le=100),
    employeeId: Optional[str] = Query(None),
    teamId: Optional[str] = Query(None),
    projectId: Optional[str] = Query(None),
    taskId: Optional[str] = Query(None),
    shiftId: Optional[str] = Query(None),
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get screenshots with filters"""
    screenshot_service = ScreenshotService(db)
    
    screenshots = screenshot_service.get_screenshots(
        organization_id=current_admin.organizationId,
        start_time=start,
        end_time=end,
        employee_id=employeeId,
        team_id=teamId,
        project_id=projectId,
        task_id=taskId,
        shift_id=shiftId,
        limit=limit
    )
    
    return screenshots


@router.get("/screenshot-paginate", response_model=ScreenshotResponse)
async def get_screenshots_paginated(
    start: int = Query(..., description="Start time in milliseconds"),
    end: int = Query(..., description="End time in milliseconds"),
    timezone: Optional[str] = Query(None),
    taskId: Optional[str] = Query(None),
    shiftId: Optional[str] = Query(None),
    projectId: Optional[str] = Query(None),
    employeeId: Optional[str] = Query(None),
    teamId: Optional[str] = Query(None),
    sortBy: Optional[str] = Query("timestamp"),
    limit: int = Query(10000, ge=1, le=10000),
    next: Optional[str] = Query(None, description="Next token for pagination"),
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get screenshots with pagination"""
    screenshot_service = ScreenshotService(db)
    
    result = screenshot_service.get_screenshots_paginated(
        organization_id=current_admin.organizationId,
        start_time=start,
        end_time=end,
        employee_id=employeeId,
        team_id=teamId,
        project_id=projectId,
        task_id=taskId,
        shift_id=shiftId,
        limit=limit,
        next_token=next,
        sort_by=sortBy
    )
    
    return result


@router.delete("/screenshot/{screenshot_id}")
async def delete_screenshot(
    screenshot_id: str,
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete screenshot by ID"""
    screenshot_service = ScreenshotService(db)
    
    # Check if screenshot exists and belongs to same organization
    screenshot = screenshot_service.get_screenshot(screenshot_id)
    if not screenshot or screenshot.organizationId != current_admin.organizationId:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    
    deleted_screenshot = screenshot_service.delete_screenshot(screenshot_id)
    if not deleted_screenshot:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    
    return {"message": "Screenshot deleted successfully"}