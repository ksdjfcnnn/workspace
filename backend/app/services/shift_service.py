from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_
from app.models.shift import Shift
from app.models.employee import Employee
from app.schemas.shift import ShiftCreate, ShiftUpdate, ShiftStart
from datetime import datetime
from typing import List, Optional, Dict, Any


class ShiftService:
    def __init__(self, db: Session):
        self.db = db

    def start_shift(self, shift_data: ShiftStart, employee_id: str, organization_id: str) -> Shift:
        """Start a new time tracking shift"""
        # Check if user has any active shifts
        active_shift = self.db.query(Shift).filter(
            and_(Shift.employeeId == employee_id, Shift.end.is_(None))
        ).first()
        
        if active_shift:
            raise ValueError("Employee already has an active shift. Please end the current shift first.")
        
        current_time = int(datetime.utcnow().timestamp() * 1000)
        
        # Get employee info for shift details
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        
        db_shift = Shift(
            type="manual",
            start=current_time,
            timezoneOffset=shift_data.timezoneOffset or 0,
            name=shift_data.name,
            employeeId=employee_id,
            teamId=employee.teamId,
            organizationId=organization_id,
            projectId=shift_data.projectId,
            taskId=shift_data.taskId,
            user=employee.name,
            startTranslated=current_time + (shift_data.timezoneOffset or 0)
        )
        
        self.db.add(db_shift)
        self.db.commit()
        self.db.refresh(db_shift)
        return db_shift

    def end_shift(self, shift_id: str, employee_id: str) -> Optional[Shift]:
        """End a time tracking shift"""
        db_shift = self.db.query(Shift).filter(
            and_(Shift.id == shift_id, Shift.employeeId == employee_id)
        ).first()
        
        if not db_shift:
            return None
        
        if db_shift.end:
            raise ValueError("Shift is already ended")
        
        current_time = int(datetime.utcnow().timestamp() * 1000)
        db_shift.end = current_time
        db_shift.endTranslated = current_time + db_shift.timezoneOffset
        db_shift.lastActivityEnd = current_time
        db_shift.lastActivityEndTranslated = current_time + db_shift.timezoneOffset
        
        self.db.commit()
        self.db.refresh(db_shift)
        return db_shift

    def get_active_shift(self, employee_id: str) -> Optional[Shift]:
        """Get employee's active shift"""
        return self.db.query(Shift).filter(
            and_(Shift.employeeId == employee_id, Shift.end.is_(None))
        ).first()

    def get_shift(self, shift_id: str) -> Optional[Shift]:
        """Get shift by ID"""
        return self.db.query(Shift).filter(Shift.id == shift_id).first()

    def get_shifts(
        self, 
        organization_id: str,
        employee_id: str = None,
        project_id: str = None,
        task_id: str = None,
        start_time: int = None,
        end_time: int = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Shift]:
        """Get shifts with optional filters"""
        query = self.db.query(Shift).filter(Shift.organizationId == organization_id)
        
        if employee_id:
            query = query.filter(Shift.employeeId == employee_id)
        
        if project_id:
            query = query.filter(Shift.projectId == project_id)
        
        if task_id:
            query = query.filter(Shift.taskId == task_id)
        
        if start_time:
            query = query.filter(Shift.start >= start_time)
        
        if end_time:
            query = query.filter(
                or_(Shift.end <= end_time, Shift.end.is_(None))
            )
        
        return query.order_by(Shift.start.desc()).offset(skip).limit(limit).all()

    def update_shift(self, shift_id: str, shift_data: ShiftUpdate, employee_id: str) -> Optional[Shift]:
        """Update shift"""
        db_shift = self.db.query(Shift).filter(
            and_(Shift.id == shift_id, Shift.employeeId == employee_id)
        ).first()
        
        if not db_shift:
            return None
        
        update_data = shift_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_shift, field, value)
        
        self.db.commit()
        self.db.refresh(db_shift)
        return db_shift

    def get_project_time_analytics(
        self,
        organization_id: str,
        start_time: int,
        end_time: int,
        employee_id: str = None,
        team_id: str = None,
        project_id: str = None,
        task_id: str = None,
        shift_id: str = None
    ) -> Dict[str, Any]:
        """Get project time analytics"""
        query = self.db.query(Shift).filter(
            and_(
                Shift.organizationId == organization_id,
                Shift.start >= start_time,
                or_(Shift.end <= end_time, Shift.end.is_(None)),
                Shift.end.isnot(None)  # Only completed shifts
            )
        )
        
        if employee_id:
            query = query.filter(Shift.employeeId == employee_id)
        
        if team_id:
            query = query.filter(Shift.teamId == team_id)
        
        if project_id:
            query = query.filter(Shift.projectId == project_id)
        
        if task_id:
            query = query.filter(Shift.taskId == task_id)
        
        if shift_id:
            query = query.filter(Shift.id == shift_id)
        
        shifts = query.all()
        
        # Calculate analytics
        total_time = sum((shift.end - shift.start) for shift in shifts if shift.end)
        total_shifts = len(shifts)
        
        # Group by project
        project_breakdown = {}
        for shift in shifts:
            if shift.projectId:
                if shift.projectId not in project_breakdown:
                    project_breakdown[shift.projectId] = {
                        "totalTime": 0,
                        "shiftCount": 0,
                        "tasks": {}
                    }
                
                shift_time = shift.end - shift.start if shift.end else 0
                project_breakdown[shift.projectId]["totalTime"] += shift_time
                project_breakdown[shift.projectId]["shiftCount"] += 1
                
                # Group by task within project
                if shift.taskId:
                    task_id = shift.taskId
                    if task_id not in project_breakdown[shift.projectId]["tasks"]:
                        project_breakdown[shift.projectId]["tasks"][task_id] = {
                            "totalTime": 0,
                            "shiftCount": 0
                        }
                    
                    project_breakdown[shift.projectId]["tasks"][task_id]["totalTime"] += shift_time
                    project_breakdown[shift.projectId]["tasks"][task_id]["shiftCount"] += 1
        
        return {
            "totalTime": total_time,
            "totalShifts": total_shifts,
            "projectBreakdown": project_breakdown,
            "averageShiftDuration": total_time / total_shifts if total_shifts > 0 else 0
        }