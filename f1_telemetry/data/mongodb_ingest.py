"""Ingest F1 Telemetry to InfluxDB.
"""
from f1_telemetry.data.udp_stream import get_udp_messages
from dotenv import load_dotenv
import os
from pymongo.mongo_client import MongoClient
from datetime import datetime

load_dotenv()

MONGODB_CONNECTION_STRING = os.environ.get("MONGODB_CONNECTION_STRING")

mongo_client = MongoClient(MONGODB_CONNECTION_STRING)


def verify_mongodb_setup() -> None:
    """Verify that db and collections exist in mongodb.
    If they don't exist, they will be created.
    """
    if not MONGODB_CONNECTION_STRING:
        raise ValueError("MONGODB_CONNECTION_STRING is missing.")
    db = mongo_client.f1
    collections = [
        "car_telemetry",
        "car_status",
        "car_setup",
        "lap",
        "motion",
        "participants",
        "session",
        "car_damage",
        "final_classification",
        "tyre_sets"
    ]
    for collection in collections:
        if collection not in db.list_collection_names():
            db.create_collection(collection)


def run_f1_telemetry_ingest() -> None:
    """Run F1 telemetry ingestion."""
    verify_mongodb_setup()
    for data in get_udp_messages():
        data["m_header"]["m_sessionUID"] = str(data["m_header"]["m_sessionUID"])
        data["_ingested_at"] = datetime.utcnow()
        packet_ids = {
            0: "motion",
            1: "session",
            2: "lap",
            4: "participants",
            5: "car_setup",
            6: "car_telemetry",
            7: "car_status",
            8: "final_classification",
            10: "car_damage",
            12: "tyre_sets"
        }
        message_type = packet_ids.get(data["m_header"]["m_packetId"], None)
        if message_type is not None:
            mongo_client.f1[message_type].insert_one(data)
