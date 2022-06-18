"""Handle F1 UDP stream and write data to influx."""
import socket
from typing import Tuple, Union
from f1_telemetry.data.structs import (
    PacketHeader,
    PacketCarTelemetryData,
    PacketLapData,
    PacketCarStatusData,
    PacketCarDamageData,
)
from f1_telemetry.config import F1_UDP_SERVER_ADDRESS, F1_UDP_SERVER_PORT


def get_udp_messages() -> Tuple[
    Union[
        PacketLapData, PacketCarTelemetryData, PacketCarStatusData, PacketCarDamageData
    ],
    str,
]:
    """Get latest telemetry message from udp socket and send to Influxdb.

    Returns:
        Tuple: Telemetry message class and message type.
    """
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
            yield (player_data, packet[1])
