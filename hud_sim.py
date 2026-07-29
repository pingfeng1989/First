"""
简单的 Python HUD 仿真工具示例

运行方式:
    python hud_sim.py

这个示例使用 Tkinter 显示简单的 HUD 数据：速度、航向、高度，以及一个模拟的飞行状态。
"""

import math
import random
import tkinter as tk
from tkinter import Canvas

FRAME_RATE_MS = 50

class HudSimulator:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("First - HUD Simulation")
        self.root.geometry("640x480")
        self.canvas = Canvas(root, width=640, height=480, bg="#07111f")
        self.canvas.pack(fill="both", expand=True)

        self.speed = 180.0
        self.altitude = 4500.0
        self.heading = 90.0
        self.pitch = 0.0
        self.roll = 0.0
        self.elapsed = 0.0

        self.text_items = {}
        self._create_hud_elements()
        self._schedule_update()

    def _create_hud_elements(self) -> None:
        self._draw_fixed_grid()

        self.text_items["speed"] = self.canvas.create_text(
            520, 380,
            text="SPD 180 kt",
            fill="#7affd4",
            font=("Consolas", 22, "bold"),
            anchor="e",
        )
        self.text_items["altitude"] = self.canvas.create_text(
            520, 420,
            text="ALT 4500 ft",
            fill="#7affd4",
            font=("Consolas", 22, "bold"),
            anchor="e",
        )
        self.text_items["heading"] = self.canvas.create_text(
            320, 50,
            text="HDG 090°",
            fill="#7affd4",
            font=("Consolas", 24, "bold"),
        )
        self.text_items["status"] = self.canvas.create_text(
            320, 450,
            text="HUD Simulation Running",
            fill="#cbd7ff",
            font=("Consolas", 16),
        )

        self.canvas.create_rectangle(80, 170, 260, 310, outline="#7affd4", width=2)
        self.canvas.create_text(
            170, 150,
            text="Attitude",
            fill="#7affd4",
            font=("Consolas", 14),
        )
        self.canvas.create_text(
            90, 50,
            text="Press arrow keys to adjust heading/speed",
            fill="#cbd7ff",
            font=("Consolas", 12),
            anchor="w",
        )
        self.root.bind("<Left>", self._decrease_heading)
        self.root.bind("<Right>", self._increase_heading)
        self.root.bind("<Up>", self._increase_speed)
        self.root.bind("<Down>", self._decrease_speed)

    def _draw_fixed_grid(self) -> None:
        for i in range(0, 640, 80):
            self.canvas.create_line(i, 0, i, 480, fill="#0c2b4a")
        for j in range(0, 480, 60):
            self.canvas.create_line(0, j, 640, j, fill="#0c2b4a")
        self.canvas.create_oval(280, 190, 360, 270, outline="#7affd4", width=2)
        self.canvas.create_line(320, 190, 320, 270, fill="#7affd4", width=2)
        self.canvas.create_line(280, 230, 360, 230, fill="#7affd4", width=2)

    def _update_simulation(self) -> None:
        self.elapsed += FRAME_RATE_MS / 1000.0
        self.speed += random.uniform(-0.4, 0.4)
        self.altitude += random.uniform(-4.0, 4.0)
        self.heading = (self.heading + random.uniform(-0.3, 0.3)) % 360
        self.pitch = math.sin(self.elapsed * 0.6) * 5
        self.roll = math.sin(self.elapsed * 0.9) * 7

        self.speed = max(60.0, min(340.0, self.speed))
        self.altitude = max(0.0, min(12000.0, self.altitude))

        self.canvas.itemconfigure(self.text_items["speed"], text=f"SPD {int(self.speed):03d} kt")
        self.canvas.itemconfigure(self.text_items["altitude"], text=f"ALT {int(self.altitude):04d} ft")
        self.canvas.itemconfigure(self.text_items["heading"], text=f"HDG {int(self.heading):03d}°")

        self._draw_attitude_indicator()

    def _draw_attitude_indicator(self) -> None:
        self.canvas.delete("attitude_line")
        center_x, center_y = 170, 240
        radius = 60
        offset_x = math.sin(math.radians(self.roll)) * 15
        offset_y = math.sin(math.radians(self.pitch)) * 12

        self.canvas.create_line(
            center_x - radius,
            center_y + offset_y,
            center_x + radius,
            center_y + offset_y,
            fill="#ffb347",
            width=3,
            tags="attitude_line",
        )
        self.canvas.create_line(
            center_x + offset_x,
            center_y - radius,
            center_x - offset_x,
            center_y + radius,
            fill="#7affd4",
            width=2,
            tags="attitude_line",
        )
        self.canvas.create_text(
            center_x,
            center_y + 70,
            text=f"P {self.pitch:+.1f}°  R {self.roll:+.1f}°",
            fill="#7affd4",
            font=("Consolas", 12),
            tags="attitude_line",
        )

    def _schedule_update(self) -> None:
        self._update_simulation()
        self.root.after(FRAME_RATE_MS, self._schedule_update)

    def _increase_heading(self, event: tk.Event) -> None:
        self.heading = (self.heading + 5) % 360

    def _decrease_heading(self, event: tk.Event) -> None:
        self.heading = (self.heading - 5) % 360

    def _increase_speed(self, event: tk.Event) -> None:
        self.speed = min(340.0, self.speed + 5.0)

    def _decrease_speed(self, event: tk.Event) -> None:
        self.speed = max(60.0, self.speed - 5.0)


def main() -> None:
    root = tk.Tk()
    HudSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
