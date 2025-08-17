from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class FamilyMemberBase(BaseModel):
    name: str

class FamilyMemberCreate(FamilyMemberBase):
    pass

class FamilyMemberUpdate(FamilyMemberBase):
    name: Optional[str] = None
    total_points: Optional[int] = None # Allow updating points, make it optional

class FamilyMemberResponse(FamilyMemberBase):
    id: int
    total_points: int

    model_config = ConfigDict(from_attributes=True) # Use ConfigDict and from_attributes

class TaskBase(BaseModel):
    description: str
    points: int

class TaskCreate(TaskBase):
    assigned_to_id: int

class TaskUpdate(TaskBase):
    description: Optional[str] = None
    points: Optional[int] = None
    status: Optional[str] = None # Allow updating status
    assigned_to_id: Optional[int] = None # Allow reassigning task

class TaskResponse(TaskBase):
    id: int
    assigned_to_id: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True) # Use ConfigDict and from_attributes

class RewardBase(BaseModel):
    name: str
    cost: int
    description: Optional[str]

class RewardCreate(RewardBase):
    pass

class RewardUpdate(BaseModel): # Inherit from BaseModel directly to make all fields optional
    name: Optional[str] = None
    cost: Optional[int] = None
    description: Optional[str] = None

class RewardResponse(RewardBase):
    id: int

    model_config = ConfigDict(from_attributes=True) # Use ConfigDict and from_attributes

class PointsHistoryResponse(BaseModel):
    id: int
    member_id: int
    task_id: Optional[int]
    reward_id: Optional[int]
    points_change: int
    reason: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True) # Use ConfigDict and from_attributes
