import logging
import time
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

logger = logging.getLogger("anicare.database")

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

db = Database()

async def connect_to_mongo() -> None:
    """Initializes the AsyncIOMotorClient connection pool and sets up database indexes."""
    try:
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL} (db: {settings.DATABASE_NAME})...")
        db.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=50,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000
        )
        db.db = db.client[settings.DATABASE_NAME]
        
        # Test connection
        await db.client.admin.command("ping")
        logger.info("Successfully connected to MongoDB!")

        # Setup indexes
        await _setup_indexes()

    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        # We do not crash the app so health checks can report offline status cleanly
        db.client = None
        db.db = None

async def close_mongo_connection() -> None:
    """Closes all MongoDB client connection sockets."""
    if db.client:
        logger.info("Closing MongoDB connection pool...")
        db.client.close()
        logger.info("MongoDB connection closed.")

def get_database() -> Optional[AsyncIOMotorDatabase]:
    """Returns the active MongoDB database instance."""
    return db.db

async def ping_database() -> Dict[str, Any]:
    """Checks MongoDB connectivity and returns ping status."""
    if not db.client or db.db is None:
        return {
            "connected": False,
            "database": settings.DATABASE_NAME,
            "error": "MongoDB client is not initialized or server is unreachable."
        }
    try:
        start = time.perf_counter()
        await db.client.admin.command("ping")
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "connected": True,
            "database": settings.DATABASE_NAME,
            "latency_ms": latency_ms
        }
    except Exception as e:
        return {
            "connected": False,
            "database": settings.DATABASE_NAME,
            "error": str(e)
        }

async def _setup_indexes() -> None:
    """Configures performance and uniqueness indexes across collections."""
    if db.db is None:
        return
    try:
        # Users indexes
        await db.db.users.create_index("email", unique=True)
        await db.db.users.create_index("username", unique=True, sparse=True)

        # Animals indexes
        await db.db.animals.create_index("animal_id", unique=True)
        await db.db.animals.create_index("tag", unique=True, sparse=True)
        await db.db.animals.create_index("species")
        await db.db.animals.create_index("health_status")

        # Health records indexes
        await db.db.health_records.create_index("animal_id")
        await db.db.health_records.create_index([("timestamp", -1)])

        # Disease assessments indexes
        await db.db.disease_assessments.create_index("assessment_id", unique=True)
        await db.db.disease_assessments.create_index("animal_id")

        # Veterinary cases indexes
        await db.db.veterinary_cases.create_index("case_id", unique=True)
        await db.db.veterinary_cases.create_index("animal_id")
        await db.db.veterinary_cases.create_index("status")

        # Alerts indexes
        await db.db.alerts.create_index("alert_id", unique=True)
        await db.db.alerts.create_index("severity")
        await db.db.alerts.create_index("alert_type")
        await db.db.alerts.create_index([("created_at", -1)])

        # Outbreak events indexes
        await db.db.outbreak_events.create_index("event_id", unique=True)
        await db.db.outbreak_events.create_index("status")
        await db.db.outbreak_events.create_index("risk_tier")
        await db.db.outbreak_events.create_index("district")
        await db.db.outbreak_events.create_index("village")
        await db.db.outbreak_events.create_index("disease_signal")
        await db.db.outbreak_events.create_index("is_demo")
        await db.db.outbreak_events.create_index([("created_at", -1)])
        await db.db.outbreak_events.create_index([("last_updated_at", -1)])

        # Sync and Idempotency indexes
        await db.db.sync_actions.create_index("idempotency_key", unique=True)
        await db.db.sync_actions.create_index("local_action_id")
        await db.db.sync_actions.create_index("device_id")
        await db.db.sync_actions.create_index([("created_at", -1)])
        await db.db.sync_audit.create_index("device_id")
        await db.db.sync_audit.create_index([("timestamp", -1)])

        # AI Monitoring & Governance indexes
        await db.db.ai_prediction_events.create_index("prediction_id", unique=True)
        await db.db.ai_prediction_events.create_index("model_version")
        await db.db.ai_prediction_events.create_index("species")
        await db.db.ai_prediction_events.create_index("prediction")
        await db.db.ai_prediction_events.create_index([("timestamp", -1)])

        await db.db.ai_feedback_events.create_index("feedback_id", unique=True)
        await db.db.ai_feedback_events.create_index("prediction_id")
        await db.db.ai_feedback_events.create_index("animal_id")
        await db.db.ai_feedback_events.create_index("feedback_type")
        await db.db.ai_feedback_events.create_index([("timestamp", -1)])

        await db.db.ai_models.create_index("model_id", unique=True)
        await db.db.ai_models.create_index("status")
        await db.db.ai_models.create_index("species")

        await db.db.ai_model_audit.create_index("model_id")
        await db.db.ai_model_audit.create_index([("timestamp", -1)])

        await db.db.ai_dataset_candidates.create_index("candidate_id", unique=True)
        await db.db.ai_dataset_candidates.create_index("sha256")
        await db.db.ai_dataset_candidates.create_index("evidence_level")
        await db.db.ai_dataset_candidates.create_index("permission_status")

        # Geospatial Intelligence indexes (Milestone 12)
        await db.db.geospatial_risk_events.create_index("event_id", unique=True)
        await db.db.geospatial_risk_events.create_index("state")
        await db.db.geospatial_risk_events.create_index("district")
        await db.db.geospatial_risk_events.create_index("block")
        await db.db.geospatial_risk_events.create_index("village")
        await db.db.geospatial_risk_events.create_index("condition")
        await db.db.geospatial_risk_events.create_index("risk_tier")
        await db.db.geospatial_risk_events.create_index("hotspot_status")
        await db.db.geospatial_risk_events.create_index("is_demo")
        await db.db.geospatial_risk_events.create_index([("timestamp", -1)])
        await db.db.geospatial_risk_events.create_index([("district", 1), ("block", 1), ("village", 1)])

        await db.db.geospatial_risk_snapshots.create_index("snapshot_id", unique=True)
        await db.db.geospatial_risk_snapshots.create_index([("created_at", -1)])

        # Field Response & Operational Workflow indexes (Milestone 13)
        await db.db.response_cases.create_index("response_case_id", unique=True)
        await db.db.response_cases.create_index("status")
        await db.db.response_cases.create_index("priority")
        await db.db.response_cases.create_index("source_id")
        await db.db.response_cases.create_index("assigned_to")
        await db.db.response_cases.create_index("is_demo")
        await db.db.response_cases.create_index([("created_at", -1)])
        await db.db.response_cases.create_index([("district", 1), ("block", 1), ("village", 1)])

        await db.db.response_alerts.create_index("alert_id", unique=True)
        await db.db.response_alerts.create_index("response_case_id")
        await db.db.response_alerts.create_index("source_id")
        await db.db.response_alerts.create_index("alert_type")
        await db.db.response_alerts.create_index("status")
        await db.db.response_alerts.create_index("priority")

        await db.db.response_investigations.create_index("investigation_id", unique=True)
        await db.db.response_investigations.create_index("response_case_id")
        await db.db.response_investigations.create_index("idempotency_key")

        await db.db.response_samples.create_index("sample_id", unique=True)
        await db.db.response_samples.create_index("response_case_id")
        await db.db.response_samples.create_index("status")
        await db.db.response_samples.create_index("idempotency_key")

        await db.db.response_actions.create_index("action_id", unique=True)
        await db.db.response_actions.create_index("response_case_id")
        await db.db.response_actions.create_index("action_type")
        await db.db.response_actions.create_index("status")

        await db.db.response_notifications.create_index("notification_id", unique=True)
        await db.db.response_notifications.create_index("status")
        await db.db.response_notifications.create_index("channel")
        await db.db.response_notifications.create_index([("created_at", -1)])

        await db.db.response_audit_logs.create_index("audit_id", unique=True)
        await db.db.response_audit_logs.create_index("response_case_id")
        await db.db.response_audit_logs.create_index([("timestamp", -1)])

        # Reminders index
        await db.db.reminders.create_index("reminder_id", unique=True)
        await db.db.reminders.create_index("animal_id")
        await db.db.reminders.create_index("status")
        await db.db.reminders.create_index([("due_date", 1)])

        logger.info("MongoDB collections indexes initialized.")
    except Exception as e:
        logger.warning(f"Note on setting indexes: {e}")

