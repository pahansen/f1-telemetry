"""F1 UDP Telemetry CLI Tool."""
from typing import Annotated

import typer

from f1_telemetry.recorder import record_binary_telemetry
from f1_telemetry.dumper import dump_binary_log

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
    dump_binary_log(input_path)


if __name__ == "__main__":
    app()
