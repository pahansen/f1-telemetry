# F1 Telemetry

A CLI tool for capturing and parsing real-time UDP telemetry data from the F1 2024 video game. Record live telemetry to binary files and convert them to structured JSON for analysis.

Based on the [F1 24 UDP Specification](https://answers.ea.com/t5/General-Discussion/F1-24-UDP-Specification/td-p/13745220).

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Clone the repository
git clone https://github.com/yourusername/f1-telemetry.git
cd f1-telemetry

# Install dependencies
uv sync
```

## Usage

The CLI provides three main commands: `record`, `dump`, and `visualize`.

### Record Telemetry

Capture live UDP telemetry from the F1 game and save to a binary file.

```bash
# Record with default settings (127.0.0.1:20777)
uv run python -m f1_telemetry.main record

# Record with custom IP and port
uv run python -m f1_telemetry.main record --ip 192.168.1.100 --port 20777

# Record to a specific output directory
uv run python -m f1_telemetry.main record --output-path ./recordings
```

Press `Ctrl+C` to stop recording. The binary file will be saved with a timestamp (e.g., `telemetry_2024-01-15_14-30-00.bin`).

### Parse to JSON

Convert a recorded binary file to JSON format for analysis.

```bash
# Parse a binary file to JSON
uv run python -m f1_telemetry.main dump ./recordings/telemetry_2024-01-15_14-30-00.bin
```

This creates a JSON file with the same name (e.g., `telemetry_2024-01-15_14-30-00.json`).

### Visualize Telemetry

> **Note:** This is a rudimentary visualization built with matplotlib and basic button navigation. It's intended for quick data inspection rather than detailed analysis.

View telemetry traces in an interactive chart window.

```bash
# Launch visualization for a JSON telemetry file
uv run python -m f1_telemetry.main visualize ./recordings/telemetry_2024-01-15_14-30-00.json
```

The visualization displays three stacked charts:
- **Throttle & Brake** - throttle (green) and brake (red) inputs as percentages
- **Steering** - steering input from -100% (left) to +100% (right)
- **Speed** - car speed in km/h

Use the navigation buttons at the bottom of the window to cycle through drivers and laps.

## F1 Game Setup

To enable UDP telemetry in F1 2024:

1. Go to **Settings** > **Telemetry Settings**
2. Set **UDP Telemetry** to **On**
3. Set **UDP Broadcast Mode** to **Off**
4. Set **UDP IP Address** to your computer's IP (or `127.0.0.1` for localhost)
5. Set **UDP Port** to `20777`
6. Set **UDP Send Rate** to your preferred frequency (e.g., 20Hz)

## Environment Variables

You can also configure defaults via environment variables:

```bash
export F1_UDP_SERVER_ADDRESS=127.0.0.1
export F1_UDP_SERVER_PORT=20777
```
