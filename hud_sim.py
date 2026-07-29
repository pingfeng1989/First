"""
简单的 Python 汽车 HUD 仿真工具示例

运行方式:
    python hud_sim.py

该示例使用 Tkinter 显示汽车 HUD 类型的信息：车速、燃油、方向、档位、RPM 和转向状态。
"""

import math
import random
import tkinter as tk
from tkinter import Canvas

FRAME_RATE_MS = 50

class CarHudSimulator:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("First - Car HUD Simulation")
        self.root.geometry("640x480")
        self.canvas = Canvas(root, width=640, height=480, bg="#041119")
        self.canvas.pack(fill="both", expand=True)

        self.speed = 80.0
        self.direction = 90.0
        self.fuel = 92.0
        self.gear = 4
        self.rpm = 2800
        self.steer = 0.0
        self.turn_signal = 0
        self.signal_timer = 0
        self.elapsed = 0.0

        self.vid = 15.0  # 可视化距离，单位米
        self.fov = 40.0  # 水平视场角，单位度
        self.aspect_ratio = 16.0 / 9.0
        self.lane_width = 3.5
        self.view_width = 0.0
        self.view_height = 0.0
        self.lanes_visible = 0.0

        self.text_items = {}
        self._create_hud_elements()
        self._compute_view_metrics()
        self._schedule_update()

    def _create_hud_elements(self) -> None:
        self._draw_static_layout()

        self.text_items["title"] = self.canvas.create_text(
            20, 20,
            text="CAR HUD SIM",
            fill="#7affd4",
            font=("Consolas", 16, "bold"),
            anchor="w",
        )
        self.text_items["direction"] = self.canvas.create_text(
            320, 40,
            text="DIR 090°",
            fill="#7affd4",
            font=("Consolas", 24, "bold"),
        )
        self.text_items["speed"] = self.canvas.create_text(
            320, 140,
            text="080 km/h",
            fill="#ffffff",
            font=("Consolas", 48, "bold"),
        )
        self.text_items["gear"] = self.canvas.create_text(
            520, 100,
            text="4",
            fill="#7affd4",
            font=("Consolas", 36, "bold"),
            anchor="e",
        )
        self.text_items["rpm"] = self.canvas.create_text(
            520, 160,
            text="RPM 2800",
            fill="#7affd4",
            font=("Consolas", 18, "bold"),
            anchor="e",
        )
        self.text_items["fuel"] = self.canvas.create_text(
            520, 420,
            text="FUEL 092%",
            fill="#7affd4",
            font=("Consolas", 22, "bold"),
            anchor="e",
        )
        self.text_items["vid"] = self.canvas.create_text(
            320, 220,
            text="VID 15.0 m",
            fill="#7affd4",
            font=("Consolas", 18, "bold"),
        )
        self.text_items["fov"] = self.canvas.create_text(
            320, 255,
            text="FOV 40.0°",
            fill="#7affd4",
            font=("Consolas", 18, "bold"),
        )
        self.text_items["view_size"] = self.canvas.create_text(
            320, 290,
            text="VIEW 13.3 m × 7.5 m",
            fill="#7affd4",
            font=("Consolas", 14),
        )
        self.text_items["lanes"] = self.canvas.create_text(
            320, 325,
            text="LANES 3.8",
            fill="#7affd4",
            font=("Consolas", 14),
        )
        self.text_items["status"] = self.canvas.create_text(
            20, 460,
            text="Use arrows: ↑ accelerate, ↓ brake, ←/→ steer, +/- adjust VID, </> adjust FOV",
            fill="#cbd7ff",
            font=("Consolas", 12),
            anchor="w",
        )

        self.root.bind("<Left>", self._turn_left)
        self.root.bind("<Right>", self._turn_right)
        self.root.bind("<Up>", self._accelerate)
        self.root.bind("<Down>", self._brake)
        self.root.bind("t", self._toggle_turn_signal)
        self.root.bind("T", self._toggle_turn_signal)
        self.root.bind("<Key>", self._on_key)

    def _draw_static_layout(self) -> None:
        self.canvas.create_rectangle(30, 30, 610, 140, outline="#0c4d73", width=2)
        self.canvas.create_rectangle(30, 150, 310, 450, outline="#0c4d73", width=2)
        self.canvas.create_rectangle(330, 150, 610, 450, outline="#0c4d73", width=2)
        self.canvas.create_text(
            170, 180,
            text="SPEED",
            fill="#7affd4",
            font=("Consolas", 14),
        )
        self.canvas.create_text(
            470, 180,
            text="CAR STATUS",
            fill="#7affd4",
            font=("Consolas", 14),
        )
        self.canvas.create_text(
            470, 250,
            text="FOV / VID",
            fill="#7affd4",
            font=("Consolas", 14),
        )
        self.canvas.create_text(
            170, 400,
            text="STEERING",
            fill="#7affd4",
            font=("Consolas", 14),
        )

        self.canvas.create_arc(
            45, 210, 275, 440,
            start=135,
            extent=270,
            style="arc",
            outline="#184657",
            width=8,
        )
        self.canvas.create_rectangle(345, 360, 585, 430, outline="#184657", width=3)
        self.canvas.create_line(345, 355, 585, 355, fill="#184657", width=2)
        self.canvas.create_text(
            345, 340,
            text="TURN SIGNAL",
            fill="#7affd4",
            font=("Consolas", 12),
            anchor="w",
        )

    def _update_simulation(self) -> None:
        self.elapsed += FRAME_RATE_MS / 1000.0
        self.speed += random.uniform(-0.25, 0.25)
        self.direction = (self.direction + random.uniform(-0.12, 0.12)) % 360
        self.fuel = max(0.0, self.fuel - self.speed * 0.00025)
        self.rpm = int(700 + self.speed * 22 + abs(self.steer) * 12)

        if self.speed < 10:
            self.gear = 1
        elif self.speed < 30:
            self.gear = 2
        elif self.speed < 60:
            self.gear = 3
        elif self.speed < 100:
            self.gear = 4
        else:
            self.gear = 5

        self.speed = max(0.0, min(220.0, self.speed))

        if self.turn_signal != 0:
            self.signal_timer += 1
            if self.signal_timer % 10 == 0:
                self.turn_signal = -self.turn_signal
        else:
            self.signal_timer = 0

        self._compute_view_metrics()

        self.canvas.itemconfigure(self.text_items["direction"], text=f"DIR {int(self.direction):03d}°")
        self.canvas.itemconfigure(self.text_items["speed"], text=f"{int(self.speed):03d} km/h")
        self.canvas.itemconfigure(self.text_items["gear"], text=f"{self.gear}")
        self.canvas.itemconfigure(self.text_items["rpm"], text=f"RPM {self.rpm}")
        self.canvas.itemconfigure(self.text_items["fuel"], text=f"FUEL {int(self.fuel):03d}%")
        self.canvas.itemconfigure(self.text_items["vid"], text=f"VID {self.vid:.1f} m")
        self.canvas.itemconfigure(self.text_items["fov"], text=f"FOV {self.fov:.1f}°")
        self.canvas.itemconfigure(self.text_items["view_size"], text=f"VIEW {self.view_width:.1f} m × {self.view_height:.1f} m")
        self.canvas.itemconfigure(self.text_items["lanes"], text=f"LANES {self.lanes_visible:.1f}")

        self._draw_speed_needle()
        self._draw_steering_indicator()
        self._draw_turn_signal()

    def _draw_speed_needle(self) -> None:
        self.canvas.delete("speed_needle")
        angle = 135 - (self.speed / 220.0) * 270.0
        radians = math.radians(angle)
        center_x, center_y = 160, 325
        length = 110
        end_x = center_x + math.cos(radians) * length
        end_y = center_y - math.sin(radians) * length
        self.canvas.create_line(
            center_x,
            center_y,
            end_x,
            end_y,
            fill="#ffb347",
            width=4,
            arrow="last",
            tags="speed_needle",
        )
        self.canvas.create_oval(
            center_x - 8,
            center_y - 8,
            center_x + 8,
            center_y + 8,
            fill="#7affd4",
            outline="",
            tags="speed_needle",
        )

    def _draw_steering_indicator(self) -> None:
        self.canvas.delete("steering_indicator")
        center_x, center_y = 170, 410
        radius = 80
        offset = math.sin(math.radians(self.steer)) * radius * 0.6

        self.canvas.create_line(
            center_x - radius,
            center_y,
            center_x + radius,
            center_y,
            fill="#7affd4",
            width=3,
            tags="steering_indicator",
        )
        self.canvas.create_line(
            center_x + offset,
            center_y - radius * 0.35,
            center_x + offset,
            center_y + radius * 0.35,
            fill="#ffb347",
            width=5,
            tags="steering_indicator",
        )
        self.canvas.create_text(
            center_x,
            center_y + 60,
            text=f"STEER {self.steer:+.1f}°",
            fill="#7affd4",
            font=("Consolas", 12),
            tags="steering_indicator",
        )

    def _draw_turn_signal(self) -> None:
        self.canvas.delete("turn_signal")
        if self.turn_signal == 0:
            text = "OFF"
            color = "#4f7c99"
        elif self.turn_signal < 0:
            text = "LEFT"
            color = "#ffb347"
        else:
            text = "RIGHT"
            color = "#ffb347"

        self.canvas.create_text(
            470,
            380,
            text=text,
            fill=color,
            font=("Consolas", 24, "bold"),
            tags="turn_signal",
        )

    def _compute_view_metrics(self) -> None:
        rad = math.radians(self.fov)
        self.view_width = 2 * self.vid * math.tan(rad / 2)
        self.view_height = self.view_width / self.aspect_ratio
        self.lanes_visible = max(0.0, self.view_width / self.lane_width)

    def _on_key(self, event: tk.Event) -> None:
        key = event.keysym
        if key == "plus" or key == "equal":
            self.vid = min(100.0, self.vid + 1.0)
        elif key == "minus" or key == "underscore":
            self.vid = max(5.0, self.vid - 1.0)
        elif key == "bracketleft":
            self.fov = max(10.0, self.fov - 1.0)
        elif key == "bracketright":
            self.fov = min(120.0, self.fov + 1.0)
        elif key.lower() == "t":
            self._toggle_turn_signal(event)
        else:
            return
        self._compute_view_metrics()
        self.canvas.itemconfigure(self.text_items["vid"], text=f"VID {self.vid:.1f} m")
        self.canvas.itemconfigure(self.text_items["fov"], text=f"FOV {self.fov:.1f}°")
        self.canvas.itemconfigure(self.text_items["view_size"], text=f"VIEW {self.view_width:.1f} m × {self.view_height:.1f} m")
        self.canvas.itemconfigure(self.text_items["lanes"], text=f"LANES {self.lanes_visible:.1f}")

    def _schedule_update(self) -> None:
        self._update_simulation()
        self.root.after(FRAME_RATE_MS, self._schedule_update)

    def _turn_left(self, event: tk.Event) -> None:
        self.direction = (self.direction - 3) % 360
        self.steer = max(-45.0, self.steer - 5.0)
        if self.turn_signal >= 0:
            self.turn_signal = -1

    def _turn_right(self, event: tk.Event) -> None:
        self.direction = (self.direction + 3) % 360
        self.steer = min(45.0, self.steer + 5.0)
        if self.turn_signal <= 0:
            self.turn_signal = 1

    def _accelerate(self, event: tk.Event) -> None:
        self.speed = min(220.0, self.speed + 5.0)

    def _brake(self, event: tk.Event) -> None:
        self.speed = max(0.0, self.speed - 5.0)

    def _toggle_turn_signal(self, event: tk.Event) -> None:
        if self.turn_signal == 0:
            self.turn_signal = -1
        elif self.turn_signal < 0:
            self.turn_signal = 1
        else:
            self.turn_signal = 0


def main() -> None:
    root = tk.Tk()
    CarHudSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
