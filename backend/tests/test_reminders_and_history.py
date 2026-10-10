import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data

def test_disease_analyze_alias():
    payload = {
        "species": "Cattle (Bovine)",
        "temperature": "104.2",
        "appetite": "Reduced",
        "activity_level": "Lethargic",
        "breathing_condition": "Rapid",
        "symptoms": ["Rapid, shallow dyspneic breathing", "Serous to mucopurulent nasal discharge"],
        "observations": "Flank breathing and reduced cud chewing."
    }
    response = client.post("/api/disease/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "assessment_id" in data
    assert "possible_condition" in data
    assert "risk_level" in data
    assert "confidence" in data
    assert "recommended_immediate_actions" in data

def test_get_history_endpoint():
    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 1

def test_get_disease_history_alias():
    response = client.get("/api/disease/history")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data

def test_reminders_crud():
    # 1. Get initial reminders
    get_res = client.get("/api/reminders")
    assert get_res.status_code == 200
    initial_items = get_res.json()["items"]
    assert len(initial_items) >= 1

    # 2. Create new reminder
    create_payload = {
        "title": "Brucellosis Surveillance Screen",
        "description": "Collect serum sample for milk ring test.",
        "animal_id": "TAG-TEST-999",
        "due_date": "2026-10-25",
        "reminder_type": "HEALTH_CHECK",
        "priority": "HIGH"
    }
    post_res = client.post("/api/reminders", json=create_payload)
    assert post_res.status_code == 201
    created_rem = post_res.json()
    rem_id = created_rem["reminder_id"]
    assert created_rem["title"] == "Brucellosis Surveillance Screen"
    assert created_rem["status"] == "PENDING"

    # 3. Update reminder to completed
    put_res = client.put(f"/api/reminders/{rem_id}", json={"status": "COMPLETED"})
    assert put_res.status_code == 200
    updated_rem = put_res.json()
    assert updated_rem["status"] == "COMPLETED"
    assert updated_rem["completed_at"] is not None

    # 4. Delete reminder
    del_res = client.delete(f"/api/reminders/{rem_id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

def test_sync_status_preservation():
    response = client.get("/api/sync/status")
    assert response.status_code == 200
    data = response.json()
    assert "server_timestamp" in data and "server_version" in data
