"""F1 telemetry ingest app."""
import argparse
from f1_telemetry.data.influx_ingest import run_f1_telemetry_influx

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Write F1 telemetry UDP stream to InfluxDB or Azure Data Explorer."
    )
    parser.add_argument(
        "--db",
        action="store",
        choices=["ADX", "InfluxDB"],
        default="ADX",
        help="db for F1 telemetry ingest.",
    )
    db_selection = vars(parser.parse_args()).get("db")
    # Run F1 telemetry ingest with selected db option
    print(f"Ingesting F1 telemetry to {db_selection}.")
    if db_selection == "influx":
        run_f1_telemetry_influx()
    elif db_selection == "adx":
        print("Not implemented yet.")
