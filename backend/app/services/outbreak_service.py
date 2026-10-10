"""
AniCare AI — Outbreak Intelligence & Early Warning Service
Milestone 9C: Aggregates individual animal health events, detects spatial-temporal
clusters across villages/blocks/districts, calculates explainable outbreak risk scores,
manages veterinary investigations, and provides epidemiological analytics.
"""

import re
import uuid
import datetime
from typing import List, Dict, Any, Optional, Tuple
from fastapi import HTTPException, status

from app.database import (
    get_outbreak_events_collection,
    get_veterinary_cases_collection,
    get_animals_collection,
    get_alerts_collection
)
from app.schemas.outbreak import (
    OutbreakRiskTier,
    OutbreakStatus,
    HotspotLevel,
    LabTestStatus,
    LocationHierarchy,
    InvestigationRecord,
    OutbreakAuditEvent,
    OutbreakEventResponse,
    OutbreakEventListResponse,
    OutbreakStatsResponse,
    OutbreakTrendItem,
    OutbreakTrendsResponse,
    HotspotVillageItem,
    HotspotsResponse,
    AffectedAnimalSummary
)
from app.schemas.alert import AlertCreate, AlertTypeEnum, AlertSeverityEnum
from app.services.alert_service import create_alert

# Configurable Decision-Support Constants (Non-binding Epidemiological Thresholds)
CLUSTER_MIN_CASES = 3
HIGH_RISK_MIN_CASES = 3
RED_ALERT_MIN_CASES = 5
DEFAULT_WINDOW_DAYS = 7

OUTBREAK_DISCLAIMER = (
    "AI-ASSISTED EARLY WARNING DECISION SUPPORT: Indicates emergent statistical clustering and syndromic telemetry patterns. "
    "Does NOT represent an official confirmed epizootic disease outbreak without regulatory laboratory diagnostic confirmation "
    "(e.g. RT-PCR, ELISA, viral isolation) and formal notification by the State Department of Animal Husbandry."
)


def parse_location(loc_str: Optional[str]) -> LocationHierarchy:
    """
    Parses administrative location strings into a structured LocationHierarchy.
    Gracefully handles free-text shed/village/district strings without fabricating GPS.
    """
    if not loc_str or not str(loc_str).strip():
        return LocationHierarchy(
            village="LOCATION_UNKNOWN",
            block="LOCATION_UNKNOWN",
            district="LOCATION_UNKNOWN",
            state="Gujarat"
        )

    clean_loc = str(loc_str).strip()
    parts = [p.strip() for p in clean_loc.split(",") if p.strip()]

    # If comma-separated administrative components are provided, use them directly
    if len(parts) >= 3:
        vil = parts[0][8:].strip() if parts[0].lower().startswith("village ") else parts[0]
        return LocationHierarchy(
            village=vil,
            block=parts[1],
            district=parts[2],
            state=parts[3] if len(parts) > 3 else "Gujarat"
        )
    elif len(parts) == 2:
        vil = parts[0][8:].strip() if parts[0].lower().startswith("village ") else parts[0]
        return LocationHierarchy(
            village=vil,
            block="General Block",
            district=parts[1],
            state="Gujarat"
        )


    # For single un-split tokens, evaluate known patterns or sheds
    loc_lower = clean_loc.lower()
    if "boriavi" in loc_lower:
        return LocationHierarchy(village="Boriavi", block="Anand Rural", district="Anand", state="Gujarat", pincode="388001")
    if "sindhari" in loc_lower or "barmer" in loc_lower:
        return LocationHierarchy(village="Sindhari", block="Sindhari Tehsil", district="Barmer", state="Rajasthan", pincode="344033")
    if "kadi" in loc_lower or "mehsana" in loc_lower:
        return LocationHierarchy(village="Kadi Rural", block="Kadi", district="Mehsana", state="Gujarat", pincode="382715")
    if "amul" in loc_lower or "sector 04" in loc_lower or "anand" in loc_lower:
        return LocationHierarchy(village="North Anand Sector", block="Anand Rural", district="Anand", state="Gujarat", pincode="388001")
    if "shed" in loc_lower or "bay" in loc_lower or "pen" in loc_lower:
        return LocationHierarchy(village=clean_loc, block="Co-op Farm Sector", district="Anand", state="Gujarat")

    return LocationHierarchy(
        village=clean_loc,
        block="LOCATION_UNKNOWN",
        district="LOCATION_UNKNOWN",
        state="Gujarat"
    )



