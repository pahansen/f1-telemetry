from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    session_type = Column(String)
    weather = Column(String)
    track_temperature = Column(Integer)
    air_temperature = Column(Integer)
    track = Column(String)

class Participant(Base):
    __tablename__ = "participants"

    session_id = Column(String, primary_key=True)
    participant_id = Column(String, primary_key=True)
    name = Column(String)
    network_id = Column(String)
    your_telemetry = Column(Integer)
    show_online_name = Column(Integer)

class Lap(Base):
    __tablename__ = "laps"

    session_id = Column(String, primary_key=True)
    pariticipant_id = Column(String, primary_key=True)
    session_time_ms = Column(Float, primary_key=True)
    lap_number = Column(Integer)
    lap_distance = Column(Float)
    last_lap_time_ms = Column(Integer)
    sector_1_time_ms = Column(Integer)
    sector_2_time_ms = Column(Integer)

class CarTelemetry(Base):
    __tablename__ = "car_telemetry"

    session_id = Column(String, primary_key=True)
    participant_id = Column(String, primary_key=True)
    session_time_ms = Column(Float, primary_key=True)
    speed = Column(Float)
    throttle = Column(Float)
    steer = Column(Float)
    brake = Column(Float)
    gear = Column(Integer)
    brakes_temperature_rl = Column(Integer)
    brakes_temperature_rr = Column(Integer)
    brakes_temperature_fl = Column(Integer)
    brakes_temperature_fr = Column(Integer)
    tyres_surface_temperature_rl = Column(Integer)
    tyres_surface_temperature_rr = Column(Integer)
    tyres_surface_temperature_fl = Column(Integer)
    tyres_surface_temperature_fr = Column(Integer)
    tyres_inner_temperature_rl = Column(Integer)
    tyres_inner_temperature_rr = Column(Integer)
    tyres_inner_temperature_fl = Column(Integer)
    tyres_inner_temperature_fr = Column(Integer)
    tyres_pressure_rl = Column(Float)
    tyres_pressure_rr = Column(Float)
    tyres_pressure_fl = Column(Float)
    tyres_pressure_fr = Column(Float)
    tyres_surface_type_rl = Column(String)
    tyres_surface_type_rr = Column(String)
    tyres_surface_type_fl = Column(String)
    tyres_surface_type_fr = Column(String)