"""Handles the parsing of F1 telemetry data packets. Reads raw byte data and converts it into structured dataclasses."""
import os
import struct
import json
from typing import Any, Callable, Dict, Type
from dataclasses import asdict, is_dataclass

from f1_telemetry.parsers.packet_header import PacketHeader
from f1_telemetry.parsers.car_telemetry_data import PacketCarTelemetryData
from f1_telemetry.parsers.motion_data import PacketMotionData
from f1_telemetry.parsers.lap_data import PacketLapData
from f1_telemetry.parsers.participant_data import PacketParticipantsData
from f1_telemetry.parsers.session_data import PacketSessionData
from f1_telemetry.parsers.final_classification_data import PacketFinalClassificationData

PACKET_PARSERS: Dict[int, Type] = {
    0: PacketMotionData,
    1: PacketSessionData,
    2: PacketLapData,
    4: PacketParticipantsData,
    6: PacketCarTelemetryData,
    8: PacketFinalClassificationData
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

def parse_binary_log(
    file_path: str,
    progress_callback: Callable[[int, int], None] | None = None,
) -> list[dict]:
    """Reads a binary log file and extracts individual packets.

    Args:
        file_path: Path to the binary log file.
        progress_callback: Optional callback(bytes_read, total_bytes) for progress updates.

    Returns:
        List of parsed packet records.
    """
    logs = []
    file_size = os.path.getsize(file_path)
    bytes_read = 0

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

            bytes_read += 2 + packet_size
            if progress_callback:
                progress_callback(bytes_read, file_size)

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

    return logs


def write_json_log(
    logs: list[dict],
    output_path: str,
    progress_callback: Callable[[int, int], None] | None = None,
) -> None:
    """Writes parsed logs to a JSON file with progress tracking.

    Args:
        logs: List of parsed packet records.
        output_path: Path to write the JSON file.
        progress_callback: Optional callback(records_written, total_records) for progress updates.
    """
    total = len(logs)
    with open(output_path, "w") as f:
        f.write("[\n")
        for i, record in enumerate(logs):
            json_str = json.dumps(record, indent=4)
            # Indent each line of the JSON object
            indented = "\n".join("    " + line for line in json_str.split("\n"))
            f.write(indented)
            if i < total - 1:
                f.write(",")
            f.write("\n")
            if progress_callback:
                progress_callback(i + 1, total)
        f.write("]\n")


def dump_binary_log(
    file_path: str,
    progress_callback: Callable[[int, int], None] | None = None,
) -> list[dict]:
    """Reads a binary log file and writes to JSON. Legacy function for backwards compatibility."""
    logs = parse_binary_log(file_path, progress_callback)
    output_path = file_path.replace(".bin", ".json")
    write_json_log(logs, output_path)
    return logs