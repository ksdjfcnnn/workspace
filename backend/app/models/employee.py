from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid
from datetime import datetime

# Association table for employee-project many-to-many relationship
employee_projects = Table(
    'employee_projects',
    Base.metadata,
    Column('employeeId', String, ForeignKey('employees.id'), primary_key=True),
    Column('projectId', String, ForeignKey('projects.id'), primary_key=True)
)


class Employee(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()).replace('-', ''))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=True)  # Null until email verification
    title = Column(String, nullable=True)
    teamId = Column(String, ForeignKey("teams.id"), nullable=True)
    sharedSettingsId = Column(String, nullable=True)
    accountId = Column(String, nullable=True)
    identifier = Column(String, nullable=True)
    type = Column(String, default="personal")  # "personal" or "office"
    organizationId = Column(String, ForeignKey("organizations.id"), nullable=False)
    deactivated = Column(Integer, nullable=True)  # Time in milliseconds since deactivation
    invited = Column(Integer, nullable=True)  # Time in milliseconds from invitation to acceptance
    emailVerified = Column(Boolean, default=False)
    isAdmin = Column(Boolean, default=False)
    systemPermissions = Column(JSON, default=list)
    createdAt = Column(Integer, default=lambda: int(datetime.utcnow().timestamp() * 1000))
    
    # Relationships
    organization = relationship("Organization", back_populates="employees")
    team = relationship("Team", back_populates="employees")
    projects = relationship("Project", secondary=employee_projects, back_populates="employees")
    tasks = relationship("Task", secondary="task_employees", back_populates="employees")
    shifts = relationship("Shift", back_populates="employee")
    screenshots = relationship("Screenshot", back_populates="employee")