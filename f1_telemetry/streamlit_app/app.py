import streamlit as st
import pymongo
from id_values import Track, SessionType


@st.cache_resource
def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])


client = init_connection()


@st.cache_data(ttl=600)
def get_sessions():
    db = client.f1
    session_ids = db.session.distinct("m_header.m_sessionUID")
    # for each session, get the first document
    sessions = []
    for session_id in session_ids:
        doc = db.session.find_one(
            {"m_header.m_sessionUID": session_id}, sort=[("_ingested_at", -1)]
        )
        sessions.append(str(doc["_ingested_at"].strftime('%Y-%m-%d %H:%M:%S')) + " - " + str(Track(doc["m_trackId"]).name) + " - " + str(SessionType(doc["m_sessionType"]).name + " - " + str(doc["m_header"]["m_sessionUID"]))
        )
    return sessions


items = get_sessions()
option = st.selectbox("Select a session", items, placeholder="Select a session...")
