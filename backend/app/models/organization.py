from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid
from datetime import datetime


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()).replace('-', ''))
    name = Column(String, nullable=False)
    domain = Column(String, unique=True, nullable=False)
    isActive = Column(Boolean, default=True)
    createdAt = Column(Integer, default=lambda: int(datetime.utcnow().timestamp() * 1000))
    
    # Relationships
    employees = relationship("Employee", back_populates="organization")
    projects = relationship("Project", back_populates="organization")
    teams = relationship("Team", back_populates="organization")
    tasks = relationship("Task", back_populates="organization")
    shifts = relationship("Shift", back_populates="organization")
    screenshots = relationship("Screenshot", back_populates="organization")