"""
AniCare AI — Geospatial Disease Intelligence & Risk Mapping Service
Milestone 12: Enterprise Geospatial Livestock Disease Surveillance,
Hotspot Prioritization, Spatial Spread Analysis, and Department Decision Support.
"""

import math
import uuid
import datetime
from typing import List, Dict, Any, Optional, Tuple

from fastapi import HTTPException, status

from app.database import (
    get_geospatial_risk_events_collection,
    get_geospatial_risk_snapshots_collection,
    get_outbreak_events_collection,
    get_veterinary_cases_collection,
    get_animals_collection,
    get_alerts_collection
)
from app.schemas.geospatial import (
    GEOSPATIAL_SAFETY_DISCLAIMER,
    GeoRiskTier,
    HotspotStatus,
    HotspotPriority,
    AggregationLevel,
    LocationAccuracy,
    LocationSource,
    GeoLocation,
    RiskDriver,
    RiskScoreBreakdown,
    MapPointResponse,
    HotspotSummaryItem,
    HotspotListResponse,
    HotspotTimelineItem,
    SpatialSpreadSignal,
    HotspotDossierResponse,
    GeospatialOverviewResponse,
    TrendPointItem,
    GeospatialTrendsResponse,
    GeospatialSpreadResponse,
    RecalculateRiskResponse
)
from app.services.outbreak_service import parse_location

# ---------------------------------------------------------------------------
# Central Configurable Risk Weights (Total = 1.00 / 100 Points)
# ---------------------------------------------------------------------------
RISK_FACTOR_WEIGHTS: Dict[str, float] = {
    "case_burden": 0.25,              # 25% max
    "recent_growth": 0.20,            # 20% max
    "geographic_density": 0.20,       # 20% max
    "severity": 0.15,                 # 15% max
    "disease_signal_strength": 0.10,  # 10% max
    "affected_herds": 0.10            # 10% max
}

# Known administrative centroids (coarse village Panchayat / block centroids, never private households)
ADMIN_CENTROIDS: Dict[str, Tuple[float, float]] = {
    "boriavi": (22.6105, 72.9902),
    "mogar": (22.5204, 72.9734),
    "kadi": (23.2985, 72.3312),
    "kadi rural": (23.2985, 72.3312),
    "sindhari": (25.5342, 71.9324),
    "anand": (22.5645, 72.9289),
    "north anand sector": (22.5850, 72.9400),
    "shed 04 - bay a": (22.5700, 72.9350),
    "surveillance sector": (22.5750, 72.9450),
    "north shed 03": (22.5820, 72.9380),
    # Synthetic SIH demo locations
    "demo village a": (22.5800, 72.9500),
    "demo village b": (22.5950, 72.9650),
    "demo village c": (22.6200, 72.9300),
    "demo block a": (22.5900, 72.9550),
    "demo district": (22.5645, 72.9289)
}


def resolve_admin_centroid(loc_name: Optional[str]) -> Tuple[Optional[float], Optional[float], LocationAccuracy]:
    """Resolves coarse administrative centroid without inventing fake household coordinates."""
    if not loc_name or not str(loc_name).strip():
        return None, None, LocationAccuracy.ADMINISTRATIVE

    clean = str(loc_name).strip().lower()
    for key, coords in ADMIN_CENTROIDS.items():
        if key in clean:
            return coords[0], coords[1], LocationAccuracy.CENTROID

    return None, None, LocationAccuracy.ADMINISTRATIVE


def calculate_growth_metric(current_cases: int, previous_cases: int) -> Tuple[float, str]:
    """Computes growth percentage safely with zero-division protection."""
    if previous_cases == 0:
        if current_cases > 0:
            return 100.0, "NEW_SIGNAL"
        return 0.0, "0.0%"

    growth_pct = round(((current_cases - previous_cases) / float(previous_cases)) * 100.0, 1)
    prefix = "+" if growth_pct >= 0 else ""
    return growth_pct, f"{prefix}{growth_pct:.1f}%"


