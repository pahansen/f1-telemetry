import struct
from dataclasses import dataclass
from f1_telemetry.parsers.packet_header import PacketHeader


@dataclass
class CarMotionData:
    m_worldPositionX: float
    m_worldPositionY: float
    m_worldPositionZ: float
    m_worldVelocityX: float
    m_worldVelocityY: float
    m_worldVelocityZ: float
    m_worldForwardDirX: int
    m_worldForwardDirY: int
    m_worldForwardDirZ: int
    m_worldRightDirX: int
    m_worldRightDirY: int
    m_worldRightDirZ: int
    m_gForceLateral: float
    m_gForceLongitudinal: float
    m_gForceVertical: float
    m_yaw: float
    m_pitch: float
    m_roll: float

    _struct = struct.Struct("<6f6h6f")

    @classmethod
    def from_buffer(cls, buffer: bytes, offset: int = 0):
        unpacked = cls._struct.unpack_from(buffer, offset)
        return cls(
            m_worldPositionX=unpacked[0],
            m_worldPositionY=unpacked[1],
            m_worldPositionZ=unpacked[2],
            m_worldVelocityX=unpacked[3],
            m_worldVelocityY=unpacked[4],
            m_worldVelocityZ=unpacked[5],
            m_worldForwardDirX=unpacked[6],
            m_worldForwardDirY=unpacked[7],
            m_worldForwardDirZ=unpacked[8],
            m_worldRightDirX=unpacked[9],
            m_worldRightDirY=unpacked[10],
            m_worldRightDirZ=unpacked[11],
            m_gForceLateral=unpacked[12],
            m_gForceLongitudinal=unpacked[13],
            m_gForceVertical=unpacked[14],
            m_yaw=unpacked[15],
            m_pitch=unpacked[16],
            m_roll=unpacked[17],
        )


@dataclass
class PacketMotionData:
    m_header: PacketHeader
    m_carMotionData: list[CarMotionData]

    @classmethod
    def from_buffer(cls, buffer: bytes):
        header = PacketHeader.from_buffer(buffer, 0)
        offset = PacketHeader._struct.size

        cars = []
        for _ in range(22):  # cs_maxNumCarsInUDPData
            car = CarMotionData.from_buffer(buffer, offset)
            cars.append(car)
            offset += CarMotionData._struct.size

        return cls(header, cars)
