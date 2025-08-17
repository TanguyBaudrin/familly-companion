from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.core.models import Base, FamilyMember, Task, Reward, PointsHistory
from datetime import datetime, UTC # Import datetime and UTC
from typing import Optional # Import Optional

SQLALCHEMY_DATABASE_URL = "sqlite:///./heros_du_foyer.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_family_members(db: Session):
    return db.query(FamilyMember).order_by(FamilyMember.total_points.desc()).all()

def get_family_member_by_id(db: Session, member_id: int):
    return db.query(FamilyMember).filter(FamilyMember.id == member_id).first()

def create_family_member(db: Session, name: str):
    db_member = FamilyMember(name=name)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def update_family_member(db: Session, member_id: int, name: Optional[str] = None, total_points: Optional[int] = None):
    db_member = db.query(FamilyMember).filter(FamilyMember.id == member_id).first()
    if db_member:
        if name is not None:
            db_member.name = name
        if total_points is not None:
            db_member.total_points = total_points # type: ignore
        db.commit()
        db.refresh(db_member)
    return db_member

def delete_family_member(db: Session, member_id: int):
    db_member = db.query(FamilyMember).filter(FamilyMember.id == member_id).first()
    if db_member:
        db.delete(db_member)
        db.commit()
        return True
    return False

def get_tasks_for_member(db: Session, member_id: int):
    return db.query(Task).filter(Task.assigned_to_id == member_id).all()

def get_task_by_id(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()

def update_task(db: Session, task_id: int, description: Optional[str] = None, points: Optional[int] = None, assigned_to_id: Optional[int] = None, status: Optional[str] = None):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task:
        if description is not None:
            db_task.description = description
        if points is not None:
            db_task.points = points # type: ignore
        if assigned_to_id is not None:
            db_task.assigned_to_id = assigned_to_id # type: ignore
        if status is not None:
            db_task.status = status # type: ignore
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False

def get_all_tasks(db: Session):
    return db.query(Task).all()

def get_rewards(db: Session):
    return db.query(Reward).all()

def get_reward_by_id(db: Session, reward_id: int):
    return db.query(Reward).filter(Reward.id == reward_id).first()

def update_reward(db: Session, reward_id: int, name: Optional[str] = None, cost: Optional[int] = None, description: Optional[str] = None):
    db_reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if db_reward:
        if name is not None:
            db_reward.name = name
        if cost is not None:
            db_reward.cost = cost # type: ignore
        if description is not None:
            db_reward.description = description
        db.commit()
        db.refresh(db_reward)
    return db_reward

def delete_reward(db: Session, reward_id: int):
    db_reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if db_reward:
        db.delete(db_reward)
        db.commit()
        return True
    return False

def create_task(db: Session, description: str, points: int, assigned_to_id: int):
    db_task = Task(description=description, points=points, assigned_to_id=assigned_to_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def create_reward(db: Session, name: str, cost: int, description: Optional[str] = None): # Changed type hint
    db_reward = Reward(name=name, cost=cost, description=description)
    db.add(db_reward)
    db.commit()
    db.refresh(db_reward)
    return db_reward

def complete_task(db: Session, task_id: int):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task and task.status == 'pending':
        task.status = 'completed' # type: ignore
        task.completed_at = datetime.now(UTC) # type: ignore
        member = db.query(FamilyMember).filter(FamilyMember.id == task.assigned_to_id).first()
        if member:
            member.total_points += task.points # type: ignore
            points_history = PointsHistory(
                member_id=member.id,
                task_id=task.id,
                points_change=task.points,
                reason=f"Task '{task.description}' completed"
            )
            db.add(points_history)
        db.commit()
        db.refresh(task)
        if member:
            db.refresh(member)
        return task
    return None

def claim_reward(db: Session, member_id: int, reward_id: int):
    member = db.query(FamilyMember).filter(FamilyMember.id == member_id).first()
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if member and reward and member.total_points >= reward.cost:
        member.total_points -= reward.cost # type: ignore
        points_history = PointsHistory(
            member_id=member.id,
            reward_id=reward.id,
            points_change=-reward.cost,
            reason=f"Reward '{reward.name}' claimed"
        )
        db.add(points_history)
        db.commit()
        db.refresh(member)
        return member
    return None

def get_points_history_for_member(db: Session, member_id: int):
    return db.query(PointsHistory).filter(PointsHistory.member_id == member_id).order_by(PointsHistory.timestamp.desc()).all()

Base.metadata.create_all(bind=engine)
