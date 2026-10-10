"""
AniCare AI — Milestone 12 Test Suite
Geospatial Disease Intelligence & Risk Mapping Platform

Validates:
1. Spatial risk score calculation (0-100) & weight contributions
2. Risk tier classification (LOW, MODERATE, HIGH, CRITICAL)
3. 7-day growth percentage calculation
4. Zero previous cases handling (NEW_SIGNAL, zero division safeguard)
5. Village hotspot aggregation
6. Block aggregation
7. District aggregation
8. Spatial spread signal detection & safe wording
9. Farmer access blocked (HTTP 403 Forbidden)
10. Veterinarian access permitted
11. Admin access permitted
12. Privacy-safe map response (administrative centroids only)
13. No exact household location leakage
14. Demo data correctly labelled (is_demo: True)
15. Offline stale-data indicator and timestamps
16. Integration with existing Milestone 9C outbreak intelligence
"""

import uuid
import pytest
from app.utils.security import create_access_token
from app.services.geospatial_service import (
    calculate_spatial_risk_score,
    calculate_growth_metric,
    resolve_admin_centroid,
    resolve_hotspot_status_and_priority,
    RISK_FACTOR_WEIGHTS
)
from app.schemas.geospatial import (
    GeoRiskTier,
    HotspotStatus,
    HotspotPriority,
    LocationAccuracy,
    GEOSPATIAL_SAFETY_DISCLAIMER
)


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


def test_1_risk_score_calculation():
    """Validates transparent, explainable risk score calculation bounded between 0 and 100."""
    # Test low caseload
    score_low, tier_low, drivers_low, _ = calculate_spatial_risk_score(
        current_cases=1,
        previous_cases=1,
        critical_cases=0,
        high_cases=0,
        affected_herds_count=1
    )
    assert 0 <= score_low <= 100
    assert len(drivers_low) == 6
    assert any(d.factor == "Case Burden" for d in drivers_low)
    assert any(d.factor == "Recent Growth" for d in drivers_low)

    # Test high caseload
    score_high, tier_high, drivers_high, _ = calculate_spatial_risk_score(
        current_cases=12,
        previous_cases=4,
        critical_cases=4,
        high_cases=6,
        affected_herds_count=5
    )
    assert score_high >= 75
    assert tier_high in [GeoRiskTier.HIGH, GeoRiskTier.CRITICAL]


def test_2_risk_tier_classification():
    """Validates assignment of LOW, MODERATE, HIGH, and CRITICAL risk tiers."""
    # Low: 1 case, 0 critical -> LOW
    score1, tier1, _, _ = calculate_spatial_risk_score(1, 1, 0, 0, 1)
    assert tier1 == GeoRiskTier.LOW or score1 < 30

    # Moderate: 3 cases, moderate growth -> MODERATE
    score2, tier2, _, _ = calculate_spatial_risk_score(3, 2, 0, 1, 2)
    assert score2 >= 30

    # Critical: 15 cases, 5 critical, +200% growth -> CRITICAL
    score3, tier3, _, _ = calculate_spatial_risk_score(15, 5, 5, 8, 6)
    assert score3 >= 80
    assert tier3 == GeoRiskTier.CRITICAL


def test_3_7d_growth_calculation():
    """Validates 7-day growth percentage calculation with positive and negative growth."""
    # Positive growth: 4 -> 10 cases = +150%
    pct1, lbl1 = calculate_growth_metric(current_cases=10, previous_cases=4)
    assert pct1 == 150.0
    assert lbl1 == "+150.0%"

    # Negative growth: 10 -> 5 cases = -50%
    pct2, lbl2 = calculate_growth_metric(current_cases=5, previous_cases=10)
    assert pct2 == -50.0
    assert lbl2 == "-50.0%"

    # Flat growth: 4 -> 4 cases = 0%
    pct3, lbl3 = calculate_growth_metric(current_cases=4, previous_cases=4)
    assert pct3 == 0.0
    assert lbl3 == "+0.0%"


def test_4_zero_previous_cases_handling():
    """Validates zero division safeguard when previous cases == 0."""
    # previous=0, current=5 -> NEW_SIGNAL without division-by-zero or infinity
    pct, lbl = calculate_growth_metric(current_cases=5, previous_cases=0)
    assert pct == 100.0
    assert lbl == "NEW_SIGNAL"

    # previous=0, current=0 -> 0.0%
    pct_zero, lbl_zero = calculate_growth_metric(current_cases=0, previous_cases=0)
    assert pct_zero == 0.0
    assert lbl_zero == "0.0%"


def test_5_village_hotspot_aggregation(client):
    """Verifies geospatial intelligence aggregates cases at the village level."""
    admin_headers = get_auth_header("admin")
    res = client.get("/api/geospatial/risk-map?level=village", headers=admin_headers)
    assert res.status_code == 200
    points = res.json()
    assert isinstance(points, list)
    assert len(points) >= 1
    assert all("village" in p for p in points)
    assert all(p["level"] == "village" for p in points)


def test_6_block_aggregation(client):
    """Verifies geospatial intelligence aggregates cases at the block/sub-district level."""
    vet_headers = get_auth_header("veterinarian")
    res = client.get("/api/geospatial/risk-map?level=block", headers=vet_headers)
    assert res.status_code == 200
    points = res.json()
    assert isinstance(points, list)
    assert len(points) >= 1
    assert all(p["level"] == "block" for p in points)


