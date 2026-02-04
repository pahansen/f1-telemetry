"""F1 UDP Telemetry CLI Tool."""
import os
from typing import Annotated

import typer
from rich.progress import Progress, BarColumn, TaskProgressColumn, TimeRemainingColumn

from f1_telemetry.recorder import record_binary_telemetry
from f1_telemetry.dumper import parse_binary_log, write_json_log

app = typer.Typer(help="F1 UDP Telemetry CLI Tool")


@app.command()
def record(
    ip: Annotated[str, typer.Option(help="IP address to bind to")] = "127.0.0.1",
    port: Annotated[int, typer.Option(help="UDP port to listen on")] = 20777,
    output_path: Annotated[str, typer.Option(help="Output directory path")] = "./",
):
    """Record F1 telemetry data to a binary file."""
    record_binary_telemetry(ip, port, output_path)


@app.command()
def dump(
    input_path: Annotated[str, typer.Argument(help="Input binary file path")],
):
    """Dump F1 telemetry data from a binary file to JSON."""
    file_size = os.path.getsize(input_path)
    output_path = input_path.replace(".bin", ".json")

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    ) as progress:
        # Phase 1: Parse binary packets
        parse_task = progress.add_task("Parsing packets...", total=file_size)

        def update_parse_progress(bytes_read: int, total: int):
            progress.update(parse_task, completed=bytes_read)

        logs = parse_binary_log(input_path, progress_callback=update_parse_progress)

        # Phase 2: Write JSON output
        write_task = progress.add_task("Writing JSON...", total=len(logs))

        def update_write_progress(records_written: int, total: int):
            progress.update(write_task, completed=records_written)

        write_json_log(logs, output_path, progress_callback=update_write_progress)


if __name__ == "__main__":
    app()
