from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.data.database import get_db, Base
from src.core.models import FamilyMember, Reward, PointsHistory
from datetime import datetime, timedelta, UTC

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_stats.db"
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

    # Create Members
    member1 = FamilyMember(name="Hero 1", total_points=100)
    member2 = FamilyMember(name="Hero 2", total_points=50)
    member3 = FamilyMember(name="Hero 3", total_points=200)
    db.add_all([member1, member2, member3])
    db.commit()

    # Create Rewards
    reward1 = Reward(name="Golden Cookie", cost=20)
    reward2 = Reward(name="Silver Sword", cost=50)
    db.add_all([reward1, reward2])
    db.commit()

    # Create Points History
    now = datetime.now(UTC)
    # This week's points
    history1 = PointsHistory(member_id=member1.id, points_change=25, reason="Quest done", timestamp=now - timedelta(days=1))
    history2 = PointsHistory(member_id=member2.id, points_change=15, reason="Quest done", timestamp=now - timedelta(days=2))
    history3 = PointsHistory(member_id=member1.id, points_change=10, reason="Quest done", timestamp=now)
    # Last week's points
    history4 = PointsHistory(member_id=member3.id, points_change=100, reason="Quest done", timestamp=now - timedelta(weeks=1))
    # This month but not this week (if applicable)
    if (now - timedelta(weeks=1)).month == now.month:
        history5 = PointsHistory(member_id=member2.id, points_change=50, reason="Quest done", timestamp=now - timedelta(weeks=1))
    
    # Claimed rewards
    history6 = PointsHistory(member_id=member1.id, reward_id=reward1.id, points_change=-20, reason="Reward claimed", timestamp=now)
    history7 = PointsHistory(member_id=member3.id, reward_id=reward1.id, points_change=-20, reason="Reward claimed", timestamp=now - timedelta(days=1))
    history8 = PointsHistory(member_id=member2.id, reward_id=reward2.id, points_change=-50, reason="Reward claimed", timestamp=now - timedelta(days=3))

    db.add_all([history1, history2, history3, history4, history6, history7, history8])
    if 'history5' in locals():
        db.add(history5)
    db.commit()
    db.close()

def teardown_function(function):
    Base.metadata.drop_all(bind=engine)

def test_get_statistics_weekly():
    response = client.get("/api/v1/statistiques?period=weekly")
    assert response.status_code == 200
    data = response.json()

    # Test points by user (weekly)
    points_data = data["points_by_user"]
    # Hero 1: 25 + 10 = 35 points
    # Hero 2: 15 points
    assert len(points_data) == 2
    assert {"name": "Hero 1", "points": 35} in points_data
    assert {"name": "Hero 2", "points": 15} in points_data
    # Check order
    assert points_data[0]["name"] == "Hero 1"

    # Test most used rewards
    rewards_data = data["most_used_rewards"]
    # Golden Cookie: 2 times
    # Silver Sword: 1 time
    assert len(rewards_data) == 2
    assert {"name": "Golden Cookie", "count": 2} in rewards_data
    assert {"name": "Silver Sword", "count": 1} in rewards_data
    # Check order
    assert rewards_data[0]["name"] == "Golden Cookie"

def test_get_statistics_monthly():
    response = client.get("/api/v1/statistiques?period=monthly")
    assert response.status_code == 200
    data = response.json()

    # Test points by user (monthly)
    points_data = data["points_by_user"]
    # This test is dependent on when it's run. If the test runs at the beginning of the month,
    # last week's data might not be in the same month.
    # We will check the members present and their minimum expected points.
    
    hero1_points = next((item['points'] for item in points_data if item["name"] == "Hero 1"), 0)
    hero2_points = next((item['points'] for item in points_data if item["name"] == "Hero 2"), 0)
    hero3_points = next((item['points'] for item in points_data if item["name"] == "Hero 3"), 0)

    assert hero1_points == 35
    # Hero 3's points from last week might be in this month
    now = datetime.now(UTC)
    if (now - timedelta(weeks=1)).month == now.month:
        assert hero2_points >= 15 # 15 from this week + maybe 50 from last week
        assert hero3_points == 100
    else:
        assert hero2_points == 15
        assert hero3_points == 0 # Points from last month

def test_get_statistics_invalid_period():
    response = client.get("/api/v1/statistiques?period=yearly")
    assert response.status_code == 400
    assert response.json()["detail"] == "La période doit être 'weekly' ou 'monthly'."
