"""
简单的 Python 汽车 HUD 仿真工具示例

运行方式:
    python hud_sim.py

这个示例使用 Tkinter 显示简单的汽车 HUD 数据：车速、燃油、方向、档位和转向状态。
"""

import math
import random
import tkinter as tk
from tkinter import Canvas

FRAME_RATE_MS = 50

class HudSimulator:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("First - Car HUD Simulation")
        self.root.geometry("640x480")
        self.canvas = Canvas(root, width=640, height=480, bg="#07111f")
        self.canvas.pack(fill="both", expand=True)

        self.speed = 80.0
        self.fuel = 88
        self.direction = 90.0
        self.gear = 4
        self.rpm = 2800
        self.steer = 0.0
        self.elapsed = 0.0

        self.text_items = {}
        self._create_hud_elements()
        self._schedule_update()

    def _create_hud_elements(self) -> None:
        self._draw_fixed_grid()

        self.text_items["speed"] = self.canvas.create_text(
            520, 360,
            text="SPD 080 km/h",
            fill="#7affd4",
            font=("Consolas", 28, "bold"),
            anchor="e",
        )
        self.text_items["fuel"] = self.canvas.create_text(
            520, 410,
            text="FUEL 088%",
            fill="#7affd4",
            font=("Consolas", 22, "bold"),
            anchor="e",
        )
        self.text_items["direction"] = self.canvas.create_text(
            320, 50,
            text="DIR 090°",
            fill="#7affd4",
            font=("Consolas", 24, "bold"),
        )
        self.text_items["gear"] = self.canvas.create_text(
            520, 320,
            text="GEAR 4",
            fill="#7affd4",
            font=("Consolas", 22, "bold"),
            anchor="e",
        )
        self.text_items["status"] = self.canvas.create_text(
            320, 450,
            text="Car HUD Simulation Running",
            fill="#cbd7ff",
            font=("Consolas", 16),
        )

        self.canvas.create_rectangle(80, 170, 260, 310, outline="#7affd4", width=2)
        self.canvas.create_text(
            170, 150,
            text="Steering",
            fill="#7affd4",
            font=("Consolas", 14),
        )
        self.canvas.create_text(
            90, 50,
            text="Use arrow keys to adjust speed/heading",
            fill="#cbd7ff",
            font=("Consolas", 12),
            anchor="w",
        )
        self.root.bind("<Left>", self._turn_left)
        self.root.bind("<Right>", self._turn_right)
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
        self.speed += random.uniform(-0.6, 0.6)
        self.direction = (self.direction + random.uniform(-0.1, 0.1)) % 360
        self.steer = math.sin(self.elapsed * 1.2) * 18
        self.fuel = max(0, self.fuel - 0.005)
        self.rpm = int(800 + self.speed * 30 + abs(self.steer) * 5)

        if self.speed < 20:
            self.gear = 1
        elif self.speed < 40:
            self.gear = 2
        elif self.speed < 70:
            self.gear = 3
        elif self.speed < 110:
            self.gear = 4
        else:
            self.gear = 5

        self.speed = max(0.0, min(200.0, self.speed))

        self.canvas.itemconfigure(self.text_items["speed"], text=f"SPD {int(self.speed):03d} km/h")
        self.canvas.itemconfigure(self.text_items["fuel"], text=f"FUEL {int(self.fuel):03d}%")
        self.canvas.itemconfigure(self.text_items["direction"], text=f"DIR {int(self.direction):03d}°")
        self.canvas.itemconfigure(self.text_items["gear"], text=f"GEAR {self.gear}")

        self._draw_steering_indicator()

    def _draw_steering_indicator(self) -> None:
        self.canvas.delete("steering_line")
        center_x, center_y = 170, 240
        radius = 60
        offset = math.sin(math.radians(self.steer)) * 20

        self.canvas.create_line(
            center_x - radius,
            center_y,
            center_x + radius,
            center_y,
            fill="#ffb347",
            width=3,
            tags="steering_line",
        )
        self.canvas.create_line(
            center_x + offset,
            center_y - radius,
            center_x - offset,
            center_y + radius,
            fill="#7affd4",
            width=2,
            tags="steering_line",
        )
        self.canvas.create_text(
            center_x,
            center_y + 70,
            text=f"STEER {self.steer:+.1f}°  RPM {self.rpm}",
            fill="#7affd4",
            font=("Consolas", 12),
            tags="steering_line",
        )

    def _schedule_update(self) -> None:
        self._update_simulation()
        self.root.after(FRAME_RATE_MS, self._schedule_update)

    def _turn_left(self, event: tk.Event) -> None:
        self.direction = (self.direction - 3) % 360
        self.steer = max(-45.0, self.steer - 5.0)

    def _turn_right(self, event: tk.Event) -> None:
        self.direction = (self.direction + 3) % 360
        self.steer = min(45.0, self.steer + 5.0)

    def _increase_speed(self, event: tk.Event) -> None:
        self.speed = min(200.0, self.speed + 5.0)

    def _decrease_speed(self, event: tk.Event) -> None:
        self.speed = max(0.0, self.speed - 5.0)


def main() -> None:
    root = tk.Tk()
    HudSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
