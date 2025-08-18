from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.data.database import get_db
from src.data.statistics import get_points_by_user_per_period, get_most_used_rewards
from typing import List, Dict, Any

router = APIRouter()

@router.get("/statistiques", response_model=Dict[str, List[Dict[str, Any]]])
def read_statistics(period: str = 'weekly', db: Session = Depends(get_db)):
    """
    Endpoint pour récupérer les statistiques de points et de récompenses.

    Args:
        period: La période pour les statistiques de points ('weekly' ou 'monthly').
        db: La session de base de données.

    Returns:
        Un dictionnaire contenant les statistiques des points par utilisateur et les récompenses les plus utilisées.
    """
    if period not in ['weekly', 'monthly']:
        raise HTTPException(status_code=400, detail="La période doit être 'weekly' ou 'monthly'.")
    
    points_stats = get_points_by_user_per_period(db, period=period)
    rewards_stats = get_most_used_rewards(db)
    
    return {
        "points_by_user": points_stats,
        "most_used_rewards": rewards_stats
    }
