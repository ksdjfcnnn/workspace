from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    billable: bool = True


class ProjectCreate(ProjectBase):
    organizationId: str
    employees: Optional[List[str]] = []
    teams: Optional[List[str]] = []
    statuses: Optional[List[str]] = None
    priorities: Optional[List[str]] = None
    payroll: Optional[Dict[str, Any]] = None
    screenshotSettings: Optional[Dict[str, Any]] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    billable: Optional[bool] = None
    archived: Optional[bool] = None
    employees: Optional[List[str]] = None
    teams: Optional[List[str]] = None
    statuses: Optional[List[str]] = None
    priorities: Optional[List[str]] = None
    payroll: Optional[Dict[str, Any]] = None
    screenshotSettings: Optional[Dict[str, Any]] = None


class Project(ProjectBase):
    id: str
    archived: bool = False
    statuses: List[str]
    priorities: List[str]
    payroll: Dict[str, Any]
    employees: List[str]
    creatorId: str
    organizationId: str
    teams: List[str]
    screenshotSettings: Dict[str, Any]
    createdAt: int

    class Config:
        from_attributes = True


class ProjectStats(BaseModel):
    totalTimeLogged: int  # in milliseconds
    totalEmployees: int
    totalTasks: int
    totalScreenshots: int
    activeShifts: int
    completedTasks: int
    pendingTasks: int