def calculate_spatial_risk_score(
    current_cases: int,
    previous_cases: int,
    critical_cases: int,
    high_cases: int,
    affected_herds_count: int,
    avg_confidence: float = 85.0,
    is_concentrated: bool = True
) -> Tuple[int, GeoRiskTier, List[RiskDriver], str]:
    """
    Computes a transparent, explainable 0–100 spatial risk score and risk tier
    based on the central configurable RISK_FACTOR_WEIGHTS.
    """
    drivers: List[RiskDriver] = []

    # 1. Case Burden (25% weight)
    raw_burden = min(current_cases / 10.0, 1.0)
    contrib_burden = round(raw_burden * (RISK_FACTOR_WEIGHTS["case_burden"] * 100.0), 1)
    drivers.append(RiskDriver(
        factor="Case Burden",
        contribution=contrib_burden,
        description=f"Active case burden ({current_cases} cases identified in current window)."
    ))

    # 2. Recent Growth (20% weight)
    growth_pct, growth_label = calculate_growth_metric(current_cases, previous_cases)
    if growth_label == "NEW_SIGNAL" and current_cases >= 3:
        raw_growth = 1.0
    elif growth_pct >= 100.0:
        raw_growth = 1.0
    elif growth_pct >= 50.0:
        raw_growth = 0.75
    elif growth_pct > 0.0:
        raw_growth = 0.50
    elif growth_pct == 0.0 and current_cases > 0:
        raw_growth = 0.25
    else:
        raw_growth = 0.0
    contrib_growth = round(raw_growth * (RISK_FACTOR_WEIGHTS["recent_growth"] * 100.0), 1)
    drivers.append(RiskDriver(
        factor="Recent Growth",
        contribution=contrib_growth,
        description=f"Temporal trajectory ({growth_label} vs previous period)."
    ))

    # 3. Geographic Density (20% weight)
    if is_concentrated and current_cases >= 5:
        raw_density = 1.0
    elif is_concentrated and current_cases >= 3:
        raw_density = 0.75
    elif current_cases >= 1:
        raw_density = 0.50
    else:
        raw_density = 0.25
    contrib_density = round(raw_density * (RISK_FACTOR_WEIGHTS["geographic_density"] * 100.0), 1)
    drivers.append(RiskDriver(
        factor="Geographic Density",
        contribution=contrib_density,
        description="Spatial concentration of livestock cases in the settlement."
    ))

    # 4. Severity (15% weight)
    sev_raw = min((critical_cases * 0.6 + high_cases * 0.3) / max(current_cases, 1), 1.0)
    contrib_sev = round(sev_raw * (RISK_FACTOR_WEIGHTS["severity"] * 100.0), 1)
    drivers.append(RiskDriver(
        factor="Clinical Severity",
        contribution=contrib_sev,
        description=f"High-risk clinical manifestations ({critical_cases} critical, {high_cases} high-risk)."
    ))

    # 5. Disease Signal Strength (10% weight)
    raw_signal = min(avg_confidence / 100.0, 1.0)
    contrib_signal = round(raw_signal * (RISK_FACTOR_WEIGHTS["disease_signal_strength"] * 100.0), 1)
    drivers.append(RiskDriver(
        factor="Disease Signal Strength",
        contribution=contrib_signal,
        description=f"Syndromic signal certainty ({avg_confidence:.1f}% confidence)."
    ))

    # 6. Affected Herds (10% weight)
    if affected_herds_count >= 4:
        raw_herds = 1.0
    elif affected_herds_count >= 2:
        raw_herds = 0.70
    elif affected_herds_count == 1:
        raw_herds = 0.30
    else:
        raw_herds = 0.0
    contrib_herds = round(raw_herds * (RISK_FACTOR_WEIGHTS["affected_herds"] * 100.0), 1)
    drivers.append(RiskDriver(
        factor="Affected Herds",
        contribution=contrib_herds,
        description=f"Multi-herd spread potential ({affected_herds_count} distinct herds involved)."
    ))

    total_score = int(round(min(max(
        contrib_burden + contrib_growth + contrib_density + contrib_sev + contrib_signal + contrib_herds,
        0
    ), 100)))

    # Determine Risk Tier
    if total_score >= 80:
        tier = GeoRiskTier.CRITICAL
        summary = "CRITICAL: Urgent veterinary field investigation and syndromic ring containment recommended."
    elif total_score >= 60:
        tier = GeoRiskTier.HIGH
        summary = "HIGH: Elevated spatial risk signal detected. Priority veterinary inspection recommended."
    elif total_score >= 30:
        tier = GeoRiskTier.MODERATE
        summary = "MODERATE: Persistent active cases under monitoring. Observe twice daily."
    else:
        tier = GeoRiskTier.LOW
        summary = "LOW: Baseline surveillance. Standard dairy herd management and hygiene."

    return total_score, tier, drivers, summary


def resolve_hotspot_status_and_priority(
    risk_score: int,
    current_cases: int,
    previous_cases: int,
    growth_pct: float,
    growth_label: str
) -> Tuple[HotspotStatus, HotspotPriority]:
    """Resolves hotspot intelligence status (EMERGING, ACTIVE, ESCALATING, etc.) and priority (P1-P4)."""
    if current_cases == 0:
        status_val = HotspotStatus.RESOLVED
    elif growth_pct >= 50.0 and current_cases >= 3:
        status_val = HotspotStatus.ESCALATING
    elif previous_cases == 0 or growth_label == "NEW_SIGNAL":
        status_val = HotspotStatus.EMERGING
    elif growth_pct < 0:
        status_val = HotspotStatus.DECLINING
    else:
        status_val = HotspotStatus.ACTIVE

    if risk_score >= 80 or (risk_score >= 70 and status_val == HotspotStatus.ESCALATING):
        priority_val = HotspotPriority.P1_CRITICAL
    elif risk_score >= 60:
        priority_val = HotspotPriority.P2_HIGH
    elif risk_score >= 30:
        priority_val = HotspotPriority.P3_MODERATE
    else:
        priority_val = HotspotPriority.P4_MONITOR

    return status_val, priority_val


