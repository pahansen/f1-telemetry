"""Layout for dash application."""
from threading import Thread

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from pandas import DataFrame
from f1_telemetry.dashboard.components.line_graphs import (
    update_tyre_temperature,
    update_break_temperature,
    update_speed,
    update_brake_throttle,
)
from f1_telemetry.data.udp_stream import get_f1_message


messages = []
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="tyre-surface-temp")),
                dbc.Col(dcc.Graph(id="break-temp")),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="speed")),
                dbc.Col(dcc.Graph(id="break-throttle")),
            ]
        ),
        dcc.Interval(id="telemetry-interval", interval=1 * 1000, n_intervals=0),
    ]
)


@app.callback(
    Output("tyre-surface-temp", "figure"),
    Output("break-temp", "figure"),
    Output("speed", "figure"),
    Output("break-throttle", "figure"),
    Input("telemetry-interval", "n_intervals"),
)
def update_metrics(_):
    """Update telemetry every second."""
    if len(messages) >= 1:
        df = DataFrame(messages)
        return [
            update_tyre_temperature(df),
            update_break_temperature(df),
            update_speed(df),
            update_brake_throttle(df),
        ]
    return None, None, None, None


if __name__ == "__main__":
    udp_thread = Thread(
        target=get_f1_message,
        args=(messages,),
    )
    udp_thread.start()
    app.run_server(debug=False, host="0.0.0.0", port=8050, processes=4, threaded=False)
