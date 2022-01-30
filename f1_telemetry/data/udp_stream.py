"""Handle F1 UDP stream.
"""
import socket
from f1_telemetry.data.telemetry import PacketHeader, PacketCarTelemetryData
from f1_telemetry.config import F1_UDP_SERVER_ADDRESS, F1_UDP_SERVER_PORT
from f1_telemetry.data.transformations import get_play_car_telemetry


def get_f1_message(messages: list):
    """Get latest telemetry message from udp socket and append to message buffer.

    Args:
        messages (list): Shared list of messages between dahboard and udp thread.
    """
    server_address = (F1_UDP_SERVER_ADDRESS, F1_UDP_SERVER_PORT)
    f1_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    f1_udp_socket.bind(server_address)

    while True:
        packet_telemetry = None
        while packet_telemetry is None:
            message, _ = f1_udp_socket.recvfrom(2000)
            packet_header = PacketHeader.from_binary(message)
            if packet_header.m_packet_id == 6:
                packet_car_telemetry_data = PacketCarTelemetryData.from_binary(
                    packet_header, message
                )
                player_telemetry = get_play_car_telemetry(packet_car_telemetry_data)
                messages.append(player_telemetry)
                packet_telemetry = packet_car_telemetry_data
        # Temporary buffer size of list to limit the amount of data that needs to be processed
        if len(messages) > 500:
            messages.pop(0)