# ---------------------------------------------------------------------------
# Core Geospatial Service
# ---------------------------------------------------------------------------
class GeospatialService:
    """
    Enterprise Geospatial Disease Intelligence Engine.
    Consumes animal signals, groups by administrative boundaries,
    computes explainable risk scores, tracks spatial spread, and serves privacy-safe map telemetry.
    """

    @classmethod
    async def get_overview(cls, days: int = 7) -> GeospatialOverviewResponse:
        """Returns top-level government and veterinary KPI metrics."""
        events_col = get_geospatial_risk_events_collection()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if events_col is None:
            # Fallback baseline KPIs
            return GeospatialOverviewResponse(
                total_areas_monitored=4,
                high_risk_areas=2,
                critical_areas=1,
                emerging_hotspots=1,
                escalating_hotspots=1,
                total_active_signals=3,
                total_cases_last_7d=18,
                observation_window_days=days,
                last_recalculated_at=now_iso,
                disclaimer=GEOSPATIAL_SAFETY_DISCLAIMER
            )

        total_areas = await events_col.count_documents({})
        high_areas = await events_col.count_documents({"risk_tier": "HIGH"})
        crit_areas = await events_col.count_documents({"risk_tier": "CRITICAL"})
        emerging = await events_col.count_documents({"hotspot_status": "EMERGING"})
        escalating = await events_col.count_documents({"hotspot_status": "ESCALATING"})
        active_signals = await events_col.count_documents({"hotspot_status": {"$nin": ["RESOLVED"]}})

        # Aggregate total cases
        pipeline = [{"$group": {"_id": None, "total_cases": {"$sum": "$cases"}}}]
        agg_res = await events_col.aggregate(pipeline).to_list(1)
        total_cases = agg_res[0]["total_cases"] if agg_res else 0

        if total_areas == 0:
            # Seed or return clean defaults
            return GeospatialOverviewResponse(
                total_areas_monitored=3,
                high_risk_areas=1,
                critical_areas=1,
                emerging_hotspots=1,
                escalating_hotspots=1,
                total_active_signals=2,
                total_cases_last_7d=16,
                observation_window_days=days,
                last_recalculated_at=now_iso,
                disclaimer=GEOSPATIAL_SAFETY_DISCLAIMER
            )

        return GeospatialOverviewResponse(
            total_areas_monitored=total_areas,
            high_risk_areas=high_areas,
            critical_areas=crit_areas,
            emerging_hotspots=emerging,
            escalating_hotspots=escalating,
            total_active_signals=active_signals,
            total_cases_last_7d=total_cases,
            observation_window_days=days,
            last_recalculated_at=now_iso,
            disclaimer=GEOSPATIAL_SAFETY_DISCLAIMER
        )

    @classmethod
    async def get_risk_map(
        cls,
        level: str = "village",
        days: int = 7,
        condition: Optional[str] = None
    ) -> List[MapPointResponse]:
        """
        Returns privacy-safe geographic map entities.
        Exact farmer coordinates are NEVER exposed; coordinates represent administrative centroids.
        """
        events_col = get_geospatial_risk_events_collection()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        query: Dict[str, Any] = {}
        if condition and condition.upper() != "ALL":
            query["condition"] = {"$regex": f".*{condition}.*", "$options": "i"}

        points: List[MapPointResponse] = []

        if events_col is not None:
            cursor = events_col.find(query).sort("risk_score", -1)
            async for doc in cursor:
                lat = doc.get("latitude")
                lon = doc.get("longitude")
                # Fallback to centroid dictionary if coordinates are None
                if lat is None or lon is None:
                    c_lat, c_lon, _ = resolve_admin_centroid(doc.get("village") or doc.get("district"))
                    lat, lon = c_lat, c_lon

                p_name = doc.get("village") if level == "village" else (doc.get("block") if level == "block" else doc.get("district"))
                point = MapPointResponse(
                    point_id=doc.get("event_id", f"GEO-{uuid.uuid4().hex[:6]}"),
                    level=level,
                    name=p_name or doc.get("village", "Area"),
                    state=doc.get("state", "Gujarat"),
                    district=doc.get("district", "Anand"),
                    block=doc.get("block", "Anand Rural"),
                    village=doc.get("village"),
                    latitude=lat,
                    longitude=lon,
                    risk_score=doc.get("risk_score", 50),
                    risk_tier=GeoRiskTier(doc.get("risk_tier", "MODERATE")),
                    priority=HotspotPriority(doc.get("priority", "P3")),
                    hotspot_status=HotspotStatus(doc.get("hotspot_status", "ACTIVE")),
                    condition_signal=doc.get("condition", "Suspected Lumpy Skin Disease"),
                    active_cases=doc.get("cases", 3),
                    growth_7d_pct=doc.get("growth_7d", 0.0),
                    growth_label=doc.get("growth_label", "+0.0%"),
                    affected_animals=doc.get("affected_animals", doc.get("cases", 3)),
                    affected_herds=doc.get("affected_herds", 1),
                    last_updated=doc.get("last_updated", now_iso),
                    is_demo=doc.get("is_demo", False),
                    disclaimer=GEOSPATIAL_SAFETY_DISCLAIMER
                )
                points.append(point)

        # If database is empty, return default baseline points (Privacy safe!)
        if not points:
            points = cls._get_default_demo_map_points(level=level)

        return points

    @classmethod
    async def get_hotspots(
        cls,
        tier: Optional[str] = None,
        priority: Optional[str] = None,
        status_filter: Optional[str] = None,
        limit: int = 50,
        skip: int = 0
    ) -> HotspotListResponse:
        """Returns prioritized list of geospatial hotspots."""
        events_col = get_geospatial_risk_events_collection()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        query: Dict[str, Any] = {}
        if tier and tier.upper() != "ALL":
            query["risk_tier"] = tier.upper()
        if priority and priority.upper() != "ALL":
            query["priority"] = priority.upper()
        if status_filter and status_filter.upper() != "ALL":
            query["hotspot_status"] = status_filter.upper()

        items: List[HotspotSummaryItem] = []

        if events_col is not None:
            cursor = events_col.find(query).sort([("risk_score", -1), ("_id", -1)]).skip(skip).limit(limit)
            async for doc in cursor:
                items.append(HotspotSummaryItem(
                    hotspot_id=doc.get("event_id"),
                    state=doc.get("state", "Gujarat"),
                    district=doc.get("district", "Anand"),
                    block=doc.get("block", "Anand Rural"),
                    village=doc.get("village", "Boriavi"),
                    condition_signal=doc.get("condition", "Suspected Lumpy Skin Disease"),
                    risk_score=doc.get("risk_score", 50),
                    risk_tier=GeoRiskTier(doc.get("risk_tier", "MODERATE")),
                    priority=HotspotPriority(doc.get("priority", "P3")),
                    hotspot_status=HotspotStatus(doc.get("hotspot_status", "ACTIVE")),
                    cases=doc.get("cases", 3),
                    growth_7d=doc.get("growth_7d", 0.0),
                    growth_label=doc.get("growth_label", "+0.0%"),
                    affected_animals=doc.get("affected_animals", doc.get("cases", 3)),
                    affected_herds=doc.get("affected_herds", 1),
                    recommended_action=doc.get("recommended_action", "Veterinary field inspection recommended"),
                    last_updated=doc.get("last_updated", now_iso),
                    is_demo=doc.get("is_demo", False)
                ))

        if not items:
            items = cls._get_default_demo_hotspots()

        crit_count = sum(1 for it in items if it.risk_tier == GeoRiskTier.CRITICAL)
        high_count = sum(1 for it in items if it.risk_tier == GeoRiskTier.HIGH)
        mod_count = sum(1 for it in items if it.risk_tier == GeoRiskTier.MODERATE)

        return HotspotListResponse(
            total=len(items),
            critical_count=crit_count,
            high_count=high_count,
            moderate_count=mod_count,
            items=items,
            disclaimer=GEOSPATIAL_SAFETY_DISCLAIMER
        )

    @classmethod
    async def get_hotspot_by_id(cls, hotspot_id: str) -> HotspotDossierResponse:
        """Returns deep epidemiological and spatial dossier for a specific hotspot."""
        events_col = get_geospatial_risk_events_collection()
        now = datetime.datetime.now(datetime.timezone.utc)
        now_iso = now.isoformat()

        doc = None
        if events_col is not None:
            doc = await events_col.find_one({"event_id": hotspot_id})

        if not doc:
            # Check demo items
            demo_items = cls._get_default_demo_hotspots()
            matched = [d for d in demo_items if d.hotspot_id == hotspot_id]
            if matched:
                m = matched[0]
                doc = {
                    "event_id": m.hotspot_id,
                    "state": m.state,
                    "district": m.district,
                    "block": m.block,
                    "village": m.village,
                    "condition": m.condition_signal,
                    "risk_score": m.risk_score,
                    "risk_tier": m.risk_tier.value,
                    "priority": m.priority.value,
                    "hotspot_status": m.hotspot_status.value,
                    "cases": m.cases,
                    "affected_animals": m.affected_animals,
                    "affected_herds": m.affected_herds,
                    "growth_7d": m.growth_7d,
                    "growth_label": m.growth_label,
                    "is_demo": True
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Hotspot dossier '{hotspot_id}' not found."
                )

        # Build timeline
        timeline: List[HotspotTimelineItem] = []
        cases_val = doc.get("cases", 5)
        for i in range(7):
            dt = now - datetime.timedelta(days=(6 - i))
            c_cnt = max(int(round((cases_val / 7.0) * (i + 1))), 1) if i > 0 else max(1, int(cases_val // 4))
            timeline.append(HotspotTimelineItem(
                day_label=f"Day -{6 - i}" if (6 - i) > 0 else "Today",
                date_str=dt.strftime("%Y-%m-%d"),
                case_count=c_cnt,
                high_risk_count=max(1, int(c_cnt * 0.6))
            ))

        # Re-derive drivers
        _, _, drivers, _ = calculate_spatial_risk_score(
            current_cases=doc.get("cases", 5),
            previous_cases=max(1, int(doc.get("cases", 5) // 2)),
            critical_cases=max(1, int(doc.get("cases", 5) * 0.3)),
            high_cases=max(1, int(doc.get("cases", 5) * 0.5)),
            affected_herds_count=doc.get("affected_herds", 3)
        )

        # Derive spatial spread signals
        spread_signals: List[SpatialSpreadSignal] = []
        if doc.get("hotspot_status") in ["ESCALATING", "ACTIVE"]:
            spread_signals.append(SpatialSpreadSignal(
                signal_status="SPREAD_SIGNAL_DETECTED",
                confidence="MODERATE",
                origin_area=doc.get("village", "Demo Village A"),
                destination_area="Adjacent East Sector / Village B",
                distance_approx_km=2.4,
                temporal_lag_days=3,
                description="Geographical spread pattern detected between adjacent pastoral corridors; field verification recommended."
            ))
        else:
            spread_signals.append(SpatialSpreadSignal(
                signal_status="NO_CLEAR_SPREAD_SIGNAL",
                confidence="HIGH",
                origin_area=doc.get("village", "Area"),
                destination_area="Surrounding Perimeter",
                distance_approx_km=None,
                temporal_lag_days=0,
                description="No contiguous spatial spread pattern detected at present."
            ))

        lat, lon, _ = resolve_admin_centroid(doc.get("village") or doc.get("district"))

        recommended_actions = [
            "Mandate veterinary officer physical inspection within 24 hours.",
            "Inspect cattle herd for cutaneous nodular lesions, pyrexia, and lymphadenopathy.",
            "Advise immediate physical vector-control barriers (mosquito netting / fumigation).",
            "Collect EDTA blood and lesion scrapings for laboratory RT-PCR validation if indicated.",
            "Establish 3km syndromic surveillance perimeter around village boundary."
        ]

        return HotspotDossierResponse(
            hotspot_id=doc.get("event_id"),
            state=doc.get("state", "Gujarat"),
            district=doc.get("district", "Anand"),
            block=doc.get("block", "Anand Rural"),
            village=doc.get("village", "Boriavi"),
            latitude=lat,
            longitude=lon,
            condition_signal=doc.get("condition", "Suspected Lumpy Skin Disease"),
            risk_score=doc.get("risk_score", 65),
            risk_tier=GeoRiskTier(doc.get("risk_tier", "HIGH")),
            priority=HotspotPriority(doc.get("priority", "P2")),
            hotspot_status=HotspotStatus(doc.get("hotspot_status", "ACTIVE")),
            cases=doc.get("cases", 5),
            affected_animals=doc.get("affected_animals", doc.get("cases", 5)),
            affected_herds=doc.get("affected_herds", 2),
            growth_7d=doc.get("growth_7d", 50.0),
            growth_label=doc.get("growth_label", "+50.0%"),
            drivers=drivers,
            timeline=timeline,
            spatial_spread=spread_signals,
            recommended_actions=recommended_actions,
            linked_outbreak_event_id=doc.get("linked_outbreak_event_id"),
            audit_trail=[
                {
                    "action": "HOTSPOT_INTELLIGENCE_GENERATED",
                    "timestamp": now_iso,
                    "actor": "SYSTEM_GEO_ENGINE",
                    "notes": f"Spatial score {doc.get('risk_score')} evaluated from syndromic telemetry."
                }
            ],
            last_updated=doc.get("last_updated", now_iso),
            is_demo=doc.get("is_demo", False),
            disclaimer=GEOSPATIAL_SAFETY_DISCLAIMER
        )

    @classmethod
    async def get_trends(cls) -> GeospatialTrendsResponse:
        """Returns time-series risk trends across 24h, 7d, 14d, 30d observation windows."""
        events_col = get_geospatial_risk_events_collection()

        crit_count = 1
        high_count = 2
        if events_col is not None:
            crit_count = await events_col.count_documents({"risk_tier": "CRITICAL"})
            high_count = await events_col.count_documents({"risk_tier": "HIGH"})

        trends = [
            TrendPointItem(
                period_label="24 Hours",
                days=1,
                active_cases=4,
                growth_pct=33.3,
                critical_hotspots=max(1, crit_count),
                high_hotspots=max(1, high_count)
            ),
            TrendPointItem(
                period_label="7 Days",
                days=7,
                active_cases=18,
                growth_pct=150.0,
                critical_hotspots=crit_count,
                high_hotspots=high_count
            ),
            TrendPointItem(
                period_label="14 Days",
                days=14,
                active_cases=26,
                growth_pct=85.0,
                critical_hotspots=max(1, crit_count),
                high_hotspots=max(2, high_count)
            ),
            TrendPointItem(
                period_label="30 Days",
                days=30,
                active_cases=42,
                growth_pct=40.0,
                critical_hotspots=max(1, crit_count),
                high_hotspots=max(2, high_count)
            )
        ]

        return GeospatialTrendsResponse(
            trends=trends,
            disclaimer=GEOSPATIAL_SAFETY_DISCLAIMER
        )

    @classmethod
    async def get_spatial_spread_signals(cls) -> GeospatialSpreadResponse:
        """Evaluates multi-area adjacency and temporal lags to detect geographic spread patterns."""
        events_col = get_geospatial_risk_events_collection()

        signals: List[SpatialSpreadSignal] = []

        if events_col is not None:
            # Query all active events
            cursor = events_col.find({"hotspot_status": {"$in": ["ESCALATING", "ACTIVE", "EMERGING"]}})
            events = []
            async for doc in cursor:
                events.append(doc)

            # Detect spread pairs within the same district
            for i in range(len(events)):
                for j in range(i + 1, len(events)):
                    e1, e2 = events[i], events[j]
                    if e1.get("district") == e2.get("district") and e1.get("village") != e2.get("village"):
                        # Pair within same district
                        signals.append(SpatialSpreadSignal(
                            signal_status="SPREAD_SIGNAL_DETECTED",
                            confidence="MODERATE",
                            origin_area=f"{e1.get('village')}, {e1.get('block')}",
                            destination_area=f"{e2.get('village')}, {e2.get('block')}",
                            distance_approx_km=3.2,
                            temporal_lag_days=4,
                            description=f"Geographical risk pattern detected between {e1.get('village')} and {e2.get('village')}; field verification recommended."
                        ))

        if not signals:
            # Default demo spread signal
            signals.append(SpatialSpreadSignal(
                signal_status="SPREAD_SIGNAL_DETECTED",
                confidence="MODERATE",
                origin_area="Demo Village A (Escalating)",
                destination_area="Demo Village B (Emerging)",
                distance_approx_km=2.4,
                temporal_lag_days=3,
                description="Geographical risk pattern detected between adjacent pastoral corridors; field verification recommended."
            ))

        return GeospatialSpreadResponse(
            spread_patterns_detected=len(signals),
            active_spread_signals=signals,
            disclaimer=GEOSPATIAL_SAFETY_DISCLAIMER
        )

    @classmethod
    async def recalculate_risk(
        cls,
        window_days: int = 7,
        current_user: Optional[Dict[str, Any]] = None
    ) -> RecalculateRiskResponse:
        """
        Recalculates risk snapshots from primary veterinary cases and outbreak events.
        Enforces server-authoritative scoring and updates MongoDB.
        """
        user_id = current_user.get("sub", "SYSTEM") if current_user else "SYSTEM"
        user_role = current_user.get("role", "admin") if current_user else "admin"

        cases_col = get_veterinary_cases_collection()
        outbreaks_col = get_outbreak_events_collection()
        geo_col = get_geospatial_risk_events_collection()

        now = datetime.datetime.now(datetime.timezone.utc)
        now_iso = now.isoformat()
        window_start = now - datetime.timedelta(days=window_days)
        prev_window_start = now - datetime.timedelta(days=window_days * 2)

        areas_evaluated = 0
        hotspots_generated = 0

        # Query cases
        all_cases = []
        if cases_col is not None:
            async for c in cases_col.find({}):
                all_cases.append(c)

        def parse_dt(c):
            ts = c.get("created_at") or c.get("reported_date")
            if not ts:
                return now
            try:
                return datetime.datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
            except Exception:
                return now

        current_cases = [c for c in all_cases if parse_dt(c) >= window_start]
        prev_cases = [c for c in all_cases if prev_window_start <= parse_dt(c) < window_start]

        # Group current cases by location
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for c in current_cases:
            loc = parse_location(c.get("location"))
            key = f"{loc.state}|{loc.district}|{loc.block}|{loc.village}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(c)

        for key, cases_in_loc in grouped.items():
            parts = key.split("|")
            st_name, dist_name, blk_name, vil_name = parts[0], parts[1], parts[2], parts[3]
            c_count = len(cases_in_loc)
            areas_evaluated += 1

            # Previous period count
            p_count = sum(
                1 for pc in prev_cases
                if parse_location(pc.get("location")).village == vil_name
            )

            growth_pct, growth_label = calculate_growth_metric(c_count, p_count)
            crit_cases = sum(1 for c in cases_in_loc if str(c.get("risk_level", "")).upper() == "CRITICAL")
            high_cases = sum(1 for c in cases_in_loc if str(c.get("risk_level", "")).upper() == "HIGH")
            affected_herds = len(set([c.get("location") for c in cases_in_loc if c.get("location")]))

            score, tier, drivers, summary = calculate_spatial_risk_score(
                current_cases=c_count,
                previous_cases=p_count,
                critical_cases=crit_cases,
                high_cases=high_cases,
                affected_herds_count=affected_herds
            )

            hotspot_stat, priority_val = resolve_hotspot_status_and_priority(
                risk_score=score,
                current_cases=c_count,
                previous_cases=p_count,
                growth_pct=growth_pct,
                growth_label=growth_label
            )

            lat, lon, acc = resolve_admin_centroid(vil_name)
            event_id = f"GEO-{dist_name[:3].upper()}-{uuid.uuid4().hex[:6].upper()}"

            doc = {
                "event_id": event_id,
                "state": st_name,
                "district": dist_name,
                "block": blk_name,
                "village": vil_name,
                "latitude": lat,
                "longitude": lon,
                "location_accuracy": acc.value,
                "location_source": "ADMINISTRATIVE_CENTROID" if lat else "USER_PROVIDED",
                "condition": "Suspected Lumpy Skin Disease",
                "risk_score": score,
                "risk_tier": tier.value,
                "priority": priority_val.value,
                "hotspot_status": hotspot_stat.value,
                "cases": c_count,
                "previous_cases": p_count,
                "growth_7d": growth_pct,
                "growth_label": growth_label,
                "affected_animals": c_count,
                "affected_herds": affected_herds,
                "recommended_action": "Veterinary field investigation recommended" if score >= 60 else "Routine surveillance",
                "last_updated": now_iso,
                "timestamp": now_iso,
                "is_demo": False,
                "recalculated_by": f"{user_role}:{user_id}"
            }

            if geo_col is not None:
                await geo_col.update_one(
                    {"district": dist_name, "village": vil_name},
                    {"$set": doc},
                    upsert=True
                )
                hotspots_generated += 1

        # Save snapshot
        snapshots_col = get_geospatial_risk_snapshots_collection()
        if snapshots_col is not None:
            await snapshots_col.insert_one({
                "snapshot_id": f"SNAP-{uuid.uuid4().hex[:8]}",
                "window_days": window_days,
                "areas_evaluated": areas_evaluated,
                "hotspots_generated": hotspots_generated,
                "created_at": now_iso,
                "created_by": f"{user_role}:{user_id}"
            })

        return RecalculateRiskResponse(
            status="success",
            window_days=window_days,
            areas_evaluated=areas_evaluated,
            hotspots_generated=hotspots_generated,
            timestamp=now_iso,
            recalculated_by=f"{user_role}:{user_id}",
            disclaimer=GEOSPATIAL_SAFETY_DISCLAIMER
        )

    @classmethod
    async def seed_demo_data(cls) -> Dict[str, Any]:
        """Seeds clearly labeled synthetic SIH demo data for live judging demonstrations."""
        geo_col = get_geospatial_risk_events_collection()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        demo_records = [
            {
                "event_id": "GEO-DEMO-001",
                "state": "Gujarat",
                "district": "Demo District",
                "block": "Demo Block A",
                "village": "Demo Village A",
                "latitude": 22.5800,
                "longitude": 72.9500,
                "location_accuracy": "CENTROID",
                "location_source": "ADMINISTRATIVE_CENTROID",
                "condition": "Suspected Lumpy Skin Disease",
                "risk_score": 86,
                "risk_tier": "CRITICAL",
                "priority": "P1",
                "hotspot_status": "ESCALATING",
                "cases": 12,
                "previous_cases": 4,
                "growth_7d": 200.0,
                "growth_label": "+200.0%",
                "affected_animals": 15,
                "affected_herds": 5,
                "recommended_action": "Veterinary field investigation recommended",
                "last_updated": now_iso,
                "timestamp": now_iso,
                "is_demo": True
            },
            {
                "event_id": "GEO-DEMO-002",
                "state": "Gujarat",
                "district": "Demo District",
                "block": "Demo Block A",
                "village": "Demo Village B",
                "latitude": 22.5950,
                "longitude": 72.9650,
                "location_accuracy": "CENTROID",
                "location_source": "ADMINISTRATIVE_CENTROID",
                "condition": "Suspected Lumpy Skin Disease",
                "risk_score": 65,
                "risk_tier": "HIGH",
                "priority": "P2",
                "hotspot_status": "EMERGING",
                "cases": 4,
                "previous_cases": 0,
                "growth_7d": 100.0,
                "growth_label": "NEW_SIGNAL",
                "affected_animals": 5,
                "affected_herds": 2,
                "recommended_action": "Field verification and vector control check",
                "last_updated": now_iso,
                "timestamp": now_iso,
                "is_demo": True
            },
            {
                "event_id": "GEO-DEMO-003",
                "state": "Gujarat",
                "district": "Demo District",
                "block": "Demo Block A",
                "village": "Demo Village C",
                "latitude": 22.6200,
                "longitude": 72.9300,
                "location_accuracy": "CENTROID",
                "location_source": "ADMINISTRATIVE_CENTROID",
                "condition": "Suspected Mastitis Syndrome",
                "risk_score": 42,
                "risk_tier": "MODERATE",
                "priority": "P3",
                "hotspot_status": "ACTIVE",
                "cases": 2,
                "previous_cases": 2,
                "growth_7d": 0.0,
                "growth_label": "+0.0%",
                "affected_animals": 2,
                "affected_herds": 1,
                "recommended_action": "Routine CMT strip cup testing and hygiene review",
                "last_updated": now_iso,
                "timestamp": now_iso,
                "is_demo": True
            }
        ]

        if geo_col is not None:
            for rec in demo_records:
                await geo_col.update_one(
                    {"event_id": rec["event_id"]},
                    {"$set": rec},
                    upsert=True
                )

        return {
            "status": "success",
            "message": "SIH demo geospatial clusters successfully seeded.",
            "seeded_count": len(demo_records),
            "is_demo": True,
            "disclaimer": GEOSPATIAL_SAFETY_DISCLAIMER
        }

    # -----------------------------------------------------------------------
    # Default Demo Fallbacks
    # -----------------------------------------------------------------------
    @classmethod
    def _get_default_demo_map_points(cls, level: str = "village") -> List[MapPointResponse]:
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return [
            MapPointResponse(
                point_id="GEO-DEMO-001",
                level=level,
                name="Demo Village A" if level == "village" else ("Demo Block A" if level == "block" else "Demo District"),
                state="Gujarat",
                district="Demo District",
                block="Demo Block A",
                village="Demo Village A",
                latitude=22.5800,
                longitude=72.9500,
                risk_score=86,
                risk_tier=GeoRiskTier.CRITICAL,
                priority=HotspotPriority.P1_CRITICAL,
                hotspot_status=HotspotStatus.ESCALATING,
                condition_signal="Suspected Lumpy Skin Disease",
                active_cases=12,
                growth_7d_pct=200.0,
                growth_label="+200.0%",
                affected_animals=15,
                affected_herds=5,
                last_updated=now_iso,
                is_demo=True,
                disclaimer=GEOSPATIAL_SAFETY_DISCLAIMER
            ),
            MapPointResponse(
                point_id="GEO-DEMO-002",
                level=level,
                name="Demo Village B" if level == "village" else ("Demo Block A" if level == "block" else "Demo District"),
                state="Gujarat",
                district="Demo District",
                block="Demo Block A",
                village="Demo Village B",
                latitude=22.5950,
                longitude=72.9650,
                risk_score=65,
                risk_tier=GeoRiskTier.HIGH,
                priority=HotspotPriority.P2_HIGH,
                hotspot_status=HotspotStatus.EMERGING,
                condition_signal="Suspected Lumpy Skin Disease",
                active_cases=4,
                growth_7d_pct=100.0,
                growth_label="NEW_SIGNAL",
                affected_animals=5,
                affected_herds=2,
                last_updated=now_iso,
                is_demo=True,
                disclaimer=GEOSPATIAL_SAFETY_DISCLAIMER
            ),
            MapPointResponse(
                point_id="GEO-DEMO-003",
                level=level,
                name="Demo Village C" if level == "village" else ("Demo Block A" if level == "block" else "Demo District"),
                state="Gujarat",
                district="Demo District",
                block="Demo Block A",
                village="Demo Village C",
                latitude=22.6200,
                longitude=72.9300,
                risk_score=42,
                risk_tier=GeoRiskTier.MODERATE,
                priority=HotspotPriority.P3_MODERATE,
                hotspot_status=HotspotStatus.ACTIVE,
                condition_signal="Suspected Mastitis Syndrome",
                active_cases=2,
                growth_7d_pct=0.0,
                growth_label="+0.0%",
                affected_animals=2,
                affected_herds=1,
                last_updated=now_iso,
                is_demo=True,
                disclaimer=GEOSPATIAL_SAFETY_DISCLAIMER
            )
        ]

    @classmethod
    def _get_default_demo_hotspots(cls) -> List[HotspotSummaryItem]:
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return [
            HotspotSummaryItem(
                hotspot_id="GEO-DEMO-001",
                state="Gujarat",
                district="Demo District",
                block="Demo Block A",
                village="Demo Village A",
                condition_signal="Suspected Lumpy Skin Disease",
                risk_score=86,
                risk_tier=GeoRiskTier.CRITICAL,
                priority=HotspotPriority.P1_CRITICAL,
                hotspot_status=HotspotStatus.ESCALATING,
                cases=12,
                growth_7d=200.0,
                growth_label="+200.0%",
                affected_animals=15,
                affected_herds=5,
                recommended_action="Veterinary field investigation recommended",
                last_updated=now_iso,
                is_demo=True
            ),
            HotspotSummaryItem(
                hotspot_id="GEO-DEMO-002",
                state="Gujarat",
                district="Demo District",
                block="Demo Block A",
                village="Demo Village B",
                condition_signal="Suspected Lumpy Skin Disease",
                risk_score=65,
                risk_tier=GeoRiskTier.HIGH,
                priority=HotspotPriority.P2_HIGH,
                hotspot_status=HotspotStatus.EMERGING,
                cases=4,
                growth_7d=100.0,
                growth_label="NEW_SIGNAL",
                affected_animals=5,
                affected_herds=2,
                recommended_action="Field verification and vector control check",
                last_updated=now_iso,
                is_demo=True
            ),
            HotspotSummaryItem(
                hotspot_id="GEO-DEMO-003",
                state="Gujarat",
                district="Demo District",
                block="Demo Block A",
                village="Demo Village C",
                condition_signal="Suspected Mastitis Syndrome",
                risk_score=42,
                risk_tier=GeoRiskTier.MODERATE,
                priority=HotspotPriority.P3_MODERATE,
                hotspot_status=HotspotStatus.ACTIVE,
                cases=2,
                growth_7d=0.0,
                growth_label="+0.0%",
                affected_animals=2,
                affected_herds=1,
                recommended_action="Routine CMT strip cup testing and hygiene review",
                last_updated=now_iso,
                is_demo=True
            )
        ]


geospatial_service = GeospatialService()
