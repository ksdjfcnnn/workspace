from pydantic import BaseModel
from typing import Optional


class OrganizationBase(BaseModel):
    name: str
    domain: str


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    isActive: Optional[bool] = None


class Organization(OrganizationBase):
    id: str
    isActive: bool
    createdAt: int

    class Config:
        from_attributes = True