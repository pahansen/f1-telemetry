import struct
from dataclasses import dataclass
@dataclass
class PacketHeader:
    m_packetFormat: int
    m_gameYear: int
    m_gameMajorVersion: int
    m_gameMinorVersion: int
    m_packetVersion: int
    m_packetId: int
    m_sessionUID: int
    m_sessionTime: float
    m_frameIdentifier: int
    m_overallFrameIdentifier: int
    m_playerCarIndex: int
    m_secondaryPlayerCarIndex: int

    _struct = struct.Struct("<HBBBBBQfIIBB")

    @classmethod
    def from_buffer(cls, buffer: bytes, offset: int = 0):
        values = cls._struct.unpack_from(buffer, offset)
        return cls(*values)