def calculate_outbreak_risk_score(
    case_count: int,
    high_crit_count: int,
    critical_count: int,
    trend_pct: float,
    location: LocationHierarchy,
    condition: str
) -> Tuple[int, List[str], OutbreakRiskTier]:
    """
    Computes a transparent, explainable Outbreak Risk Score (0–100) and assigns an Outbreak Risk Tier.
    """
    score = 0
    reasons: List[str] = []

    # 1. Case count signal (max 35 pts)
    if case_count >= 8:
        score += 35
        reasons.append(f"+35 pts: Severe caseload volume ({case_count} active cases in temporal window)")
    elif case_count >= 5:
        score += 25
        reasons.append(f"+25 pts: Elevated cluster volume ({case_count} active cases in temporal window)")
    elif case_count >= 3:
        score += 15
        reasons.append(f"+15 pts: Cluster threshold reached ({case_count} cases)")
    else:
        score += 5
        reasons.append(f"+5 pts: Low case volume ({case_count} cases)")

    # 2. Severity & Criticality signal (max 35 pts)
    crit_pts = min(critical_count * 10, 20)
    high_pts = min((high_crit_count - critical_count) * 5, 15)
    severity_pts = crit_pts + high_pts
    if severity_pts > 0:
        score += severity_pts
        reasons.append(f"+{severity_pts} pts: High clinical severity ({critical_count} critical, {high_crit_count - critical_count} high-risk animals)")

    # 3. Temporal growth signal (max 15 pts)
    if trend_pct >= 100.0:
        score += 15
        reasons.append(f"+15 pts: Rapid epidemiological surge (+{trend_pct:.1f}% vs previous period)")
    elif trend_pct > 0.0:
        score += 10
        reasons.append(f"+10 pts: Increasing case trajectory (+{trend_pct:.1f}% vs previous period)")
    elif trend_pct == 0.0 and case_count >= CLUSTER_MIN_CASES:
        score += 5
        reasons.append("+5 pts: Persistent active caseload in area")

    # 4. Geographic concentration signal (max 10 pts)
    if location.village != "LOCATION_UNKNOWN":
        score += 10
        reasons.append(f"+10 pts: Geographic density concentrated in village '{location.village}'")
    elif location.district != "LOCATION_UNKNOWN":
        score += 5
        reasons.append(f"+5 pts: Geographic density identified in district '{location.district}'")

    # 5. Pathogen/Disease signal homogeneity (max 5 pts)
    if condition and "unknown" not in condition.lower():
        score += 5
        reasons.append(f"+5 pts: Syndromic concordance on condition '{condition}'")

    final_score = min(max(score, 0), 100)

    # Resolve Risk Tier based on multi-parameter thresholds
    if (case_count >= RED_ALERT_MIN_CASES and (critical_count >= 1 or high_crit_count >= 3 or trend_pct > 0)) or final_score >= 75:
        tier = OutbreakRiskTier.TIER_3_RED_ALERT
    elif case_count >= CLUSTER_MIN_CASES or final_score >= 40:
        tier = OutbreakRiskTier.TIER_2_SURVEILLANCE
    else:
        tier = OutbreakRiskTier.TIER_1_ROUTINE

    return final_score, reasons, tier


def get_recommended_actions_for_tier(tier: OutbreakRiskTier, condition: str) -> List[str]:
    """Generates standard precautionary biosecurity and veterinary action items."""
    if tier == OutbreakRiskTier.TIER_3_RED_ALERT:
        return [
            "Emergency dispatch of District Veterinary Officer (DVO) containment unit.",
            "Establish 100-meter physical standoff quarantine around affected sheds.",
            "Immediate halt of outward livestock movement, cattle bazaars, and farm transport vehicles.",
            "Institute emergency vector fogging against Stomoxys/Tabanid flies and mosquitoes.",
            "Issue 5km ring vaccination advisory for susceptible herd cohorts.",
            "Collect EDTA blood and lesion scab samples for certified laboratory RT-PCR testing."
        ]
    elif tier == OutbreakRiskTier.TIER_2_SURVEILLANCE:
        return [
            "Schedule priority on-site veterinary inspection within 24 hours.",
            "Isolate symptomatic animals in designated recovery bays under protective netting.",
            "Daily core rectal temperature logging across all shared trough cohorts.",
            "Disinfect barn entryways and troughs with 2% sodium hypochlorite / 4% sodium carbonate.",
            "Audit herd vaccination logs and flag unvaccinated livestock."
        ]
    else:
        return [
            "Maintain baseline syndromic surveillance and good dairy hygiene.",
            "Conduct twice-daily observational checks for nodular or mucosal eruptions.",
            "Ensure regular drinking water sanitization."
        ]


