from sqlalchemy import create_engine, func
from src.core import schemas
from sqlalchemy.orm import sessionmaker, Session
from src.core.models import FamilyMember, Task, Reward, PointsHistory, TaskCompletion
from datetime import datetime, UTC, timedelta
from typing import Optional, List

SQLALCHEMY_DATABASE_URL = "sqlite:///./db/heros_du_foyer.db"

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

def calculate_expiration_time(created_at: datetime, duration_value: int, duration_unit: str) -> datetime:
    if duration_unit == "days":
        return created_at + timedelta(days=duration_value)
    elif duration_unit == "weeks":
        return created_at + timedelta(weeks=duration_value)
    elif duration_unit == "months":
        return created_at + timedelta(days=duration_value * 30)
    else:
        raise ValueError("Invalid duration unit")

def is_task_expired(task: Task) -> bool:
    if task.duration_value is None or task.duration_unit is None:
        return False
    
    expiration_time = calculate_expiration_time(task.created_at, task.duration_value, task.duration_unit)
    return datetime.now(UTC) > expiration_time

def update_task(db: Session, task_id: int, description: Optional[str] = None, points: Optional[int] = None, assigned_to_id: Optional[int] = None, status: Optional[str] = None, duration_value: Optional[int] = None, duration_unit: Optional[str] = None):
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
        if duration_value is not None:
            db_task.duration_value = duration_value # type: ignore
        if duration_unit is not None:
            db_task.duration_unit = duration_unit # type: ignore
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task:
        # Delete associated TaskCompletion records first
        db.query(TaskCompletion).filter(TaskCompletion.task_id == task_id).delete(synchronize_session=False)
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

def create_task(db: Session, description: str, points: int, assigned_to_id: Optional[int] = None, duration_value: Optional[int] = None, duration_unit: Optional[str] = None):
    db_task = Task(description=description, points=points, assigned_to_id=assigned_to_id, duration_value=duration_value, duration_unit=duration_unit)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def create_reward(db: Session, name: str, cost: int, description: Optional[str] = None):
    db_reward = Reward(name=name, cost=cost, description=description)
    db.add(db_reward)
    db.commit()
    db.refresh(db_reward)
    return db_reward

def complete_task(db: Session, task_id: int, completions: List[schemas.TaskCompletionData]):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task or task.status != 'pending':
        return None

    if is_task_expired(task):
        return None

    total_percentage = sum(c.percentage for c in completions)
    if total_percentage != 100:
        raise ValueError("Total percentage must be 100")

    members_to_update = []
    for completion_data in completions:
        member = db.query(FamilyMember).filter(FamilyMember.id == completion_data.member_id).first()
        if member:
            points_to_add = int(task.points * (completion_data.percentage / 100))
            
            completion = TaskCompletion(task_id=task.id, member_id=member.id)
            db.add(completion)
            
            member.total_points += points_to_add
            
            points_history = PointsHistory(
                member_id=member.id,
                points_change=points_to_add,
                reason=f"Task '{task.description}' completed"
            )
            points_history.completion = completion
            db.add(points_history)
            members_to_update.append(member)

    if not members_to_update:
        return None

    task.status = 'completed'
    task.completed_at = datetime.now(UTC)

    db.commit()

    db.refresh(task)
    for member in members_to_update:
        db.refresh(member)

    return task

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

def get_tasks_for_member_by_status(db: Session, member_id: int, status: str):
    """Récupère les tâches d'un membre avec un statut spécifique."""
    return db.query(Task).filter(Task.assigned_to_id == member_id, Task.status == status).all()

def get_daily_points_for_member(db: Session, member_id: int, period: str):
    """Calcule les points journaliers gagnés par un membre sur une période."""
    today = datetime.now(UTC)
    if period == 'weekly':
        start_date = today - timedelta(days=today.weekday())
    elif period == 'monthly':
        start_date = today.replace(day=1)
    else:
        return []

    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    results = (
        db.query(
            func.date(PointsHistory.timestamp).label('date'),
            func.sum(PointsHistory.points_change).label('total_points')
        )
        .filter(
            PointsHistory.member_id == member_id,
            PointsHistory.timestamp >= start_date,
            PointsHistory.points_change > 0
        )
        .group_by(func.date(PointsHistory.timestamp))
        .order_by(func.date(PointsHistory.timestamp))
        .all()
    )
    return [{"date": str(date), "points": total_points} for date, total_points in results]

def get_claimed_rewards_for_member(db: Session, member_id: int):
    """Récupère l'historique des récompenses réclamées par un membre."""
    return (
        db.query(Reward.name, PointsHistory.timestamp)
        .join(PointsHistory, Reward.id == PointsHistory.reward_id)
        .filter(PointsHistory.member_id == member_id)
        .order_by(PointsHistory.timestamp.desc())
        .all()
    )
