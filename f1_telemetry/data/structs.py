"""Struct classes for car telemetry. Classes parse data from binary format and extract player data."""
import struct
import ctypes
from dataclasses import dataclass, asdict
from typing import List

PACKET_HEADER_FORMAT = "<HBBBBQfLBB"
PACKET_CAR_TELEMETRY_DATA_FORMAT = "BBb"
CAR_TELEMETRY_DATA_FORMAT = "HfffBbHBBHHHHHBBBBBBBBHffffBBBB"
LAP_DATA_FORMAT = "LLHHfffBBBBBBBBBBBBBBHHB"
CAR_STATUS_DATA_FORMAT = "BBBBBfffHHBBHBBBbfBfffB"
CAR_DAMAGE_DATA_FORMAT = "ffffBBBBBBBBBBBBBBBBBBBBBBB"


def _telemetry_list_to_attributes(telemetry_values: list, attribute_name: str) -> dict:
    """Get single attributes from attributes list and allocate to position on car (fl, fr, rl, rr).

    Args:
        telemetry_values(list): List of telemetry values that should be mapped to attributes.
        attribute_name(str): Attribute name used as keys in dict.
    """
    car_position_mapping = ["rl", "rr", "fl", "fr"]
    telemetry_values_dict = {}
    for i, telemetry_value in enumerate(telemetry_values):
        key_name = str(attribute_name) + "_" + car_position_mapping[i]
        telemetry_values_dict[key_name] = telemetry_value
    return telemetry_values_dict


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
class PacketWOAdditionalAttributes:
    """PacketCarStatusData struct."""

    m_header: PacketHeader

    @classmethod
    def get_message_list(
        cls,
        packet_header: PacketHeader,
        binary_message: str,
        message_format: str,
        message_type: object,
    ):
        """Create class form binary UDP package.

        Args:
            packet_header (PacketHeader): PacketHeader class.
            binary_message (str): Binary representation of struct.
        """
        # Unpack struct
        unpacked = struct.unpack_from(
            PACKET_HEADER_FORMAT + "".join(message_format * 22),
            binary_message,
        )
        # Remove header from struct
        unpacked_wo_header = unpacked[len(asdict(packet_header)) : :]

        # Get lap data for each active car
        data_list = list()
        for i in range(22):
            data = message_type.from_unpacked(
                unpacked_wo_header[
                    i * len(message_format) : (i + 1) * len(message_format)
                ]
            )
            data_list.append(data)

        return data_list


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

    def get_player_car_data(self) -> dict:
        """Get data from player car."""
        player_car_index = self.m_header.m_player_car_index
        player_car_telemetry = self.m_car_telemetry_data[player_car_index]
        player_telemetry_message = (
            self.m_header.__dict__ | player_car_telemetry.__dict__.copy()
        )
        # Map tyre temperature values from list to attributes
        player_telemetry_message = (
            player_telemetry_message
            | _telemetry_list_to_attributes(
                player_telemetry_message["m_tyres_surface_temperature"],
                "m_tyres_surface_temperature",
            )
        )
        player_telemetry_message.pop("m_tyres_surface_temperature")
        # Map tyre inner temperature values from list to attributes
        player_telemetry_message = (
            player_telemetry_message
            | _telemetry_list_to_attributes(
                player_telemetry_message["m_tyres_inner_temperature"],
                "m_tyres_inner_temperature",
            )
        )
        player_telemetry_message.pop("m_tyres_inner_temperature")
        # Map brake temperature values from list to attributes
        player_telemetry_message = (
            player_telemetry_message
            | _telemetry_list_to_attributes(
                player_telemetry_message["m_brakes_temperature"],
                "m_brakes_temperature",
            )
        )
        player_telemetry_message.pop("m_brakes_temperature")
        # Map tyres pressure values from list to attributes
        player_telemetry_message = (
            player_telemetry_message
            | _telemetry_list_to_attributes(
                player_telemetry_message["m_tyres_pressure"],
                "m_tyres_pressure",
            )
        )
        player_telemetry_message.pop("m_tyres_pressure")
        player_telemetry_message.pop("m_surface_type")

        return player_telemetry_message


@dataclass
class LapData:
    """LapData struct."""

    m_lastLapTimeInMS: ctypes.c_uint32
    m_currentLapTimeInMS: ctypes.c_uint32
    m_sector1TimeInMS: ctypes.c_uint16
    m_sector2TimeInMS: ctypes.c_uint16
    m_lapDistance: ctypes.c_uint32
    m_currentLapNum: ctypes.c_uint8

    @classmethod
    def from_unpacked(cls, unpacked: List):
        """Parse unpacked struct into class attributes.

        Args:
            unpacked (list): Unpacked struct containing all
                attributes to construct CarTelemetryData class.
        """
        return cls(
            unpacked[0], unpacked[1], unpacked[2], unpacked[3], unpacked[4], unpacked[8]
        )


