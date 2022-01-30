"""Struct classes for car telemetry."""
import struct
import ctypes
from dataclasses import dataclass, asdict
from typing import List

PACKET_HEADER_FORMAT = "<HBBBBQfLBB"
PACKET_CAR_TELEMETRY_DATA_FORMAT = "BBb"
CAR_TELEMETRY_DATA_FORMAT = "HfffBbHBBHHHHHBBBBBBBBHffffBBBB"


@dataclass
class PacketHeader:
    """PacketHeader struct."""

    m_packet_format: ctypes.c_uint16
    m_game_major_version: ctypes.c_uint8
    m_game_minor_version: ctypes.c_uint8
    m_packet_version: ctypes.c_uint8
    m_packet_id: ctypes.c_uint8
    m_session_uid: ctypes.c_uint64
    m_session_time: ctypes.c_float
    m_frame_identifier: ctypes.c_uint32
    m_player_car_index: ctypes.c_uint8
    m_secondary_player_car_index: ctypes.c_uint8

    @classmethod
    def from_binary(cls, binary_message: str):
        """Create class form binary UDP package.

        Args:
            binary_message (str): Binary representation of package header.
        """
        format_string = "<HBBBBQfLBB"
        unpacked = struct.unpack_from(format_string, binary_message)
        return cls(
            unpacked[0],
            unpacked[1],
            unpacked[2],
            unpacked[3],
            unpacked[4],
            unpacked[5],
            unpacked[6],
            unpacked[7],
            unpacked[8],
            unpacked[9],
        )


@dataclass
class CarTelemetryData:
    """CarTelemetryData struct."""

    m_speed: ctypes.c_uint16
    m_throttle: ctypes.c_float
    m_steer: ctypes.c_float
    m_brake: ctypes.c_float
    m_clutch: ctypes.c_uint8
    m_gear: ctypes.c_int8
    m_engine_rpm: ctypes.c_uint16
    m_drs: ctypes.c_uint8
    m_rev_lights_percent: ctypes.c_uint8
    m_rev_lights_bit_value: ctypes.c_uint16
    m_brakes_temperature: List[ctypes.c_uint16]
    m_tyres_surface_temperature: List[ctypes.c_uint8]
    m_tyres_inner_temperature: List[ctypes.c_uint8]
    m_engine_temperature: ctypes.c_uint16
    m_tyres_pressure: List[ctypes.c_float]
    m_surface_type: List[ctypes.c_uint8]

    @classmethod
    def from_unpacked(cls, unpacked: List):
        """Parse unpacked struct into class attributes.

        Args:
            unpacked (list): Unpacked struct containing all
                attributes to construct CarTelemetryData class.
        """
        return cls(
            unpacked[0],
            unpacked[1],
            unpacked[2],
            unpacked[3],
            unpacked[4],
            unpacked[5],
            unpacked[6],
            unpacked[7],
            unpacked[8],
            unpacked[9],
            list([unpacked[10], unpacked[11], unpacked[12], unpacked[13]]),
            list([unpacked[14], unpacked[15], unpacked[16], unpacked[17]]),
            list([unpacked[18], unpacked[19], unpacked[20], unpacked[21]]),
            unpacked[22],
            list([unpacked[23], unpacked[24], unpacked[25], unpacked[26]]),
            list([unpacked[27], unpacked[28], unpacked[29], unpacked[30]]),
        )


@dataclass
class PacketCarTelemetryData:
    """PacketCarTelemetryData struct."""

    m_header: PacketHeader
    m_car_telemetry_data: List[CarTelemetryData]
    m_mfd_panel_index: ctypes.c_uint8
    m_mfd_panel_index_secondary_player: ctypes.c_uint8
    m_suggested_gear: ctypes.c_int8

    @classmethod
    def from_binary(cls, packet_header: PacketHeader, binary_message: str):
        """Create class form binary UDP package.

        Args:
            packet_header (PacketHeader): PacketHeader class.
            binary_message (str): Binary representation of struct.
        """
        # Unpack struct
        unpacked = struct.unpack_from(
            PACKET_HEADER_FORMAT
            + "".join(CAR_TELEMETRY_DATA_FORMAT * 22)
            + PACKET_CAR_TELEMETRY_DATA_FORMAT,
            binary_message,
        )
        # Remove header from struct
        unpacked_wo_header = unpacked[len(asdict(packet_header)) : :]

        # Get telemetry for each active car
        car_telemetry_data_list = list()
        for i in range(22):
            car_telemetry_data = CarTelemetryData.from_unpacked(
                unpacked_wo_header[
                    i
                    * len(CAR_TELEMETRY_DATA_FORMAT) : (i + 1)
                    * len(CAR_TELEMETRY_DATA_FORMAT)
                ]
            )
            car_telemetry_data_list.append(car_telemetry_data)

        return cls(
            packet_header,
            car_telemetry_data_list,
            unpacked_wo_header[-3],
            unpacked_wo_header[-2],
            unpacked_wo_header[-1],
        )
