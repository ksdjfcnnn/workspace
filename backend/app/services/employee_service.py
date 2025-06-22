from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.employee import Employee
from app.models.project import Project
from app.models.shift import Shift
from app.models.task import Task
from app.models.screenshot import Screenshot
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeStats
from app.core.security import get_password_hash
from app.services.email_service import email_service
from datetime import datetime, timedelta
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class EmployeeService:
    def __init__(self, db: Session):
        self.db = db

    def create_employee(self, employee_data: EmployeeCreate) -> Employee:
        """Create a new employee and send invitation email"""
        # Check if email already exists
        existing = self.db.query(Employee).filter(Employee.email == employee_data.email).first()
        if existing:
            raise ValueError("Employee with this email already exists")
        
        # Create employee
        db_employee = Employee(
            name=employee_data.name,
            email=employee_data.email,
            title=employee_data.title,
            teamId=employee_data.teamId,
            sharedSettingsId=employee_data.sharedSettingsId,
            accountId=employee_data.accountId,
            identifier=employee_data.identifier,
            type=employee_data.type,
            organizationId=employee_data.organizationId,
            isAdmin=employee_data.isAdmin,
            invited=int(datetime.utcnow().timestamp() * 1000)
        )
        
        self.db.add(db_employee)
        self.db.commit()
        self.db.refresh(db_employee)
        
        # Add projects if specified
        if employee_data.projects:
            projects = self.db.query(Project).filter(Project.id.in_(employee_data.projects)).all()
            db_employee.projects.extend(projects)
            self.db.commit()
        
        # Send invitation email
        email_sent = email_service.send_email_verification(employee_data.email, employee_data.name)
        if not email_sent:
            logger.warning(f"Failed to send invitation email to {employee_data.email}")
        
        return db_employee

    def get_employee(self, employee_id: str) -> Optional[Employee]:
        """Get employee by ID"""
        return self.db.query(Employee).filter(Employee.id == employee_id).first()

    def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """Get employee by email"""
        return self.db.query(Employee).filter(Employee.email == email).first()

    def get_employees(self, organization_id: str, skip: int = 0, limit: int = 100) -> List[Employee]:
        """Get all employees for an organization"""
        return self.db.query(Employee).filter(
            Employee.organizationId == organization_id
        ).offset(skip).limit(limit).all()

    def update_employee(self, employee_id: str, employee_data: EmployeeUpdate) -> Optional[Employee]:
        """Update employee"""
        db_employee = self.get_employee(employee_id)
        if not db_employee:
            return None
        
        update_data = employee_data.dict(exclude_unset=True)
        
        # Handle projects update
        if "projects" in update_data:
            project_ids = update_data.pop("projects")
            projects = self.db.query(Project).filter(Project.id.in_(project_ids)).all()
            db_employee.projects.clear()
            db_employee.projects.extend(projects)
        
        # Update other fields
        for field, value in update_data.items():
            setattr(db_employee, field, value)
        
        self.db.commit()
        self.db.refresh(db_employee)
        return db_employee

    def deactivate_employee(self, employee_id: str) -> Optional[Employee]:
        """Deactivate employee"""
        db_employee = self.get_employee(employee_id)
        if not db_employee:
            return None
        
        if db_employee.deactivated:
            raise ValueError("Employee is already deactivated")
        
        db_employee.deactivated = int(datetime.utcnow().timestamp() * 1000)
        self.db.commit()
        self.db.refresh(db_employee)
        return db_employee

    def activate_employee(self, employee_id: str) -> Optional[Employee]:
        """Activate employee"""
        db_employee = self.get_employee(employee_id)
        if not db_employee:
            return None
        
        db_employee.deactivated = None
        self.db.commit()
        self.db.refresh(db_employee)
        return db_employee

    def verify_email_and_set_password(self, email: str, password: str) -> Optional[Employee]:
        """Verify email and set password for new employee"""
        db_employee = self.get_employee_by_email(email)
        if not db_employee:
            return None
        
        if db_employee.emailVerified:
            raise ValueError("Email already verified")
        
        db_employee.password_hash = get_password_hash(password)
        db_employee.emailVerified = True
        self.db.commit()
        self.db.refresh(db_employee)
        return db_employee

    def get_employee_stats(self, employee_id: str) -> EmployeeStats:
        """Get employee statistics"""
        now = datetime.utcnow()
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        # Convert to milliseconds
        week_start_ms = int(week_start.timestamp() * 1000)
        month_start_ms = int(month_start.timestamp() * 1000)
        
        # Total time logged
        total_time = self.db.query(func.sum(Shift.end - Shift.start)).filter(
            and_(Shift.employeeId == employee_id, Shift.end.isnot(None))
        ).scalar() or 0
        
        # Weekly time logged
        weekly_time = self.db.query(func.sum(Shift.end - Shift.start)).filter(
            and_(
                Shift.employeeId == employee_id,
                Shift.end.isnot(None),
                Shift.start >= week_start_ms
            )
        ).scalar() or 0
        
        # Monthly time logged
        monthly_time = self.db.query(func.sum(Shift.end - Shift.start)).filter(
            and_(
                Shift.employeeId == employee_id,
                Shift.end.isnot(None),
                Shift.start >= month_start_ms
            )
        ).scalar() or 0
        
        # Count projects
        total_projects = self.db.query(Project).join(Project.employees).filter(
            Employee.id == employee_id
        ).count()
        
        # Count tasks
        total_tasks = self.db.query(Task).join(Task.employees).filter(
            Employee.id == employee_id
        ).count()
        
        # Count screenshots
        total_screenshots = self.db.query(Screenshot).filter(
            Screenshot.employeeId == employee_id
        ).count()
        
        # Active shifts (not ended)
        active_shifts = self.db.query(Shift).filter(
            and_(Shift.employeeId == employee_id, Shift.end.is_(None))
        ).count()
        
        return EmployeeStats(
            totalTimeLogged=total_time,
            totalProjects=total_projects,
            totalTasks=total_tasks,
            totalScreenshots=total_screenshots,
            activeShifts=active_shifts,
            weeklyTimeLogged=weekly_time,
            monthlyTimeLogged=monthly_time
        )