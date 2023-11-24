"""Parser functions for F1 2023 telemetry data.
"""
import struct

## PACKET HEADER
PACKET_HEADER_DATA_FORMAT = "<HBBBBBQfLLBB"
HEADER_SIZE = 12


def parse_packet_header(data, is_unpacked=False):
    if is_unpacked:
        unpacked_data = data
    else:
        unpacked_data = struct.unpack_from(PACKET_HEADER_DATA_FORMAT, data)

    packet_header_dict = {
        "m_packetFormat": unpacked_data[0],
        "m_gameYear": unpacked_data[1],
        "m_gameMajorVersion": unpacked_data[2],
        "m_gameMinorVersion": unpacked_data[3],
        "m_packetVersion": unpacked_data[4],
        "m_packetId": unpacked_data[5],
        "m_sessionUID": unpacked_data[6],
        "m_sessionTime": unpacked_data[7],
        "m_frameIdentifier": unpacked_data[8],
        "m_overallFrameIdentifier": unpacked_data[9],
        "m_playerCarIndex": unpacked_data[10],
        "m_secondaryPlayerCarIndex": unpacked_data[11],
    }

    return packet_header_dict


## CAR MOTION DATA
CAR_MOTION_DATA_FORMAT = "ffffffhhhhhhffffff"
PACKET_MOTION_DATA_FORMAT = PACKET_HEADER_DATA_FORMAT + (CAR_MOTION_DATA_FORMAT * 22)


def parse_car_motion_data(unpacked_data):
    car_motion_data_dict = {
        "m_worldPositionX": unpacked_data[0],
        "m_worldPositionY": unpacked_data[1],
        "m_worldPositionZ": unpacked_data[2],
        "m_worldVelocityX": unpacked_data[3],
        "m_worldVelocityY": unpacked_data[4],
        "m_worldVelocityZ": unpacked_data[5],
        "m_worldForwardDirX": unpacked_data[6],
        "m_worldForwardDirY": unpacked_data[7],
        "m_worldForwardDirZ": unpacked_data[8],
        "m_worldRightDirX": unpacked_data[9],
        "m_worldRightDirY": unpacked_data[10],
        "m_worldRightDirZ": unpacked_data[11],
        "m_gForceLateral": unpacked_data[12],
        "m_gForceLongitudinal": unpacked_data[13],
        "m_gForceVertical": unpacked_data[14],
        "m_yaw": unpacked_data[15],
        "m_pitch": unpacked_data[16],
        "m_roll": unpacked_data[17],
    }

    return car_motion_data_dict


def parse_packet_motion_data(data):
    unpacked_data = struct.unpack_from(PACKET_MOTION_DATA_FORMAT, data)

    header_dict = parse_packet_header(unpacked_data[0:12], True)
    unpacked_without_header = unpacked_data[len(header_dict) : :]

    car_motion_data_array = []
    for i in range(22):
        car_motion_data_array.append(
            parse_car_motion_data(
                unpacked_without_header[
                    i
                    * len(CAR_MOTION_DATA_FORMAT) : (i + 1)
                    * len(CAR_MOTION_DATA_FORMAT)
                ]
            )
        )
    packet_motion_data_dict = {
        "m_header": header_dict,
        "m_carMotionData": car_motion_data_array,
    }

    return packet_motion_data_dict


## SESSION DATA
MARSHAL_ZONE_FORMAT = "fb"
WEATHER_FORECAST_SAMPLE_FORMAT = "BBBbbbbB"
packet_session_data_format = (
    PACKET_HEADER_DATA_FORMAT
    + "BbbBHBbBHHBBBBBB"
    + (MARSHAL_ZONE_FORMAT * 21)
    + "BBB"
    + (WEATHER_FORECAST_SAMPLE_FORMAT * 56)
    + "BBLLLBBBBBBBBBBBBBBLBBBBBBBB"
)


def parse_marshal_zone(unpacked_data):
    marshal_zone_dict = {
        "m_zoneStart": unpacked_data[0],
        "m_zoneFlag": unpacked_data[1],
    }

    return marshal_zone_dict


