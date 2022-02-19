"""Handle F1 UDP stream and write data to influx."""
import socket
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import WriteOptions
from f1_telemetry_influx.data.structs import (
    PacketHeader,
    PacketCarTelemetryData,
    PacketLapData,
    PacketCarStatusData,
    PacketCarDamageData,
)
from f1_telemetry_influx.config import F1_UDP_SERVER_ADDRESS, F1_UDP_SERVER_PORT

# Create client on start up
client = InfluxDBClient(
    url="http://localhost:8086", token="f1_telemetry_token", org="f1_telemetry"
)
write_api = client.write_api(write_options=WriteOptions(flush_interval=200))


def dict_to_influx(message_dict: dict, measurement: str):
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


def udp_to_influx():
    """Get latest telemetry message from udp socket and send to Influxdb."""
    server_address = (F1_UDP_SERVER_ADDRESS, F1_UDP_SERVER_PORT)
    f1_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    f1_udp_socket.bind(server_address)

    while True:
        message, _ = f1_udp_socket.recvfrom(2000)
        packet_header = PacketHeader.from_binary(message)
        packet_ids = {
            2: (PacketLapData, "lap"),
            6: (PacketCarTelemetryData, "car_telemetry"),
            7: (PacketCarStatusData, "car_status"),
            10: (PacketCarDamageData, "car_damage"),
        }
        packet = packet_ids.get(packet_header.m_packet_id)

        if packet is not None:
            packet_data = packet[0].from_binary(packet_header, message)
            player_data = packet_data.get_player_car_data()
            # Write message to influx
            dict_to_influx(player_data, packet[1])
