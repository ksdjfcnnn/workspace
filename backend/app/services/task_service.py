from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.task import Task
from app.models.employee import Employee
from app.models.team import Team
from app.models.shift import Shift
from app.schemas.task import TaskCreate, TaskUpdate
from typing import List, Optional


class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def create_task(self, task_data: TaskCreate, creator_id: str, organization_id: str) -> Task:
        """Create a new task"""
        db_task = Task(
            name=task_data.name,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            billable=task_data.billable,
            projectId=task_data.projectId,
            deadline=task_data.deadline,
            labels=task_data.labels or [],
            creatorId=creator_id,
            organizationId=organization_id
        )
        
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        
        # Add employees if specified
        if task_data.employees:
            employees = self.db.query(Employee).filter(Employee.id.in_(task_data.employees)).all()
            db_task.employees.extend(employees)
        
        # Add teams if specified
        if task_data.teams:
            teams = self.db.query(Team).filter(Team.id.in_(task_data.teams)).all()
            db_task.teams.extend(teams)
        
        self.db.commit()
        return db_task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_tasks(self, organization_id: str, project_id: str = None, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get tasks for an organization, optionally filtered by project"""
        query = self.db.query(Task).filter(Task.organizationId == organization_id)
        
        if project_id:
            query = query.filter(Task.projectId == project_id)
        
        return query.offset(skip).limit(limit).all()

    def get_user_tasks(self, employee_id: str, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get tasks assigned to a specific employee"""
        return self.db.query(Task).join(Task.employees).filter(
            Employee.id == employee_id
        ).offset(skip).limit(limit).all()

    def update_task(self, task_id: str, task_data: TaskUpdate) -> Optional[Task]:
        """Update task"""
        db_task = self.get_task(task_id)
        if not db_task:
            return None
        
        update_data = task_data.dict(exclude_unset=True)
        
        # Handle employees update
        if "employees" in update_data:
            employee_ids = update_data.pop("employees")
            employees = self.db.query(Employee).filter(Employee.id.in_(employee_ids)).all()
            db_task.employees.clear()
            db_task.employees.extend(employees)
        
        # Update other fields
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def delete_task(self, task_id: str) -> Optional[Task]:
        """Delete task"""
        db_task = self.get_task(task_id)
        if not db_task:
            return None
        
        # Check if task has active shifts
        active_shifts = self.db.query(Shift).filter(
            and_(Shift.taskId == task_id, Shift.end.is_(None))
        ).count()
        
        if active_shifts > 0:
            raise ValueError("Cannot delete task with active time tracking sessions")
        
        self.db.delete(db_task)
        self.db.commit()
        return db_task