# Collection accessors
def get_users_collection():
    database = get_database()
    return database.users if database is not None else None

def get_animals_collection():
    database = get_database()
    return database.animals if database is not None else None

def get_health_records_collection():
    database = get_database()
    return database.health_records if database is not None else None

def get_disease_assessments_collection():
    database = get_database()
    return database.disease_assessments if database is not None else None

def get_treatments_collection():
    database = get_database()
    return database.treatments if database is not None else None

def get_vaccinations_collection():
    database = get_database()
    return database.vaccinations if database is not None else None

def get_alerts_collection():
    database = get_database()
    return database.alerts if database is not None else None

def get_veterinary_cases_collection():
    database = get_database()
    return database.veterinary_cases if database is not None else None

def get_outbreak_events_collection():
    database = get_database()
    return database.outbreak_events if database is not None else None

def get_sync_actions_collection():
    database = get_database()
    return database.sync_actions if database is not None else None

def get_sync_audit_collection():
    database = get_database()
    return database.sync_audit if database is not None else None

def get_ai_prediction_events_collection():
    database = get_database()
    return database.ai_prediction_events if database is not None else None

def get_ai_feedback_events_collection():
    database = get_database()
    return database.ai_feedback_events if database is not None else None

def get_ai_models_collection():
    database = get_database()
    return database.ai_models if database is not None else None

def get_ai_model_audit_collection():
    database = get_database()
    return database.ai_model_audit if database is not None else None

def get_ai_dataset_candidates_collection():
    database = get_database()
    return database.ai_dataset_candidates if database is not None else None

def get_geospatial_risk_events_collection():
    database = get_database()
    return database.geospatial_risk_events if database is not None else None

def get_geospatial_risk_snapshots_collection():
    database = get_database()
    return database.geospatial_risk_snapshots if database is not None else None

def get_response_cases_collection():
    database = get_database()
    return database.response_cases if database is not None else None

def get_response_alerts_collection():
    database = get_database()
    return database.response_alerts if database is not None else None

def get_response_investigations_collection():
    database = get_database()
    return database.response_investigations if database is not None else None

def get_response_samples_collection():
    database = get_database()
    return database.response_samples if database is not None else None

def get_response_actions_collection():
    database = get_database()
    return database.response_actions if database is not None else None

def get_response_notifications_collection():
    database = get_database()
    return database.response_notifications if database is not None else None

def get_response_audit_logs_collection():
    database = get_database()
    return database.response_audit_logs if database is not None else None

def get_reminders_collection():
    database = get_database()
    return database.reminders if database is not None else None