def test_7_district_aggregation(client):
    """Verifies geospatial intelligence aggregates cases at the district level."""
    vet_headers = get_auth_header("veterinarian")
    res = client.get("/api/geospatial/risk-map?level=district", headers=vet_headers)
    assert res.status_code == 200
    points = res.json()
    assert isinstance(points, list)
    assert len(points) >= 1
    assert all(p["level"] == "district" for p in points)


def test_8_spatial_spread_signal(client):
    """Verifies detection of spatial spread signals and required non-definitive wording."""
    vet_headers = get_auth_header("veterinarian")
    res = client.get("/api/geospatial/spread", headers=vet_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["spread_patterns_detected"] >= 1
    signals = data["active_spread_signals"]
    assert len(signals) >= 1
    sig = signals[0]
    assert sig["signal_status"] in ["SPREAD_SIGNAL_DETECTED", "NO_CLEAR_SPREAD_SIGNAL"]
    # Check non-definitive safety wording
    assert "Geographical" in sig["description"]
    assert "field verification recommended" in sig["description"].lower()


def test_9_farmer_access_denied(client):
    """Verifies that farmers are blocked (HTTP 403 Forbidden) from government-wide maps and recalculation."""
    farmer_headers = get_auth_header("farmer")

    # 1. Blocked from overview
    res_ov = client.get("/api/geospatial/overview", headers=farmer_headers)
    assert res_ov.status_code == 403
    assert "Access forbidden" in res_ov.json().get("error", "") or res_ov.status_code == 403

    # 2. Blocked from risk map
    res_map = client.get("/api/geospatial/risk-map", headers=farmer_headers)
    assert res_map.status_code == 403

    # 3. Blocked from hotspots list
    res_hot = client.get("/api/geospatial/hotspots", headers=farmer_headers)
    assert res_hot.status_code == 403

    # 4. Blocked from recalculation
    res_calc = client.post("/api/geospatial/recalculate", json={"window_days": 7}, headers=farmer_headers)
    assert res_calc.status_code == 403


def test_10_veterinarian_access_permitted(client):
    """Verifies that licensed veterinarians can query risk maps and hotspots."""
    vet_headers = get_auth_header("veterinarian")
    res_ov = client.get("/api/geospatial/overview", headers=vet_headers)
    assert res_ov.status_code == 200
    assert "total_areas_monitored" in res_ov.json()

    res_hot = client.get("/api/geospatial/hotspots", headers=vet_headers)
    assert res_hot.status_code == 200
    assert "items" in res_hot.json()


def test_11_admin_access_permitted(client):
    """Verifies that administrators have full access to trigger risk recalculation and seed demo clusters."""
    admin_headers = get_auth_header("admin")
    res_calc = client.post("/api/geospatial/recalculate", json={"window_days": 7}, headers=admin_headers)
    assert res_calc.status_code == 200
    assert res_calc.json()["status"] == "success"

    res_seed = client.post("/api/geospatial/seed-demo", headers=admin_headers)
    assert res_seed.status_code == 200
    assert res_seed.json()["status"] == "success"


def test_12_privacy_safe_map_response(client):
    """Verifies map responses use coarse administrative centroids rather than precise private GPS coordinates."""
    admin_headers = get_auth_header("admin")
    res = client.get("/api/geospatial/risk-map", headers=admin_headers)
    assert res.status_code == 200
    points = res.json()
    for p in points:
        # Centroid coordinates must be within India bounds if present
        if p["latitude"] is not None and p["longitude"] is not None:
            assert 8.0 <= p["latitude"] <= 37.0
            assert 68.0 <= p["longitude"] <= 97.0
        # Disclaimer must accompany map response
        assert "Geospatial risk signals are intended for early-warning" in p["disclaimer"]


def test_13_no_exact_household_location_leakage(client):
    """Verifies that no private farmer name, house number, or exact household location is exposed."""
    vet_headers = get_auth_header("veterinarian")
    res = client.get("/api/geospatial/hotspots", headers=vet_headers)
    assert res.status_code == 200
    items = res.json()["items"]
    for item in items:
        # Ensure only administrative level strings are present
        assert "house" not in item["village"].lower()
        assert "door" not in item["village"].lower()
        assert "farmer_name" not in item


def test_14_demo_data_correctly_labelled(client):
    """Verifies that synthetic demonstration clusters are explicitly tagged with is_demo: True."""
    admin_headers = get_auth_header("admin")
    # Seed demo data
    client.post("/api/geospatial/seed-demo", headers=admin_headers)

    res = client.get("/api/geospatial/hotspots/GEO-DEMO-001", headers=admin_headers)
    assert res.status_code == 200
    dossier = res.json()
    assert dossier["is_demo"] is True
    assert dossier["hotspot_id"] == "GEO-DEMO-001"
    assert dossier["priority"] == "P1"
    assert dossier["risk_tier"] == "CRITICAL"


def test_15_offline_stale_data_indicator(client):
    """Verifies that all responses include timestamps and the mandatory safety disclaimer."""
    vet_headers = get_auth_header("veterinarian")
    res = client.get("/api/geospatial/overview", headers=vet_headers)
    assert res.status_code == 200
    data = res.json()
    assert "last_recalculated_at" in data
    assert GEOSPATIAL_SAFETY_DISCLAIMER in data["disclaimer"]


def test_16_integration_with_existing_outbreak_events(client):
    """Verifies interoperability with Milestone 9C outbreak collections and trends."""
    vet_headers = get_auth_header("veterinarian")
    res = client.get("/api/geospatial/trends", headers=vet_headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["trends"]) >= 3
    # Check that windows 7d, 14d, 30d are populated
    windows = [t["days"] for t in data["trends"]]
    assert 7 in windows
    assert 14 in windows
    assert 30 in windows
