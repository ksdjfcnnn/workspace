from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.core.deps import get_current_admin_user
from app.models.employee import Employee
from app.schemas.employee import Employee as EmployeeSchema, EmployeeCreate, EmployeeUpdate, EmployeeInvite, EmployeeStats
from app.services.employee_service import EmployeeService

router = APIRouter()


@router.post("/", response_model=EmployeeSchema)
async def create_employee(
    employee_data: EmployeeInvite,
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new employee and send invitation email"""
    employee_service = EmployeeService(db)
    
    # Use admin's organization
    employee_create_data = EmployeeCreate(
        **employee_data.dict(),
        organizationId=current_admin.organizationId
    )
    
    try:
        employee = employee_service.create_employee(employee_create_data)
        return employee
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[EmployeeSchema])
async def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all employees in the organization"""
    employee_service = EmployeeService(db)
    employees = employee_service.get_employees(
        organization_id=current_admin.organizationId,
        skip=skip,
        limit=limit
    )
    return employees


@router.get("/{employee_id}", response_model=EmployeeSchema)
async def get_employee(
    employee_id: str,
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get employee by ID"""
    employee_service = EmployeeService(db)
    employee = employee_service.get_employee(employee_id)
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check if employee belongs to same organization
    if employee.organizationId != current_admin.organizationId:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return employee


@router.put("/{employee_id}", response_model=EmployeeSchema)
async def update_employee(
    employee_id: str,
    employee_data: EmployeeUpdate,
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update employee by ID"""
    employee_service = EmployeeService(db)
    
    # Check if employee exists and belongs to same organization
    employee = employee_service.get_employee(employee_id)
    if not employee or employee.organizationId != current_admin.organizationId:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    try:
        updated_employee = employee_service.update_employee(employee_id, employee_data)
        if not updated_employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        return updated_employee
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/deactivate/{employee_id}", response_model=EmployeeSchema)
async def deactivate_employee(
    employee_id: str,
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Deactivate employee by ID"""
    employee_service = EmployeeService(db)
    
    # Check if employee exists and belongs to same organization
    employee = employee_service.get_employee(employee_id)
    if not employee or employee.organizationId != current_admin.organizationId:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Prevent admin from deactivating themselves
    if employee_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    
    try:
        deactivated_employee = employee_service.deactivate_employee(employee_id)
        if not deactivated_employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        return deactivated_employee
    except ValueError as e:
        if "already deactivated" in str(e):
            raise HTTPException(status_code=409, detail="Employee is already deactivated")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/activate/{employee_id}", response_model=EmployeeSchema)
async def activate_employee(
    employee_id: str,
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Activate employee by ID"""
    employee_service = EmployeeService(db)
    
    # Check if employee exists and belongs to same organization
    employee = employee_service.get_employee(employee_id)
    if not employee or employee.organizationId != current_admin.organizationId:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    activated_employee = employee_service.activate_employee(employee_id)
    if not activated_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return activated_employee


@router.get("/{employee_id}/stats", response_model=EmployeeStats)
async def get_employee_stats(
    employee_id: str,
    current_admin: Employee = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get employee statistics"""
    employee_service = EmployeeService(db)
    
    # Check if employee exists and belongs to same organization
    employee = employee_service.get_employee(employee_id)
    if not employee or employee.organizationId != current_admin.organizationId:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    stats = employee_service.get_employee_stats(employee_id)
    return stats