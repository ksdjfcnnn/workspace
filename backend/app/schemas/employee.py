from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any


class SystemPermission(BaseModel):
    computer: str
    permissions: Dict[str, str]
    createdAt: int
    updatedAt: int


class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    title: Optional[str] = None
    type: str = "personal"


class EmployeeCreate(EmployeeBase):
    organizationId: str
    teamId: Optional[str] = None
    sharedSettingsId: Optional[str] = None
    accountId: Optional[str] = None
    identifier: Optional[str] = None
    projects: Optional[List[str]] = []
    isAdmin: bool = False


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    title: Optional[str] = None
    teamId: Optional[str] = None
    sharedSettingsId: Optional[str] = None
    projects: Optional[List[str]] = None


class EmployeeInvite(BaseModel):
    name: str
    email: EmailStr
    title: Optional[str] = None
    teamId: Optional[str] = None
    projects: Optional[List[str]] = []
    isAdmin: bool = False


class Employee(EmployeeBase):
    id: str
    teamId: Optional[str] = None
    sharedSettingsId: Optional[str] = None
    accountId: Optional[str] = None
    identifier: Optional[str] = None
    organizationId: str
    projects: List[str] = []
    deactivated: Optional[int] = None
    invited: Optional[int] = None
    emailVerified: bool = False
    isAdmin: bool = False
    systemPermissions: List[SystemPermission] = []
    createdAt: int

    class Config:
        from_attributes = True


class EmployeeStats(BaseModel):
    totalTimeLogged: int  # in milliseconds
    totalProjects: int
    totalTasks: int
    totalScreenshots: int
    activeShifts: int
    weeklyTimeLogged: int
    monthlyTimeLogged: int