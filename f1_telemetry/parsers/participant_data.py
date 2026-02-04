import struct
from dataclasses import dataclass

from f1_telemetry.parsers.packet_header import PacketHeader

CS_MAX_PARTICIPANT_NAME_LEN = 48
CS_MAX_CARS = 22


@dataclass
class ParticipantData:
    m_aiControlled: int
    m_driverId: int
    m_networkId: int
    m_teamId: int
    m_myTeam: int
    m_raceNumber: int
    m_nationality: int
    m_name: str
    m_yourTelemetry: int
    m_showOnlineNames: int
    m_platform: int

    _struct = struct.Struct("<BBBBBBB48sBBB")

    @classmethod
    def from_buffer(cls, buffer: bytes, offset: int):
        unpacked = cls._struct.unpack_from(buffer, offset)
        name = unpacked[7].split(b"\x00", 1)[0].decode("utf-8", errors="replace")

        return cls(
            m_aiControlled=unpacked[0],
            m_driverId=unpacked[1],
            m_networkId=unpacked[2],
            m_teamId=unpacked[3],
            m_myTeam=unpacked[4],
            m_raceNumber=unpacked[5],
            m_nationality=unpacked[6],
            m_name=name,
            m_yourTelemetry=unpacked[8],
            m_showOnlineNames=unpacked[9],
            m_platform=unpacked[10],
        )


@dataclass
class PacketParticipantsData:
    m_header: PacketHeader
    m_numActiveCars: int
    m_participants: list[ParticipantData]

    @classmethod
    def from_buffer(cls, buffer: bytes):
        header = PacketHeader.from_buffer(buffer, 0)
        offset = PacketHeader._struct.size
        (num_active_cars,) = struct.unpack_from("<B", buffer, offset)
        offset += 1

        participants = []
        for _ in range(num_active_cars):
            participants.append(ParticipantData.from_buffer(buffer, offset))
            offset += ParticipantData._struct.size - 1

        return cls(header, num_active_cars, participants)
