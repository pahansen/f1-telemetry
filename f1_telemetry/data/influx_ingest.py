"""Ingest F1 Telemetry to InfluxDB.
"""
from f1_telemetry.data.udp_stream import get_udp_messages
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import WriteApi, WriteOptions


def dict_to_influx(message_dict: dict, measurement: str, write_api: WriteApi):
    """Take f1 message as dict and write to Influxdb.

    Args:
        message_dict (dict): Packet class as dict.
        measurement (str): Name of influxdb measurement.
    """
    message_dict_wo_tags = message_dict.copy()
    message_dict_wo_tags.pop("m_session_uid")
    point = Point.from_dict(
        {
            "measurement": measurement,
            "tags": {"m_session_uid": message_dict.get("m_session_uid")},
            "fields": message_dict_wo_tags,
            "time": datetime.utcnow(),
        }
    )
    write_api.write("f1_telemetry", "f1", [point], write_precision=WritePrecision.MS)


def run_f1_telemetry_influx() -> None:
    """Run F1 telemetry ingestion.

    Args:
        db_selection (str): Selected db for ingest either influx or adx.
    """
    client = InfluxDBClient(
        url="http://localhost:8086", token="f1_telemetry_token", org="f1_telemetry"
    )
    write_api = client.write_api(write_options=WriteOptions(flush_interval=200))
    for player_data, message_type in get_udp_messages():
        dict_to_influx(player_data, message_type, write_api)
