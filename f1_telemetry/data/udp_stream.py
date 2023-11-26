"""Handle F1 UDP stream and write data to influx."""
import socket
from f1_telemetry.data.struct_parsers import *
from dotenv import load_dotenv
import os

load_dotenv()

F1_UDP_SERVER_ADDRESS = str(os.environ.get("F1_UDP_SERVER_ADDRESS", "127.0.0.1"))
F1_UDP_SERVER_PORT = int(os.environ.get("F1_UDP_SERVER_PORT", 20777))


def get_udp_messages() -> dict:
    """Get latest telemetry message from udp socket and send to Influxdb.

    Returns:
        Tuple: Telemetry message class and message type.
    """
    server_address = (F1_UDP_SERVER_ADDRESS, F1_UDP_SERVER_PORT)
    f1_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    f1_udp_socket.bind(server_address)

    while True:
        message, _ = f1_udp_socket.recvfrom(2048)
        packet_header = parse_packet_header(message)

        packet_ids = {
            0: parse_packet_motion_data,
            1: parse_packet_session_data,
            2: parse_packet_lap_data,
            4: parse_packet_participants_data,
            5: parse_packet_car_setup_data,
            6: parse_packet_car_telemetry_data,
            7: parse_packet_car_status_data,
            8: parse_packet_final_classification_data,
            10: parse_packet_car_damage_data,
            12: parse_packet_tyre_sets_data
        }
        parser = packet_ids.get(packet_header["m_packetId"])
        if parser is not None:
            packet_data = parser(message)
            yield packet_data
