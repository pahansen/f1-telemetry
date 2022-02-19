"""Layout for dash application."""
from threading import Thread
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from plotly import graph_objects as go
from f1_telemetry_influx.data.queries import query_car_telemetry
from f1_telemetry_influx.data.udp_to_influx import udp_to_influx
from f1_telemetry_influx.dashboard.components import scatter


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="m-tyres-surface-temperature")),
                dbc.Col(dcc.Graph(id="m-tyres-inner-temperature")),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="m-brakes-temperature")),
                dbc.Col(dcc.Graph(id="m-brake-throttle")),
            ]
        ),
        dcc.Interval(id="telemetry-interval", interval=500),
    ]
)


@app.callback(
    Output("m-tyres-surface-temperature", "figure"),
    Output("m-tyres-inner-temperature", "figure"),
    Output("m-brakes-temperature", "figure"),
    Output("m-brake-throttle", "figure"),
    Input("telemetry-interval", "n_intervals"),
)
def update_car_telemetry(_):
    """Update car telemetry every second."""
    df = query_car_telemetry()
    if df.empty:
        return go.Figure(), go.Figure(), go.Figure(), go.Figure()
    else:
        return [
            scatter.create_tyre_surface_temperature_plot(df),
            scatter.create_tyre_inner_temperature_plot(df),
            scatter.create_brake_temperature_plot(df),
            scatter.create_brake_throttle_plot(df),
        ]


if __name__ == "__main__":
    # Run udp_to_influx on seperate thread
    udp_thread = Thread(
        target=udp_to_influx,
    )
    udp_thread.start()
    # Start dashboard
    app.run_server(debug=False, host="0.0.0.0", port=8050)
