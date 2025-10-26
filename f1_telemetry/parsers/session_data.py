import struct
from dataclasses import dataclass
from typing import List

from .packet_header import PacketHeader

# Constants as defined in the telemetry specification
MAX_MARSHALS_ZONE_PER_LAP = 21
MAX_WEATHER_FORECAST_SAMPLES = 64
MAX_SESSIONS_IN_WEEKEND = 12

@dataclass
class MarshalZone:
    """Represents a marshal zone on the track."""
    zone_start: float  # Fraction (0..1) of way through the lap the marshal zone starts
    zone_flag: int    # -1 = invalid/unknown, 0 = none, 1 = green, 2 = blue, 3 = yellow

    _struct = struct.Struct("<fb")  # float for zone_start, int8 for zone_flag

    @classmethod
    def from_buffer(cls, buffer: bytes, offset: int = 0) -> 'MarshalZone':
        """Unpack a MarshalZone from a buffer."""
        unpacked = cls._struct.unpack_from(buffer, offset)
        return cls(*unpacked)


@dataclass
class WeatherForecastSample:
    """Represents a weather forecast sample for a session."""
    session_type: int           # 0 = unknown, see appendix
    time_offset: int           # Time in minutes the forecast is for
    weather: int               # Weather - 0 = clear, 1 = light cloud, 2 = overcast, 3 = light rain, 4 = heavy rain, 5 = storm
    track_temperature: int     # Track temp. in degrees celsius
    track_temperature_change: int  # Track temp. change - 0 = up, 1 = down, 2 = no change
    air_temperature: int       # Air temp. in degrees celsius
    air_temperature_change: int  # Air temp. change - 0 = up, 1 = down, 2 = no change
    rain_percentage: int       # Rain percentage (0-100)

    # 3x uint8, 4x int8, 1x uint8 => 8 bytes total
    _struct = struct.Struct("<BBBbbbbB")  # sessionType,timeOffset,weather,trackTemp,trackTempChange,airTemp,airTempChange,rain%

    @classmethod
    def from_buffer(cls, buffer: bytes, offset: int = 0) -> 'WeatherForecastSample':
        """Unpack a WeatherForecastSample from a buffer."""
        unpacked = cls._struct.unpack_from(buffer, offset)
        return cls(*unpacked)


