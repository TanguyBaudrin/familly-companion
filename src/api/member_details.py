from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.data.database import (
    get_db,
    get_family_member_by_id,
    get_tasks_for_member_by_status,
    get_daily_points_for_member,
    get_claimed_rewards_for_member
)
from src.core import schemas
from typing import List

router = APIRouter()

@router.get("/members/{member_id}/details")
def get_member_details(
    member_id: int, 
    period: str = 'weekly', 
    db: Session = Depends(get_db)
):
    """
    Récupère toutes les informations détaillées pour un membre de la famille.
    """
    member = get_family_member_by_id(db, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Membre non trouvé")

    pending_tasks = get_tasks_for_member_by_status(db, member_id, 'pending')
    completed_tasks = get_tasks_for_member_by_status(db, member_id, 'completed')
    daily_points = get_daily_points_for_member(db, member_id, period)
    claimed_rewards = get_claimed_rewards_for_member(db, member_id)

    # Conversion en schemas Pydantic pour la réponse
    pending_tasks_response = [schemas.TaskResponse.from_orm(t) for t in pending_tasks]
    completed_tasks_response = [schemas.TaskResponse.from_orm(t) for t in completed_tasks]
    
    claimed_rewards_response = [
        {"name": name, "claimed_at": timestamp} for name, timestamp in claimed_rewards
    ]

    return {
        "member": schemas.FamilyMemberResponse.from_orm(member),
        "pending_tasks": pending_tasks_response,
        "completed_tasks": completed_tasks_response,
        "daily_points": daily_points,
        "claimed_rewards": claimed_rewards_response
    }
