from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid
from datetime import datetime


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()).replace('-', ''))
    token = Column(String, nullable=True)
    type = Column(String, default="manual")  # manual, automated, scheduled, leave
    start = Column(Integer, nullable=False)  # Time in milliseconds when shift started
    end = Column(Integer, nullable=True)  # Time in milliseconds when shift ended
    timezoneOffset = Column(Integer, default=0)  # Timezone difference in milliseconds
    name = Column(String, nullable=True)
    user = Column(String, nullable=True)
    domain = Column(String, nullable=True)
    computer = Column(String, nullable=True)
    hwid = Column(String, nullable=True)
    os = Column(String, nullable=True)
    osVersion = Column(String, nullable=True)
    paid = Column(Boolean, default=False)
    payRate = Column(Float, default=0.0)
    overtimePayRate = Column(Float, default=0.0)
    overtimeStart = Column(Integer, nullable=True)
    employeeId = Column(String, ForeignKey("employees.id"), nullable=False)
    teamId = Column(String, ForeignKey("teams.id"), nullable=True)
    organizationId = Column(String, ForeignKey("organizations.id"), nullable=False)
    projectId = Column(String, ForeignKey("projects.id"), nullable=True)
    taskId = Column(String, ForeignKey("tasks.id"), nullable=True)
    startTranslated = Column(Integer, nullable=True)
    endTranslated = Column(Integer, nullable=True)
    overtimeStartTranslated = Column(Integer, nullable=True)
    negativeTime = Column(Integer, default=0)
    deletedScreenshots = Column(Integer, default=0)
    lastActivityEnd = Column(Integer, nullable=True)
    lastActivityEndTranslated = Column(Integer, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="shifts")
    employee = relationship("Employee", back_populates="shifts")
    team = relationship("Team", back_populates="shifts")
    project = relationship("Project", back_populates="shifts")
    task = relationship("Task", back_populates="shifts")
    screenshots = relationship("Screenshot", back_populates="shift")