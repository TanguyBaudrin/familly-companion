from src.core.models import FamilyMember, Reward, PointsHistory
from datetime import datetime, timedelta, UTC

def test_get_statistics_weekly(client, db_session):
    # Create Members
    member1 = FamilyMember(name="Hero 1", total_points=100)
    member2 = FamilyMember(name="Hero 2", total_points=50)
    member3 = FamilyMember(name="Hero 3", total_points=200)
    db_session.add_all([member1, member2, member3])
    db_session.commit()
    db_session.refresh(member1)
    db_session.refresh(member2)
    db_session.refresh(member3)

    # Create Rewards
    reward1 = Reward(name="Golden Cookie", cost=20)
    reward2 = Reward(name="Silver Sword", cost=50)
    db_session.add_all([reward1, reward2])
    db_session.commit()
    db_session.refresh(reward1)
    db_session.refresh(reward2)

    # Create Points History
    now = datetime.now(UTC)
    test_start_of_week = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=now.weekday())
    # This week's points
    history1 = PointsHistory(member_id=member1.id, points_change=25, reason="Quest done", timestamp=test_start_of_week + timedelta(days=0)) # Monday
    history2 = PointsHistory(member_id=member2.id, points_change=15, reason="Quest done", timestamp=test_start_of_week + timedelta(days=1)) # Tuesday
    history3 = PointsHistory(member_id=member1.id, points_change=10, reason="Quest done", timestamp=test_start_of_week + timedelta(days=2)) # Wednesday
    # Last week's points (should not be included in weekly stats)
    history4 = PointsHistory(member_id=member3.id, points_change=100, reason="Quest done", timestamp=test_start_of_week - timedelta(weeks=1))
    # This month but not this week (should not be included in weekly stats)
    history5 = PointsHistory(member_id=member2.id, points_change=50, reason="Quest done", timestamp=test_start_of_week - timedelta(days=10)) # Example: 10 days before start of week
    
    # Claimed rewards
    history6 = PointsHistory(member_id=member1.id, reward_id=reward1.id, points_change=-20, reason="Reward claimed", timestamp=test_start_of_week + timedelta(days=0))
    history7 = PointsHistory(member_id=member3.id, reward_id=reward1.id, points_change=-20, reason="Reward claimed", timestamp=test_start_of_week + timedelta(days=1))
    history8 = PointsHistory(member_id=member2.id, reward_id=reward2.id, points_change=-50, reason="Reward claimed", timestamp=test_start_of_week + timedelta(days=3))

    db_session.add_all([history1, history2, history3, history4, history5, history6, history7, history8])
    db_session.commit()

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

def test_get_statistics_monthly(client, db_session):
    # Create Members
    member1 = FamilyMember(name="Hero 1", total_points=100)
    member2 = FamilyMember(name="Hero 2", total_points=50)
    member3 = FamilyMember(name="Hero 3", total_points=200)
    db_session.add_all([member1, member2, member3])
    db_session.commit()
    db_session.refresh(member1)
    db_session.refresh(member2)
    db_session.refresh(member3)

    # Create Points History
    now = datetime.now(UTC)
    # This month's points
    history1 = PointsHistory(member_id=member1.id, points_change=25, reason="Quest done", timestamp=now - timedelta(days=1))
    history2 = PointsHistory(member_id=member2.id, points_change=15, reason="Quest done", timestamp=now - timedelta(days=2))
    history3 = PointsHistory(member_id=member1.id, points_change=10, reason="Quest done", timestamp=now)
    history4 = PointsHistory(member_id=member3.id, points_change=100, reason="Quest done", timestamp=now - timedelta(days=5)) # Still in this month
    db_session.add_all([history1, history2, history3, history4])
    db_session.commit()

    response = client.get("/api/v1/statistiques?period=monthly")
    assert response.status_code == 200
    data = response.json()

    # Test points by user (monthly)
    points_data = data["points_by_user"]
    
    now = datetime.now(UTC)
    test_start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # This month's points
    history1 = PointsHistory(member_id=member1.id, points_change=25, reason="Quest done", timestamp=test_start_of_month + timedelta(days=0))
    history2 = PointsHistory(member_id=member2.id, points_change=15, reason="Quest done", timestamp=test_start_of_month + timedelta(days=1))
    history3 = PointsHistory(member_id=member1.id, points_change=10, reason="Quest done", timestamp=test_start_of_month + timedelta(days=2))
    history4 = PointsHistory(member_id=member3.id, points_change=100, reason="Quest done", timestamp=test_start_of_month + timedelta(days=3))

def test_get_statistics_invalid_period(client):
    response = client.get("/api/v1/statistiques?period=yearly")
    assert response.status_code == 400
    assert response.json()["detail"] == "La période doit être 'weekly' ou 'monthly'."