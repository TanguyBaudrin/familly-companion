from src.core.models import FamilyMember, Task, Reward

def test_read_members(client, db_session):
    member1 = FamilyMember(name="Test Member 1", total_points=100)
    member2 = FamilyMember(name="Test Member 2", total_points=50)
    db_session.add_all([member1, member2])
    db_session.commit()
    db_session.refresh(member1)
    db_session.refresh(member2)

    response = client.get("/api/members", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Test Member 1"

def test_read_member_by_id(client, db_session):
    member = FamilyMember(name="Test Member 1", total_points=100)
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)

    response = client.get(f"/api/members/{member.id}", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 200
    assert response.json()["name"] == member.name

def test_read_nonexistent_member(client):
    response = client.get("/api/members/999", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Member not found"

def test_create_member(client, db_session):
    response = client.post(
        "/api/members",
        headers={"Authorization": "Bearer dummy-token"},
        json={"name": "New Member"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "New Member"
    # Verify it's in the database
    new_member = db_session.query(FamilyMember).filter_by(name="New Member").first()
    assert new_member is not None

def test_update_member(client, db_session):
    member = FamilyMember(name="Original Name", total_points=100)
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)

    response = client.put(
        f"/api/members/{member.id}",
        headers={"Authorization": "Bearer dummy-token"},
        json={"name": "Updated Member Name", "total_points": 150}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Member Name"
    assert response.json()["total_points"] == 150
    # Verify it's updated in the database
    updated_member = db_session.query(FamilyMember).filter_by(id=member.id).first()
    assert updated_member.name == "Updated Member Name"
    assert updated_member.total_points == 150

def test_update_nonexistent_member(client):
    response = client.put(
        "/api/members/999",
        headers={"Authorization": "Bearer dummy-token"},
        json={"name": "Nonexistent", "total_points": 100}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Member not found"

def test_delete_member(client, db_session):
    member = FamilyMember(name="Member to Delete", total_points=100)
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)

    response = client.delete(f"/api/members/{member.id}", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 204

    # Verify member is deleted
    deleted_member = db_session.query(FamilyMember).filter(FamilyMember.id == member.id).first()
    assert deleted_member is None

def test_delete_nonexistent_member(client):
    response = client.delete("/api/members/999", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Member not found"

def test_read_tasks(client, db_session):
    member = FamilyMember(name="Task Member", total_points=0)
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)

    task = Task(description="Test Task", points=10, assigned_to_id=member.id)
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.get("/api/tasks", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["description"] == "Test Task"

def test_read_task_by_id(client, db_session):
    member = FamilyMember(name="Task Member", total_points=0)
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)

    task = Task(description="Specific Task", points=10, assigned_to_id=member.id)
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.get(f"/api/tasks/{task.id}", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 200
    assert response.json()["description"] == "Specific Task"

def test_read_nonexistent_task(client):
    response = client.get("/api/tasks/999", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_create_task(client, db_session):
    member = FamilyMember(name="New Task Member", total_points=0)
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)

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
    new_task = db_session.query(Task).filter_by(description="New Task").first()
    assert new_task is not None

def test_update_task(client, db_session):
    member = FamilyMember(name="Update Task Member", total_points=0)
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)

    task = Task(description="Task to Update", points=10, assigned_to_id=member.id)
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.put(
        f"/api/tasks/{task.id}",
        headers={"Authorization": "Bearer dummy-token"},
        json={"description": "Updated Task", "points": 25, "status": "completed"}
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Updated Task"
    assert response.json()["points"] == 25
    assert response.json()["status"] == "completed"
    updated_task = db_session.query(Task).filter_by(id=task.id).first()
    assert updated_task.description == "Updated Task"
    assert updated_task.points == 25
    assert updated_task.status == "completed"

def test_update_nonexistent_task(client):
    response = client.put(
        "/api/tasks/999",
        headers={"Authorization": "Bearer dummy-token"},
        json={"description": "Nonexistent Task", "points": 10}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_delete_task(client, db_session):
    member = FamilyMember(name="Delete Task Member", total_points=0)
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)

    task = Task(description="Task to Delete", points=10, assigned_to_id=member.id)
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.delete(f"/api/tasks/{task.id}", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 204

    deleted_task = db_session.query(Task).filter(Task.id == task.id).first()
    assert deleted_task is None

def test_delete_nonexistent_task(client):
    response = client.delete("/api/tasks/999", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_complete_task(client, db_session):
    member = FamilyMember(name="Completing Member", total_points=100)
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)

    task = Task(description="Task to Complete", points=15, assigned_to_id=member.id)
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.post(
            f"/api/tasks/{task.id}/complete",
            headers={"Authorization": "Bearer dummy-token"},
            json={"completions": [{"member_id": member.id, "percentage": 100}]}
        )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    
    updated_member = db_session.query(FamilyMember).filter(FamilyMember.id == member.id).first()
    assert updated_member.total_points == 100 + 15

def test_read_rewards(client, db_session):
    reward = Reward(name="Test Reward", cost=50)
    db_session.add(reward)
    db_session.commit()
    db_session.refresh(reward)

    response = client.get("/api/rewards", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Test Reward"

def test_read_reward_by_id(client, db_session):
    reward = Reward(name="Specific Reward", cost=50)
    db_session.add(reward)
    db_session.commit()
    db_session.refresh(reward)

    response = client.get(f"/api/rewards/{reward.id}", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 200
    assert response.json()["name"] == "Specific Reward"

def test_read_nonexistent_reward(client):
    response = client.get("/api/rewards/999", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Reward not found"

def test_create_reward(client, db_session):
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
    new_reward = db_session.query(Reward).filter_by(name="New Reward").first()
    assert new_reward is not None

def test_update_reward(client, db_session):
    reward = Reward(name="Reward to Update", cost=50)
    db_session.add(reward)
    db_session.commit()
    db_session.refresh(reward)

    response = client.put(
        f"/api/rewards/{reward.id}",
        headers={"Authorization": "Bearer dummy-token"},
        json={"name": "Updated Reward", "cost": 100, "description": "An updated reward"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Reward"
    assert response.json()["cost"] == 100
    assert response.json()["description"] == "An updated reward"
    updated_reward = db_session.query(Reward).filter_by(id=reward.id).first()
    assert updated_reward.name == "Updated Reward"
    assert updated_reward.cost == 100

def test_update_nonexistent_reward(client):
    response = client.put(
        "/api/rewards/999",
        headers={"Authorization": "Bearer dummy-token"},
        json={}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Reward not found"

def test_delete_reward(client, db_session):
    reward = Reward(name="Reward to Delete", cost=50)
    db_session.add(reward)
    db_session.commit()
    db_session.refresh(reward)

    response = client.delete(f"/api/rewards/{reward.id}", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 204

    deleted_reward = db_session.query(Reward).filter(Reward.id == reward.id).first()
    assert deleted_reward is None

def test_delete_nonexistent_reward(client):
    response = client.delete("/api/rewards/999", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Reward not found"

def test_claim_reward(client, db_session):
    member = FamilyMember(name="Claiming Member", total_points=100)
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)

    reward = Reward(name="Claimable Reward", cost=30)
    db_session.add(reward)
    db_session.commit()
    db_session.refresh(reward)

    response = client.post(
        "/api/rewards/claim",  # Correct endpoint
        headers={"Authorization": "Bearer dummy-token"},
        json={"member_id": member.id, "reward_id": reward.id} # Correct payload
    )
    assert response.status_code == 200
    updated_member = db_session.query(FamilyMember).filter_by(id=member.id).first()
    assert updated_member.total_points == 100 - 30

def test_claim_reward_insufficient_points(client, db_session):
    member = FamilyMember(name="Poor Member", total_points=10)
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)

    reward = Reward(name="Expensive Reward", cost=200)
    db_session.add(reward)
    db_session.commit()
    db_session.refresh(reward)

    response = client.post(
        "/api/rewards/claim", # Correct endpoint
        headers={"Authorization": "Bearer dummy-token"},
        json={"member_id": member.id, "reward_id": reward.id} # Correct payload
    )
    assert response.status_code == 400
    assert "insufficient points" in response.json()["detail"]

def test_get_leaderboard(client, db_session):
    member1 = FamilyMember(name="Leader 1", total_points=200)
    member2 = FamilyMember(name="Leader 2", total_points=150)
    db_session.add_all([member1, member2])
    db_session.commit()
    db_session.refresh(member1)
    db_session.refresh(member2)

    response = client.get("/api/leaderboard", headers={"Authorization": "Bearer dummy-token"})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Leader 1"
    assert response.json()[1]["name"] == "Leader 2"
