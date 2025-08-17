from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, declarative_base # Import declarative_base from sqlalchemy.orm
from datetime import datetime, UTC # Import datetime and UTC

Base = declarative_base()

class FamilyMember(Base): # type: ignore
    __tablename__ = 'family_members'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    total_points = Column(Integer, default=0)

    tasks = relationship("Task", back_populates="assigned_to")
    points_history = relationship("PointsHistory", back_populates="member")

class Task(Base): # type: ignore
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    points = Column(Integer, nullable=False)
    assigned_to_id = Column(Integer, ForeignKey('family_members.id'))
    status = Column(String, default='pending') # e.g., 'pending', 'completed'
    created_at = Column(DateTime, default=lambda: datetime.now(UTC)) # Use datetime.now(UTC)
    completed_at = Column(DateTime, nullable=True)

    assigned_to = relationship("FamilyMember", back_populates="tasks")
    points_history = relationship("PointsHistory", back_populates="task")

class Reward(Base): # type: ignore
    __tablename__ = 'rewards'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    cost = Column(Integer, nullable=False)
    description = Column(String, nullable=True)

class PointsHistory(Base): # type: ignore
    __tablename__ = 'points_history'
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey('family_members.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    reward_id = Column(Integer, ForeignKey('rewards.id'), nullable=True)
    points_change = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC)) # Use datetime.now(UTC)

    member = relationship("FamilyMember", back_populates="points_history")
    task = relationship("Task", back_populates="points_history")
    reward = relationship("Reward") # No back_populates needed if Reward doesn't need to know about PointsHistory