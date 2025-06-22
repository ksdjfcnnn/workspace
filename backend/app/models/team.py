from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid
from datetime import datetime


class Team(Base):
    __tablename__ = "teams"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()).replace('-', ''))
    name = Column(String, nullable=False)
    organizationId = Column(String, ForeignKey("organizations.id"), nullable=False)
    createdAt = Column(Integer, default=lambda: int(datetime.utcnow().timestamp() * 1000))
    
    # Relationships
    organization = relationship("Organization", back_populates="teams")
    employees = relationship("Employee", back_populates="team")
    projects = relationship("Project", secondary="project_teams", back_populates="teams")
    tasks = relationship("Task", secondary="task_teams", back_populates="teams")
    shifts = relationship("Shift", back_populates="team")