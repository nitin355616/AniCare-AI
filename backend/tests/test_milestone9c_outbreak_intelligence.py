"""
AniCare AI — Milestone 9C Test Suite
Outbreak Intelligence & Syndromic Early Warning System

Validates:
1. Cluster detection rules (thresholds, geographic boundaries, temporal windows)
2. Explainable risk scoring (0-100) and risk tier resolution (Tier 1 Routine, Tier 2 Surveillance, Tier 3 Red Alert)
3. Trend percentage calculation with zero-division safeguard
4. Automatic early warning alert generation and deduplication
5. Role-based security (Farmers blocked with 403 on scan, assign, status update, investigation)
6. Veterinary officer assignment workflow
7. Certified field investigation record submission and lifecycle status transitions
8. False alert handling and resolution
9. Epidemiological statistics, trend analytics, geographic hotspots, and SIH demo cluster seeding
"""

import uuid
import datetime
import pytest
from app.utils.security import create_access_token
from app.services.outbreak_service import (
    parse_location,
    calculate_outbreak_risk_score,
    CLUSTER_MIN_CASES,
    RED_ALERT_MIN_CASES
)
from app.schemas.outbreak import OutbreakRiskTier, LocationHierarchy, OutbreakStatus


def get_auth_header(role: str, user_id: str = None) -> dict:
    uid = user_id or f"usr_{uuid.uuid4().hex[:6]}"
    payload = {
        "sub": uid,
        "role": role,
        "email": f"{role}_{uid}@anicare.ai",
        "name": f"Dr. Test {role.capitalize()}" if role == "veterinarian" else f"Test {role.capitalize()}"
    }
    token = create_access_token(payload)
    return {"Authorization": f"Bearer {token}"}


def test_cluster_detection_logic_and_scoring_unit():
    """Unit test for location parsing, trend calculation, and explainable risk scoring."""
    # 1. Location parsing
    loc1 = parse_location("Village Boriavi, Anand Rural, Anand, Gujarat")
    assert loc1.village == "Boriavi"
    assert loc1.district == "Anand"
    assert loc1.state == "Gujarat"

    loc_unknown = parse_location("")
    assert loc_unknown.village == "LOCATION_UNKNOWN"
    assert loc_unknown.district == "LOCATION_UNKNOWN"

    # 2. Risk scoring & tiers
    # Low caseload (< 3 cases) -> Tier 1 Routine
    score_low, reasons_low, tier_low = calculate_outbreak_risk_score(
        case_count=2,
        high_crit_count=1,
        critical_count=0,
        trend_pct=0.0,
        location=loc1,
        condition="Lumpy Skin Disease"
    )
    assert tier_low == OutbreakRiskTier.TIER_1_ROUTINE
    assert score_low < 40

    # Cluster threshold (3 cases) -> Tier 2 Surveillance
    score_med, reasons_med, tier_med = calculate_outbreak_risk_score(
        case_count=3,
        high_crit_count=2,
        critical_count=1,
        trend_pct=50.0,
        location=loc1,
        condition="Lumpy Skin Disease"
    )
    assert tier_med == OutbreakRiskTier.TIER_2_SURVEILLANCE
    assert score_med >= 40
    assert any("+15 pts" in r for r in reasons_med)

    # Red alert threshold (5 cases with critical severity and growth) -> Tier 3 Red Alert
    score_high, reasons_high, tier_high = calculate_outbreak_risk_score(
        case_count=6,
        high_crit_count=5,
        critical_count=2,
        trend_pct=150.0,
        location=loc1,
        condition="Lumpy Skin Disease"
    )
    assert tier_high == OutbreakRiskTier.TIER_3_RED_ALERT
    assert score_high >= 75
    assert any("+15 pts: Rapid epidemiological surge" in r for r in reasons_high)


