"""F1 telemetry ingest app."""
from f1_telemetry.data.mongodb_ingest import run_f1_telemetry_ingest

if __name__ == "__main__":
    print(f"Ingesting F1 telemetry to MongoDB.")
    run_f1_telemetry_ingest()
