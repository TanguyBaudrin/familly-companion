from src.core.models import FamilyMember, Task, Reward, PointsHistory
from datetime import datetime, timedelta, UTC

def test_get_member_details_weekly(client, db_session):
    # Create Member
    hero = FamilyMember(name="Test Hero", total_points=155)
    db_session.add(hero)
    db_session.commit()
    db_session.refresh(hero)

    # Create Tasks
    pending_task = Task(description="Pending Quest", points=20, assigned_to_id=hero.id, status='pending')
    completed_task = Task(description="Completed Quest", points=50, assigned_to_id=hero.id, status='completed', completed_at=datetime.now(UTC) - timedelta(days=2))
    db_session.add_all([pending_task, completed_task])
    db_session.commit()
    db_session.refresh(pending_task)
    db_session.refresh(completed_task)

    # Create Reward
    reward = Reward(name="Magic Sword", cost=30)
    db_session.add(reward)
    db_session.commit()
    db_session.refresh(reward)

    # Create Points History
    now = datetime.now(UTC)
    test_start_of_week = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=now.weekday())
    # Points from this week
    points1 = PointsHistory(member_id=hero.id, points_change=50, reason="Quest done", timestamp=test_start_of_week + timedelta(days=5)) # Friday
    points2 = PointsHistory(member_id=hero.id, points_change=15, reason="Another quest", timestamp=test_start_of_week + timedelta(days=6)) # Saturday
    # Points from last month
    points3 = PointsHistory(member_id=hero.id, points_change=100, reason="Old quest", timestamp=test_start_of_week - timedelta(days=40))
    # Reward claimed
    reward_claim = PointsHistory(member_id=hero.id, reward_id=reward.id, points_change=-30, reason="Reward claimed", timestamp=test_start_of_week + timedelta(days=4)) # Thursday
    
    db_session.add_all([points1, points2, points3, reward_claim])
    db_session.commit()

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

def test_get_member_details_monthly(client, db_session):
    hero = FamilyMember(name="Test Hero Monthly", total_points=155)
    db_session.add(hero)
    db_session.commit()
    db_session.refresh(hero)

    now = datetime.now(UTC)
    points1 = PointsHistory(member_id=hero.id, points_change=50, reason="Quest done", timestamp=now - timedelta(days=2))
    points2 = PointsHistory(member_id=hero.id, points_change=15, reason="Another quest", timestamp=now - timedelta(days=1))
    points3 = PointsHistory(member_id=hero.id, points_change=100, reason="Old quest", timestamp=now - timedelta(days=40))
    db_session.add_all([points1, points2, points3])
    db_session.commit()

    response = client.get(f"/api/v1/members/{hero.id}/details?period=monthly")
    assert response.status_code == 200
    data = response.json()

    # Check daily points (monthly)
    # This test assumes the test runs in a month where the weekly data is also in the same month.
    # The logic should be robust enough to handle this.
    assert len(data["daily_points"]) >= 2 # At least the two points from this week

def test_get_member_details_not_found(client):
    response = client.get("/api/v1/members/999/details")
    assert response.status_code == 404
    assert response.json()["detail"] == "Membre non trouvé"