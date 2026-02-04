import struct
from dataclasses import dataclass
from typing import List

from .packet_header import PacketHeader

MAX_MARSHALS_ZONE_PER_LAP = 21
MAX_WEATHER_FORECAST_SAMPLES = 64
MAX_SESSIONS_IN_WEEKEND = 12


@dataclass
class MarshalZone:
    zone_start: float
    zone_flag: int

    _struct = struct.Struct("<fb")

    @classmethod
    def from_buffer(cls, buffer: bytes, offset: int = 0) -> "MarshalZone":
        unpacked = cls._struct.unpack_from(buffer, offset)
        return cls(*unpacked)


@dataclass
class WeatherForecastSample:
    session_type: int
    time_offset: int
    weather: int
    track_temperature: int
    track_temperature_change: int
    air_temperature: int
    air_temperature_change: int
    rain_percentage: int

    _struct = struct.Struct("<BBBbbbbB")

    @classmethod
    def from_buffer(cls, buffer: bytes, offset: int = 0) -> "WeatherForecastSample":
        unpacked = cls._struct.unpack_from(buffer, offset)
        return cls(*unpacked)


@dataclass
class PacketSessionData:
    m_header: PacketHeader
    m_weather: int
    m_trackTemperature: int
    m_airTemperature: int
    m_totalLaps: int
    m_trackLength: int
    m_sessionType: int
    m_trackId: int
    m_formula: int
    m_sessionTimeLeft: int
    m_sessionDuration: int
    m_pitSpeedLimit: int
    m_gamePaused: int
    m_isSpectating: int
    m_spectatorCarIndex: int
    m_sliProNativeSupport: int
    m_numMarshalZones: int
    m_marshalZones: List[MarshalZone]
    m_safetyCarStatus: int
    m_networkGame: int
    m_numWeatherForecastSamples: int
    m_weatherForecastSamples: List[WeatherForecastSample]
    m_forecastAccuracy: int
    m_aiDifficulty: int
    m_seasonLinkIdentifier: int
    m_weekendLinkIdentifier: int
    m_sessionLinkIdentifier: int
    m_pitStopWindowIdealLap: int
    m_pitStopWindowLatestLap: int
    m_pitStopRejoinPosition: int
    m_steeringAssist: int
    m_brakingAssist: int
    m_gearboxAssist: int
    m_pitAssist: int
    m_pitReleaseAssist: int
    m_ersAssist: int
    m_drsAssist: int
    m_dynamicRacingLine: int
    m_dynamicRacingLineType: int
    m_gameMode: int
    m_ruleSet: int
    m_timeOfDay: int
    m_sessionLength: int
    m_speedUnitsLeadPlayer: int
    m_temperatureUnitsLeadPlayer: int
    m_speedUnitsSecondaryPlayer: int
    m_temperatureUnitsSecondaryPlayer: int
    m_numSafetyCarPeriods: int
    m_numVirtualSafetyCarPeriods: int
    m_numRedFlagPeriods: int
    m_equalCarPerformance: int
    m_recoveryMode: int
    m_flashbackLimit: int
    m_surfaceType: int
    m_lowFuelMode: int
    m_raceStarts: int
    m_tyreTemperature: int
    m_pitLaneTyreSim: int
    m_carDamage: int
    m_carDamageRate: int
    m_collisions: int
    m_collisionsOffForFirstLapOnly: int
    m_mpUnsafePitRelease: int
    m_mpOffForGriefing: int
    m_cornerCuttingStringency: int
    m_parcFermeRules: int
    m_pitStopExperience: int
    m_safetyCar: int
    m_safetyCarExperience: int
    m_formationLap: int
    m_formationLapExperience: int
    m_redFlags: int
    m_affectsLicenceLevelSolo: int
    m_affectsLicenceLevelMP: int
    m_numSessionsInWeekend: int
    m_weekendStructure: List[int]
    m_sector2LapDistanceStart: float
    m_sector3LapDistanceStart: float

    @classmethod
    def from_buffer(cls, buffer: bytes) -> "PacketSessionData":
        offset = 0
        m_header = PacketHeader.from_buffer(buffer, offset)
        offset += PacketHeader._struct.size

        fmt1 = "<BbbBHBbBHHBBBBBB"
        (
            m_weather,
            m_trackTemperature,
            m_airTemperature,
            m_totalLaps,
            m_trackLength,
            m_sessionType,
            m_trackId,
            m_formula,
            m_sessionTimeLeft,
            m_sessionDuration,
            m_pitSpeedLimit,
            m_gamePaused,
            m_isSpectating,
            m_spectatorCarIndex,
            m_sliProNativeSupport,
            m_numMarshalZones,
        ) = struct.unpack_from(fmt1, buffer, offset)
        offset += struct.calcsize(fmt1)

        m_marshalZones = []
        for _ in range(m_numMarshalZones):
            mz = MarshalZone.from_buffer(buffer, offset)
            m_marshalZones.append(mz)
            offset += MarshalZone._struct.size
        offset += (
            MAX_MARSHALS_ZONE_PER_LAP - m_numMarshalZones
        ) * MarshalZone._struct.size

        m_safetyCarStatus, m_networkGame, m_numWeatherForecastSamples = (
            struct.unpack_from("<BBB", buffer, offset)
        )
        offset += 3

        m_weatherForecastSamples = []
        for _ in range(m_numWeatherForecastSamples):
            ws = WeatherForecastSample.from_buffer(buffer, offset)
            m_weatherForecastSamples.append(ws)
            offset += WeatherForecastSample._struct.size
        offset += (
            MAX_WEATHER_FORECAST_SAMPLES - m_numWeatherForecastSamples
        ) * WeatherForecastSample._struct.size

        fmt3 = "<BBIII" + ("B" * 14) + "I" + ("B" * 33)
        tail = struct.unpack_from(fmt3, buffer, offset)

        idx = 0
        m_forecastAccuracy = tail[idx]
        idx += 1
        m_aiDifficulty = tail[idx]
        idx += 1
        m_seasonLinkIdentifier = tail[idx]
        idx += 1
        m_weekendLinkIdentifier = tail[idx]
        idx += 1
        m_sessionLinkIdentifier = tail[idx]
        idx += 1

        (
            m_pitStopWindowIdealLap,
            m_pitStopWindowLatestLap,
            m_pitStopRejoinPosition,
            m_steeringAssist,
            m_brakingAssist,
            m_gearboxAssist,
            m_pitAssist,
            m_pitReleaseAssist,
            m_ersAssist,
            m_drsAssist,
            m_dynamicRacingLine,
            m_dynamicRacingLineType,
            m_gameMode,
            m_ruleSet,
        ) = tail[idx : idx + 14]
        idx += 14

        m_timeOfDay = tail[idx]
        idx += 1

        (
            m_sessionLength,
            m_speedUnitsLeadPlayer,
            m_temperatureUnitsLeadPlayer,
            m_speedUnitsSecondaryPlayer,
            m_temperatureUnitsSecondaryPlayer,
            m_numSafetyCarPeriods,
            m_numVirtualSafetyCarPeriods,
            m_numRedFlagPeriods,
            m_equalCarPerformance,
            m_recoveryMode,
            m_flashbackLimit,
            m_surfaceType,
            m_lowFuelMode,
            m_raceStarts,
            m_tyreTemperature,
            m_pitLaneTyreSim,
            m_carDamage,
            m_carDamageRate,
            m_collisions,
            m_collisionsOffForFirstLapOnly,
            m_mpUnsafePitRelease,
            m_mpOffForGriefing,
            m_cornerCuttingStringency,
            m_parcFermeRules,
            m_pitStopExperience,
            m_safetyCar,
            m_safetyCarExperience,
            m_formationLap,
            m_formationLapExperience,
            m_redFlags,
            m_affectsLicenceLevelSolo,
            m_affectsLicenceLevelMP,
            m_numSessionsInWeekend,
        ) = tail[idx : idx + 33]

        offset += struct.calcsize(fmt3)

        m_weekendStructure = list(struct.unpack_from("<12B", buffer, offset))
        m_weekendStructure = m_weekendStructure[:m_numSessionsInWeekend]
        offset += MAX_SESSIONS_IN_WEEKEND

        m_sector2LapDistanceStart, m_sector3LapDistanceStart = struct.unpack_from(
            "<ff", buffer, offset
        )

        return cls(
            m_header=m_header,
            m_weather=m_weather,
            m_trackTemperature=m_trackTemperature,
            m_airTemperature=m_airTemperature,
            m_totalLaps=m_totalLaps,
            m_trackLength=m_trackLength,
            m_sessionType=m_sessionType,
            m_trackId=m_trackId,
            m_formula=m_formula,
            m_sessionTimeLeft=m_sessionTimeLeft,
            m_sessionDuration=m_sessionDuration,
            m_pitSpeedLimit=m_pitSpeedLimit,
            m_gamePaused=m_gamePaused,
            m_isSpectating=m_isSpectating,
            m_spectatorCarIndex=m_spectatorCarIndex,
            m_sliProNativeSupport=m_sliProNativeSupport,
            m_numMarshalZones=m_numMarshalZones,
            m_marshalZones=m_marshalZones,
            m_safetyCarStatus=m_safetyCarStatus,
            m_networkGame=m_networkGame,
            m_numWeatherForecastSamples=m_numWeatherForecastSamples,
            m_weatherForecastSamples=m_weatherForecastSamples,
            m_forecastAccuracy=m_forecastAccuracy,
            m_aiDifficulty=m_aiDifficulty,
            m_seasonLinkIdentifier=m_seasonLinkIdentifier,
            m_weekendLinkIdentifier=m_weekendLinkIdentifier,
            m_sessionLinkIdentifier=m_sessionLinkIdentifier,
            m_pitStopWindowIdealLap=m_pitStopWindowIdealLap,
            m_pitStopWindowLatestLap=m_pitStopWindowLatestLap,
            m_pitStopRejoinPosition=m_pitStopRejoinPosition,
            m_steeringAssist=m_steeringAssist,
            m_brakingAssist=m_brakingAssist,
            m_gearboxAssist=m_gearboxAssist,
            m_pitAssist=m_pitAssist,
            m_pitReleaseAssist=m_pitReleaseAssist,
            m_ersAssist=m_ersAssist,
            m_drsAssist=m_drsAssist,
            m_dynamicRacingLine=m_dynamicRacingLine,
            m_dynamicRacingLineType=m_dynamicRacingLineType,
            m_gameMode=m_gameMode,
            m_ruleSet=m_ruleSet,
            m_timeOfDay=m_timeOfDay,
            m_sessionLength=m_sessionLength,
            m_speedUnitsLeadPlayer=m_speedUnitsLeadPlayer,
            m_temperatureUnitsLeadPlayer=m_temperatureUnitsLeadPlayer,
            m_speedUnitsSecondaryPlayer=m_speedUnitsSecondaryPlayer,
            m_temperatureUnitsSecondaryPlayer=m_temperatureUnitsSecondaryPlayer,
            m_numSafetyCarPeriods=m_numSafetyCarPeriods,
            m_numVirtualSafetyCarPeriods=m_numVirtualSafetyCarPeriods,
            m_numRedFlagPeriods=m_numRedFlagPeriods,
            m_equalCarPerformance=m_equalCarPerformance,
            m_recoveryMode=m_recoveryMode,
            m_flashbackLimit=m_flashbackLimit,
            m_surfaceType=m_surfaceType,
            m_lowFuelMode=m_lowFuelMode,
            m_raceStarts=m_raceStarts,
            m_tyreTemperature=m_tyreTemperature,
            m_pitLaneTyreSim=m_pitLaneTyreSim,
            m_carDamage=m_carDamage,
            m_carDamageRate=m_carDamageRate,
            m_collisions=m_collisions,
            m_collisionsOffForFirstLapOnly=m_collisionsOffForFirstLapOnly,
            m_mpUnsafePitRelease=m_mpUnsafePitRelease,
            m_mpOffForGriefing=m_mpOffForGriefing,
            m_cornerCuttingStringency=m_cornerCuttingStringency,
            m_parcFermeRules=m_parcFermeRules,
            m_pitStopExperience=m_pitStopExperience,
            m_safetyCar=m_safetyCar,
            m_safetyCarExperience=m_safetyCarExperience,
            m_formationLap=m_formationLap,
            m_formationLapExperience=m_formationLapExperience,
            m_redFlags=m_redFlags,
            m_affectsLicenceLevelSolo=m_affectsLicenceLevelSolo,
            m_affectsLicenceLevelMP=m_affectsLicenceLevelMP,
            m_numSessionsInWeekend=m_numSessionsInWeekend,
            m_weekendStructure=m_weekendStructure,
            m_sector2LapDistanceStart=m_sector2LapDistanceStart,
            m_sector3LapDistanceStart=m_sector3LapDistanceStart,
        )