def parse_weather_forecast_sample(unpacked_data):
    weather_forecast_sample_dict = {
        "m_sessionType": unpacked_data[0],
        "m_timeOffset": unpacked_data[1],
        "m_weather": unpacked_data[2],
        "m_trackTemperature": unpacked_data[3],
        "m_trackTemperatureChange": unpacked_data[4],
        "m_airTemperature": unpacked_data[5],
        "m_airTemperatureChange": unpacked_data[6],
        "m_rainPercentage": unpacked_data[7],
    }

    return weather_forecast_sample_dict


def parse_packet_session_data(data):
    unpacked_data = struct.unpack_from(packet_session_data_format, data)

    header_dict = parse_packet_header(unpacked_data[0:12], True)
    unpacked_without_header = unpacked_data[len(header_dict) : :]

    unpacked_marshal_zones = unpacked_without_header[
        16 : (len(MARSHAL_ZONE_FORMAT) * 21 + 16)
    ]
    marshal_zones_array = []
    for i in range(21):
        marshal_zones_array.append(
            parse_marshal_zone(
                unpacked_marshal_zones[
                    i * len(MARSHAL_ZONE_FORMAT) : (i + 1) * len(MARSHAL_ZONE_FORMAT)
                ]
            )
        )

    unpacked_weather_forecast_samples = unpacked_without_header[
        61 : (61 + len(WEATHER_FORECAST_SAMPLE_FORMAT) * 56)
    ]
    weather_forecast_samples_array = []
    for i in range(56):
        weather_forecast_samples_array.append(
            parse_weather_forecast_sample(
                unpacked_weather_forecast_samples[
                    i
                    * len(WEATHER_FORECAST_SAMPLE_FORMAT) : (i + 1)
                    * len(WEATHER_FORECAST_SAMPLE_FORMAT)
                ]
            )
        )

    packet_session_data_dict = {
        "m_header": header_dict,
        "m_weather": unpacked_data[12],
        "m_trackTemperature": unpacked_data[13],
        "m_airTemperature": unpacked_data[14],
        "m_totalLaps": unpacked_data[15],
        "m_trackLength": unpacked_data[16],
        "m_sessionType": unpacked_data[17],
        "m_trackId": unpacked_data[18],
        "m_formula": unpacked_data[19],
        "m_sessionTimeLeft": unpacked_data[20],
        "m_sessionDuration": unpacked_data[21],
        "m_pitSpeedLimit": unpacked_data[22],
        "m_gamePaused": unpacked_data[23],
        "m_isSpectating": unpacked_data[24],
        "m_spectatorCarIndex": unpacked_data[25],
        "m_sliProNativeSupport": unpacked_data[26],
        "m_numMarshalZones": unpacked_data[27],
        "m_marshalZones": marshal_zones_array,
        "m_safetyCarStatus": unpacked_data[70],
        "m_networkGame": unpacked_data[71],
        "m_numWeatherForecastSamples": unpacked_data[72],
        "m_weatherForecastSamples": weather_forecast_samples_array,
        "m_forecastAccuracy": unpacked_data[521],
        "m_aiDifficulty": unpacked_data[522],
        "m_seasonLinkIdentifier": unpacked_data[523],
        "m_weekendLinkIdentifier": unpacked_data[524],
        "m_sessionLinkIdentifier": unpacked_data[525],
        "m_pitStopWindowIdealLap": unpacked_data[526],
        "m_pitStopWindowLatestLap": unpacked_data[527],
        "m_pitStopRejoinPosition": unpacked_data[528],
        "m_steeringAssist": unpacked_data[529],
        "m_brakingAssist": unpacked_data[530],
        "m_gearboxAssist": unpacked_data[531],
        "m_pitAssist": unpacked_data[532],
        "m_pitReleaseAssist": unpacked_data[533],
        "m_ERSAssist": unpacked_data[534],
        "m_DRSAssist": unpacked_data[535],
        "m_dynamicRacingLine": unpacked_data[536],
        "m_dynamicRacingLineType": unpacked_data[537],
        "m_gameMode": unpacked_data[538],
        "m_ruleSet": unpacked_data[539],
        "m_timeOfDay": unpacked_data[540],
        "m_sessionLength": unpacked_data[541],
        "m_speedUnitsLeadPlayer": unpacked_data[542],
        "m_temperatureUnitsLeadPlayer": unpacked_data[543],
        "m_speedUnitsSecondaryPlayer": unpacked_data[544],
        "m_temperatureUnitsSecondaryPlayer": unpacked_data[545],
        "m_numSafetyCarPeriods": unpacked_data[546],
        "m_numVirtualSafetyCarPeriods": unpacked_data[547],
        "m_numRedFlagPeriods": unpacked_data[548],
    }

    return packet_session_data_dict


