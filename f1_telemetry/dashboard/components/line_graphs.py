"""Collection of different line grpahs that are rendered on app."""
from pandas import DataFrame
from plotly import graph_objects as go


def update_tyre_temperature(df: DataFrame) -> go.Figure:
    """Create traces in fig for tyre surface temperature.

    Args:
        df(DataFrame): DataFrame containing telemetry data.
    """
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["m_session_time"], y=df["m_tyres_surface_temperature_rl"], name="RL"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["m_session_time"], y=df["m_tyres_surface_temperature_rr"], name="RR"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["m_session_time"], y=df["m_tyres_surface_temperature_fl"], name="FL"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["m_session_time"], y=df["m_tyres_surface_temperature_fr"], name="FR"
        )
    )
    fig.update_layout(
        yaxis_range=[0, 150],
        title="Tyres Surface Temperature",
        yaxis_title="Temperature (°C)",
        xaxis_title="Session Time (s)",
    )
    return fig


def update_break_temperature(df: DataFrame) -> go.Figure:
    """Create traces in fig for break temperature.

    Args:
        df(DataFrame): DataFrame containing telemetry data.
    """
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df["m_session_time"], y=df["m_brakes_temperature_rl"], name="RL")
    )
    fig.add_trace(
        go.Scatter(x=df["m_session_time"], y=df["m_brakes_temperature_rr"], name="RR")
    )
    fig.add_trace(
        go.Scatter(x=df["m_session_time"], y=df["m_brakes_temperature_fl"], name="FL")
    )
    fig.add_trace(
        go.Scatter(x=df["m_session_time"], y=df["m_brakes_temperature_fr"], name="FR")
    )
    fig.update_layout(
        yaxis_range=[0, 1200],
        title="Brakes Temperature",
        yaxis_title="Temperature (°C)",
        xaxis_title="Session Time (s)",
    )
    return fig


def update_speed(df: DataFrame) -> go.Figure:
    """Create traces in fig for speed.

    Args:
        df(DataFrame): DataFrame containing telemetry data.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["m_session_time"], y=df["m_speed"], name="Speed"))
    fig.update_layout(
        yaxis_range=[0, 400],
        title="Speed",
        yaxis_title="Speed (km/h)",
        xaxis_title="Session Time (s)",
    )
    return fig


def update_brake_throttle(df: DataFrame) -> go.Figure:
    """Create traces in fig for brake and throttle.

    Args:
        df(DataFrame): DataFrame containing telemetry data.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["m_session_time"], y=df["m_brake"], name="Brake"))
    fig.add_trace(
        go.Scatter(x=df["m_session_time"], y=df["m_throttle"], name="Throttle")
    )
    fig.update_layout(
        title="Brake / Throttle",
        yaxis_title="Brake / Throttle (%)",
        xaxis_title="Session Time (s)",
    )
    return fig
