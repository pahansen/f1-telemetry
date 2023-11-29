import os
import pymongo
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from f1_telemetry.session_post_processing.id_enums import Track, SessionType, Weather
from f1_telemetry.session_post_processing.db.engine import engine
from f1_telemetry.session_post_processing.db.tables import Base, Session, Participant, Lap, CarTelemetry

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

def ingest_laps(ingested_participants):
    db_session = DBSession()
    db = mongo_client.f1
    for ingested_participant in ingested_participants:
        session_id = ingested_participant["session_id"]
        participant_ids = ingested_participant["participant_ids"]
        lap_docs = db.lap.find(
            {"m_header.m_sessionUID": session_id}
        )
        for lap_doc in lap_docs:
            laps = []
            for participant_id in participant_ids:
                lap = lap_doc["m_lapData"][participant_id]
                session_time_ms = lap_doc["m_header"]["m_sessionTime"]
                lap_number = lap["m_currentLapNum"]
                lap_distance = lap["m_lapDistance"]
                last_lap_time_ms = lap["m_lastLapTimeInMS"]
                current_lap_time_ms = lap["m_currentLapTimeInMS"]
                sector_1_time_ms = lap["m_sector1TimeInMS"]
                sector_2_time_ms = lap["m_sector2TimeInMS"]
                lap = Lap(
                    session_id=session_id,
                    participant_id=participant_id,
                    session_time_ms=session_time_ms,
                    lap_number=lap_number,
                    lap_distance=lap_distance,
                    last_lap_time_ms=last_lap_time_ms,
                    current_lap_time_ms=current_lap_time_ms,
                    sector_1_time_ms=sector_1_time_ms,
                    sector_2_time_ms=sector_2_time_ms,
                )
                laps.append(lap)
            db_session.add_all(laps)
            db_session.commit()
    db_session.close()

def ingest_car_telemetry(ingested_participants):
    db_session = DBSession()
    db = mongo_client.f1
    for ingested_participant in ingested_participants:
        session_id = ingested_participant["session_id"]
        participant_ids = ingested_participant["participant_ids"]
        car_telemetry_docs = db.car_telemetry.find(
            {"m_header.m_sessionUID": session_id}
        )
        for car_telemetry_doc in car_telemetry_docs:
            car_telemetry_data = []
            for participant_id in participant_ids:
                car_telemetry = car_telemetry_doc["m_carTelemetryData"][participant_id]
                session_time_ms = car_telemetry_doc["m_header"]["m_sessionTime"]
                speed = car_telemetry["m_speed"]
                throttle = car_telemetry["m_throttle"]
                steer = car_telemetry["m_steer"]
                brake = car_telemetry["m_brake"]
                gear = car_telemetry["m_gear"]
                brakes_temperature_rl = car_telemetry["m_brakesTemperatureRL"]
                brakes_temperature_rr = car_telemetry["m_brakesTemperatureRR"]
                brakes_temperature_fl = car_telemetry["m_brakesTemperatureFL"]
                brakes_temperature_fr = car_telemetry["m_brakesTemperatureFR"]
                tyres_surface_temperature_rl = car_telemetry["m_tyresSurfaceTemperatureRL"]
                tyres_surface_temperature_rr = car_telemetry["m_tyresSurfaceTemperatureRR"]
                tyres_surface_temperature_fl = car_telemetry["m_tyresSurfaceTemperatureFL"]
                tyres_surface_temperature_fr = car_telemetry["m_tyresSurfaceTemperatureFR"]
                tyres_inner_temperature_rl = car_telemetry["m_tyresInnerTemperatureRL"]
                tyres_inner_temperature_rr = car_telemetry["m_tyresInnerTemperatureRR"]
                tyres_inner_temperature_fl = car_telemetry["m_tyresInnerTemperatureFL"]
                tyres_inner_temperature_fr = car_telemetry["m_tyresInnerTemperatureFR"]
                tyres_pressure_rl = car_telemetry["m_tyresPressureRL"]
                tyres_pressure_rr = car_telemetry["m_tyresPressureRR"]
                tyres_pressure_fl = car_telemetry["m_tyresPressureFL"]
                tyres_pressure_fr = car_telemetry["m_tyresPressureFR"]
                tyres_surface_type_rl = car_telemetry["m_surfaceTypeRL"]
                tyres_surface_type_rr = car_telemetry["m_surfaceTypeRR"]
                tyres_surface_type_fl = car_telemetry["m_surfaceTypeFL"]
                tyres_surface_type_fr = car_telemetry["m_surfaceTypeFR"]

                car_telemetry = CarTelemetry(
                    session_id=session_id,
                    participant_id=participant_id,
                    session_time_ms=session_time_ms,
                    speed=speed,
                    throttle=throttle,
                    steer=steer,
                    brake=brake,
                    gear=gear,
                    brakes_temperature_rl=brakes_temperature_rl,
                    brakes_temperature_rr=brakes_temperature_rr,
                    brakes_temperature_fl=brakes_temperature_fl,
                    brakes_temperature_fr=brakes_temperature_fr,
                    tyres_surface_temperature_rl=tyres_surface_temperature_rl,
                    tyres_surface_temperature_rr=tyres_surface_temperature_rr,
                    tyres_surface_temperature_fl=tyres_surface_temperature_fl,
                    tyres_surface_temperature_fr=tyres_surface_temperature_fr,
                    tyres_inner_temperature_rl=tyres_inner_temperature_rl,
                    tyres_inner_temperature_rr=tyres_inner_temperature_rr,
                    tyres_inner_temperature_fl=tyres_inner_temperature_fl,
                    tyres_inner_temperature_fr=tyres_inner_temperature_fr,
                    tyres_pressure_rl=tyres_pressure_rl,
                    tyres_pressure_rr=tyres_pressure_rr,
                    tyres_pressure_fl=tyres_pressure_fl,
                    tyres_pressure_fr=tyres_pressure_fr,
                    tyres_surface_type_rl=tyres_surface_type_rl,
                    tyres_surface_type_rr=tyres_surface_type_rr,
                    tyres_surface_type_fl=tyres_surface_type_fl,
                    tyres_surface_type_fr=tyres_surface_type_fr,
                )
                car_telemetry_data.append(car_telemetry)
            db_session.add_all(car_telemetry_data)
            db_session.commit()
    db_session.close()
    

if __name__ == "__main__":
    ingested_session_ids = ingest_sessions()
    ingested_participants = ingest_participants(ingested_session_ids)
    ingest_laps(ingested_participants)
    ingest_car_telemetry(ingested_participants)