class OutbreakService:
    """
    Core engine managing outbreak detection, risk tiers, veterinary investigations,
    and alerting workflows.
    """

    @classmethod
    async def get_outbreaks(
        cls,
        status_filter: Optional[str] = None,
        risk_tier: Optional[str] = None,
        district: Optional[str] = None,
        is_demo: Optional[bool] = None,
        limit: int = 200,
        skip: int = 0
    ) -> OutbreakEventListResponse:
        col = get_outbreak_events_collection()
        if col is None:
            return OutbreakEventListResponse(total=0, active_clusters=0, red_alerts=0, items=[])

        query: Dict[str, Any] = {}
        if status_filter and status_filter.upper() != "ALL":
            query["status"] = status_filter.upper()
        if risk_tier and risk_tier.upper() != "ALL":
            query["risk_tier"] = risk_tier.upper()
        if district and district.upper() != "ALL":
            query["location.district"] = {"$regex": f"^{district}$", "$options": "i"}
        if is_demo is not None:
            query["is_demo"] = is_demo

        total = await col.count_documents(query)
        active_clusters = await col.count_documents({
            "status": {"$in": ["DETECTED", "UNDER_SURVEILLANCE", "VETERINARY_INVESTIGATION", "ACTION_RECOMMENDED", "MONITORING"]}
        })
        red_alerts = await col.count_documents({
            "risk_tier": "TIER_3_RED_ALERT",
            "status": {"$nin": ["RESOLVED", "FALSE_ALERT"]}
        })

        cursor = col.find(query).sort([("last_updated_at", -1), ("_id", -1)]).skip(skip).limit(limit)
        items = []
        async for doc in cursor:
            doc.pop("_id", None)
            items.append(OutbreakEventResponse(**doc))

        return OutbreakEventListResponse(
            total=total,
            active_clusters=active_clusters,
            red_alerts=red_alerts,
            items=items
        )

    @classmethod
    async def get_outbreak_by_id(cls, event_id: str) -> OutbreakEventResponse:
        col = get_outbreak_events_collection()
        if col is None:
            raise HTTPException(status_code=503, detail="Database unavailable.")

        doc = await col.find_one({"event_id": event_id})
        if not doc:
            raise HTTPException(status_code=404, detail=f"Outbreak event '{event_id}' not found.")

        doc.pop("_id", None)

        # Enrich with details of affected animals if available
        animals_col = get_animals_collection()
        if animals_col is not None and doc.get("animal_ids"):
            details = []
            animal_cursor = animals_col.find({"animal_id": {"$in": doc["animal_ids"]}})
            async for a in animal_cursor:
                details.append(AffectedAnimalSummary(
                    animal_id=a.get("animal_id", ""),
                    tag=a.get("tag"),
                    species=a.get("species", "Cattle"),
                    risk_level=a.get("risk_level", "HIGH"),
                    condition=doc.get("condition", "Suspected Condition"),
                    owner=a.get("owner"),
                    detected_at=a.get("created_at", "")
                ))
            doc["affected_animals_details"] = details

        return OutbreakEventResponse(**doc)

    @classmethod
    async def scan_and_detect_outbreaks(
        cls,
        window_days: int = DEFAULT_WINDOW_DAYS,
        district_filter: Optional[str] = None,
        village_filter: Optional[str] = None,
        current_user: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Scans livestock cases across the temporal window, clusters by geography and condition signal,
        calculates outbreak risk scores, generates/updates outbreak events, and triggers alerts.
        """
        cases_col = get_veterinary_cases_collection()
        outbreaks_col = get_outbreak_events_collection()
        if cases_col is None or outbreaks_col is None:
            raise HTTPException(status_code=503, detail="Database unavailable.")

        now = datetime.datetime.now(datetime.timezone.utc)
        window_start_dt = now - datetime.timedelta(days=window_days)
        prev_window_start_dt = now - datetime.timedelta(days=window_days * 2)

        # Query all cases in current and previous windows
        cases_cursor = cases_col.find({})
        all_cases = []
        async for c in cases_cursor:
            all_cases.append(c)

        # Parse timestamp safely
        def parse_dt(c):
            ts = c.get("created_at") or c.get("reported_date") or c.get("updated_at")
            if not ts:
                return now
            try:
                return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                return now

        current_window_cases = [c for c in all_cases if parse_dt(c) >= window_start_dt]
        prev_window_cases = [c for c in all_cases if prev_window_start_dt <= parse_dt(c) < window_start_dt]

        # Group current cases by location & condition
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for c in current_window_cases:
            loc = parse_location(c.get("location"))
            if district_filter and district_filter.lower() != loc.district.lower():
                continue
            if village_filter and village_filter.lower() != loc.village.lower():
                continue

            cond = c.get("condition", "Suspected Lumpy Skin Disease")
            # Normalize condition
            cond_key = "Lumpy Skin Disease" if "lumpy" in cond.lower() else ("Foot and Mouth Disease" if "foot" in cond.lower() or "fmd" in cond.lower() else cond)
            group_key = f"{loc.state}|{loc.district}|{loc.block}|{loc.village}|{cond_key}"
            if group_key not in grouped:
                grouped[group_key] = []
            grouped[group_key].append(c)

        detected_count = 0
        updated_count = 0
        now_iso = now.isoformat()
        actor = current_user.get("sub", "SYSTEM") if current_user else "SYSTEM"
        role = current_user.get("role", "system") if current_user else "system"

        for group_key, cases in grouped.items():
            case_count = len(cases)
            if case_count < CLUSTER_MIN_CASES:
                continue

            parts = group_key.split("|")
            state_name, dist_name, blk_name, vil_name, cond_name = parts[0], parts[1], parts[2], parts[3], parts[4]

            # Previous period count for trend
            prev_count = sum(
                1 for pc in prev_window_cases
                if parse_location(pc.get("location")).district == dist_name
                and parse_location(pc.get("location")).village == vil_name
            )

            if prev_count > 0:
                trend_pct = round(((case_count - prev_count) / prev_count) * 100.0, 1)
            else:
                trend_pct = round(100.0 * case_count, 1) if case_count > 0 else 0.0

            high_crit_count = sum(1 for c in cases if str(c.get("risk_level", "")).upper() in ["HIGH", "CRITICAL"])
            crit_count = sum(1 for c in cases if str(c.get("risk_level", "")).upper() == "CRITICAL")

            loc_obj = LocationHierarchy(
                village=vil_name,
                block=blk_name,
                district=dist_name,
                state=state_name
            )

            risk_score, trigger_reasons, risk_tier = calculate_outbreak_risk_score(
                case_count=case_count,
                high_crit_count=high_crit_count,
                critical_count=crit_count,
                trend_pct=trend_pct,
                location=loc_obj,
                condition=cond_name
            )

            recommended_actions = get_recommended_actions_for_tier(risk_tier, cond_name)
            animal_ids = list(set([c.get("animal_id") for c in cases if c.get("animal_id")]))
            herd_ids = list(set([c.get("location") for c in cases if c.get("location")]))

            # Check for existing event matching this location and condition
            existing_event = await outbreaks_col.find_one({
                "location.district": dist_name,
                "location.village": vil_name,
                "disease_signal": cond_name,
                "status": {"$nin": ["RESOLVED", "FALSE_ALERT"]}
            })

            if existing_event:
                # Update existing event
                event_id = existing_event["event_id"]
                update_fields = {
                    "case_count": case_count,
                    "animal_ids": animal_ids,
                    "herd_ids": herd_ids,
                    "risk_score": risk_score,
                    "risk_tier": risk_tier.value,
                    "trend_percentage": trend_pct,
                    "trigger_reasons": trigger_reasons,
                    "last_updated_at": now_iso,
                    "updated_at": now_iso
                }
                audit_entry = {
                    "action": "CLUSTER_TELEMETRY_UPDATED",
                    "actor_id": actor,
                    "actor_role": role,
                    "timestamp": now_iso,
                    "event_id": event_id,
                    "notes": f"Automated cluster scan updated metrics: {case_count} cases, score {risk_score}."
                }
                await outbreaks_col.update_one(
                    {"event_id": event_id},
                    {
                        "$set": update_fields,
                        "$push": {"audit_trail": audit_entry}
                    }
                )
                updated_count += 1
                # Trigger alert dispatch / update
                existing_event.update(update_fields)
                await cls.dispatch_outbreak_alert(existing_event)
            else:
                # Create brand new outbreak event
                event_id = f"OUT-2026-{uuid.uuid4().hex[:6].upper()}"
                initial_status = OutbreakStatus.DETECTED.value

                event_doc = {
                    "event_id": event_id,
                    "status": initial_status,
                    "risk_tier": risk_tier.value,
                    "risk_score": risk_score,
                    "disease_signal": cond_name,
                    "condition": f"Suspected {cond_name} Clustering",
                    "animal_ids": animal_ids,
                    "case_count": case_count,
                    "herd_ids": herd_ids,
                    "location": loc_obj.model_dump(),
                    "window_start": window_start_dt.strftime("%Y-%m-%d"),
                    "window_end": now.strftime("%Y-%m-%d"),
                    "first_detected_at": now_iso,
                    "last_updated_at": now_iso,
                    "trend_percentage": trend_pct,
                    "trigger_reasons": trigger_reasons,
                    "veterinary_review_status": "PENDING",
                    "assigned_veterinary_officer": None,
                    "assigned_at": None,
                    "assigned_by": None,
                    "investigation_record": None,
                    "investigation_notes": None,
                    "recommended_actions": recommended_actions,
                    "audit_trail": [
                        {
                            "action": "CLUSTER_DETECTED",
                            "actor_id": actor,
                            "actor_role": role,
                            "timestamp": now_iso,
                            "event_id": event_id,
                            "new_status": initial_status,
                            "notes": f"Spatial cluster detected with {case_count} cases in {vil_name}, {dist_name}."
                        }
                    ],
                    "is_demo": False,
                    "disclaimer": OUTBREAK_DISCLAIMER,
                    "created_at": now_iso,
                    "updated_at": now_iso
                }
                await outbreaks_col.insert_one(event_doc)
                detected_count += 1
                # Trigger alert dispatch
                await cls.dispatch_outbreak_alert(event_doc)

        return {
            "status": "success",
            "temporal_window_days": window_days,
            "new_clusters_detected": detected_count,
            "existing_clusters_updated": updated_count,
            "scanned_cases_count": len(current_window_cases),
            "timestamp": now_iso
        }

    @classmethod
    async def dispatch_outbreak_alert(cls, event_doc: Dict[str, Any]) -> None:
        """
        Creates or updates a Biosecurity Early Warning Alert in the alerts collection.
        Enforces deduplication to prevent alert spam.
        """
        alerts_col = get_alerts_collection()
        if alerts_col is None:
            return

        event_id = event_doc.get("event_id")
        risk_tier = event_doc.get("risk_tier", "TIER_1_ROUTINE")
        status_val = event_doc.get("status", "DETECTED")

        if risk_tier == "TIER_1_ROUTINE" or status_val in ["RESOLVED", "FALSE_ALERT"]:
            # If resolved or routine, mark any active alert for this event as Resolved
            await alerts_col.update_many(
                {"affected_tag": {"$regex": event_id}, "status": "Active"},
                {"$set": {"status": "Resolved", "action_required": "Cluster investigation concluded."}}
            )
            return

        # Check for existing active alert for this event
        existing_alert = await alerts_col.find_one({
            "affected_tag": {"$regex": event_id},
            "status": "Active"
        })

        loc = event_doc.get("location", {})
        loc_str = f"{loc.get('village', 'Village')}, {loc.get('district', 'District')}"
        severity_enum = AlertSeverityEnum.CRITICAL if risk_tier == "TIER_3_RED_ALERT" else AlertSeverityEnum.HIGH
        alert_type_enum = AlertTypeEnum.CRITICAL if risk_tier == "TIER_3_RED_ALERT" else AlertTypeEnum.DISEASE_RISK

        title = f"{'RED ALERT: Suspected Outbreak' if risk_tier == 'TIER_3_RED_ALERT' else 'EARLY WARNING: Possible Cluster'} in {loc_str}"
        desc = (
            f"{event_doc.get('case_count', 3)} suspected cases of {event_doc.get('disease_signal', 'disease')} "
            f"detected within temporal surveillance window. Risk Score: {event_doc.get('risk_score', 0)}/100."
        )
        action_req = (
            "Immediate Veterinary Officer Dispatch & 5km Ring Biosecurity Advisory"
            if risk_tier == "TIER_3_RED_ALERT"
            else "Veterinary On-Site Verification & Cohort Isolation Required"
        )

        if existing_alert:
            # Update existing alert
            await alerts_col.update_one(
                {"alert_id": existing_alert["alert_id"]},
                {
                    "$set": {
                        "title": title,
                        "description": desc,
                        "severity": severity_enum.value,
                        "action_required": action_req,
                        "affected_tag": f"{event_id} ({event_doc.get('case_count', 0)} Cases)"
                    }
                }
            )
        else:
            # Create new alert
            try:
                alert_payload = AlertCreate(
                    title=title,
                    description=desc,
                    alert_type=alert_type_enum,
                    severity=severity_enum,
                    location=loc_str,
                    affected_tag=f"{event_id} ({event_doc.get('case_count', 0)} Cases)",
                    animal_id=event_doc.get("animal_ids", [None])[0] if event_doc.get("animal_ids") else None,
                    action_required=action_req,
                    dispatch_status="Pending On-Site Vet Review"
                )
                await create_alert(alert_payload)
            except Exception as e:
                # Log without crashing core flow
                pass

    @classmethod
    async def assign_veterinary_officer(
        cls,
        event_id: str,
        officer_name: str,
        current_user: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = ""
    ) -> OutbreakEventResponse:
        """Assigns an active outbreak event to a designated Veterinary Officer."""
        # Role check: farmers forbidden
        if current_user:
            role = current_user.get("role", "farmer")
            if role == "farmer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access forbidden: Farmers are not permitted to assign veterinary officers or manage outbreaks."
                )

        col = get_outbreak_events_collection()
        if col is None:
            raise HTTPException(status_code=503, detail="Database unavailable.")

        event = await col.find_one({"event_id": event_id})
        if not event:
            raise HTTPException(status_code=404, detail=f"Outbreak event '{event_id}' not found.")

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        actor = current_user.get("sub", "ADMIN") if current_user else "ADMIN"
        actor_role = current_user.get("role", "veterinarian") if current_user else "veterinarian"

        new_status = event["status"]
        if new_status in [OutbreakStatus.DETECTED.value, OutbreakStatus.UNDER_SURVEILLANCE.value]:
            new_status = OutbreakStatus.VETERINARY_INVESTIGATION.value

        audit_entry = {
            "action": "OFFICER_ASSIGNED",
            "actor_id": actor,
            "actor_role": actor_role,
            "timestamp": now_iso,
            "event_id": event_id,
            "previous_status": event["status"],
            "new_status": new_status,
            "notes": f"Assigned to {officer_name}. {notes}".strip()
        }

        await col.update_one(
            {"event_id": event_id},
            {
                "$set": {
                    "assigned_veterinary_officer": officer_name,
                    "assigned_at": now_iso,
                    "assigned_by": actor,
                    "status": new_status,
                    "veterinary_review_status": "IN_PROGRESS",
                    "updated_at": now_iso
                },
                "$push": {"audit_trail": audit_entry}
            }
        )

        return await cls.get_outbreak_by_id(event_id)

    @classmethod
    async def update_outbreak_status(
        cls,
        event_id: str,
        new_status: OutbreakStatus,
        current_user: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = ""
    ) -> OutbreakEventResponse:
        """Transitions an outbreak event's operational lifecycle status."""
        # Role check: farmers forbidden
        if current_user:
            role = current_user.get("role", "farmer")
            if role == "farmer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access forbidden: Farmers are not permitted to change outbreak investigation status."
                )

        col = get_outbreak_events_collection()
        if col is None:
            raise HTTPException(status_code=503, detail="Database unavailable.")

        event = await col.find_one({"event_id": event_id})
        if not event:
            raise HTTPException(status_code=404, detail=f"Outbreak event '{event_id}' not found.")

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        actor = current_user.get("sub", "ADMIN") if current_user else "ADMIN"
        actor_role = current_user.get("role", "veterinarian") if current_user else "veterinarian"

        audit_entry = {
            "action": "STATUS_CHANGED",
            "actor_id": actor,
            "actor_role": actor_role,
            "timestamp": now_iso,
            "event_id": event_id,
            "previous_status": event["status"],
            "new_status": new_status.value,
            "notes": notes or f"Status transitioned to {new_status.value}."
        }

        update_payload: Dict[str, Any] = {
            "status": new_status.value,
            "updated_at": now_iso
        }

        if new_status == OutbreakStatus.RESOLVED:
            update_payload["veterinary_review_status"] = "RESOLVED"
            # Deactivate linked alerts
            alerts_col = get_alerts_collection()
            if alerts_col is not None:
                await alerts_col.update_many(
                    {"affected_tag": {"$regex": event_id}, "status": "Active"},
                    {"$set": {"status": "Resolved"}}
                )
        elif new_status == OutbreakStatus.FALSE_ALERT:
            update_payload["veterinary_review_status"] = "FALSE_ALERT"
            alerts_col = get_alerts_collection()
            if alerts_col is not None:
                await alerts_col.update_many(
                    {"affected_tag": {"$regex": event_id}, "status": "Active"},
                    {"$set": {"status": "Resolved", "action_required": "Marked FALSE_ALERT upon veterinary inspection."}}
                )

        await col.update_one(
            {"event_id": event_id},
            {
                "$set": update_payload,
                "$push": {"audit_trail": audit_entry}
            }
        )

        return await cls.get_outbreak_by_id(event_id)

    @classmethod
    async def record_investigation(
        cls,
        event_id: str,
        record: InvestigationRecord,
        current_user: Optional[Dict[str, Any]] = None
    ) -> OutbreakEventResponse:
        """Records certified clinical field investigation by an inspecting Veterinary Officer."""
        # Role check: farmers forbidden
        if current_user:
            role = current_user.get("role", "farmer")
            if role == "farmer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access forbidden: Farmers are not permitted to submit clinical outbreak investigations."
                )

        col = get_outbreak_events_collection()
        if col is None:
            raise HTTPException(status_code=503, detail="Database unavailable.")

        event = await col.find_one({"event_id": event_id})
        if not event:
            raise HTTPException(status_code=404, detail=f"Outbreak event '{event_id}' not found.")

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        actor = current_user.get("sub", record.investigating_officer) if current_user else record.investigating_officer
        actor_role = current_user.get("role", "veterinarian") if current_user else "veterinarian"

        record_dict = record.model_dump()
        record_dict["submitted_at"] = now_iso

        new_status = OutbreakStatus.ACTION_RECOMMENDED.value
        audit_entry = {
            "action": "INVESTIGATION_RECORDED",
            "actor_id": actor,
            "actor_role": actor_role,
            "timestamp": now_iso,
            "event_id": event_id,
            "previous_status": event["status"],
            "new_status": new_status,
            "notes": f"Field visit on {record.field_visit_date} examined {record.animals_examined} animals. Lab required: {record.laboratory_test_required}."
        }

        await col.update_one(
            {"event_id": event_id},
            {
                "$set": {
                    "investigation_record": record_dict,
                    "investigation_notes": record.investigation_notes,
                    "status": new_status,
                    "veterinary_review_status": "VERIFIED",
                    "assigned_veterinary_officer": record.investigating_officer,
                    "updated_at": now_iso
                },
                "$push": {"audit_trail": audit_entry}
            }
        )

        return await cls.get_outbreak_by_id(event_id)

    @classmethod
    async def get_outbreak_stats(cls) -> OutbreakStatsResponse:
        """Returns real-time aggregated outbreak surveillance KPIs."""
        col = get_outbreak_events_collection()
        if col is None:
            return OutbreakStatsResponse(
                active_clusters=0,
                surveillance_alerts=0,
                red_alerts=0,
                routine_events=0,
                resolved_events=0,
                false_alerts=0,
                total_events=0,
                affected_animals_count=0,
                affected_villages_count=0,
                affected_districts_count=0
            )

        total = await col.count_documents({})
        active = await col.count_documents({
            "status": {"$in": ["DETECTED", "UNDER_SURVEILLANCE", "VETERINARY_INVESTIGATION", "ACTION_RECOMMENDED", "MONITORING"]}
        })
        red = await col.count_documents({
            "risk_tier": "TIER_3_RED_ALERT",
            "status": {"$nin": ["RESOLVED", "FALSE_ALERT"]}
        })
        surv = await col.count_documents({
            "risk_tier": "TIER_2_SURVEILLANCE",
            "status": {"$nin": ["RESOLVED", "FALSE_ALERT"]}
        })
        routine = await col.count_documents({
            "risk_tier": "TIER_1_ROUTINE"
        })
        resolved = await col.count_documents({"status": "RESOLVED"})
        false_alerts = await col.count_documents({"status": "FALSE_ALERT"})

        # Collect unique animals, villages, and districts
        animal_ids = set()
        villages = set()
        districts = set()

        cursor = col.find({}, {"animal_ids": 1, "location": 1})
        async for doc in cursor:
            for aid in doc.get("animal_ids", []):
                animal_ids.add(aid)
            loc = doc.get("location", {})
            v = loc.get("village")
            d = loc.get("district")
            if v and v != "LOCATION_UNKNOWN":
                villages.add(v)
            if d and d != "LOCATION_UNKNOWN":
                districts.add(d)

        return OutbreakStatsResponse(
            active_clusters=active,
            surveillance_alerts=surv,
            red_alerts=red,
            routine_events=routine,
            resolved_events=resolved,
            false_alerts=false_alerts,
            total_events=total,
            affected_animals_count=len(animal_ids),
            affected_villages_count=len(villages),
            affected_districts_count=len(districts)
        )

    @classmethod
    async def get_outbreak_trends(cls) -> OutbreakTrendsResponse:
        """Returns epidemiological trend metrics aggregated across 7, 14, and 30-day windows."""
        col = get_outbreak_events_collection()
        cases_col = get_veterinary_cases_collection()

        now = datetime.datetime.now(datetime.timezone.utc)
        windows_config = [
            ("Last 7 Days", 7),
            ("Last 14 Days", 14),
            ("Last 30 Days", 30)
        ]

        items = []
        for label, days in windows_config:
            win_start = now - datetime.timedelta(days=days)
            prev_start = now - datetime.timedelta(days=days * 2)

            curr_cases = 0
            prev_cases = 0
            high_risk = 0
            crit_cases = 0

            if cases_col is not None:
                async for c in cases_col.find({}):
                    ts = c.get("created_at") or c.get("reported_date")
                    if ts:
                        try:
                            dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        except Exception:
                            dt = now
                        if dt >= win_start:
                            curr_cases += 1
                            if str(c.get("risk_level", "")).upper() in ["HIGH", "CRITICAL"]:
                                high_risk += 1
                            if str(c.get("risk_level", "")).upper() == "CRITICAL":
                                crit_cases += 1
                        elif prev_start <= dt < win_start:
                            prev_cases += 1

            if prev_cases > 0:
                trend_pct = round(((curr_cases - prev_cases) / prev_cases) * 100.0, 1)
            else:
                trend_pct = round(100.0 * curr_cases, 1) if curr_cases > 0 else 0.0

            clusters = 0
            outbreaks = 0
            red_alerts = 0
            resolved = 0

            if col is not None:
                clusters = await col.count_documents({
                    "risk_tier": "TIER_2_SURVEILLANCE",
                    "created_at": {"$gte": win_start.isoformat()}
                })
                outbreaks = await col.count_documents({
                    "risk_tier": "TIER_3_RED_ALERT",
                    "created_at": {"$gte": win_start.isoformat()}
                })
                red_alerts = outbreaks
                resolved = await col.count_documents({
                    "status": "RESOLVED",
                    "updated_at": {"$gte": win_start.isoformat()}
                })

            items.append(OutbreakTrendItem(
                period_label=label,
                days=days,
                total_cases=curr_cases,
                high_risk_cases=high_risk,
                critical_cases=crit_cases,
                possible_clusters=clusters,
                suspected_outbreaks=outbreaks,
                red_alerts=red_alerts,
                resolved_events=resolved,
                trend_percentage=trend_pct
            ))

        return OutbreakTrendsResponse(windows=items)

    @classmethod
    async def get_geographic_hotspots(cls) -> HotspotsResponse:
        """Aggregates caseload by District -> Block -> Village and assigns Hotspot priority levels."""
        cases_col = get_veterinary_cases_collection()
        outbreaks_col = get_outbreak_events_collection()

        village_stats: Dict[str, Dict[str, Any]] = {}

        if cases_col is not None:
            async for c in cases_col.find({}):
                loc = parse_location(c.get("location"))
                v_key = f"{loc.state}|{loc.district}|{loc.block}|{loc.village}"
                if v_key not in village_stats:
                    village_stats[v_key] = {
                        "village": loc.village,
                        "block": loc.block,
                        "district": loc.district,
                        "state": loc.state,
                        "case_count": 0,
                        "high_critical_count": 0,
                        "conditions": {},
                        "active_clusters": 0
                    }
                village_stats[v_key]["case_count"] += 1
                if str(c.get("risk_level", "")).upper() in ["HIGH", "CRITICAL"]:
                    village_stats[v_key]["high_critical_count"] += 1

                cond = c.get("condition", "Suspected Lumpy Skin Disease")
                village_stats[v_key]["conditions"][cond] = village_stats[v_key]["conditions"].get(cond, 0) + 1

        if outbreaks_col is not None:
            async for ev in outbreaks_col.find({"status": {"$nin": ["RESOLVED", "FALSE_ALERT"]}}):
                loc = ev.get("location", {})
                v_key = f"{loc.get('state', 'Gujarat')}|{loc.get('district', 'District')}|{loc.get('block', 'Block')}|{loc.get('village', 'Village')}"
                if v_key in village_stats:
                    village_stats[v_key]["active_clusters"] += 1

        hotspots_list: List[HotspotVillageItem] = []
        high_p = 0
        med_p = 0
        low_p = 0

        for _, data in village_stats.items():
            cc = data["case_count"]
            hc = data["high_critical_count"]

            if cc >= 5 or hc >= 4 or data["active_clusters"] >= 1:
                level = HotspotLevel.HOTSPOT_HIGH
                high_p += 1
            elif cc >= 3 or hc >= 2:
                level = HotspotLevel.HOTSPOT_MEDIUM
                med_p += 1
            else:
                level = HotspotLevel.HOTSPOT_LOW
                low_p += 1

            dom_cond = "Suspected Lumpy Skin Disease"
            if data["conditions"]:
                dom_cond = max(data["conditions"].items(), key=lambda x: x[1])[0]

            hotspots_list.append(HotspotVillageItem(
                village=data["village"],
                block=data["block"],
                district=data["district"],
                state=data["state"],
                case_count=cc,
                high_critical_count=hc,
                hotspot_level=level,
                dominant_condition=dom_cond,
                active_clusters=data["active_clusters"]
            ))

        # Sort by hotspot priority then case count
        def rank(h):
            p = 3 if h.hotspot_level == HotspotLevel.HOTSPOT_HIGH else (2 if h.hotspot_level == HotspotLevel.HOTSPOT_MEDIUM else 1)
            return (p, h.case_count)

        hotspots_list.sort(key=rank, reverse=True)

        return HotspotsResponse(
            total_hotspots=len(hotspots_list),
            high_priority_hotspots=high_p,
            medium_priority_hotspots=med_p,
            low_priority_hotspots=low_p,
            hotspots=hotspots_list
        )

    @classmethod
    async def seed_sih_demo_cluster(cls) -> OutbreakEventResponse:
        """
        Seeds the official controlled SIH 2026 presentation demonstration cluster.
        Clearly tags all generated records with is_demo: True and disclaimer.
        """
        outbreaks_col = get_outbreak_events_collection()
        cases_col = get_veterinary_cases_collection()
        animals_col = get_animals_collection()
        if outbreaks_col is None:
            raise HTTPException(status_code=503, detail="Database unavailable.")

        now = datetime.datetime.now(datetime.timezone.utc)
        now_iso = now.isoformat()
        demo_event_id = "OUT-DEMO-SIH-01"

        # Check if already seeded
        existing = await outbreaks_col.find_one({"event_id": demo_event_id})
        if existing:
            existing.pop("_id", None)
            return OutbreakEventResponse(**existing)

        # 5 Demo Animals in Village Demo-A (Anand District)
        demo_animals = [
            {"animal_id": "AN-DEMO-01", "name": "Ganga #01", "tag": "TAG-DEMO-01", "species": "Cattle", "risk_level": "HIGH", "health_status": "Under Observation", "location": "Village Demo-A, Anand, Gujarat", "is_demo": True},
            {"animal_id": "AN-DEMO-02", "name": "Kankrej #02", "tag": "TAG-DEMO-02", "species": "Cattle", "risk_level": "HIGH", "health_status": "Under Observation", "location": "Village Demo-A, Anand, Gujarat", "is_demo": True},
            {"animal_id": "AN-DEMO-03", "name": "Gir #03", "tag": "TAG-DEMO-03", "species": "Cattle", "risk_level": "CRITICAL", "health_status": "Critical", "location": "Village Demo-A, Anand, Gujarat", "is_demo": True},
            {"animal_id": "AN-DEMO-04", "name": "Surti #04", "tag": "TAG-DEMO-04", "species": "Cattle", "risk_level": "HIGH", "health_status": "Under Observation", "location": "Village Demo-A, Anand, Gujarat", "is_demo": True},
            {"animal_id": "AN-DEMO-05", "name": "Sahiwal #05", "tag": "TAG-DEMO-05", "species": "Cattle", "risk_level": "CRITICAL", "health_status": "Critical", "location": "Village Demo-A, Anand, Gujarat", "is_demo": True}
        ]

        # Seed animals if not present
        if animals_col is not None:
            for da in demo_animals:
                exists = await animals_col.find_one({"animal_id": da["animal_id"]})
                if not exists:
                    da_doc = da.copy()
                    da_doc["created_at"] = now_iso
                    da_doc["updated_at"] = now_iso
                    await animals_col.insert_one(da_doc)

        # Seed veterinary cases for each
        if cases_col is not None:
            for idx, da in enumerate(demo_animals):
                c_id = f"CASE-DEMO-0{idx+1}"
                ai_assess = {
                    "possible_condition": "Suspected Lumpy Skin Disease",
                    "confidence": 88.5,
                    "risk_level": da["risk_level"],
                    "veterinary_review_required": True,
                    "symptoms_detected": ["Cutaneous nodules", "Pyrexia"]
                }
                c_exists = await cases_col.find_one({"case_id": c_id})
                if not c_exists:
                    await cases_col.insert_one({
                        "case_id": c_id,
                        "animal_id": da["animal_id"],
                        "animal_tag": da["tag"],
                        "animal_name": da["name"],
                        "species": da["species"],
                        "owner_name": "Village Demo-A Cooperative Dairy",
                        "location": da["location"],
                        "risk_level": da["risk_level"],
                        "condition": "Suspected Lumpy Skin Disease",
                        "case_status": "REVIEWED",
                        "status": "REVIEWED",
                        "ai_assessment": ai_assess,
                        "is_demo": True,
                        "audit_trail": [],
                        "created_at": (now - datetime.timedelta(days=idx)).isoformat(),
                        "updated_at": now_iso
                    })
                elif "ai_assessment" not in c_exists:
                    await cases_col.update_one(
                        {"case_id": c_id},
                        {"$set": {"ai_assessment": ai_assess, "case_status": "REVIEWED", "owner_name": "Village Demo-A Cooperative Dairy"}}
                    )


        loc_obj = LocationHierarchy(
            village="Village Demo-A",
            block="Anand Rural",
            district="Anand",
            state="Gujarat",
            pincode="388001"
        )

        trigger_reasons = [
            "+35 pts: Severe caseload volume (5 active cases in temporal window)",
            "+30 pts: High clinical severity (2 critical, 3 high-risk animals)",
            "+15 pts: Rapid epidemiological surge (+250.0% vs previous period)",
            "+10 pts: Geographic density concentrated in village 'Village Demo-A'",
            "+5 pts: Syndromic concordance on condition 'Lumpy Skin Disease'"
        ]

        demo_doc = {
            "event_id": demo_event_id,
            "status": OutbreakStatus.DETECTED.value,
            "risk_tier": OutbreakRiskTier.TIER_3_RED_ALERT.value,
            "risk_score": 95,
            "disease_signal": "Lumpy Skin Disease",
            "condition": "Suspected Lumpy Skin Disease (Capripoxvirus Cluster)",
            "animal_ids": [d["animal_id"] for d in demo_animals],
            "case_count": len(demo_animals),
            "herd_ids": ["Dairy Bay 01", "Paddock A"],
            "location": loc_obj.model_dump(),
            "window_start": (now - datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
            "window_end": now.strftime("%Y-%m-%d"),
            "first_detected_at": (now - datetime.timedelta(days=5)).isoformat(),
            "last_updated_at": now_iso,
            "trend_percentage": 250.0,
            "trigger_reasons": trigger_reasons,
            "veterinary_review_status": "PENDING",
            "assigned_veterinary_officer": None,
            "assigned_at": None,
            "assigned_by": None,
            "investigation_record": None,
            "investigation_notes": None,
            "recommended_actions": get_recommended_actions_for_tier(OutbreakRiskTier.TIER_3_RED_ALERT, "Lumpy Skin Disease"),
            "audit_trail": [
                {
                    "action": "DEMO_CLUSTER_SEEDED",
                    "actor_id": "SIH_EVALUATOR",
                    "actor_role": "admin",
                    "timestamp": now_iso,
                    "event_id": demo_event_id,
                    "new_status": OutbreakStatus.DETECTED.value,
                    "notes": "Seeded synthetic demonstration cluster for SIH 2026 early warning jury review."
                }
            ],
            "is_demo": True,
            "disclaimer": "DEMO / SIMULATED DATA: Prototype cluster simulation for SIH 2026 early-warning dashboard.",
            "created_at": now_iso,
            "updated_at": now_iso
        }

        await outbreaks_col.insert_one(demo_doc)
        await cls.dispatch_outbreak_alert(demo_doc)

        demo_doc.pop("_id", None)
        return OutbreakEventResponse(**demo_doc)


outbreak_service = OutbreakService()


async def seed_default_outbreaks_if_empty() -> None:
    """Seeds baseline demonstration cluster if outbreak collection is empty."""
    col = get_outbreak_events_collection()
    if col is not None:
        count = await col.count_documents({})
        if count == 0:
            await outbreak_service.seed_sih_demo_cluster()
