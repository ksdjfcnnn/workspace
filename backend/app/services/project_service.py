from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.project import Project
from app.models.employee import Employee
from app.models.team import Team
from app.models.task import Task
from app.models.shift import Shift
from app.models.screenshot import Screenshot
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectStats
from typing import List, Optional


class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def create_project(self, project_data: ProjectCreate, creator_id: str) -> Project:
        """Create a new project"""
        db_project = Project(
            name=project_data.name,
            description=project_data.description,
            billable=project_data.billable,
            organizationId=project_data.organizationId,
            creatorId=creator_id,
            statuses=project_data.statuses or ["To do", "On hold", "In progress", "Done"],
            priorities=project_data.priorities or ["low", "medium", "high"],
            payroll=project_data.payroll or {"billRate": 0, "overtimeBillRate": 0},
            screenshotSettings=project_data.screenshotSettings or {"screenshotEnabled": True}
        )
        
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        
        # Add employees if specified
        if project_data.employees:
            employees = self.db.query(Employee).filter(Employee.id.in_(project_data.employees)).all()
            db_project.employees.extend(employees)
        
        # Add teams if specified
        if project_data.teams:
            teams = self.db.query(Team).filter(Team.id.in_(project_data.teams)).all()
            db_project.teams.extend(teams)
        
        self.db.commit()
        return db_project

    def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        return self.db.query(Project).filter(Project.id == project_id).first()

    def get_projects(self, organization_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get all projects for an organization"""
        return self.db.query(Project).filter(
            Project.organizationId == organization_id
        ).offset(skip).limit(limit).all()

    def get_user_projects(self, employee_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get projects assigned to a specific employee"""
        return self.db.query(Project).join(Project.employees).filter(
            Employee.id == employee_id
        ).offset(skip).limit(limit).all()

    def update_project(self, project_id: str, project_data: ProjectUpdate) -> Optional[Project]:
        """Update project"""
        db_project = self.get_project(project_id)
        if not db_project:
            return None
        
        update_data = project_data.dict(exclude_unset=True)
        
        # Handle employees update
        if "employees" in update_data:
            employee_ids = update_data.pop("employees")
            employees = self.db.query(Employee).filter(Employee.id.in_(employee_ids)).all()
            db_project.employees.clear()
            db_project.employees.extend(employees)
        
        # Handle teams update
        if "teams" in update_data:
            team_ids = update_data.pop("teams")
            teams = self.db.query(Team).filter(Team.id.in_(team_ids)).all()
            db_project.teams.clear()
            db_project.teams.extend(teams)
        
        # Update other fields
        for field, value in update_data.items():
            setattr(db_project, field, value)
        
        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def delete_project(self, project_id: str) -> Optional[Project]:
        """Delete project"""
        db_project = self.get_project(project_id)
        if not db_project:
            return None
        
        # Check if project has active shifts
        active_shifts = self.db.query(Shift).filter(
            and_(Shift.projectId == project_id, Shift.end.is_(None))
        ).count()
        
        if active_shifts > 0:
            raise ValueError("Cannot delete project with active time tracking sessions")
        
        self.db.delete(db_project)
        self.db.commit()
        return db_project

    def get_project_stats(self, project_id: str) -> ProjectStats:
        """Get project statistics"""
        # Total time logged
        total_time = self.db.query(func.sum(Shift.end - Shift.start)).filter(
            and_(Shift.projectId == project_id, Shift.end.isnot(None))
        ).scalar() or 0
        
        # Count employees
        total_employees = self.db.query(Employee).join(Employee.projects).filter(
            Project.id == project_id
        ).count()
        
        # Count tasks
        total_tasks = self.db.query(Task).filter(Task.projectId == project_id).count()
        
        # Count completed tasks
        completed_tasks = self.db.query(Task).filter(
            and_(Task.projectId == project_id, Task.status == "Done")
        ).count()
        
        # Count pending tasks
        pending_tasks = total_tasks - completed_tasks
        
        # Count screenshots
        total_screenshots = self.db.query(Screenshot).filter(
            Screenshot.projectId == project_id
        ).count()
        
        # Active shifts
        active_shifts = self.db.query(Shift).filter(
            and_(Shift.projectId == project_id, Shift.end.is_(None))
        ).count()
        
        return ProjectStats(
            totalTimeLogged=total_time,
            totalEmployees=total_employees,
            totalTasks=total_tasks,
            totalScreenshots=total_screenshots,
            activeShifts=active_shifts,
            completedTasks=completed_tasks,
            pendingTasks=pending_tasks
        )