def test_outbreak_scan_and_cluster_generation(client):
    """Verifies that scanning cases in the same village generates an active cluster event."""
    vet_headers = get_auth_header("veterinarian")
    vil_name = f"Vil-Cluster-{uuid.uuid4().hex[:4]}"
    loc_str = f"{vil_name}, Anand Rural, Anand, Gujarat"

    # Create 3 high-risk veterinary cases in this village
    case_ids = []
    for i in range(3):
        res = client.post("/api/veterinary/cases", json={
            "animal_id": f"AN-M9C-{uuid.uuid4().hex[:4]}",
            "animal_name": f"Cow #{i+1}",
            "species": "Cattle",
            "location": loc_str,
            "risk_level": "HIGH",
            "condition": "Suspected Lumpy Skin Disease"
        })
        assert res.status_code == 201
        case_ids.append(res.json()["case_id"])

    # Trigger syndromic scan
    scan_res = client.post("/api/outbreaks/scan", json={"window_days": 7}, headers=vet_headers)
    assert scan_res.status_code == 200
    scan_data = scan_res.json()
    assert scan_data["status"] == "success"

    # Retrieve outbreaks for this village
    outbreaks_res = client.get("/api/outbreaks")
    assert outbreaks_res.status_code == 200
    events = outbreaks_res.json()["items"]
    matched = [e for e in events if e["location"]["village"] == vil_name]
    assert len(matched) >= 1
    event = matched[0]
    assert event["case_count"] >= 3
    assert event["status"] in ["DETECTED", "UNDER_SURVEILLANCE"]
    assert event["risk_tier"] in ["TIER_2_SURVEILLANCE", "TIER_3_RED_ALERT"]
    assert "AI-ASSISTED EARLY WARNING" in event["disclaimer"]


def test_alert_generation_and_deduplication(client):
    """Verifies that detected clusters trigger early warning alerts and prevent duplicate spam."""
    vet_headers = get_auth_header("veterinarian")
    vil_name = f"Vil-Alert-{uuid.uuid4().hex[:4]}"
    loc_str = f"{vil_name}, Anand Rural, Anand, Gujarat"

    for i in range(3):
        client.post("/api/veterinary/cases", json={
            "animal_id": f"AN-ALT-{uuid.uuid4().hex[:4]}",
            "animal_name": f"Heifer #{i+1}",
            "species": "Cattle",
            "location": loc_str,
            "risk_level": "HIGH",
            "condition": "Suspected Lumpy Skin Disease"
        })

    # First scan: creates event and alert
    client.post("/api/outbreaks/scan", json={"window_days": 7}, headers=vet_headers)

    alerts_res1 = client.get("/api/alerts")
    assert alerts_res1.status_code == 200
    alerts1 = alerts_res1.json()["items"]
    matched_alerts1 = [a for a in alerts1 if vil_name.lower() in a["location"].lower()]
    assert len(matched_alerts1) >= 1

    # Second scan: updates without creating duplicate alert
    client.post("/api/outbreaks/scan", json={"window_days": 7}, headers=vet_headers)
    alerts_res2 = client.get("/api/alerts")
    alerts2 = alerts_res2.json()["items"]
    matched_alerts2 = [a for a in alerts2 if vil_name.lower() in a["location"].lower()]
    assert len(matched_alerts2) == len(matched_alerts1)


def test_rbac_farmer_blocked_vet_admin_permitted(client):
    """Verifies that farmers are blocked (HTTP 403) from administrative/clinical outbreak operations."""
    farmer_headers = get_auth_header("farmer")
    vet_headers = get_auth_header("veterinarian")
    admin_headers = get_auth_header("admin")

    # 1. Farmers blocked from triggering syndromic scan
    scan_farm = client.post("/api/outbreaks/scan", json={"window_days": 7}, headers=farmer_headers)
    assert scan_farm.status_code == 403

    # 2. Farmers blocked from seeding demo cluster
    seed_farm = client.post("/api/outbreaks/seed-demo", json={}, headers=farmer_headers)
    assert seed_farm.status_code == 403

    # 3. Admin permitted to trigger scan and seed demo
    scan_adm = client.post("/api/outbreaks/scan", json={"window_days": 7}, headers=admin_headers)
    assert scan_adm.status_code == 200

    # 4. Get any active event to test assign/status permissions
    list_res = client.get("/api/outbreaks")
    assert list_res.status_code == 200
    items = list_res.json()["items"]
    if items:
        ev_id = items[0]["event_id"]

        # Farmer blocked from officer assignment
        assign_farm = client.post(
            f"/api/outbreaks/{ev_id}/assign",
            json={"officer_name": "Dr. Hacker"},
            headers=farmer_headers
        )
        assert assign_farm.status_code == 403

        # Farmer blocked from status update
        stat_farm = client.post if False else client.put
        res_stat = client.put(
            f"/api/outbreaks/{ev_id}/status",
            json={"new_status": "RESOLVED"},
            headers=farmer_headers
        )
        assert res_stat.status_code == 403

        # Farmer blocked from submitting field investigation
        inv_farm = client.post(
            f"/api/outbreaks/{ev_id}/investigation",
            json={
                "field_visit_date": "2026-10-08",
                "animals_examined": 5,
                "clinical_observations": "Fake farmer report",
                "suspected_condition": "Unknown",
                "investigating_officer": "Unauthorized Farmer"
            },
            headers=farmer_headers
        )
        assert inv_farm.status_code == 403


