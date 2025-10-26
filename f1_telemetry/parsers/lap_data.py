import struct
from dataclasses import dataclass

from f1_telemetry.parsers.packet_header import PacketHeader


@dataclass
class LapData:
    m_lastLapTimeInMS: int
    m_currentLapTimeInMS: int
    m_sector1TimeMSPart: int
    m_sector1TimeMinutesPart: int
    m_sector2TimeMSPart: int
    m_sector2TimeMinutesPart: int
    m_deltaToCarInFrontMSPart: int
    m_deltaToCarInFrontMinutesPart: int
    m_deltaToRaceLeaderMSPart: int
    m_deltaToRaceLeaderMinutesPart: int
    m_lapDistance: float
    m_totalDistance: float
    m_safetyCarDelta: float
    m_carPosition: int
    m_currentLapNum: int
    m_pitStatus: int
    m_numPitStops: int
    m_sector: int
    m_currentLapInvalid: int
    m_penalties: int
    m_totalWarnings: int
    m_cornerCuttingWarnings: int
    m_numUnservedDriveThroughPens: int
    m_numUnservedStopGoPens: int
    m_gridPosition: int
    m_driverStatus: int
    m_resultStatus: int
    m_pitLaneTimerActive: int
    m_pitLaneTimeInLaneInMS: int
    m_pitStopTimerInMS: int
    m_pitStopShouldServePen: int
    m_speedTrapFastestSpeed: float
    m_speedTrapFastestLap: int

    # ✅ Correct struct format (34 values)
    _struct = struct.Struct("<IIHBHBHBHBfffBBBBBBBBBBBBBBBHHBfB"            
    )

    @classmethod
    def from_buffer(cls, buffer: bytes, offset: int = 0):
        unpacked = cls._struct.unpack_from(buffer, offset)
        return cls(*unpacked)


@dataclass
class PacketLapData:
    m_header: PacketHeader
    m_lapData: list[LapData]
    m_timeTrialPBCarIdx: int
    m_timeTrialRivalCarIdx: int

    @classmethod
    def from_buffer(cls, buffer: bytes):
        header = PacketHeader.from_buffer(buffer, 0)
        offset = PacketHeader._struct.size

        lap_data_list = []
        for _ in range(22):  # one entry per car
            lap = LapData.from_buffer(buffer, offset)
            lap_data_list.append(lap)
            offset += LapData._struct.size

        m_timeTrialPBCarIdx, m_timeTrialRivalCarIdx = struct.unpack_from("<BB", buffer, offset)

        return cls(header, lap_data_list, m_timeTrialPBCarIdx, m_timeTrialRivalCarIdx)
