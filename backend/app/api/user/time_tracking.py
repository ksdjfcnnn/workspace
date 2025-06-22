from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.models.employee import Employee
from app.schemas.shift import Shift as ShiftSchema, ShiftStart, ShiftEnd
from app.services.shift_service import ShiftService

router = APIRouter()


@router.post("/start", response_model=ShiftSchema)
async def start_time_tracking(
    shift_data: ShiftStart,
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start time tracking for current user"""
    shift_service = ShiftService(db)
    
    # Validate project and task assignment if provided
    if shift_data.projectId:
        user_project_ids = [p.id for p in current_user.projects]
        if shift_data.projectId not in user_project_ids:
            raise HTTPException(status_code=400, detail="You are not assigned to this project")
    
    if shift_data.taskId:
        user_task_ids = [t.id for t in current_user.tasks]
        if shift_data.taskId not in user_task_ids:
            raise HTTPException(status_code=400, detail="You are not assigned to this task")
    
    try:
        shift = shift_service.start_shift(
            shift_data, 
            current_user.id, 
            current_user.organizationId
        )
        return shift
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/end", response_model=ShiftSchema)
async def end_time_tracking(
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """End current active time tracking session"""
    shift_service = ShiftService(db)
    
    # Get active shift
    active_shift = shift_service.get_active_shift(current_user.id)
    if not active_shift:
        raise HTTPException(status_code=400, detail="No active time tracking session found")
    
    try:
        shift = shift_service.end_shift(active_shift.id, current_user.id)
        if not shift:
            raise HTTPException(status_code=404, detail="Shift not found")
        return shift
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/active", response_model=ShiftSchema)
async def get_active_shift(
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current active time tracking session"""
    shift_service = ShiftService(db)
    
    active_shift = shift_service.get_active_shift(current_user.id)
    if not active_shift:
        raise HTTPException(status_code=404, detail="No active time tracking session")
    
    return active_shift


@router.get("/history", response_model=List[ShiftSchema])
async def get_time_tracking_history(
    project_id: Optional[str] = Query(None),
    task_id: Optional[str] = Query(None),
    start_time: Optional[int] = Query(None),
    end_time: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get time tracking history for current user"""
    shift_service = ShiftService(db)
    
    shifts = shift_service.get_shifts(
        organization_id=current_user.organizationId,
        employee_id=current_user.id,
        project_id=project_id,
        task_id=task_id,
        start_time=start_time,
        end_time=end_time,
        skip=skip,
        limit=limit
    )
    
    return shifts