@dataclass
class PacketSessionData:
    """Represents session data for the current F1 session."""
    m_header: PacketHeader
    m_weather: int                          # Weather - 0 = clear, 1 = light cloud, 2 = overcast, 3 = light rain, 4 = heavy rain, 5 = storm
    m_trackTemperature: int                # Track temp. in degrees celsius
    m_airTemperature: int                  # Air temp. in degrees celsius
    m_totalLaps: int                       # Total number of laps in this race
    m_trackLength: int                     # Track length in metres
    m_sessionType: int                     # 0 = unknown, see appendix
    m_trackId: int                         # -1 for unknown, see appendix
    m_formula: int                         # Formula, 0 = F1 Modern, 1 = F1 Classic, 2 = F2, etc
    m_sessionTimeLeft: int                 # Time left in session in seconds
    m_sessionDuration: int                 # Session duration in seconds
    m_pitSpeedLimit: int                  # Pit speed limit in kilometres per hour
    m_gamePaused: int                      # Whether the game is paused
    m_isSpectating: int                    # Whether the player is spectating
    m_spectatorCarIndex: int              # Index of the car being spectated
    m_sliProNativeSupport: int           # SLI Pro support, 0 = inactive, 1 = active
    m_numMarshalZones: int                # Number of marshal zones to follow
    m_marshalZones: List[MarshalZone]      # List of marshal zones
    m_safetyCarStatus: int                # 0 = no safety car, 1 = full, 2 = virtual, 3 = formation lap
    m_networkGame: int                     # 0 = offline, 1 = online
    m_numWeatherForecastSamples: int      # Number of weather samples to follow
    m_weatherForecastSamples: List[WeatherForecastSample]  # Array of weather forecast samples
    m_forecastAccuracy: int                 # 0 = Perfect, 1 = Approximate
    m_aiDifficulty: int                    # AI difficulty - 0-110
    m_seasonLinkIdentifier: int           # Identifier for season - persists across saves
    m_weekendLinkIdentifier: int          # Identifier for weekend - persists across saves
    m_sessionLinkIdentifier: int          # Identifier for session - persists across saves
    m_pitStopWindowIdealLap: int        # Ideal lap to pit on for current strategy (player)
    m_pitStopWindowLatestLap: int       # Latest lap to pit on for current strategy (player)
    m_pitStopRejoinPosition: int         # Predicted position to rejoin at (player)
    m_steeringAssist: int                  # 0 = off, 1 = on
    m_brakingAssist: int                   # 0 = off, 1 = low, 2 = medium, 3 = high
    m_gearboxAssist: int                   # 1 = manual, 2 = manual & suggested gear, 3 = auto
    m_pitAssist: int                       # 0 = off, 1 = on
    m_pitReleaseAssist: int               # 0 = off, 1 = on
    m_ersAssist: int                       # 0 = off, 1 = on
    m_drsAssist: int                       # 0 = off, 1 = on
    m_dynamicRacingLine: int              # 0 = off, 1 = corners only, 2 = full
    m_dynamicRacingLineType: int         # 0 = 2D, 1 = 3D
    m_gameMode: int                        # Game mode id - see appendix
    m_ruleSet: int                         # Ruleset - see appendix
    m_timeOfDay: int                      # Local time of day - minutes since midnight
    m_sessionLength: int                   # 0 = None, 2 = Very Short, 3 = Short, etc
    m_speedUnitsLeadPlayer: int          # 0 = MPH, 1 = KPH
    m_temperatureUnitsLeadPlayer: int    # 0 = Celsius, 1 = Fahrenheit
    m_speedUnitsSecondaryPlayer: int     # 0 = MPH, 1 = KPH
    m_temperatureUnitsSecondaryPlayer: int # 0 = Celsius, 1 = Fahrenheit
    m_numSafetyCarPeriods: int           # Number of safety cars called during session
    m_numVirtualSafetyCarPeriods: int   # Number of virtual safety cars called
    m_numRedFlagPeriods: int             # Number of red flags called during session
    m_equalCarPerformance: int            # 0 = Off, 1 = On
    m_recoveryMode: int                    # 0 = None, 1 = Flashbacks, 2 = Auto-recovery
    m_flashbackLimit: int                  # 0 = Low, 1 = Medium, 2 = High, 3 = Unlimited
    m_surfaceType: int                     # 0 = Simplified, 1 = Realistic
    m_lowFuelMode: int                    # 0 = Easy, 1 = Hard
    m_raceStarts: int                      # 0 = Manual, 1 = Assisted
    m_tyreTemperature: int                 # 0 = Surface only, 1 = Surface & Carcass
    m_pitLaneTyreSim: int               # 0 = On, 1 = Off
    m_carDamage: int                       # 0 = Off, 1 = Reduced, 2 = Standard, 3 = Simulation
    m_carDamageRate: int                  # 0 = Reduced, 1 = Standard, 2 = Simulation
    m_collisions: int                       # 0 = Off, 1 = Player-to-Player Off, 2 = On
    m_collisionsOffForFirstLapOnly: int # 0 = Disabled, 1 = Enabled
    m_mpUnsafePitRelease: int            # 0 = On, 1 = Off (Multiplayer)
    m_mpOffForGriefing: int             # 0 = Disabled, 1 = Enabled (Multiplayer)
    m_cornerCuttingStringency: int        # 0 = Regular, 1 = Strict
    m_parcFermeRules: int                # 0 = Off, 1 = On
    m_pitStopExperience: int              # 0 = Automatic, 1 = Broadcast, 2 = Immersive
    m_safetyCar: int                       # 0 = Off, 1 = Reduced, 2 = Standard, 3 = Increased
    m_safetyCarExperience: int            # 0 = Broadcast, 1 = Immersive
    m_formationLap: int                    # 0 = Off, 1 = On
    m_formationLapExperience: int         # 0 = Broadcast, 1 = Immersive
    m_redFlags: int                        # 0 = Off, 1 = Reduced, 2 = Standard, 3 = Increased
    m_affectsLicenceLevelSolo: int       # 0 = Off, 1 = On
    m_affectsLicenceLevelMP: int         # 0 = Off, 1 = On
    m_numSessionsInWeekend: int          # Number of session in following array
    m_weekendStructure: List[int]          # List of session types for weekend structure
    m_sector2LapDistanceStart: float     # Distance in m around track where sector 2 starts
    m_sector3LapDistanceStart: float     # Distance in m around track where sector 3 starts

    @classmethod
    def from_buffer(cls, buffer: bytes) -> 'PacketSessionData':
        """Unpack the session data packet from a buffer (step-by-step).

        This mirrors the style used in `lap_data.py`: read header, read small
        fixed chunks, then variable-length arrays, then the remaining fixed
        fields, weekend structure and sector distances.
        """
        offset = 0
        m_header = PacketHeader.from_buffer(buffer, offset)
        offset += PacketHeader._struct.size

        # --- Read first fixed block (up to m_numMarshalZones) ---
        fmt1 = "<BbbBHBbBHHBBBBBB"  # 19 bytes
        (m_weather,
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
         m_numMarshalZones) = struct.unpack_from(fmt1, buffer, offset)
        offset += struct.calcsize(fmt1)

        # --- Marshal zones ---
        m_marshalZones = []
        for _ in range(m_numMarshalZones):
            mz = MarshalZone.from_buffer(buffer, offset)
            m_marshalZones.append(mz)
            offset += MarshalZone._struct.size
        # skip unused marshal zone slots
        offset += (MAX_MARSHALS_ZONE_PER_LAP - m_numMarshalZones) * MarshalZone._struct.size

        # --- safety/network/weather-samples count ---
        m_safetyCarStatus, m_networkGame, m_numWeatherForecastSamples = struct.unpack_from("<BBB", buffer, offset)
        offset += 3

        # --- Weather forecast samples ---
        m_weatherForecastSamples = []
        for _ in range(m_numWeatherForecastSamples):
            ws = WeatherForecastSample.from_buffer(buffer, offset)
            m_weatherForecastSamples.append(ws)
            offset += WeatherForecastSample._struct.size
        # skip remaining slots
        offset += (MAX_WEATHER_FORECAST_SAMPLES - m_numWeatherForecastSamples) * WeatherForecastSample._struct.size

        # --- Remaining fixed fields up to weekend structure ---
        # This block is 65 bytes (as per packet layout)
        # Build format: 2xB, 3xI, 14xB, I, 33xB => total 65 bytes
        fmt3 = "<BBIII" + ("B" * 14) + "I" + ("B" * 33)
        tail = struct.unpack_from(fmt3, buffer, offset)

        # Map tail to named fields
        idx = 0
        m_forecastAccuracy = tail[idx]; idx += 1
        m_aiDifficulty = tail[idx]; idx += 1
        m_seasonLinkIdentifier = tail[idx]; idx += 1
        m_weekendLinkIdentifier = tail[idx]; idx += 1
        m_sessionLinkIdentifier = tail[idx]; idx += 1

        # next 14 bytes
        (m_pitStopWindowIdealLap,
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
         m_ruleSet) = tail[idx:idx+14]
        idx += 14

        m_timeOfDay = tail[idx]; idx += 1

        # remaining 33 bytes
        (m_sessionLength,
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
         m_numSessionsInWeekend) = tail[idx:idx+33]

        offset += struct.calcsize(fmt3)

        # weekend structure (fixed 12 bytes)
        m_weekendStructure = list(struct.unpack_from("<12B", buffer, offset))
        # slice to only active sessions
        m_weekendStructure = m_weekendStructure[:m_numSessionsInWeekend]
        offset += MAX_SESSIONS_IN_WEEKEND

        # sector distances
        m_sector2LapDistanceStart, m_sector3LapDistanceStart = struct.unpack_from("<ff", buffer, offset)

        # Build and return
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