## LAP DATA
LAP_DATA_FORMAT = "IIHBHBHHfffBBBBBBBBBBBBBBBHHB"


def parse_lap_data(unpacked_data):
    lap_data_dict = {
        "m_lastLapTimeInMS": unpacked_data[0],
        "m_currentLapTimeInMS": unpacked_data[1],
        "m_sector1TimeInMS": unpacked_data[2],
        "m_sector1TimeMinutes": unpacked_data[3],
        "m_sector2TimeInMS": unpacked_data[4],
        "m_sector2TimeMinutes": unpacked_data[5],
        "m_deltaToCarInFrontInMS": unpacked_data[6],
        "m_deltaToRaceLeaderInMS": unpacked_data[7],
        "m_lapDistance": unpacked_data[8],
        "m_totalDistance": unpacked_data[9],
        "m_safetyCarDelta": unpacked_data[10],
        "m_carPosition": unpacked_data[11],
        "m_currentLapNum": unpacked_data[12],
        "m_pitStatus": unpacked_data[13],
        "m_numPitStops": unpacked_data[14],
        "m_sector": unpacked_data[15],
        "m_currentLapInvalid": unpacked_data[16],
        "m_penalties": unpacked_data[17],
        "m_totalWarnings": unpacked_data[18],
        "m_cornerCuttingWarnings": unpacked_data[19],
        "m_numUnservedDriveThroughPens": unpacked_data[20],
        "m_numUnservedStopGoPens": unpacked_data[21],
        "m_gridPosition": unpacked_data[22],
        "m_driverStatus": unpacked_data[23],
        "m_resultStatus": unpacked_data[24],
        "m_pitLaneTimerActive": unpacked_data[25],
        "m_pitLaneTimeInLaneInMS": unpacked_data[26],
        "m_pitStopTimerInMS": unpacked_data[27],
        "m_pitStopShouldServePen": unpacked_data[28],
    }

    return lap_data_dict


PACKET_LAP_DATA_FORMAT = PACKET_HEADER_DATA_FORMAT + (LAP_DATA_FORMAT * 22) + "BB"


def parse_packet_lap_data(data):
    unpacked_data = struct.unpack_from(PACKET_LAP_DATA_FORMAT, data)
    header_dict = parse_packet_header(unpacked_data[0:HEADER_SIZE], True)

    unpacked_lap_data = unpacked_data[HEADER_SIZE:]
    lap_data_array = []

    for i in range(22):
        start = i * len(LAP_DATA_FORMAT)
        end = (i + 1) * len(LAP_DATA_FORMAT)
        lap_data_array.append(parse_lap_data(unpacked_lap_data[start:end]))

    packet_lap_data_dict = {
        "m_header": header_dict,
        "m_lapData": lap_data_array,
        "m_timeTrialPBCarIdx": unpacked_data[-2],
        "m_timeTrialRivalCarIdx": unpacked_data[-1],
    }

    return packet_lap_data_dict


## PARTICIPANT DATA
PARTICIPANT_DATA_FORMAT = "BBBBBBB48sBBB"
PACKET_PARTICIPANTS_DATA_FORMAT = (
    PACKET_HEADER_DATA_FORMAT + "B" + (PARTICIPANT_DATA_FORMAT * 22)
)


def parse_participant_data(unpacked_data):
    name_utf8 = unpacked_data[7].decode("utf-8").rstrip("\x00")
    if len(name_utf8) > 48:
        name_utf8 = name_utf8[:48]  # Ensure it's not longer than 48 characters

    participant_data_dict = {
        "m_aiControlled": unpacked_data[0],
        "m_driverId": unpacked_data[1],
        "m_networkId": unpacked_data[2],
        "m_teamId": unpacked_data[3],
        "m_myTeam": unpacked_data[4],
        "m_raceNumber": unpacked_data[5],
        "m_nationality": unpacked_data[6],
        "m_name": name_utf8,
        "m_yourTelemetry": unpacked_data[8],
        "m_showOnlineNames": unpacked_data[9],
        "m_platform": unpacked_data[10],
    }

    return participant_data_dict


