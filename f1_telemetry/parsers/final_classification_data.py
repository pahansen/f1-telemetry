import struct
from dataclasses import dataclass

from f1_telemetry.parsers.packet_header import PacketHeader

# Reasonable defaults used elsewhere in the project
cs_maxTyreStints = 8
cs_maxNumCarsInUDPData = 22


@dataclass
class FinalClassificationData:
    m_position: int
    m_numLaps: int
    m_gridPosition: int
    m_points: int
    m_numPitStops: int
    m_resultStatus: int
    m_bestLapTimeInMS: int
    m_totalRaceTime: float
    m_penaltiesTime: int
    m_numPenalties: int
    m_numTyreStints: int
    m_tyreStintsActual: tuple[int, ...]
    m_tyreStintsVisual: tuple[int, ...]
    m_tyreStintsEndLaps: tuple[int, ...]

    # < 6 x uint8, uint32, double, 3 x uint8, 3 arrays of cs_maxTyreStints uint8
    # Use double for total race time (matches packet layout)
    _struct = struct.Struct(
        f"<6BId3B{cs_maxTyreStints}B{cs_maxTyreStints}B{cs_maxTyreStints}B"
    )

    @classmethod
    def from_buffer(cls, buffer: bytes, offset: int = 0):
        unpacked = list(cls._struct.unpack_from(buffer, offset))
        return cls(
            m_position=unpacked[0],
            m_numLaps=unpacked[1],
            m_gridPosition=unpacked[2],
            m_points=unpacked[3],
            m_numPitStops=unpacked[4],
            m_resultStatus=unpacked[5],
            m_bestLapTimeInMS=unpacked[6],
            m_totalRaceTime=unpacked[7],
            m_penaltiesTime=unpacked[8],
            m_numPenalties=unpacked[9],
            m_numTyreStints=unpacked[10],
            m_tyreStintsActual=tuple(unpacked[11 : 11 + cs_maxTyreStints]),
            m_tyreStintsVisual=tuple(
                unpacked[11 + cs_maxTyreStints : 11 + 2 * cs_maxTyreStints]
            ),
            m_tyreStintsEndLaps=tuple(
                unpacked[11 + 2 * cs_maxTyreStints : 11 + 3 * cs_maxTyreStints]
            ),
        )


@dataclass
class PacketFinalClassificationData:
    m_header: PacketHeader
    m_numCars: int
    m_classificationData: list[FinalClassificationData]

    @classmethod
    def from_buffer(cls, buffer: bytes):
        header = PacketHeader.from_buffer(buffer, 0)
        offset = PacketHeader._struct.size

        (m_numCars,) = struct.unpack_from("<B", buffer, offset)
        offset += 1

        cars: list[FinalClassificationData] = []
        for _ in range(cs_maxNumCarsInUDPData):
            car = FinalClassificationData.from_buffer(buffer, offset)
            cars.append(car)
            offset += FinalClassificationData._struct.size

        return cls(header, m_numCars, cars)
