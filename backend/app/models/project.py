from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid
from datetime import datetime

# Association table for project-team many-to-many relationship
project_teams = Table(
    'project_teams',
    Base.metadata,
    Column('projectId', String, ForeignKey('projects.id'), primary_key=True),
    Column('teamId', String, ForeignKey('teams.id'), primary_key=True)
)


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()).replace('-', ''))
    archived = Column(Boolean, default=False)
    statuses = Column(JSON, default=lambda: ["To do", "On hold", "In progress", "Done"])
    priorities = Column(JSON, default=lambda: ["low", "medium", "high"])
    billable = Column(Boolean, default=True)
    payroll = Column(JSON, default=lambda: {"billRate": 0, "overtimeBillRate": 0})
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    creatorId = Column(String, ForeignKey("employees.id"), nullable=False)
    organizationId = Column(String, ForeignKey("organizations.id"), nullable=False)
    screenshotSettings = Column(JSON, default=lambda: {"screenshotEnabled": True})
    createdAt = Column(Integer, default=lambda: int(datetime.utcnow().timestamp() * 1000))
    
    # Relationships
    organization = relationship("Organization", back_populates="projects")
    creator = relationship("Employee", foreign_keys=[creatorId])
    employees = relationship("Employee", secondary="employee_projects", back_populates="projects")
    teams = relationship("Team", secondary=project_teams, back_populates="projects")
    tasks = relationship("Task", back_populates="project")
    shifts = relationship("Shift", back_populates="project")
    screenshots = relationship("Screenshot", back_populates="project")