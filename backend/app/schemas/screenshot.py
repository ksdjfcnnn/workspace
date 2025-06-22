from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class ScreenshotBase(BaseModel):
    site: Optional[str] = None
    productivity: float = 0.0
    timestamp: int


class ScreenshotCreate(ScreenshotBase):
    projectId: Optional[str] = None
    taskId: Optional[str] = None
    shiftId: Optional[str] = None
    systemPermissions: Optional[Dict[str, str]] = None
    imageUrl: Optional[str] = None


class ScreenshotUpdate(BaseModel):
    productivity: Optional[float] = None
    systemPermissions: Optional[Dict[str, str]] = None


class Screenshot(ScreenshotBase):
    id: str
    employeeId: str
    appId: Optional[str] = None
    appOrgId: Optional[str] = None
    appTeamId: Optional[str] = None
    teamId: Optional[str] = None
    organizationId: str
    projectId: Optional[str] = None
    taskId: Optional[str] = None
    shiftId: Optional[str] = None
    srcEmployeeId: Optional[str] = None
    srcTeamId: Optional[str] = None
    timestampTranslated: Optional[str] = None
    systemPermissions: Dict[str, str]
    next: Optional[str] = None
    imageUrl: Optional[str] = None

    class Config:
        from_attributes = True


class ScreenshotResponse(BaseModel):
    data: List[Screenshot]
    next: Optional[str] = None
    total: int