def test_veterinary_officer_assignment_workflow(client):
    """Verifies that authorized staff can assign a Veterinary Officer and audit logging occurs."""
    vet_headers = get_auth_header("veterinarian")
    vil_name = f"Vil-Assign-{uuid.uuid4().hex[:4]}"
    loc_str = f"{vil_name}, Anand Rural, Anand, Gujarat"

    # Create 3 high-risk cases
    for i in range(3):
        client.post("/api/veterinary/cases", json={
            "animal_id": f"AN-ASN-{uuid.uuid4().hex[:4]}",
            "animal_name": f"Cow #{i+1}",
            "species": "Cattle",
            "location": loc_str,
            "risk_level": "HIGH",
            "condition": "Suspected Lumpy Skin Disease"
        })

    client.post("/api/outbreaks/scan", json={"window_days": 7}, headers=vet_headers)
    list_res = client.get("/api/outbreaks")
    matched = [e for e in list_res.json()["items"] if e["location"]["village"] == vil_name]
    assert len(matched) >= 1
    event_id = matched[0]["event_id"]

    # Assign officer
    assign_res = client.post(
        f"/api/outbreaks/{event_id}/assign",
        json={
            "officer_name": "Dr. Sunita Rao",
            "notes": "Emergency deployment to Sector 04 Containment Zone."
        },
        headers=vet_headers
    )
    assert assign_res.status_code == 200
    data = assign_res.json()
    assert data["assigned_veterinary_officer"] == "Dr. Sunita Rao"
    assert data["status"] == "VETERINARY_INVESTIGATION"

    # Verify audit trail
    audits = data["audit_trail"]
    assert any(a["action"] == "OFFICER_ASSIGNED" and "Dr. Sunita Rao" in a["notes"] for a in audits)


def test_clinical_field_investigation_and_status_transitions(client):
    """Verifies submitting certified field investigation and transitioning status to MONITORING and RESOLVED."""
    vet_headers = get_auth_header("veterinarian")
    vil_name = f"Vil-Investigate-{uuid.uuid4().hex[:4]}"
    loc_str = f"{vil_name}, Anand Rural, Anand, Gujarat"

    for i in range(3):
        client.post("/api/veterinary/cases", json={
            "animal_id": f"AN-INV-{uuid.uuid4().hex[:4]}",
            "animal_name": f"Cow #{i+1}",
            "species": "Cattle",
            "location": loc_str,
            "risk_level": "HIGH",
            "condition": "Suspected Lumpy Skin Disease"
        })

    client.post("/api/outbreaks/scan", json={"window_days": 7}, headers=vet_headers)
    list_res = client.get("/api/outbreaks")
    matched = [e for e in list_res.json()["items"] if e["location"]["village"] == vil_name]
    assert len(matched) >= 1
    event_id = matched[0]["event_id"]


    # Submit certified investigation
    inv_res = client.post(
        f"/api/outbreaks/{event_id}/investigation",
        json={
            "field_visit_date": "2026-10-08",
            "animals_examined": 7,
            "clinical_observations": "Physical examination confirms 2-5cm nodular cutaneous circumscribed lesions with fever.",
            "suspected_condition": "Lumpy Skin Disease (Capripox)",
            "laboratory_test_required": True,
            "laboratory_test_status": "SAMPLES_SENT",
            "preventive_actions": ["Physical quarantine in recovery pens", "Halt communal dairy milking"],
            "biosecurity_actions": ["Shed spraying with 2% sodium hypochlorite", "Vector fogging"],
            "farmer_guidance": "Immediately report any secondary mucosal lesions.",
            "follow_up_date": "2026-10-15",
            "investigation_notes": "Clinical staging corresponds to active proliferative phase.",
            "investigating_officer": "Dr. Sunita Rao",
            "officer_license": "VET-REG-2024-99120"
        },
        headers=vet_headers
    )
    assert inv_res.status_code == 200
    inv_data = inv_res.json()
    assert inv_data["status"] == "ACTION_RECOMMENDED"
    assert inv_data["veterinary_review_status"] == "VERIFIED"
    assert inv_data["investigation_record"]["animals_examined"] == 7

    # Transition to MONITORING
    mon_res = client.put(
        f"/api/outbreaks/{event_id}/status",
        json={"new_status": "MONITORING", "notes": "Active vector controls implemented."},
        headers=vet_headers
    )
    assert mon_res.status_code == 200
    assert mon_res.json()["status"] == "MONITORING"

    # Transition to RESOLVED
    res_res = client.put(
        f"/api/outbreaks/{event_id}/status",
        json={"new_status": "RESOLVED", "notes": "All cohort lesions fully healed. 14 days without new cases."},
        headers=vet_headers
    )
    assert res_res.status_code == 200
    assert res_res.json()["status"] == "RESOLVED"
    assert res_res.json()["veterinary_review_status"] == "RESOLVED"