@dataclass
class PacketLapData(PacketWOAdditionalAttributes):
    """PacketCarTelemetryData struct."""

    m_lap_data: List[LapData]

    @classmethod
    def from_binary(cls, packet_header: PacketHeader, binary_message: str):
        """Create class form binary UDP package.

        Args:
            packet_header (PacketHeader): PacketHeader class.
            binary_message (str): Binary representation of struct.
        """
        lap_data_list = cls.get_message_list(
            packet_header, binary_message, LAP_DATA_FORMAT, LapData
        )
        return cls(packet_header, lap_data_list)

    def get_player_car_data(self) -> dict:
        """Get data from player car."""
        player_car_index = self.m_header.m_player_car_index
        player_values = (
            self.m_header.__dict__ | self.m_lap_data[player_car_index].__dict__.copy()
        )
        return player_values


@dataclass
class CarStatusData:
    """CarStatusData struct."""

    m_fuelInTank: ctypes.c_float
    m_fuelCapacity: ctypes.c_float
    m_fuelRemainingLaps: ctypes.c_float
    m_actualTyreCompound: ctypes.c_uint8
    m_tyresAgeLaps: ctypes.c_uint8
    m_ersStoreEnergy: ctypes.c_float
    m_ersDeployMode: ctypes.c_uint8
    m_ersHarvestedThisLapMGUK: ctypes.c_float
    m_ersHarvestedThisLapMGUH: ctypes.c_float
    m_ersDeployedThisLap: ctypes.c_float

    @classmethod
    def from_unpacked(cls, unpacked: List):
        """Parse unpacked struct into class attributes.

        Args:
            unpacked (list): Unpacked struct containing all
                attributes to construct CarTelemetryData class.
        """
        return cls(
            unpacked[5],
            unpacked[6],
            unpacked[7],
            unpacked[13],
            unpacked[15],
            unpacked[17],
            unpacked[18],
            unpacked[19],
            unpacked[20],
            unpacked[21],
        )


@dataclass
class PacketCarStatusData(PacketWOAdditionalAttributes):
    """PacketCarStatusData struct."""

    m_carStatusData: List[CarStatusData]

    @classmethod
    def from_binary(cls, packet_header: PacketHeader, binary_message: str):
        """Create class form binary UDP package.

        Args:
            packet_header (PacketHeader): PacketHeader class.
            binary_message (str): Binary representation of struct.
        """
        car_status_data_list = cls.get_message_list(
            packet_header, binary_message, CAR_STATUS_DATA_FORMAT, CarStatusData
        )
        return cls(packet_header, car_status_data_list)

    def get_player_car_data(self) -> dict:
        """Get data from player car."""
        player_car_index = self.m_header.m_player_car_index
        player_values = (
            self.m_header.__dict__
            | self.m_carStatusData[player_car_index].__dict__.copy()
        )
        return player_values


@dataclass
class CarDamageData:
    """CarStatusData struct."""

    m_tyresWear: ctypes.c_float
    m_tyresDamage: ctypes.c_uint8
    m_brakesDamage: ctypes.c_uint8

    @classmethod
    def from_unpacked(cls, unpacked: List):
        """Parse unpacked struct into class attributes.

        Args:
            unpacked (list): Unpacked struct containing all
                attributes to construct CarTelemetryData class.
        """
        return cls(
            list([unpacked[0], unpacked[1], unpacked[2], unpacked[3]]),
            list([unpacked[4], unpacked[5], unpacked[6], unpacked[7]]),
            list([unpacked[8], unpacked[9], unpacked[10], unpacked[11]]),
        )


@dataclass
class PacketCarDamageData(PacketWOAdditionalAttributes):
    """PacketCarStatusData struct."""

    m_carDamageData: List[CarDamageData]

    @classmethod
    def from_binary(cls, packet_header: PacketHeader, binary_message: str):
        """Create class form binary UDP package.

        Args:
            packet_header (PacketHeader): PacketHeader class.
            binary_message (str): Binary representation of struct.
        """
        car_damage_data_list = cls.get_message_list(
            packet_header, binary_message, CAR_DAMAGE_DATA_FORMAT, CarDamageData
        )
        return cls(packet_header, car_damage_data_list)

    def get_player_car_data(self) -> dict:
        """Get data from player car."""
        player_car_index = self.m_header.m_player_car_index
        player_car_damage = self.m_carDamageData[player_car_index]
        player_car_damage_message = (
            self.m_header.__dict__ | player_car_damage.__dict__.copy()
        )
        # Map tyre wear values from list to attributes
        player_car_damage_message = (
            player_car_damage_message
            | _telemetry_list_to_attributes(
                player_car_damage_message["m_tyresWear"],
                "m_tyresWear",
            )
        )
        player_car_damage_message.pop("m_tyresWear")
        # Map tyre damage values from list to attributes
        player_car_damage_message = (
            player_car_damage_message
            | _telemetry_list_to_attributes(
                player_car_damage_message["m_tyresDamage"],
                "m_tyresDamage",
            )
        )
        player_car_damage_message.pop("m_tyresDamage")
        # Map brake damage values from list to attributes
        player_car_damage_message = (
            player_car_damage_message
            | _telemetry_list_to_attributes(
                player_car_damage_message["m_brakesDamage"],
                "m_brakesDamage",
            )
        )
        player_car_damage_message.pop("m_brakesDamage")

        return player_car_damage_message
