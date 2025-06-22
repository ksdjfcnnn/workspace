from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid
from datetime import datetime


class Screenshot(Base):
    __tablename__ = "screenshots"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()).replace('-', ''))
    site = Column(String, nullable=True)
    productivity = Column(Float, default=0.0)
    employeeId = Column(String, ForeignKey("employees.id"), nullable=False)
    appId = Column(String, nullable=True)
    appOrgId = Column(String, nullable=True)
    appTeamId = Column(String, nullable=True)
    teamId = Column(String, ForeignKey("teams.id"), nullable=True)
    organizationId = Column(String, ForeignKey("organizations.id"), nullable=False)
    projectId = Column(String, ForeignKey("projects.id"), nullable=True)
    taskId = Column(String, ForeignKey("tasks.id"), nullable=True)
    shiftId = Column(String, ForeignKey("shifts.id"), nullable=True)
    srcEmployeeId = Column(String, nullable=True)
    srcTeamId = Column(String, nullable=True)
    timestamp = Column(Integer, nullable=False)
    timestampTranslated = Column(String, nullable=True)
    systemPermissions = Column(JSON, default=lambda: {
        "accessibility": "undetermined",
        "screenAndSystemAudioRecording": "undetermined"
    })
    next = Column(String, nullable=True)  # Hash value for pagination
    imageUrl = Column(String, nullable=True)  # URL to screenshot image
    
    # Relationships
    organization = relationship("Organization", back_populates="screenshots")
    employee = relationship("Employee", back_populates="screenshots")
    team = relationship("Team")
    project = relationship("Project", back_populates="screenshots")
    task = relationship("Task", back_populates="screenshots")
    shift = relationship("Shift", back_populates="screenshots")