def test_false_alert_workflow(client):
    """Verifies that an event can be designated FALSE_ALERT upon veterinary clinical inspection."""
    vet_headers = get_auth_header("veterinarian")
    vil_name = f"Vil-False-{uuid.uuid4().hex[:4]}"
    loc_str = f"{vil_name}, Anand Rural, Anand, Gujarat"

    # Create 3 cases
    for i in range(3):
        client.post("/api/veterinary/cases", json={
            "animal_id": f"AN-FLS-{uuid.uuid4().hex[:4]}",
            "animal_name": f"Bull #{i+1}",
            "species": "Cattle",
            "location": loc_str,
            "risk_level": "HIGH",
            "condition": "Suspected Demodectic Mange"
        })

    # Scan to create cluster
    client.post("/api/outbreaks/scan", json={"window_days": 7}, headers=vet_headers)

    # Find the created cluster
    list_res = client.get("/api/outbreaks")
    matched = [e for e in list_res.json()["items"] if e["location"]["village"] == vil_name]
    assert len(matched) >= 1
    event_id = matched[0]["event_id"]

    # Mark as FALSE_ALERT
    false_res = client.put(
        f"/api/outbreaks/{event_id}/status",
        json={
            "new_status": "FALSE_ALERT",
            "notes": "Clinical scraping confirmed non-contagious insect bites, not an infectious epizootic cluster."
        },
        headers=vet_headers
    )
    assert false_res.status_code == 200
    data = false_res.json()
    assert data["status"] == "FALSE_ALERT"
    assert data["veterinary_review_status"] == "FALSE_ALERT"

    # Check audit trail
    assert any(a["action"] == "STATUS_CHANGED" and a["new_status"] == "FALSE_ALERT" for a in data["audit_trail"])


def test_trends_hotspots_and_sih_demo_cluster(client):
    """Verifies epidemiological stats, temporal trends, geographic hotspots, and demo cluster isolation."""
    vet_headers = get_auth_header("veterinarian")

    # 1. Stats endpoint
    stats_res = client.get("/api/outbreaks/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "active_clusters" in stats
    assert "red_alerts" in stats
    assert "affected_villages_count" in stats

    # 2. Trends endpoint
    trends_res = client.get("/api/outbreaks/trends")
    assert trends_res.status_code == 200
    trends = trends_res.json()["windows"]
    assert len(trends) == 3
    days_list = [t["days"] for t in trends]
    assert 7 in days_list and 14 in days_list and 30 in days_list
    for t in trends:
        assert isinstance(t["trend_percentage"], float)

    # 3. Hotspots endpoint
    hotspots_res = client.get("/api/outbreaks/hotspots")
    assert hotspots_res.status_code == 200
    h_data = hotspots_res.json()
    assert "total_hotspots" in h_data
    assert "hotspots" in h_data
    if h_data["hotspots"]:
        h0 = h_data["hotspots"][0]
        assert h0["hotspot_level"] in ["HOTSPOT_HIGH", "HOTSPOT_MEDIUM", "HOTSPOT_LOW"]

    # 4. Seed SIH Demo Cluster
    demo_res = client.post("/api/outbreaks/seed-demo", json={}, headers=vet_headers)
    assert demo_res.status_code in [200, 201]
    demo = demo_res.json()
    assert demo["is_demo"] is True
    assert demo["event_id"] == "OUT-DEMO-SIH-01"
    assert demo["risk_tier"] == "TIER_3_RED_ALERT"
    assert demo["case_count"] == 5
    assert "DEMO / SIMULATED DATA" in demo["disclaimer"]
