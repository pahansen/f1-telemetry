import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
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
def get_laps_and_telemetry(session_id, driver_ids):
    session_id = str(session_id)
    if not session_id.isnumeric():
        return None
    
    driver_ids = [str(driver_id) for driver_id in driver_ids]
    if not all(driver_id.isnumeric() for driver_id in driver_ids):
        return None
    
    # add query string for SQL to filter by driver_ids driver_ids have to be enclosed in single quotes withuot using fstring
    driver_ids_query = "and l.participant_id in ("
    if driver_ids:
        for index, driver_id in enumerate(driver_ids):
            driver_ids_query += "'" + driver_id + "'"
            if index < len(driver_ids) - 1:
                driver_ids_query += ","
    driver_ids_query += ")"

    df = client.query(
        f"""
        with laps_session_time_clean as (
            SELECT * 
            FROM public.laps l where l.session_id = '{session_id}' and l.session_time_ms > 1 and l.lap_distance > 0 {driver_ids_query}
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

@st.cache_data(ttl=600)
def get_fastest_laps(dataframe: pd.DataFrame, drivers_list: list) -> dict:
    """Returns a dictionary with drivers_list as keys and returns (Fastest Lap, Fastest Lap Time)"""
    # TODO: Check if this works for last lap
    fastest_lap_dict = {}
    for d in drivers_list:
        d_df = dataframe[
            (dataframe["participant_id"] == d) & (dataframe["lap_number"] > 1)
        ]
        if d_df.empty:
            fastest_lap_dict[d] = (0, 0)
        else:
            time = d_df["last_lap_time_ms"].min()
            n_lap = (
                d_df.iloc[d_df["last_lap_time_ms"].argmin()]["lap_number"]
                - 1
            )
            fastest_lap_dict[d] = (n_lap, time)

    return fastest_lap_dict

def create_lap_time_string(lap_time: int):
    minutes, remainder = divmod(lap_time, 60000)
    seconds, ms = divmod(remainder, 1000)
    return f"{minutes:02d}:{seconds:02d}:{ms:03d}"


def create_delta_time_string(delta_time: int):
    if delta_time == None:
        return None
    seconds, ms = divmod(delta_time, 1000)
    return f"{seconds}.{ms:03d} s"


items = get_sessions()
session = st.selectbox("Select a session", items, placeholder="Select a session...")

if session:
    driver_for_session = client.query(
        f"""
        select p.participant_id, p.name from public.participants p where p.session_id = '{session.split("-")[0].strip()}'
    """
    )
    driver_for_session_multi = []
    for row in driver_for_session.itertuples():
        driver_for_session_multi.append(str(row.participant_id) + " - " + str(row.name))
    drivers = st.multiselect("Select drivers", driver_for_session_multi, max_selections=3)

if session and drivers:
    session_id = session.split("-")[0].strip()
    driver_ids = [driver.split("-")[0].strip() for driver in drivers]
    laps_and_telemetry = get_laps_and_telemetry(session_id, driver_ids)
    
    fastest_laps_dict = get_fastest_laps(laps_and_telemetry, driver_ids)
    plotted_telemetry = []
    lap_times = []
    for driver in drivers:
        driver_id = driver.split("-")[0].strip()
        lap = st.select_slider(
            f"Select lap for {driver}:",
            options=laps_and_telemetry.lap_number.unique(),
            value=fastest_laps_dict[driver_id][0],
            key=f"{driver}_lap_slider",
        )

        lap_times.append(
            laps_and_telemetry[
                (laps_and_telemetry["participant_id"] == driver_id)
                & (laps_and_telemetry["lap_number"] == lap + 1)
            ]["last_lap_time_ms"].min()
        )
        # Create distplot with custom bin_size
        # TODO: Origin of "A Value is trying to be set on a copy.."
        merged_telemetry_filtered = laps_and_telemetry[
            (laps_and_telemetry["lap_number"] == lap)
            & (laps_and_telemetry["participant_id"] == driver_id)
        ]

        merged_telemetry_filtered.loc[
            :, f"{driver}_current_lap_time_in_ms"
        ] = merged_telemetry_filtered["current_lap_time_ms"]
        plotted_telemetry.append(merged_telemetry_filtered)

    fastest_driver_selected_laps = drivers[lap_times.index(min(lap_times))]
    plotted_telemetry_df = (
        pd.concat(plotted_telemetry).set_index("lap_distance").sort_index()
    )
    plotted_telemetry_df = plotted_telemetry_df.interpolate(
        method="index", limit_direction="both"
    ).reset_index()

    plotted_telemetry_df[f"delta_to_{fastest_driver_selected_laps}"] = None
    for driver in drivers:
        plotted_telemetry_df[f"delta_to_{fastest_driver_selected_laps}"].mask(
            plotted_telemetry_df["participant_id"] == driver_id,
            plotted_telemetry_df[f"{driver}_current_lap_time_in_ms"]
            - plotted_telemetry_df[
                f"{fastest_driver_selected_laps}_current_lap_time_in_ms"
            ],
            inplace=True,
        )

    plots = [
        f"delta_to_{fastest_driver_selected_laps}",
        "speed",
        "gear",
        "throttle",
        "brake",
        "steer",
    ]
    fig = make_subplots(rows=len(plots), cols=1, shared_xaxes=True)

    colors = ["darkorange", "lightskyblue", "lightseagreen"]
    
    for i, col in enumerate(plots, start=1):
        SHOW_LEGEND = True if i == 1 else False
        for driver_i, driver in enumerate(plotted_telemetry_df.name.unique()):
            fig.add_trace(
                go.Scatter(
                    x=plotted_telemetry_df[
                        plotted_telemetry_df["name"] == driver
                    ].index,
                    y=plotted_telemetry_df[plotted_telemetry_df["name"] == driver][
                        col
                    ].values,
                    legendgroup=driver,
                    name=driver,
                    line=dict(color=colors[driver_i]),
                    showlegend=SHOW_LEGEND,
                ),
                row=i,
                col=1,
            )

    # Plot!
    st.plotly_chart(fig, use_container_width=True)

    # display metrics
    fastest_lap_time = min(
        [x[1] for x in list(fastest_laps_dict.values()) if x[1] != 0]
    )
    fastest_lap_time_driver = [
        k for k, v in fastest_laps_dict.items() if v[1] == fastest_lap_time
    ][0]
    for driver in drivers:
        driver_id = driver.split("-")[0].strip()
        fastest_lap_driver_id = fastest_lap_time_driver.split("-")[0].strip()
        if driver == fastest_driver_selected_laps:
            lap_delta = None
        else:
            lap_delta = (
                lap_times[drivers.index(driver)].item()
                - lap_times[drivers.index(fastest_driver_selected_laps)].item()
            )
        if driver == fastest_lap_time_driver:
            fastest_lap_delta = None
        else:
            fastest_lap_delta = (
                fastest_laps_dict[driver_id][1].item()
                - fastest_laps_dict[fastest_lap_driver_id][1].item()
            )

        cols = st.columns(2)
        cols[0].metric(
            f"{driver} current lap time",
            create_lap_time_string(lap_times[drivers.index(driver)]),
            create_delta_time_string(lap_delta),
            delta_color="inverse",
        )
        cols[1].metric(
            f"{driver} fastest lap time",
            create_lap_time_string(fastest_laps_dict[driver_id][1]),
            create_delta_time_string(fastest_lap_delta),
            delta_color="inverse",
        )
