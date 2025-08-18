from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class TaskCompletionBase(BaseModel):
    member_id: int

class TaskCompletionCreate(TaskCompletionBase):
    task_id: int

class TaskCompletionResponse(TaskCompletionBase):
    id: int
    completed_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FamilyMemberBase(BaseModel):
    name: str

class FamilyMemberCreate(FamilyMemberBase):
    pass

class FamilyMemberUpdate(FamilyMemberBase):
    name: Optional[str] = None
    total_points: Optional[int] = None

class FamilyMemberResponse(FamilyMemberBase):
    id: int
    total_points: int
    completions: List[TaskCompletionResponse] = []

    model_config = ConfigDict(from_attributes=True)

class TaskBase(BaseModel):
    description: str
    points: int
    duration_value: Optional[int] = None
    duration_unit: Optional[str] = None

class TaskCreate(TaskBase):
    assigned_to_id: Optional[int] = None

class TaskUpdate(TaskBase):
    description: Optional[str] = None
    points: Optional[int] = None
    status: Optional[str] = None
    assigned_to_id: Optional[int] = None
    duration_value: Optional[int] = None
    duration_unit: Optional[str] = None

class TaskResponse(TaskBase):
    id: int
    assigned_to_id: Optional[int]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    completions: List[TaskCompletionResponse] = []

    model_config = ConfigDict(from_attributes=True)

class RewardBase(BaseModel):
    name: str
    cost: int
    description: Optional[str]

class RewardCreate(RewardBase):
    pass

class RewardUpdate(BaseModel):
    name: Optional[str] = None
    cost: Optional[int] = None
    description: Optional[str] = None

class RewardResponse(RewardBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class PointsHistoryResponse(BaseModel):
    id: int
    member_id: int
    task_completion_id: Optional[int]
    reward_id: Optional[int]
    points_change: int
    reason: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskCompletionData(BaseModel):
    member_id: int
    percentage: int


class TaskComplete(BaseModel):
    completions: List[TaskCompletionData]
