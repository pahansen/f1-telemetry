import os
import pymongo
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from f1_telemetry.session_post_processing.id_enums import Track, SessionType, Weather
from f1_telemetry.session_post_processing.db.engine import engine
from f1_telemetry.session_post_processing.db.tables import Base, Session, Participant

load_dotenv()

Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
mongo_client = pymongo.MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))

def ingest_sessions():
    db = mongo_client.f1
    session_ids = db.session.distinct("m_header.m_sessionUID")
    # for each session, get the first document
    sessions = []
    for session_id in session_ids:
        doc = db.session.find_one(
            {"m_header.m_sessionUID": session_id}, sort=[("_ingested_at", -1)]
        )
        sessions.append(doc)

    # insert session into db
    ingested_sessions_ids = []
    db_session = DBSession()
    existing_sessions = db_session.query(Session).distinct("id").all()
    # remove existing sessions from sessions list
    for existing_session in existing_sessions:
        for session in sessions:
            if session["m_header"]["m_sessionUID"] == existing_session.id:
                sessions.remove(session)

    for session in sessions:
        if session is not None:
            if session["m_header"]["m_sessionUID"] not in ingested_sessions_ids:
                session_id = session["m_header"]["m_sessionUID"]
                session_type = SessionType(session["m_sessionType"]).name
                weather = Weather(session["m_weather"]).name
                track_temperature = session["m_trackTemperature"]
                air_temperature = session["m_airTemperature"]
                track = Track(session["m_trackId"]).name
                session = Session(
                    id=session_id,
                    session_type=session_type,
                    weather=weather,
                    track_temperature=track_temperature,
                    air_temperature=air_temperature,
                    track=track,
                )
                db_session.add(session)
                db_session.commit()
                ingested_sessions_ids.append(session_id)
    
    db_session.close()

    return ingested_sessions_ids

def ingest_participants(ingested_session_ids):
    db_session = DBSession()
    db = mongo_client.f1
    ingested_participants = []
    for session_id in ingested_session_ids:
        participant_doc = db.participants.find_one(
                {"m_header.m_sessionUID": session_id})
        participants = []
        participant_ids = []
        for index, participant in enumerate(participant_doc["m_participants"]):
            if participant["m_aiControlled"] == 0 and (participant["m_networkId"] != 255 or index == participant_doc["m_header"]["m_playerCarIndex"]):
                participant_ids.append(index)
                participant_id = index
                name = participant["m_name"]
                network_id = participant["m_networkId"]
                your_telemetry = participant["m_yourTelemetry"]
                show_online_name = participant["m_showOnlineNames"]
                participant = Participant(
                    session_id=session_id,
                    participant_id=participant_id,
                    name=name,
                    network_id=network_id,
                    your_telemetry=your_telemetry,
                    show_online_name=show_online_name,
                )
                participants.append(participant)
        db_session.add_all(participants)
        db_session.commit()
        ingested_participants.append({"session_id": session_id, "participant_ids": participant_ids})
    db_session.close()

    return ingested_participants
    

if __name__ == "__main__":
    ingested_session_ids = ingest_sessions()
    ingested_participants = ingest_participants(ingested_session_ids)

