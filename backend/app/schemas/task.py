from pydantic import BaseModel
from typing import Optional, List


class TaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "To Do"
    priority: str = "low"
    billable: bool = True


class TaskCreate(TaskBase):
    projectId: str
    employees: Optional[List[str]] = []
    teams: Optional[List[str]] = []
    deadline: Optional[int] = None
    labels: Optional[List[str]] = []


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    employees: Optional[List[str]] = None
    deadline: Optional[int] = None
    status: Optional[str] = None
    labels: Optional[List[str]] = None
    priority: Optional[str] = None
    billable: Optional[bool] = None


class Task(TaskBase):
    id: str
    projectId: str
    employees: List[str]
    deadline: Optional[int] = None
    labels: List[str]
    creatorId: str
    organizationId: str
    teams: List[str]
    createdAt: int

    class Config:
        from_attributes = True