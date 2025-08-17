from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.data.database import get_db, Base
from src.core.models import FamilyMember, Task, Reward

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency for testing
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def setup_function(function):
    # Create tables before each test
    Base.metadata.create_all(bind=engine)
    # Add some initial data
    db = TestingSessionLocal()
    member1 = FamilyMember(name="Test Member 1", total_points=100)
    member2 = FamilyMember(name="Test Member 2", total_points=50)
    db.add_all([member1, member2])
    db.commit()
    db.close()

def teardown_function(function):
    # Drop tables after each test
    Base.metadata.drop_all(bind=engine)


def test_read_members():
    response = client.get("/api/members", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Test Member 1"

def test_read_member_by_id():
    db = TestingSessionLocal()
    member = db.query(FamilyMember).first()
    member_id = member.id # Store ID
    db.close()

    response = client.get(f"/api/members/{member_id}", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 200
    assert response.json()["name"] == member.name

def test_read_nonexistent_member():
    response = client.get("/api/members/999", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Member not found"

def test_create_member():
    response = client.post(
        "/api/members",
        headers={"Authorization": "Bearer dummy-token"},
        json={"name": "New Member"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "New Member"

def test_update_member():
    db = TestingSessionLocal()
    member = db.query(FamilyMember).first()
    member_id = member.id # Store ID
    db.close()

    response = client.put(
        f"/api/members/{member_id}",
        headers={"Authorization": "Bearer dummy-token"},
        json={"name": "Updated Member Name", "total_points": 150}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Member Name"
    assert response.json()["total_points"] == 150

def test_update_nonexistent_member():
    response = client.put(
        "/api/members/999",
        headers={"Authorization": "Bearer dummy-token"},
        json={"name": "Nonexistent", "total_points": 100}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Member not found"

def test_delete_member():
    db = TestingSessionLocal()
    member = db.query(FamilyMember).first()
    member_id = member.id
    db.close()

    response = client.delete(f"/api/members/{member_id}", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 204

    # Verify member is deleted
    db = TestingSessionLocal()
    deleted_member = db.query(FamilyMember).filter(FamilyMember.id == member_id).first()
    db.close()
    assert deleted_member is None

def test_delete_nonexistent_member():
    response = client.delete("/api/members/999", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Member not found"

def test_read_tasks():
    # Add a task first
    db = TestingSessionLocal()
    member = db.query(FamilyMember).first()
    task = Task(description="Test Task", points=10, assigned_to_id=member.id)
    db.add(task)
    db.commit()
    db.close()

    response = client.get("/api/tasks", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["description"] == "Test Task"

def test_read_task_by_id():
    db = TestingSessionLocal()
    member = db.query(FamilyMember).first()
    task = Task(description="Specific Task", points=10, assigned_to_id=member.id)
    db.add(task)
    db.commit()
    task_id = task.id # Store ID
    db.close()

    response = client.get(f"/api/tasks/{task_id}", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 200
    assert response.json()["description"] == "Specific Task"

def test_read_nonexistent_task():
    response = client.get("/api/tasks/999", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_create_task():
    db = TestingSessionLocal()
    member = db.query(FamilyMember).first()
    db.close()

    response = client.post(
        "/api/tasks",
        headers={"Authorization": "Bearer dummy-token"},
        json={
            "description": "New Task",
            "points": 20,
            "assigned_to_id": member.id
        }
    )
    assert response.status_code == 201
    assert response.json()["description"] == "New Task"

def test_update_task():
    db = TestingSessionLocal()
    member = db.query(FamilyMember).first()
    task = Task(description="Task to Update", points=10, assigned_to_id=member.id)
    db.add(task)
    db.commit()
    task_id = task.id # Store ID
    db.close()

    response = client.put(
        f"/api/tasks/{task_id}",
        headers={"Authorization": "Bearer dummy-token"},
        json={"description": "Updated Task", "points": 25, "status": "completed"}
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Updated Task"
    assert response.json()["points"] == 25
    assert response.json()["status"] == "completed"

def test_update_nonexistent_task():
    response = client.put(
        "/api/tasks/999",
        headers={"Authorization": "Bearer dummy-token"},
        json={"description": "Nonexistent Task", "points": 10}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_delete_task():
    db = TestingSessionLocal()
    member = db.query(FamilyMember).first()
    task = Task(description="Task to Delete", points=10, assigned_to_id=member.id)
    db.add(task)
    db.commit()
    task_id = task.id
    db.close()

    response = client.delete(f"/api/tasks/{task_id}", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 204

    db = TestingSessionLocal()
    deleted_task = db.query(Task).filter(Task.id == task_id).first()
    db.close()
    assert deleted_task is None

def test_delete_nonexistent_task():
    response = client.delete("/api/tasks/999", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_complete_task():
    db = TestingSessionLocal()
    member = db.query(FamilyMember).first()
    member_id = member.id # Store member.id before closing session
    task = Task(description="Task to Complete", points=15, assigned_to_id=member_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    db.close()

    response = client.post(
        f"/api/tasks/{task.id}/complete",
        headers={"Authorization": "Bearer dummy-token"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    
    # Verify points updated
    db = TestingSessionLocal()
    updated_member = db.query(FamilyMember).filter(FamilyMember.id == member_id).first()
    db.close()
    assert updated_member.total_points == 100 + 15 # Initial 100 + 15 from task

def test_read_rewards():
    # Add a reward first
    db = TestingSessionLocal()
    reward = Reward(name="Test Reward", cost=50)
    db.add(reward)
    db.commit()
    db.close()

    response = client.get("/api/rewards", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Test Reward"

def test_read_reward_by_id():
    db = TestingSessionLocal()
    reward = Reward(name="Specific Reward", cost=50)
    db.add(reward)
    db.commit()
    reward_id = reward.id # Store ID
    db.close()

    response = client.get(f"/api/rewards/{reward_id}", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 200
    assert response.json()["name"] == "Specific Reward"

def test_read_nonexistent_reward():
    response = client.get("/api/rewards/999", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Reward not found"

def test_create_reward():
    response = client.post(
        "/api/rewards",
        headers={"Authorization": "Bearer dummy-token"},
        json={
            "name": "New Reward",
            "cost": 75,
            "description": "A shiny new reward"
        }
    )
    assert response.status_code == 201
    assert response.json()["name"] == "New Reward"

def test_update_reward():
    db = TestingSessionLocal()
    reward = Reward(name="Reward to Update", cost=50)
    db.add(reward)
    db.commit()
    reward_id = reward.id # Store ID
    db.close()

    response = client.put(
        f"/api/rewards/{reward_id}",
        headers={"Authorization": "Bearer dummy-token"},
        json={"name": "Updated Reward", "cost": 100, "description": "An updated reward"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Reward"
    assert response.json()["cost"] == 100
    assert response.json()["description"] == "An updated reward"

def test_update_nonexistent_reward():
    response = client.put(
        "/api/rewards/999",
        headers={"Authorization": "Bearer dummy-token"},
        json={}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Reward not found"

def test_delete_reward():
    db = TestingSessionLocal()
    reward = Reward(name="Reward to Delete", cost=50)
    db.add(reward)
    db.commit()
    reward_id = reward.id
    db.close()

    response = client.delete(f"/api/rewards/{reward_id}", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 204

    db = TestingSessionLocal()
    deleted_reward = db.query(Reward).filter(Reward.id == reward_id).first()
    db.close()
    assert deleted_reward is None

def test_delete_nonexistent_reward():
    response = client.delete("/api/rewards/999", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Reward not found"

def test_claim_reward():
    db = TestingSessionLocal()
    member = db.query(FamilyMember).first()
    member_id = member.id # Store member.id before closing session
    reward = Reward(name="Claimable Reward", cost=30)
    db.add(reward)
    db.commit()
    db.refresh(member)
    db.refresh(reward)
    db.close()

    response = client.post(
        f"/api/members/{member_id}/claim_reward/{reward.id}",
        headers={"Authorization": "Bearer dummy-token"}
    )
    assert response.status_code == 200
    assert response.json()["total_points"] == 100 - 30 # Initial 100 - 30 from reward

def test_claim_reward_insufficient_points():
    db = TestingSessionLocal()
    member = db.query(FamilyMember).first()
    member_id = member.id # Store member.id before closing session
    reward = Reward(name="Expensive Reward", cost=200)
    db.add(reward)
    db.commit()
    db.refresh(member)
    db.refresh(reward)
    db.close()

    response = client.post(
        f"/api/members/{member_id}/claim_reward/{reward.id}",
        headers={"Authorization": "Bearer dummy-token"}
    )
    assert response.status_code == 400
    assert "insufficient points" in response.json()["detail"]

def test_get_leaderboard():
    response = client.get("/api/leaderboard", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Test Member 1" # Sorted by points desc
    assert response.json()[1]["name"] == "Test Member 2"