from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid
from datetime import datetime

# Association tables
task_employees = Table(
    'task_employees',
    Base.metadata,
    Column('taskId', String, ForeignKey('tasks.id'), primary_key=True),
    Column('employeeId', String, ForeignKey('employees.id'), primary_key=True)
)

task_teams = Table(
    'task_teams',
    Base.metadata,
    Column('taskId', String, ForeignKey('tasks.id'), primary_key=True),
    Column('teamId', String, ForeignKey('teams.id'), primary_key=True)
)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()).replace('-', ''))
    status = Column(String, default="To Do")
    priority = Column(String, default="low")
    billable = Column(Boolean, default=True)
    name = Column(String, nullable=False)
    projectId = Column(String, ForeignKey("projects.id"), nullable=False)
    description = Column(String, nullable=True)
    deadline = Column(Integer, nullable=True)  # Date in milliseconds
    labels = Column(JSON, default=list)
    creatorId = Column(String, ForeignKey("employees.id"), nullable=False)
    organizationId = Column(String, ForeignKey("organizations.id"), nullable=False)
    createdAt = Column(Integer, default=lambda: int(datetime.utcnow().timestamp() * 1000))
    
    # Relationships
    organization = relationship("Organization", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
    creator = relationship("Employee", foreign_keys=[creatorId])
    employees = relationship("Employee", secondary=task_employees, back_populates="tasks")
    teams = relationship("Team", secondary=task_teams, back_populates="tasks")
    shifts = relationship("Shift", back_populates="task")
    screenshots = relationship("Screenshot", back_populates="task")