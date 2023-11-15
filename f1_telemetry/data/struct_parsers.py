"""Struct classes for car telemetry. Classes parse data from binary format and extract player data.
F1 2023 data format.
"""
import struct

PACKET_HEADER_DATA_FORMAT = "<HBBBBBQfLLBB"

def parse_packet_header(data, is_unpacked=False):
    # Define the format string based on the struct members
    
    # Unpack the binary data using the format string
    if is_unpacked:
        unpacked_data = data
    else:
        unpacked_data = struct.unpack_from(PACKET_HEADER_DATA_FORMAT, data)
    
    # Create a dictionary with the struct members as keys
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

CAR_MOTION_DATA_FORMAT = "ffffffhhhhhhffffff"
PACKET_MOTION_DATA_FORMAT = PACKET_HEADER_DATA_FORMAT + (CAR_MOTION_DATA_FORMAT * 22)

def parse_packet_motion_data(data):
    # Unpack the binary data using the format string for PacketMotionData
    unpacked_data = struct.unpack_from(PACKET_MOTION_DATA_FORMAT, data)
    
    # Extract the PacketHeader from the unpacked data
    header_dict = parse_packet_header(unpacked_data[0:12], True)
    unpacked_without_header = unpacked_data[len(header_dict) : :]
    
    # Extract the CarMotionData array from the unpacked data
    car_motion_data_array = []
    for i in range(22):
        car_motion_data_array.append(parse_car_motion_data(unpacked_without_header[i
                    * len(CAR_MOTION_DATA_FORMAT) : (i + 1)
                    * len(CAR_MOTION_DATA_FORMAT)]))

    # Create a dictionary with the PacketHeader and CarMotionData array
    packet_motion_data_dict = {
        "m_header": header_dict,
        "m_carMotionData": car_motion_data_array,
    }
    
    return packet_motion_data_dict

MARSHAL_ZONE_FORMAT = "fb"
WEATHER_FORECAST_SAMPLE_FORMAT="BBBbbbbB"
packet_session_data_format = (
    PACKET_HEADER_DATA_FORMAT +
    "BbbBHBbBHHBBBBBB" +
    (MARSHAL_ZONE_FORMAT * 21) +
    "BBB" +
    (WEATHER_FORECAST_SAMPLE_FORMAT * 56) +
    "BBLLLBBBBBBBBBBBBBBLBBBBBBBB"
)

def parse_marshal_zone(unpacked_data):
    # Create a dictionary with the struct members as keys
    marshal_zone_dict = {
        "m_zoneStart": unpacked_data[0],
        "m_zoneFlag": unpacked_data[1],
    }
    
    return marshal_zone_dict

def parse_weather_forecast_sample(unpacked_data):
    # Create a dictionary with the struct members as keys
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
    # Use the provided function to parse the header
    # Extract the PacketHeader from the unpacked data
    unpacked_data = struct.unpack_from(packet_session_data_format, data)
    
    header_dict = parse_packet_header(unpacked_data[0:12], True)
    unpacked_without_header = unpacked_data[len(header_dict) : :]
    
    # Extract the MarshalZone array from the unpacked data
    unpacked_marshal_zones = unpacked_without_header[16:(len(MARSHAL_ZONE_FORMAT)*21+16)]
    marshal_zones_array = []
    for i in range(21):
        marshal_zones_array.append(parse_marshal_zone(unpacked_marshal_zones[
                    i
                    * len(MARSHAL_ZONE_FORMAT) : (i + 1)
                    * len(MARSHAL_ZONE_FORMAT)]))

    # Extract the WeatherForecastSample array from the unpacked data
    unpacked_weather_forecast_samples = unpacked_without_header[61:(61 + len(WEATHER_FORECAST_SAMPLE_FORMAT) * 56)]
    weather_forecast_samples_array = []
    for i in range(56):
        weather_forecast_samples_array.append(parse_weather_forecast_sample(unpacked_weather_forecast_samples[
                    i
                    * len(WEATHER_FORECAST_SAMPLE_FORMAT) : (i + 1)
                    * len(WEATHER_FORECAST_SAMPLE_FORMAT)]))

    # Create a dictionary with the header, MarshalZone array, and WeatherForecastSample array
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
        "m_numRedFlagPeriods": unpacked_data[548]
    }
    
    return packet_session_data_dict