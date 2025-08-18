from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, UTC

Base = declarative_base()

class FamilyMember(Base): # type: ignore
    __tablename__ = 'family_members'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    total_points = Column(Integer, default=0)

    tasks = relationship("Task", back_populates="assigned_to")
    points_history = relationship("PointsHistory", back_populates="member")
    completions = relationship("TaskCompletion", back_populates="member")

class Task(Base): # type: ignore
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    points = Column(Integer, nullable=False)
    assigned_to_id = Column(Integer, ForeignKey('family_members.id'), nullable=True) # Allow tasks to be unassigned
    status = Column(String, default='pending') # e.g., 'pending', 'completed'
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    completed_at = Column(DateTime, nullable=True)
    duration_value = Column(Integer, nullable=True)
    duration_unit = Column(String, nullable=True)

    assigned_to = relationship("FamilyMember", back_populates="tasks")
    completions = relationship("TaskCompletion", back_populates="task")

class Reward(Base): # type: ignore
    __tablename__ = 'rewards'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    cost = Column(Integer, nullable=False)
    description = Column(String, nullable=True)

class TaskCompletion(Base): # type: ignore
    __tablename__ = 'task_completions'
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    member_id = Column(Integer, ForeignKey('family_members.id'), nullable=False)
    completed_at = Column(DateTime, default=lambda: datetime.now(UTC))

    task = relationship("Task", back_populates="completions")
    member = relationship("FamilyMember", back_populates="completions")
    points_history = relationship("PointsHistory", back_populates="completion")

class PointsHistory(Base): # type: ignore
    __tablename__ = 'points_history'
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey('family_members.id'), nullable=False)
    task_completion_id = Column(Integer, ForeignKey('task_completions.id'), nullable=True)
    reward_id = Column(Integer, ForeignKey('rewards.id'), nullable=True)
    points_change = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))

    member = relationship("FamilyMember", back_populates="points_history")
    completion = relationship("TaskCompletion", back_populates="points_history")
    reward = relationship("Reward")
