"""Queries to retrieve data from InfluxDB."""

from influxdb_client import InfluxDBClient


def query_car_telemetry():
    """Query car telemetry from InfluxDB.

    Returns:
        DataFrame: Query result as data frame.
    """
    with InfluxDBClient(
        url="http://localhost:8086", token="f1_telemetry_token", org="f1"
    ) as client:
        query_api = client.query_api()
        data_frame = query_api.query_data_frame(
            """
                    from(bucket: "f1_telemetry")
                |> range(start: -1m)
                |> filter(fn: (r) => r["_measurement"] == "car_telemetry")
                |> aggregateWindow(every: 500ms, fn: last, createEmpty: false)
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                |> yield(name: "last")
            """
        )
    return data_frame
