from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.models.employee import Employee
from app.schemas.employee import Employee as EmployeeSchema, EmployeeStats
from app.services.employee_service import EmployeeService

router = APIRouter()


@router.get("/me", response_model=EmployeeSchema)
async def get_current_user_profile(
    current_user: Employee = Depends(get_current_active_user)
):
    """Get current user's profile"""
    return current_user


@router.get("/me/stats", response_model=EmployeeStats)
async def get_current_user_stats(
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's statistics"""
    employee_service = EmployeeService(db)
    stats = employee_service.get_employee_stats(current_user.id)
    return stats