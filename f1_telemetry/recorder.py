"""Handles the recording of F1 telemetry data. Stores all received packets into a binary file."""

import socket
import struct
import time


def record_binary_telemetry(ip: str, port: int, output_path: str):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    sock.settimeout(0.5)
    print(f"🏎️  Listening for F1 24 telemetry on {ip}:{port} ... (Ctrl+C to stop)")
    print(f"📁 Logging to: {output_path}")
    start_time = time.time()

    file_name = (
        output_path + str(start_time).replace(".", "_") + "_f1_telemetry_log.bin"
    )
    try:
        with open(file_name, "wb") as f:
            while True:
                try:
                    data, _ = sock.recvfrom(2048)
                except socket.timeout:
                    continue
                except OSError:
                    break

                f.write(struct.pack(">H", len(data)))
                f.write(data)

    except KeyboardInterrupt:
        print("\n🛑 Listener stopped by user.")
    finally:
        sock.close()
        print("✅ Socket closed. Binary log file saved.")
