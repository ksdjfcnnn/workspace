from pydantic import BaseModel
from typing import Optional


class ShiftBase(BaseModel):
    type: str = "manual"
    start: int
    end: Optional[int] = None
    name: Optional[str] = None


class ShiftCreate(ShiftBase):
    projectId: Optional[str] = None
    taskId: Optional[str] = None
    timezoneOffset: Optional[int] = 0
    user: Optional[str] = None
    domain: Optional[str] = None
    computer: Optional[str] = None
    hwid: Optional[str] = None
    os: Optional[str] = None
    osVersion: Optional[str] = None


class ShiftUpdate(BaseModel):
    end: Optional[int] = None
    projectId: Optional[str] = None
    taskId: Optional[str] = None
    name: Optional[str] = None


class ShiftStart(BaseModel):
    projectId: Optional[str] = None
    taskId: Optional[str] = None
    name: Optional[str] = None
    timezoneOffset: Optional[int] = 0


class ShiftEnd(BaseModel):
    shiftId: str


class Shift(ShiftBase):
    id: str
    token: Optional[str] = None
    timezoneOffset: int
    user: Optional[str] = None
    domain: Optional[str] = None
    computer: Optional[str] = None
    hwid: Optional[str] = None
    os: Optional[str] = None
    osVersion: Optional[str] = None
    paid: bool = False
    payRate: float = 0.0
    overtimePayRate: float = 0.0
    overtimeStart: Optional[int] = None
    employeeId: str
    teamId: Optional[str] = None
    organizationId: str
    projectId: Optional[str] = None
    taskId: Optional[str] = None
    startTranslated: Optional[int] = None
    endTranslated: Optional[int] = None
    overtimeStartTranslated: Optional[int] = None
    negativeTime: int = 0
    deletedScreenshots: int = 0
    lastActivityEnd: Optional[int] = None
    lastActivityEndTranslated: Optional[int] = None

    class Config:
        from_attributes = True