def parse_packet_participants_data(data):
    unpacked_data = struct.unpack_from(PACKET_PARTICIPANTS_DATA_FORMAT, data)
    header_dict = parse_packet_header(unpacked_data[0:HEADER_SIZE], True)

    unpacked_participants_data = unpacked_data[HEADER_SIZE + 1 :]

    participants_data_array = []

    for i in range(22):
        start = i * (
            len(PARTICIPANT_DATA_FORMAT) - 2
        )  # reduce by two because of the 48s char array
        end = (i + 1) * (
            len(PARTICIPANT_DATA_FORMAT) - 2
        )  # reduce by two because of the 48s char array
        participants_data_array.append(
            parse_participant_data(unpacked_participants_data[start:end])
        )

    packet_participants_data_dict = {
        "m_header": header_dict,
        "m_numActiveCars": unpacked_data[HEADER_SIZE],
        "m_participants": participants_data_array,
    }

    return packet_participants_data_dict


## CAR SETUPS DATA
CAR_SETUP_DATA_FORMAT = "BBBBffffBBBBBBBBffffBf"
PACKET_CAR_SETUP_DATA_FORMAT = PACKET_HEADER_DATA_FORMAT + (CAR_SETUP_DATA_FORMAT * 22)


def parse_car_setup_data(unpacked_data):
    car_setup_data_dict = {
        "m_frontWing": unpacked_data[0],
        "m_rearWing": unpacked_data[1],
        "m_onThrottle": unpacked_data[2],
        "m_offThrottle": unpacked_data[3],
        "m_frontCamber": unpacked_data[4],
        "m_rearCamber": unpacked_data[5],
        "m_frontToe": unpacked_data[6],
        "m_rearToe": unpacked_data[7],
        "m_frontSuspension": unpacked_data[8],
        "m_rearSuspension": unpacked_data[9],
        "m_frontAntiRollBar": unpacked_data[10],
        "m_rearAntiRollBar": unpacked_data[11],
        "m_frontSuspensionHeight": unpacked_data[12],
        "m_rearSuspensionHeight": unpacked_data[13],
        "m_brakePressure": unpacked_data[14],
        "m_brakeBias": unpacked_data[15],
        "m_rearLeftTyrePressure": unpacked_data[16],
        "m_rearRightTyrePressure": unpacked_data[17],
        "m_frontLeftTyrePressure": unpacked_data[18],
        "m_frontRightTyrePressure": unpacked_data[19],
        "m_ballast": unpacked_data[20],
        "m_fuelLoad": unpacked_data[21],
    }

    return car_setup_data_dict


def parse_packet_car_setup_data(data):
    unpacked_data = struct.unpack_from(PACKET_CAR_SETUP_DATA_FORMAT, data)
    header_dict = parse_packet_header(unpacked_data[0:HEADER_SIZE], True)

    car_setups_array = []
    car_setups_data_start = HEADER_SIZE

    for i in range(22):  # Loop over each car setup
        start_index = car_setups_data_start + (i * len(CAR_SETUP_DATA_FORMAT))
        end_index = start_index + len(CAR_SETUP_DATA_FORMAT)
        car_setup_data = unpacked_data[start_index:end_index]
        car_setups_array.append(parse_car_setup_data(car_setup_data))

    packet_car_setup_data_dict = {
        "m_header": header_dict,
        "m_carSetups": car_setups_array,
    }

    return packet_car_setup_data_dict


## CAR TELEMETRY DATA
CAR_TELEMETRY_DATA_FORMAT = "HfffBbHBBHHHHHBBBBBBBBHffffBBBB"
PACKET_CAR_TELEMETRY_DATA_FORMAT = (
    PACKET_HEADER_DATA_FORMAT + (CAR_TELEMETRY_DATA_FORMAT * 22) + "BBb"
)


