"""Utility functions for retrieving clean data sets."""
from f1_telemetry.data.telemetry import PacketCarTelemetryData


def telemetry_list_to_attributes(telemetry_values: list, attribute_name: str) -> dict:
    """Get single attributes from attributes list and allocate to position on car (fl, fr, rl, rr).

    Args:
        telemetry_values(list): List of telemetry values that should be mapped to attributes.
        attribute_name(str): Attribute name used as keys in dict.
    """
    car_position_mapping = ["rl", "rr", "fl", "fr"]
    telemetry_values_dict = {}
    for i, telemetry_value in enumerate(telemetry_values):
        key_name = str(attribute_name) + "_" + car_position_mapping[i]
        telemetry_values_dict[key_name] = telemetry_value
    return telemetry_values_dict


def get_play_car_telemetry(telemetry_message: PacketCarTelemetryData) -> dict:
    """Get telemetry from player car.

    Args:
        telemetry_message(PacketCarTelemetryData): Telemetry of all cars including header.
    """
    player_car_index = telemetry_message.m_header.m_player_car_index
    player_car_telemetry = telemetry_message.m_car_telemetry_data[player_car_index]
    player_telemetry_message = {
        "m_session_time": telemetry_message.m_header.m_session_time
    } | player_car_telemetry.__dict__
    # Map tyre temperature values from list to attributes
    player_telemetry_message = player_telemetry_message | telemetry_list_to_attributes(
        player_telemetry_message["m_tyres_surface_temperature"],
        "m_tyres_surface_temperature",
    )
    player_telemetry_message.pop("m_tyres_surface_temperature")
    # Map brake temperature values from list to attributes
    player_telemetry_message = player_telemetry_message | telemetry_list_to_attributes(
        player_telemetry_message["m_brakes_temperature"],
        "m_brakes_temperature",
    )
    player_telemetry_message.pop("m_brakes_temperature")

    return player_telemetry_message
