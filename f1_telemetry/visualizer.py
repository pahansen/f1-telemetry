"""Telemetry visualization module."""

import json
from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.widgets import Button


@dataclass
class TelemetryPoint:
    lap_distance: float
    throttle: float
    brake: float
    steer: float
    speed: int


class TelemetryVisualizer:
    def __init__(self, json_path: str):
        self.data = self._load_data(json_path)
        self.drivers = self._get_drivers()
        self.driver_indices = sorted(self.drivers.keys())
        self.current_driver_pos = 0
        self.current_lap_pos = 0
        self.available_laps = []

        # Set up the figure with 3 subplots
        self.fig, (self.ax_throttle, self.ax_steer, self.ax_speed) = plt.subplots(
            3, 1, figsize=(14, 10), sharex=True
        )
        plt.subplots_adjust(bottom=0.15, hspace=0.3)

        # Driver navigation buttons
        ax_prev_driver = plt.axes([0.15, 0.08, 0.08, 0.05])
        ax_next_driver = plt.axes([0.24, 0.08, 0.08, 0.05])
        self.btn_prev_driver = Button(ax_prev_driver, "◀ Driver")
        self.btn_next_driver = Button(ax_next_driver, "Driver ▶")
        self.btn_prev_driver.on_clicked(self._prev_driver)
        self.btn_next_driver.on_clicked(self._next_driver)

        # Driver label
        self.ax_driver_label = plt.axes([0.33, 0.08, 0.2, 0.05])
        self.ax_driver_label.set_xticks([])
        self.ax_driver_label.set_yticks([])
        self.driver_label = self.ax_driver_label.text(
            0.5, 0.5, "", ha="center", va="center", fontsize=10, fontweight="bold"
        )

        # Lap navigation buttons
        ax_prev_lap = plt.axes([0.58, 0.08, 0.08, 0.05])
        ax_next_lap = plt.axes([0.67, 0.08, 0.08, 0.05])
        self.btn_prev_lap = Button(ax_prev_lap, "◀ Lap")
        self.btn_next_lap = Button(ax_next_lap, "Lap ▶")
        self.btn_prev_lap.on_clicked(self._prev_lap)
        self.btn_next_lap.on_clicked(self._next_lap)

        # Lap label
        self.ax_lap_label = plt.axes([0.76, 0.08, 0.1, 0.05])
        self.ax_lap_label.set_xticks([])
        self.ax_lap_label.set_yticks([])
        self.lap_label = self.ax_lap_label.text(
            0.5, 0.5, "", ha="center", va="center", fontsize=10, fontweight="bold"
        )

        # Initialize
        if self.driver_indices:
            self._update_driver()

    def _load_data(self, json_path: str) -> list[dict]:
        with open(json_path, "r") as f:
            return json.load(f)

    def _get_drivers(self) -> dict[int, str]:
        for packet in self.data:
            if packet["packetType"] == "PacketParticipantsData":
                return {
                    i: p["m_name"]
                    for i, p in enumerate(packet["data"]["m_participants"])
                    if p["m_name"]
                }
        return {}

    def _get_available_laps(self, car_index: int) -> list[int]:
        laps = set()
        for packet in self.data:
            if packet["packetType"] == "PacketLapData":
                lap_data = packet["data"]["m_lapData"][car_index]
                lap_num = lap_data["m_currentLapNum"]
                if lap_num > 0:
                    laps.add(lap_num)
        return sorted(laps)

    def _extract_lap_telemetry(self, car_index: int, lap_num: int) -> list[TelemetryPoint]:
        frame_to_lap = {}
        for packet in self.data:
            if packet["packetType"] == "PacketLapData":
                frame_id = packet["data"]["m_header"]["m_frameIdentifier"]
                lap_data = packet["data"]["m_lapData"][car_index]
                frame_to_lap[frame_id] = {
                    "lap_num": lap_data["m_currentLapNum"],
                    "lap_distance": lap_data["m_lapDistance"],
                }

        points = []
        for packet in self.data:
            if packet["packetType"] == "PacketCarTelemetryData":
                frame_id = packet["data"]["m_header"]["m_frameIdentifier"]
                if frame_id in frame_to_lap and frame_to_lap[frame_id]["lap_num"] == lap_num:
                    car_telemetry = packet["data"]["m_carTelemetryData"][car_index]
                    points.append(
                        TelemetryPoint(
                            lap_distance=frame_to_lap[frame_id]["lap_distance"],
                            throttle=car_telemetry["m_throttle"],
                            brake=car_telemetry["m_brake"],
                            steer=car_telemetry["m_steer"],
                            speed=car_telemetry["m_speed"],
                        )
                    )

        points.sort(key=lambda p: p.lap_distance)
        return points

    def _prev_driver(self, event):
        if self.current_driver_pos > 0:
            self.current_driver_pos -= 1
            self._update_driver()

    def _next_driver(self, event):
        if self.current_driver_pos < len(self.driver_indices) - 1:
            self.current_driver_pos += 1
            self._update_driver()

    def _prev_lap(self, event):
        if self.current_lap_pos > 0:
            self.current_lap_pos -= 1
            self._update_plot()

    def _next_lap(self, event):
        if self.current_lap_pos < len(self.available_laps) - 1:
            self.current_lap_pos += 1
            self._update_plot()

    def _update_driver(self):
        car_index = self.driver_indices[self.current_driver_pos]
        driver_name = self.drivers[car_index]
        self.driver_label.set_text(driver_name)

        self.available_laps = self._get_available_laps(car_index)
        self.current_lap_pos = 0

        self._update_plot()

    def _update_plot(self):
        car_index = self.driver_indices[self.current_driver_pos]
        driver_name = self.drivers[car_index]

        if not self.available_laps:
            self.ax_throttle.clear()
            self.ax_steer.clear()
            self.ax_speed.clear()
            self.ax_throttle.set_title(f"{driver_name} - No lap data available")
            self.lap_label.set_text("N/A")
            self.fig.canvas.draw_idle()
            return

        lap_num = self.available_laps[self.current_lap_pos]
        self.lap_label.set_text(f"Lap {lap_num}")

        points = self._extract_lap_telemetry(car_index, lap_num)
        if not points:
            self.ax_throttle.clear()
            self.ax_steer.clear()
            self.ax_speed.clear()
            self.ax_throttle.set_title(f"{driver_name} - Lap {lap_num}: No telemetry data")
            self.fig.canvas.draw_idle()
            return

        distances = [p.lap_distance for p in points]
        throttle = [p.throttle * 100 for p in points]
        brake = [p.brake * 100 for p in points]
        steer = [p.steer * 100 for p in points]  # Convert to percentage (-100 to 100)
        speed = [p.speed for p in points]

        # Throttle & Brake chart
        self.ax_throttle.clear()
        self.ax_throttle.plot(distances, throttle, color="green", label="Throttle", linewidth=1)
        self.ax_throttle.plot(distances, brake, color="red", label="Brake", linewidth=1)
        self.ax_throttle.set_title(f"{driver_name} - Lap {lap_num}")
        self.ax_throttle.set_ylabel("Throttle/Brake (%)")
        self.ax_throttle.set_ylim(0, 105)
        self.ax_throttle.legend(loc="upper right")
        self.ax_throttle.grid(True, alpha=0.3)

        # Steering chart
        self.ax_steer.clear()
        self.ax_steer.plot(distances, steer, color="blue", label="Steering", linewidth=1)
        self.ax_steer.axhline(y=0, color="gray", linestyle="--", linewidth=0.5)
        self.ax_steer.set_ylabel("Steering (%)")
        self.ax_steer.set_ylim(-105, 105)
        self.ax_steer.legend(loc="upper right")
        self.ax_steer.grid(True, alpha=0.3)

        # Speed chart
        self.ax_speed.clear()
        self.ax_speed.plot(distances, speed, color="purple", label="Speed", linewidth=1)
        self.ax_speed.set_xlabel("Lap Distance (m)")
        self.ax_speed.set_ylabel("Speed (km/h)")
        self.ax_speed.legend(loc="upper right")
        self.ax_speed.grid(True, alpha=0.3)

        self.fig.canvas.draw_idle()

    def show(self):
        plt.show()


def visualize_telemetry(json_path: str):
    """Launch interactive telemetry visualization."""
    viz = TelemetryVisualizer(json_path)
    viz.show()