def parse_car_telemetry_data(unpacked_data):
    car_telemetry_data_dict = {
        "m_speed": unpacked_data[0],
        "m_throttle": unpacked_data[1],
        "m_steer": unpacked_data[2],
        "m_brake": unpacked_data[3],
        "m_clutch": unpacked_data[4],
        "m_gear": unpacked_data[5],
        "m_engineRPM": unpacked_data[6],
        "m_drs": unpacked_data[7],
        "m_revLightsPercent": unpacked_data[8],
        "m_revLightsBitValue": unpacked_data[9],
        "m_brakesTemperatureRL": unpacked_data[10],
        "m_brakesTemperatureRR": unpacked_data[11],
        "m_brakesTemperatureFL": unpacked_data[12],
        "m_brakesTemperatureFR": unpacked_data[13],
        "m_tyresSurfaceTemperatureRL": unpacked_data[14],
        "m_tyresSurfaceTemperatureRR": unpacked_data[15],
        "m_tyresSurfaceTemperatureFL": unpacked_data[16],
        "m_tyresSurfaceTemperatureFR": unpacked_data[17],
        "m_tyresInnerTemperatureRL": unpacked_data[18],
        "m_tyresInnerTemperatureRR": unpacked_data[19],
        "m_tyresInnerTemperatureFL": unpacked_data[20],
        "m_tyresInnerTemperatureFR": unpacked_data[21],
        "m_engineTemperature": unpacked_data[22],
        "m_tyresPressureRL": unpacked_data[23],
        "m_tyresPressureRR": unpacked_data[24],
        "m_tyresPressureFL": unpacked_data[25],
        "m_tyresPressureFR": unpacked_data[26],
        "m_surfaceTypeRL": unpacked_data[27],
        "m_surfaceTypeRR": unpacked_data[28],
        "m_surfaceTypeFL": unpacked_data[29],
        "m_surfaceTypeFR": unpacked_data[30],
    }

    return car_telemetry_data_dict


def parse_packet_car_telemetry_data(data):
    unpacked_data = struct.unpack_from(PACKET_CAR_TELEMETRY_DATA_FORMAT, data)
    header_dict = parse_packet_header(unpacked_data[0:HEADER_SIZE], True)
    car_telemetry_data_start = HEADER_SIZE

    car_telemetry_data_array = []
    for i in range(22):
        start_index = car_telemetry_data_start + (i * len(CAR_TELEMETRY_DATA_FORMAT))
        end_index = start_index + len(CAR_TELEMETRY_DATA_FORMAT)
        car_telemetry_data = unpacked_data[start_index:end_index]
        car_telemetry_data_array.append(parse_car_telemetry_data(car_telemetry_data))

    mfd_panel_index_idx = HEADER_SIZE + (len(CAR_TELEMETRY_DATA_FORMAT) * 22)
    packet_car_telemetry_data_dict = {
        "m_header": header_dict,
        "m_carTelemetryData": car_telemetry_data_array,
        "m_mfdPanelIndex": unpacked_data[mfd_panel_index_idx],
        "m_mfdPanelIndexSecondaryPlayer": unpacked_data[mfd_panel_index_idx + 1],
        "m_suggestedGear": unpacked_data[mfd_panel_index_idx + 2],
    }

    return packet_car_telemetry_data_dict


## CAR STATUS DATA
CAR_STATUS_DATA_FORMAT = "BBBBBfffHHBBHBBBbfffBfffB"
PACKET_CAR_STATUS_DATA_FORMAT = PACKET_HEADER_DATA_FORMAT + (
    CAR_STATUS_DATA_FORMAT * 22
)


def parse_car_status_data(unpacked_data):
    car_status_data_dict = {
        "m_tractionControl": unpacked_data[0],
        "m_antiLockBrakes": unpacked_data[1],
        "m_fuelMix": unpacked_data[2],
        "m_frontBrakeBias": unpacked_data[3],
        "m_pitLimiterStatus": unpacked_data[4],
        "m_fuelInTank": unpacked_data[5],
        "m_fuelCapacity": unpacked_data[6],
        "m_fuelRemainingLaps": unpacked_data[7],
        "m_maxRPM": unpacked_data[8],
        "m_idleRPM": unpacked_data[9],
        "m_maxGears": unpacked_data[10],
        "m_drsAllowed": unpacked_data[11],
        "m_drsActivationDistance": unpacked_data[12],
        "m_actualTyreCompound": unpacked_data[13],
        "m_visualTyreCompound": unpacked_data[14],
        "m_tyresAgeLaps": unpacked_data[15],
        "m_vehicleFiaFlags": unpacked_data[16],
        "m_enginePowerICE": unpacked_data[17],
        "m_enginePowerMGUK": unpacked_data[18],
        "m_ersStoreEnergy": unpacked_data[19],
        "m_ersDeployMode": unpacked_data[20],
        "m_ersHarvestedThisLapMGUK": unpacked_data[21],
        "m_ersHarvestedThisLapMGUH": unpacked_data[22],
        "m_ersDeployedThisLap": unpacked_data[23],
        "m_networkPaused": unpacked_data[24],
    }

    return car_status_data_dict


