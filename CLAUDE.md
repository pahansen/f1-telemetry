# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

F1 UDP telemetry ingestion system that captures real-time data from F1 2024 video game, records to binary files, and parses into structured JSON output.

## Commands

```bash
# Install dependencies (using uv)
uv sync

# Record live telemetry from F1 game
uv run python -m f1_telemetry.main record --ip 127.0.0.1 --port 20777 --output-path ./

# Parse recorded binary log to JSON
uv run python -m f1_telemetry.main dump --input-path <path_to_bin_file>
```

## Architecture

```
F1 Game (UDP 127.0.0.1:20777)
    ↓
recorder.py (UDP socket → binary file with size-prefixed packets)
    ↓
dumper.py (binary file → packet parsers → JSON)
    ↓
parsers/*.py (struct unpacking → dataclasses)
```

### Key Modules

- **main.py**: Typer CLI with `record` and `dump` subcommands
- **recorder.py**: UDP socket listener, writes packets as `[2-byte size][data]` pairs to `.bin` files
- **dumper.py**: Reads binary logs, dispatches to parsers via `PACKET_PARSERS` dict by packet ID, outputs JSON
- **parsers/**: Each packet type is a dataclass with `_struct` (format string) and `from_buffer()` classmethod

### Packet Types

| ID | Parser | Data |
|----|--------|------|
| 0 | motion_data.py | Car positions, velocity, G-forces |
| 1 | session_data.py | Weather, track, session config |
| 2 | lap_data.py | Lap times, positions, pit status |
| 4 | participant_data.py | Driver names, teams |
| 6 | car_telemetry_data.py | Speed, throttle, brakes, temps |
| 8 | final_classification_data.py | Race results, points |

### Binary Format

- All packets use little-endian encoding
- Packet header (24 bytes) present in all packets - parsed first to get `packet_id` for dispatch
- Each parser handles fixed arrays (e.g., 4 wheel temps, 22 cars)
- The file ./logs/F1_24_Telemetry_Output_Structures.txt shows a specification for all packages. Always refer this file when working on parser code

## Environment Variables

```bash
F1_UDP_SERVER_ADDRESS=127.0.0.1  # Default UDP address
F1_UDP_SERVER_PORT=20777         # Default UDP port
```
