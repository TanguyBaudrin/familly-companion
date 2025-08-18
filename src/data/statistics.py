from sqlalchemy import func, extract
from sqlalchemy.orm import Session
from src.core.models import PointsHistory, FamilyMember, Reward
from datetime import datetime, timedelta, UTC

def get_points_by_user_per_period(db: Session, period: str):
    """
    Calcule le total des points gagnés par chaque membre de la famille sur une période donnée (semaine ou mois).

    Args:
        db: La session de base de données.
        period: La période pour laquelle calculer les statistiques ('weekly' ou 'monthly').

    Returns:
        Une liste de dictionnaires contenant le nom du membre et le total des points gagnés.
    """
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
            FamilyMember.name,
            func.sum(PointsHistory.points_change).label('total_points')
        )
        .join(PointsHistory, FamilyMember.id == PointsHistory.member_id)
        .filter(
            PointsHistory.timestamp >= start_date,
            PointsHistory.points_change > 0  # On ne compte que les points gagnés
        )
        .group_by(FamilyMember.name)
        .order_by(func.sum(PointsHistory.points_change).desc())
        .all()
    )
    
    return [{"name": name, "points": total_points} for name, total_points in results]

def get_most_used_rewards(db: Session):
    """
    Détermine les récompenses les plus utilisées par les membres de la famille.

    Args:
        db: La session de base de données.

    Returns:
        Une liste de dictionnaires contenant le nom de la récompense et le nombre de fois où elle a été réclamée.
    """
    results = (
        db.query(
            Reward.name,
            func.count(PointsHistory.id).label('times_claimed')
        )
        .join(PointsHistory, Reward.id == PointsHistory.reward_id)
        .group_by(Reward.name)
        .order_by(func.count(PointsHistory.id).desc())
        .all()
    )

    return [{"name": name, "count": times_claimed} for name, times_claimed in results]
