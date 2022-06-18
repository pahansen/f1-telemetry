"""F1 telemetry ingest app."""
import argparse
from f1_telemetry.data.influx_ingest import run_f1_telemetry_influx

if __name__ == "__main__":
    print(f"Ingesting F1 telemetry to InfluxDB.")
    run_f1_telemetry_influx()
