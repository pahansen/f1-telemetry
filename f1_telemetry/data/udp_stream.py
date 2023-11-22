"""Handle F1 UDP stream and write data to influx."""
import socket
from f1_telemetry.data.struct_parsers import *
from f1_telemetry.config import F1_UDP_SERVER_ADDRESS, F1_UDP_SERVER_PORT


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
        #packet_header = PacketHeader.from_binary(message)
        # packet_ids = {
        #     2: (PacketLapData, "lap"),
        #     6: (PacketCarTelemetryData, "car_telemetry"),
        #     7: (PacketCarStatusData, "car_status"),
        #     10: (PacketCarDamageData, "car_damage"),
        # }
        packet_ids = {
            0: parse_packet_motion_data,
            1: parse_packet_session_data,
            2: parse_packet_lap_data,
            4: parse_packet_participants_data,
            5: parse_packet_car_setup_data
        }
        parser = packet_ids.get(packet_header["m_packetId"])
        if parser is not None:
            packet_data = parser(message)
            yield packet_data

        #    if packet is not None:
        #     packet_data = packet[0].from_binary(packet_header, message)
        #     player_data = packet_data.get_player_car_data()
        #     yield (player_data, packet[1])