def parse_packet_car_status_data(data):
    unpacked_data = struct.unpack_from(PACKET_CAR_STATUS_DATA_FORMAT, data)
    header_dict = parse_packet_header(unpacked_data[0:HEADER_SIZE], True)
    car_status_data_start = HEADER_SIZE

    car_status_data_array = []
    for i in range(22):
        start_index = car_status_data_start + (i * len(CAR_STATUS_DATA_FORMAT))
        end_index = start_index + len(CAR_STATUS_DATA_FORMAT)
        car_status_data = unpacked_data[start_index:end_index]
        car_status_data_array.append(parse_car_status_data(car_status_data))

    packet_car_status_data_dict = {
        "m_header": header_dict,
        "m_carStatusData": car_status_data_array,
    }

    return packet_car_status_data_dict


## CAR DAMAGE DATA
CAR_DAMAGE_DATA_FORMAT = "ffffBBBBBBBBBBBBBBBBBBBBBBBBBB"
PACKET_CAR_DAMAGE_DATA_FORMAT = PACKET_HEADER_DATA_FORMAT + (
    CAR_DAMAGE_DATA_FORMAT * 22
)


def parse_car_damage_data(unpacked_data):
    car_damage_data_dict = {
        "m_tyresWearRL": unpacked_data[0],
        "m_tyresWearRR": unpacked_data[1],
        "m_tyresWearFL": unpacked_data[2],
        "m_tyresWearFR": unpacked_data[3],
        "m_tyresDamageRL": unpacked_data[4],
        "m_tyresDamageRR": unpacked_data[5],
        "m_tyresDamageFL": unpacked_data[6],
        "m_tyresDamageFR": unpacked_data[7],
        "m_brakesDamageRL": unpacked_data[8],
        "m_brakesDamageRR": unpacked_data[9],
        "m_brakesDamageFL": unpacked_data[10],
        "m_brakesDamageFR": unpacked_data[11],
        "m_frontLeftWingDamage": unpacked_data[12],
        "m_frontRightWingDamage": unpacked_data[13],
        "m_rearWingDamage": unpacked_data[14],
        "m_floorDamage": unpacked_data[15],
        "m_diffuserDamage": unpacked_data[16],
        "m_sidepodDamage": unpacked_data[17],
        "m_drsFault": unpacked_data[18],
        "m_ersFault": unpacked_data[19],
        "m_gearBoxDamage": unpacked_data[20],
        "m_engineDamage": unpacked_data[21],
        "m_engineMGUHWear": unpacked_data[22],
        "m_engineESWear": unpacked_data[23],
        "m_engineCEWear": unpacked_data[24],
        "m_engineICEWear": unpacked_data[25],
        "m_engineMGUKWear": unpacked_data[26],
        "m_engineTCWear": unpacked_data[27],
        "m_engineBlown": unpacked_data[28],
        "m_engineSeized": unpacked_data[29],
    }

    return car_damage_data_dict


def parse_packet_car_damage_data(data):
    unpacked_data = struct.unpack_from(PACKET_CAR_DAMAGE_DATA_FORMAT, data)
    header_dict = parse_packet_header(unpacked_data[0:HEADER_SIZE], True)
    car_damage_data_start = HEADER_SIZE

    car_damage_data_array = []
    for i in range(22):
        start_index = car_damage_data_start + (i * len(CAR_DAMAGE_DATA_FORMAT))
        end_index = start_index + len(CAR_DAMAGE_DATA_FORMAT)
        car_damage_data = unpacked_data[start_index:end_index]
        car_damage_data_array.append(parse_car_damage_data(car_damage_data))

    packet_car_damage_data_dict = {
        "m_header": header_dict,
        "m_carDamageData": car_damage_data_array,
    }

    return packet_car_damage_data_dict
