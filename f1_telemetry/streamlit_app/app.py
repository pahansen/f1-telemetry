import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()


@st.cache_resource
def init_connection():
    return st.connection(
        "postgresql",
        type="sql",
        dialect="postgresql",
        host="localhost",
        port="5432",
        username=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        database="postgres",
    )


client = init_connection()


@st.cache_data(ttl=600)
def get_sessions():
    df = client.query("SELECT * FROM public.sessions")
    sessions = []
    for row in df.itertuples():
        sessions.append(
            str(row.id) + " - " + str(row.track) + " - " + str(row.session_type)
        )
    return sessions


@st.cache_data(ttl=600)
def get_laps_and_telemetry(session_id):
    session_id = str(session_id)
    if not session_id.isnumeric():
        return None

    df = client.query(
        f"""
        with laps_session_time_clean as (
            SELECT * 
            FROM public.laps l where l.session_id = '{session_id}' and l.session_time_ms > 1 and l.lap_distance > 0
        ),
        joined_tables as (
            select 
                l.session_id, 
                l.participant_id,
                p.name, 
                l.session_time_ms,
                l.lap_number,
                l.lap_distance,
                l.last_lap_time_ms,
                l.current_lap_time_ms,
                l.sector_1_time_ms,
                l.sector_2_time_ms,
                ct.speed,
                ct.throttle,
                ct.steer,
                ct.brake,
                ct.gear,
                ct.brakes_temperature_rl,
                ct.brakes_temperature_rr,
                ct.brakes_temperature_fl,
                ct.brakes_temperature_fr,
                ct.tyres_surface_temperature_rl,
                ct.tyres_surface_temperature_rr,
                ct.tyres_surface_temperature_fl,
                ct.tyres_surface_temperature_fr,
                ct.tyres_inner_temperature_rl,
                ct.tyres_inner_temperature_rr,
                ct.tyres_inner_temperature_fl,
                ct.tyres_inner_temperature_fr,
                ct.tyres_pressure_rl,
                ct.tyres_pressure_rr,
                ct.tyres_pressure_fl,
                ct.tyres_pressure_fr,
                ct.tyres_surface_type_rl,
                ct.tyres_surface_type_rr,
                ct.tyres_surface_type_fl,
                ct.tyres_surface_type_fr
            from laps_session_time_clean l
            left join public.car_telemetry ct on l.session_id = ct.session_id and l.session_time_ms = ct.session_time_ms and l.participant_id = ct.participant_id 
            left join public.participants p on l.participant_id = p.participant_id and l.session_id = p.session_id
            order by l.session_id, l.session_time_ms, l.participant_id  asc)
        select * from joined_tables;
    """
    )
    return df


items = get_sessions()
option = st.selectbox("Select a session", items, placeholder="Select a session...")

if option:
    session_id = option.split("-")[0].strip()
    laps_and_telemetry = get_laps_and_telemetry(session_id)
    st.dataframe(laps_and_telemetry)
