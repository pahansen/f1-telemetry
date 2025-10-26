"""Handles the parsing of F1 telemetry data packets. Reads raw byte data and converts it into structured dataclasses."""
import struct
import json
from typing import Any, Dict, Type
from dataclasses import asdict, is_dataclass

from f1_telemetry.parsers.packet_header import PacketHeader
from f1_telemetry.parsers.car_telemetry_data import PacketCarTelemetryData
from f1_telemetry.parsers.motion_data import PacketMotionData
from f1_telemetry.parsers.lap_data import PacketLapData
from f1_telemetry.parsers.participant_data import PacketParticipantsData

PACKET_PARSERS: Dict[int, Type] = {
    0: PacketMotionData,
    2: PacketLapData,
    4: PacketParticipantsData,
    6: PacketCarTelemetryData
}

def parse_packet(buffer: bytes) -> Any:
    """Parses a raw F1 UDP packet into a Python dataclass."""
    header = PacketHeader.from_buffer(buffer)
    parser_cls = PACKET_PARSERS.get(header.m_packetId)
    if not parser_cls:
        return None
    return parser_cls.from_buffer(buffer)

def dataclass_to_dict(obj: Any) -> Any:
    """Recursively converts dataclasses (and their contents) into JSON-safe dicts."""
    if is_dataclass(obj):
        return {k: dataclass_to_dict(v) for k, v in asdict(obj).items()}
    elif isinstance(obj, dict):
        return {k: dataclass_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [dataclass_to_dict(v) for v in obj]
    elif isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    else:
        # Fallback for unexpected types (e.g., enums)
        return str(obj)

def dump_binary_log(file_path: str) -> list[bytes]:
    """Reads a binary log file and extracts individual packets."""
    logs = []

    with open(file_path, "rb") as f:
        while True:
            # Read packet size (2 bytes)
            size_bytes = f.read(2)
            if not size_bytes:
                break  # End of file

            packet_size = struct.unpack('>H', size_bytes)[0]
            data = f.read(packet_size)

            if not data:
                break  # Corrupt or incomplete file

            # Parse packet using your existing logic
            packet = parse_packet(data)
            if not packet:
                continue

            # Build same dict structure you use in live mode
            record = {
                "packetType": packet.__class__.__name__,
                "data": dataclass_to_dict(packet)
            }
            logs.append(record)

    with open(file_path.replace(".bin", ".json"), "w") as f:
        json.dump(logs, f, indent=4)