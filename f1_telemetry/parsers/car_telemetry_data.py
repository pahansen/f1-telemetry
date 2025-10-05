import struct
from dataclasses import dataclass
from typing import Any, Dict, Type

from f1_telemetry.parsers.packet_header import PacketHeader

@dataclass
class CarTelemetryData:
    m_speed: int
    m_throttle: float
    m_steer: float
    m_brake: float
    m_clutch: int
    m_gear: int
    m_engineRPM: int
    m_drs: int
    m_revLightsPercent: int
    m_revLightsBitValue: int
    m_brakesTemperature: tuple[int, int, int, int]
    m_tyresSurfaceTemperature: tuple[int, int, int, int]
    m_tyresInnerTemperature: tuple[int, int, int, int]
    m_engineTemperature: int
    m_tyresPressure: tuple[float, float, float, float]
    m_surfaceType: tuple[int, int, int, int]

    _struct = struct.Struct("<HfffBbHBBH4H4B4BH4f4B")

    @classmethod
    def from_buffer(cls, buffer: bytes, offset: int = 0):
        unpacked = list(cls._struct.unpack_from(buffer, offset))
        return cls(
            m_speed=unpacked[0],
            m_throttle=unpacked[1],
            m_steer=unpacked[2],
            m_brake=unpacked[3],
            m_clutch=unpacked[4],
            m_gear=unpacked[5],
            m_engineRPM=unpacked[6],
            m_drs=unpacked[7],
            m_revLightsPercent=unpacked[8],
            m_revLightsBitValue=unpacked[9],
            m_brakesTemperature=tuple(unpacked[10:14]),
            m_tyresSurfaceTemperature=tuple(unpacked[14:18]),
            m_tyresInnerTemperature=tuple(unpacked[18:22]),
            m_engineTemperature=unpacked[22],
            m_tyresPressure=tuple(unpacked[23:27]),
            m_surfaceType=tuple(unpacked[27:31]),
        )


@dataclass
class PacketCarTelemetryData:
    m_header: PacketHeader
    m_carTelemetryData: list[CarTelemetryData]
    m_mfdPanelIndex: int
    m_mfdPanelIndexSecondaryPlayer: int
    m_suggestedGear: int

    @classmethod
    def from_buffer(cls, buffer: bytes):
        header = PacketHeader.from_buffer(buffer, 0)
        offset = PacketHeader._struct.size

        cars = []
        for _ in range(22):  # cs_maxNumCarsInUDPData
            car = CarTelemetryData.from_buffer(buffer, offset)
            cars.append(car)
            offset += CarTelemetryData._struct.size

        mfd_panel, mfd_secondary, suggested_gear = struct.unpack_from("<BBb", buffer, offset)

        return cls(header, cars, mfd_panel, mfd_secondary, suggested_gear)
