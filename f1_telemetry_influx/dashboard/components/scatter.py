"""Collection of different line grpahs that are rendered in app."""
from pandas import DataFrame
from plotly import graph_objects as go


def create_scatter_fig(
    df: DataFrame,
    traces: list,
    title: str,
    yaxis_range: list,
    yaxis_title: str,
    xaxis_title: str,
) -> go.Figure:
    """Generic function to create a scatter plot with multiple traces.

    Args:
        df (DataFrame): DataFrame that contains data that should be visualized.
        traces (list): List of traces containing three attributes per element (x, y, name).
        title (str): Scatter plot title.
        yaxis_range (list): Min, Max values for y axis.
        yaxis_title (str): Title shown on y axis.
        xaxis_title (str): Title shown on x axis.

    Returns:
        go.Figure: Scatter plot based on plotly graph objects.
    """
    fig = go.Figure()
    for trace in traces:
        fig.add_trace(go.Scatter(x=df[trace[0]], y=df[trace[1]], name=trace[2]))
    fig.update_layout(
        yaxis_range=yaxis_range,
        title=title,
        yaxis_title=yaxis_title,
        xaxis_title=xaxis_title,
    )
    return fig


def create_tyre_surface_temperature_plot(df: DataFrame) -> go.Figure:
    """Create scatter plot to visualize tyre surface temperature.

    Args:
        df (DataFrame):  DataFrame that contains data that should be visualized.

    Returns:
        go.Figure: Scatter plot based on plotly graph objects.
    """
    traces = [
        ["_time", "m_tyres_surface_temperature_rl", "RL"],
        ["_time", "m_tyres_surface_temperature_rr", "RR"],
        ["_time", "m_tyres_surface_temperature_fl", "FL"],
        ["_time", "m_tyres_surface_temperature_fr", "FR"],
    ]
    return create_scatter_fig(
        df, traces, "Tyres Surface Temperature", [0, 150], "Temperature (°C)", "Time"
    )


def create_tyre_inner_temperature_plot(df: DataFrame) -> go.Figure:
    """Create scatter plot to visualize tyre inner temperature.

    Args:
        df (DataFrame):  DataFrame that contains data that should be visualized.

    Returns:
        go.Figure: Scatter plot based on plotly graph objects.
    """
    traces = [
        ["_time", "m_tyres_inner_temperature_rl", "RL"],
        ["_time", "m_tyres_inner_temperature_rr", "RR"],
        ["_time", "m_tyres_inner_temperature_fl", "FL"],
        ["_time", "m_tyres_inner_temperature_fr", "FR"],
    ]
    return create_scatter_fig(
        df, traces, "Tyres Inner Temperature", [0, 150], "Temperature (°C)", "Time"
    )


def create_brake_temperature_plot(df: DataFrame) -> go.Figure:
    """Create scatter plot to visualize brake temperature.

    Args:
        df (DataFrame):  DataFrame that contains data that should be visualized.

    Returns:
        go.Figure: Scatter plot based on plotly graph objects.
    """
    traces = [
        ["_time", "m_brakes_temperature_rl", "RL"],
        ["_time", "m_brakes_temperature_rr", "RR"],
        ["_time", "m_brakes_temperature_fl", "FL"],
        ["_time", "m_brakes_temperature_fr", "FR"],
    ]
    return create_scatter_fig(
        df, traces, "Brakes Temperature", [0, 1200], "Temperature (°C)", "Time"
    )


def create_brake_throttle_plot(df: DataFrame) -> go.Figure:
    """Create scatter plot to visualize brake and throttle controls.

    Args:
        df (DataFrame):  DataFrame that contains data that should be visualized.

    Returns:
        go.Figure: Scatter plot based on plotly graph objects.
    """
    traces = [
        ["_time", "m_brake", "Brake"],
        ["_time", "m_throttle", "Throttle"],
    ]
    return create_scatter_fig(df, traces, "Brake / Throttle", [0, 1], "", "Time")
