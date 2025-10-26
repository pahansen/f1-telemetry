"""F1 UDP Telemetry CLI Tool."""
import argparse

from f1_telemetry.recorder import record_binary_telemetry
from f1_telemetry.dumper import dump_binary_log


def prompt_with_default(prompt_text: str, default_value: str) -> str:
    """Prompt user with a default value shown in brackets."""
    user_input = input(f"{prompt_text} [{default_value}]: ").strip()
    return user_input if user_input else default_value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="F1 UDP Telemetry CLI Tool"
    )
    subparser = parser.add_subparsers(dest="command", required=True)
    record_parser = subparser.add_parser("record", help="Record F1 telemetry data to a binary file")
    record_parser.add_argument("--ip", type=str, help="IP address to bind to (default: 127.0.0.1)", required=True)
    record_parser.add_argument("--port", type=int, help="UDP port to listen on (default: 20777)", required=True)
    record_parser.add_argument("--output-path", type=str, help="Output file path (default: current directory)", required=True)

    dump_parser = subparser.add_parser("dump", help="Dump F1 telemetry data from a binary file")
    dump_parser.add_argument("--input-path", type=str, help="Input file path", required=True)

    args = parser.parse_args()

    if args.command == "record":
        ip = args.ip or prompt_with_default("Enter IP", "127.0.0.1")
        port = args.port or int(prompt_with_default("Enter port", "20777"))
        output_path = args.output_path or prompt_with_default("Enter output path", "./")
        record_binary_telemetry(ip, port, output_path)
    elif args.command == "dump":
        dump_binary_log(args.input_path)