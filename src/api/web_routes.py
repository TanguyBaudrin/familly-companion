from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordBearer

from src.data.database import get_db, get_family_members, get_all_tasks, get_rewards, create_task, create_family_member, create_reward, complete_task, claim_reward, get_family_member_by_id, update_family_member, delete_family_member, get_task_by_id, update_task, delete_task, get_reward_by_id, update_reward, delete_reward
from src.core import schemas

router = APIRouter()

templates = Jinja2Templates(directory="src/web/templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # In a real application, this would validate the token against an external auth provider
    # For now, we'll just check if a token is present.
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Dummy user for now. Replace with actual user retrieval from token.
    return {"username": "testuser", "id": 1}

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/members", response_class=HTMLResponse) # New route for members management page
async def manage_members(request: Request):
    return templates.TemplateResponse("members.html", {"request": request})

@router.get("/quests-rewards", response_class=HTMLResponse) # New route for quests and rewards management page
async def manage_quests_rewards(request: Request):
    return templates.TemplateResponse("quests_rewards.html", {"request": request})

# API Endpoints - Members

@router.get("/api/members", response_model=List[schemas.FamilyMemberResponse])
def read_members(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    members = get_family_members(db)
    return members

@router.get("/api/members/{member_id}", response_model=schemas.FamilyMemberResponse)
def read_member(member_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    member = get_family_member_by_id(db, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return member

@router.post("/api/members", response_model=schemas.FamilyMemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(member: schemas.FamilyMemberCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_member = create_family_member(db, name=member.name)
    return db_member

@router.put("/api/members/{member_id}", response_model=schemas.FamilyMemberResponse)
def update_member(member_id: int, member: schemas.FamilyMemberUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_member = update_family_member(db, member_id, name=member.name, total_points=member.total_points)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member

@router.delete("/api/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    success = delete_family_member(db, member_id)
    if not success:
        raise HTTPException(status_code=404, detail="Member not found")
    return

# API Endpoints - Tasks

@router.get("/api/tasks", response_model=List[schemas.TaskResponse])
def read_tasks(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    tasks = get_all_tasks(db)
    return tasks

@router.get("/api/tasks/{task_id}", response_model=schemas.TaskResponse)
def read_task(task_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    task = get_task_by_id(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/api/tasks", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def add_task(task: schemas.TaskCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_task = create_task(db, description=task.description, points=task.points, assigned_to_id=task.assigned_to_id, duration_value=task.duration_value, duration_unit=task.duration_unit)
    return db_task

@router.put("/api/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task_api(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_task = update_task(db, task_id, description=task.description, points=task.points, assigned_to_id=task.assigned_to_id, status=task.status, duration_value=task.duration_value, duration_unit=task.duration_unit)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_api(task_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    success = delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return

@router.post("/api/tasks/{task_id}/complete", response_model=schemas.TaskResponse)
def complete_task_api(task_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    completed_task = complete_task(db, task_id)
    if completed_task is None:
        # Differentiate between not found and expired
        task = get_task_by_id(db, task_id)
        if task and task.status == 'pending' and is_task_expired(task):
            raise HTTPException(status_code=400, detail="Task is expired and cannot be completed")
        else:
            raise HTTPException(status_code=404, detail="Task not found or already completed")
    return completed_task

# API Endpoints - Rewards

@router.get("/api/rewards", response_model=List[schemas.RewardResponse])
def read_rewards(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    rewards = get_rewards(db)
    return rewards

@router.get("/api/rewards/{reward_id}", response_model=schemas.RewardResponse)
def read_reward(reward_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    reward = get_reward_by_id(db, reward_id)
    if reward is None:
        raise HTTPException(status_code=404, detail="Reward not found")
    return reward

@router.post("/api/rewards", response_model=schemas.RewardResponse, status_code=status.HTTP_201_CREATED)
def add_reward(reward: schemas.RewardCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_reward = create_reward(db, name=reward.name, cost=reward.cost, description=reward.description) # Pass description directly
    return db_reward

@router.put("/api/rewards/{reward_id}", response_model=schemas.RewardResponse)
def update_reward_api(reward_id: int, reward: schemas.RewardUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_reward = update_reward(db, reward_id, name=reward.name, cost=reward.cost, description=reward.description)
    if db_reward is None:
        raise HTTPException(status_code=404, detail="Reward not found")
    return db_reward

@router.delete("/api/rewards/{reward_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reward_api(reward_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    success = delete_reward(db, reward_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reward not found")
    return

@router.post("/api/members/{member_id}/claim_reward/{reward_id}", response_model=schemas.FamilyMemberResponse)
def claim_reward_api(member_id: int, reward_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    updated_member = claim_reward(db, member_id, reward_id)
    if not updated_member:
        raise HTTPException(status_code=400, detail="Member not found, reward not found, or insufficient points")
    return updated_member

@router.get("/api/leaderboard", response_model=List[schemas.FamilyMemberResponse])
def get_leaderboard(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    leaderboard = get_family_members(db) # Already sorted by total_points desc
    return leaderboard