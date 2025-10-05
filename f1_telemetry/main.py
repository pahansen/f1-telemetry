"""Handle F1 UDP stream and write data to influx."""
import socket
from typing import Dict, Type, Any
import json
import time
import argparse
from dataclasses import dataclass, asdict, is_dataclass

from f1_telemetry.parsers.packet_header import PacketHeader
from f1_telemetry.parsers.car_telemetry_data import PacketCarTelemetryData

PACKET_PARSERS: Dict[int, Type] = {
    6: PacketCarTelemetryData,
    # Add other IDs (0–14) here as you implement them
}

def parse_packet(buffer: bytes) -> Any:
    """Parses a raw F1 UDP packet into a Python dataclass."""
    header = PacketHeader.from_buffer(buffer)
    parser_cls = PACKET_PARSERS.get(header.m_packetId)
    if not parser_cls:
        raise ValueError(f"Unsupported packet type ID {header.m_packetId}")
    return parser_cls.from_buffer(buffer)


def dataclass_to_dict(obj: Any) -> Any:
    """Recursively converts dataclasses (and lists of them) to JSON-safe dicts."""
    if is_dataclass(obj):
        return {k: dataclass_to_dict(v) for k, v in asdict(obj).items()}
    elif isinstance(obj, (list, tuple)):
        return [dataclass_to_dict(v) for v in obj]
    elif isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    else:
        return str(obj)  # fallback for anything unexpected

def start_udp_listener(ip: str, port: int, output_path: str):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    sock.settimeout(0.5)
    print(f"🏎️  Listening for F1 24 telemetry on {ip}:{port} ... (Ctrl+C to stop)")
    print(f"📁 Logging to: {output_path}")

    logs = []
    start_time = time.time()

    try:
        while True:
            try:
                data, _ = sock.recvfrom(2048)
            except socket.timeout:
                continue
            except OSError:
                break

            packet = parse_packet(data)
            if not packet:
                continue

            # Dynamic record
            timestamp = time.time() - start_time
            record = {
                "timestamp": timestamp,
                "packetType": packet.__class__.__name__,
                "data": dataclass_to_dict(packet)
            }
            logs.append(record)

            # Minimal console output (optional)
            print(f"[{timestamp:6.2f}s] Received {packet.__class__.__name__}")

    except KeyboardInterrupt:
        print("\n🛑 Listener stopped by user.")
    finally:
        sock.close()
        print("✅ Socket closed. Writing log file...")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)
        print(f"💾 Saved {len(logs)} packets to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="F1 UDP Telemetry CLI Listener"
    )
    parser.add_argument(
        "--ip", type=str, default="127.0.0.1", help="IP address to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=20777, help="UDP port to listen on (default: 20777)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="telemetry_log.json",
        help="Output file path for telemetry log (default: telemetry_log.json)",
    )

    args = parser.parse_args()
    start_udp_listener(args.ip, args.port, args.output)

