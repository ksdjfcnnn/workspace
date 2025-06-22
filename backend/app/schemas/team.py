from pydantic import BaseModel
from typing import Optional


class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    organizationId: str


class TeamUpdate(BaseModel):
    name: Optional[str] = None


class Team(TeamBase):
    id: str
    organizationId: str
    createdAt: int

    class Config:
        from_attributes = True