from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.data.database import get_db, Base
from src.core.models import FamilyMember, Task, Reward, PointsHistory
from datetime import datetime, timedelta, UTC

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_hero_details.db"
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
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Create Member
    hero = FamilyMember(name="Test Hero", total_points=155)
    db.add(hero)
    db.commit()

    # Create Tasks
    pending_task = Task(description="Pending Quest", points=20, assigned_to_id=hero.id, status='pending')
    completed_task = Task(description="Completed Quest", points=50, assigned_to_id=hero.id, status='completed', completed_at=datetime.now(UTC) - timedelta(days=2))
    db.add_all([pending_task, completed_task])
    db.commit()

    # Create Reward
    reward = Reward(name="Magic Sword", cost=30)
    db.add(reward)
    db.commit()

    # Create Points History
    now = datetime.now(UTC)
    # Points from this week
    points1 = PointsHistory(member_id=hero.id, points_change=50, reason="Quest done", timestamp=now - timedelta(days=2)) # from completed_task
    points2 = PointsHistory(member_id=hero.id, points_change=15, reason="Another quest", timestamp=now - timedelta(days=1))
    # Points from last month
    points3 = PointsHistory(member_id=hero.id, points_change=100, reason="Old quest", timestamp=now - timedelta(days=40))
    # Reward claimed
    reward_claim = PointsHistory(member_id=hero.id, reward_id=reward.id, points_change=-30, reason="Reward claimed", timestamp=now - timedelta(days=3))
    
    db.add_all([points1, points2, points3, reward_claim])
    db.commit()
    db.close()

def teardown_function(function):
    Base.metadata.drop_all(bind=engine)

def test_get_member_details_weekly():
    db = TestingSessionLocal()
    hero = db.query(FamilyMember).first()
    db.close()

    response = client.get(f"/api/v1/members/{hero.id}/details?period=weekly")
    assert response.status_code == 200
    data = response.json()

    # Check member name
    assert data["member"]["name"] == "Test Hero"

    # Check tasks
    assert len(data["pending_tasks"]) == 1
    assert data["pending_tasks"][0]["description"] == "Pending Quest"
    assert len(data["completed_tasks"]) == 1
    assert data["completed_tasks"][0]["description"] == "Completed Quest"

    # Check daily points (weekly)
    # Expecting 2 entries: one for 2 days ago, one for 1 day ago
    assert len(data["daily_points"]) == 2
    assert data["daily_points"][0]["points"] == 50
    assert data["daily_points"][1]["points"] == 15

    # Check claimed rewards
    assert len(data["claimed_rewards"]) == 1
    assert data["claimed_rewards"][0]["name"] == "Magic Sword"

def test_get_member_details_monthly():
    db = TestingSessionLocal()
    hero = db.query(FamilyMember).first()
    db.close()

    response = client.get(f"/api/v1/members/{hero.id}/details?period=monthly")
    assert response.status_code == 200
    data = response.json()

    # Check daily points (monthly)
    # This test assumes the test runs in a month where the weekly data is also in the same month.
    # The logic should be robust enough to handle this.
    assert len(data["daily_points"]) >= 2 # At least the two points from this week

def test_get_member_details_not_found():
    response = client.get("/api/v1/members/999/details")
    assert response.status_code == 404
    assert response.json()["detail"] == "Membre non trouvé"
