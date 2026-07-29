"""
HUD 光学参数可视化工具

运行方式:
    python hud_optical_sim.py

根据用户输入的 VID/FOV 等光学参数，生成可交互的第一人称透视道路可视化，
展示虚像尺寸和覆盖的车道线情况。

交互方式:
    拖动左侧滑块调整参数
    鼠标悬停在可视化区域查看真实世界坐标
    键盘: +/- 调整 VID, [/] 调整 FOV, R 重置, Q/Esc 退出
"""

import math
import tkinter as tk
from tkinter import ttk

# ─── 计算函数 ──────────────────────────────────────────────

def compute_view_width(vid: float, h_fov_deg: float) -> float:
    rad = math.radians(h_fov_deg)
    return 2.0 * vid * math.tan(rad / 2.0)

def compute_view_height(vid: float, v_fov_deg: float) -> float:
    rad = math.radians(v_fov_deg)
    return 2.0 * vid * math.tan(rad / 2.0)

def compute_lanes_visible(view_width: float, lane_width: float) -> float:
    return view_width / lane_width if lane_width > 0 else 0.0

def compute_display_fov(display_m: float, eyebox_m: float) -> float:
    if eyebox_m <= 0:
        return 0.0
    return math.degrees(2.0 * math.atan(display_m / (2.0 * eyebox_m)))

# ─── 颜色常量 ──────────────────────────────────────────────

BG_DARK       = "#041119"
BG_SKY        = "#0a1628"
COLOR_GREEN   = "#7affd4"
COLOR_ORANGE  = "#ffb347"
COLOR_CYAN    = "#00bfff"
COLOR_RED     = "#ff4444"
COLOR_ROAD    = "#333333"
COLOR_LANE    = "#ffffff"
COLOR_DIM     = "#4f7c99"
COLOR_PANEL_BG = "#0a1a24"
COLOR_TEXT    = "#cbd7ff"

# ─── 默认参数 ──────────────────────────────────────────────

DEFAULTS = {
    "vid": 15.0,
    "h_fov": 40.0,
    "v_fov": 20.0,
    "lane_width": 3.5,
    "vehicle_width": 1.8,
    "display_size": 6.0,
    "eyebox_dist": 0.7,
}

ASPECT_PRESETS = {"16:9": 16/9, "4:3": 4/3, "21:9": 21/9, "1:1": 1.0}

LANE_WIDTH_PRESETS = {
    "China Highway":    3.75,
    "China Urban":      3.50,
    "US Interstate":    3.66,
    "US Urban":         3.30,
    "Germany Autobahn": 3.75,
    "UK Motorway":      3.65,
    "France Highway":   3.50,
    "Japan Expressway": 3.50,
    "Japan Urban":      3.00,
}


# ─── 主程序 ────────────────────────────────────────────────

class HudOpticalSimulator:

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HUD Optical Parameter Simulator")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)
        self.root.configure(bg=BG_DARK)

        self._updating = False
        self._redraw_pending = None

        self._init_parameters()
        self._build_ui()
        self._bind_events()
        self.root.after(50, self._on_resize)

    # ─── 参数初始化 ─────────────────────────────────────────

    def _init_parameters(self) -> None:
        self.vid = tk.DoubleVar(value=DEFAULTS["vid"])
        self.h_fov = tk.DoubleVar(value=DEFAULTS["h_fov"])
        self.v_fov = tk.DoubleVar(value=DEFAULTS["v_fov"])
        self.lane_width = tk.DoubleVar(value=DEFAULTS["lane_width"])
        self.vehicle_width = tk.DoubleVar(value=DEFAULTS["vehicle_width"])
        self.display_size = tk.DoubleVar(value=DEFAULTS["display_size"])
        self.eyebox_dist = tk.DoubleVar(value=DEFAULTS["eyebox_dist"])
        self.aspect_key = tk.StringVar(value="16:9")
        self.lane_preset_key = tk.StringVar(value="")

        self.view_width = 0.0
        self.view_height = 0.0
        self.lanes_visible = 0.0
        self.display_fov = 0.0

    def _compute_metrics(self) -> None:
        self.view_width = compute_view_width(self.vid.get(), self.h_fov.get())
        self.view_height = compute_view_height(self.vid.get(), self.v_fov.get())
        self.lanes_visible = compute_lanes_visible(self.view_width, self.lane_width.get())
        self.display_fov = compute_display_fov(
            self.display_size.get() * 0.0254, self.eyebox_dist.get()
        )

    # ─── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        main = tk.Frame(self.root, bg=BG_DARK)
        main.pack(fill="both", expand=True, padx=6, pady=6)

        left = tk.Frame(main, bg=COLOR_PANEL_BG, width=300)
        left.pack(side="left", fill="y", padx=(0, 6))
        left.pack_propagate(False)

        right = tk.Frame(main, bg=BG_DARK)
        right.pack(side="left", fill="both", expand=True)

        self._build_input_panel(left)
        self._build_canvas(right)

    def _build_input_panel(self, parent: tk.Frame) -> None:
        header = tk.Label(parent, text="OPTICAL PARAMETERS", bg=COLOR_PANEL_BG,
                          fg=COLOR_GREEN, font=("Consolas", 12, "bold"))
        header.pack(anchor="w", padx=10, pady=(10, 6))

        sliders_frame = tk.Frame(parent, bg=COLOR_PANEL_BG)
        sliders_frame.pack(fill="x", padx=10)

        self._create_slider_row(sliders_frame, "VID", self.vid, 2, 50, 0.5, "m", 0)
        self._create_slider_row(sliders_frame, "H-FOV", self.h_fov, 0, 30, 0.5, "deg", 1)
        self._create_slider_row(sliders_frame, "V-FOV", self.v_fov, 0, 10, 0.5, "deg", 2)

        # Aspect ratio dropdown
        ar_row = tk.Frame(sliders_frame, bg=COLOR_PANEL_BG)
        ar_row.grid(row=3, column=0, columnspan=3, sticky="ew", pady=4)
        tk.Label(ar_row, text="Aspect:", bg=COLOR_PANEL_BG, fg=COLOR_GREEN,
                 font=("Consolas", 10), width=8, anchor="w").pack(side="left")
        ar_menu = ttk.Combobox(ar_row, textvariable=self.aspect_key,
                               values=list(ASPECT_PRESETS.keys()), state="readonly", width=8)
        ar_menu.pack(side="left", padx=(0, 8))
        ar_menu.bind("<<ComboboxSelected>>", lambda e: self._on_param_change())

        # Lane width region preset dropdown
        lane_preset_row = tk.Frame(sliders_frame, bg=COLOR_PANEL_BG)
        lane_preset_row.grid(row=4, column=0, columnspan=3, sticky="ew", pady=4)
        tk.Label(lane_preset_row, text="Region:", bg=COLOR_PANEL_BG, fg=COLOR_GREEN,
                 font=("Consolas", 10), width=8, anchor="w").pack(side="left")
        lane_menu = ttk.Combobox(lane_preset_row, textvariable=self.lane_preset_key,
                                 values=list(LANE_WIDTH_PRESETS.keys()),
                                 state="readonly", width=14)
        lane_menu.pack(side="left", padx=(0, 4))
        lane_menu.bind("<<ComboboxSelected>>", self._on_lane_preset)

        self._create_slider_row(sliders_frame, "Lane W", self.lane_width, 2.5, 4.5, 0.1, "m", 5)
        self._create_slider_row(sliders_frame, "Veh W", self.vehicle_width, 1.5, 2.5, 0.1, "m", 6)
        self._create_slider_row(sliders_frame, "Display", self.display_size, 4, 20, 0.5, '"', 7)
        self._create_slider_row(sliders_frame, "Eyebox", self.eyebox_dist, 0.3, 1.5, 0.05, "m", 8)

        sliders_frame.columnconfigure(1, weight=1)

        # Separator
        tk.Frame(parent, bg=COLOR_DIM, height=1).pack(fill="x", padx=10, pady=(10, 6))

        # Calculation results
        calc_header = tk.Label(parent, text="CALCULATIONS", bg=COLOR_PANEL_BG,
                               fg=COLOR_GREEN, font=("Consolas", 11, "bold"))
        calc_header.pack(anchor="w", padx=10, pady=(0, 4))

        calc_frame = tk.Frame(parent, bg=COLOR_PANEL_BG)
        calc_frame.pack(fill="x", padx=10)

        self.lbl_width = self._create_calc_label(calc_frame, "View Width:", 0)
        self.lbl_height = self._create_calc_label(calc_frame, "View Height:", 1)
        self.lbl_lanes = self._create_calc_label(calc_frame, "Lanes Visible:", 2)
        self.lbl_coverage = self._create_calc_label(calc_frame, "Coverage:", 3)
        self.lbl_display_fov = self._create_calc_label(calc_frame, "Display FOV:", 4)

        calc_frame.columnconfigure(1, weight=1)

        # Separator
        tk.Frame(parent, bg=COLOR_DIM, height=1).pack(fill="x", padx=10, pady=(10, 6))

        # Reset button
        btn_frame = tk.Frame(parent, bg=COLOR_PANEL_BG)
        btn_frame.pack(fill="x", padx=10, pady=(4, 10))
        tk.Button(btn_frame, text="Reset Defaults (R)", command=self._reset_defaults,
                  bg="#1a3040", fg=COLOR_GREEN, font=("Consolas", 10),
                  relief="flat", cursor="hand2").pack(fill="x")

    def _create_slider_row(self, parent: tk.Frame, label: str, var: tk.DoubleVar,
                           from_: float, to: float, resolution: float,
                           unit: str, row: int) -> None:
        lbl = tk.Label(parent, text=f"{label}:", bg=COLOR_PANEL_BG, fg=COLOR_GREEN,
                       font=("Consolas", 10), width=8, anchor="w")
        lbl.grid(row=row, column=0, sticky="w", pady=3)

        spin_var = tk.StringVar(value=f"{var.get():.1f}")
        spinbox = ttk.Spinbox(parent, textvariable=spin_var, from_=from_, to=to,
                              increment=resolution, width=6, justify="right",
                              font=("Consolas", 10, "bold"))
        spinbox.grid(row=row, column=2, sticky="e", pady=3, padx=(4, 0))

        def on_spinbox_change(_event=None):
            if self._updating:
                return
            try:
                val = float(spin_var.get())
                val = max(from_, min(to, val))
                var.set(round(val / resolution) * resolution)
            except ValueError:
                spin_var.set(f"{var.get():.1f}")
            self._on_param_change()

        spinbox.bind("<Return>", on_spinbox_change)
        spinbox.bind("<FocusOut>", on_spinbox_change)

        def sync_spinbox(*_args):
            if not self._updating:
                spin_var.set(f"{var.get():.1f}")

        var.trace_add("write", sync_spinbox)

        slider = tk.Scale(parent, variable=var, from_=from_, to=to,
                          resolution=resolution, orient="horizontal",
                          bg=COLOR_PANEL_BG, fg=COLOR_GREEN,
                          highlightthickness=0, troughcolor="#1a3040",
                          sliderlength=18, length=140,
                          command=lambda _: self._on_param_change())
        slider.grid(row=row, column=1, sticky="ew", pady=3, padx=(0, 4))

        sync_spinbox()

    def _create_calc_label(self, parent: tk.Frame, label: str, row: int) -> tk.Label:
        tk.Label(parent, text=label, bg=COLOR_PANEL_BG, fg=COLOR_DIM,
                 font=("Consolas", 10), anchor="w").grid(row=row, column=0, sticky="w", pady=2)
        val = tk.Label(parent, text="0.0", bg=COLOR_PANEL_BG, fg=COLOR_ORANGE,
                       font=("Consolas", 10, "bold"), anchor="e")
        val.grid(row=row, column=1, sticky="e", pady=2)
        return val

    def _build_canvas(self, parent: tk.Frame) -> None:
        self.canvas = tk.Canvas(parent, bg=BG_DARK, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Hover info bar
        self.hover_label = tk.Label(parent, text="Hover over visualization for coordinates",
                                    bg=BG_DARK, fg=COLOR_DIM, font=("Consolas", 10), anchor="w")
        self.hover_label.pack(fill="x", padx=4)

    # ─── 事件绑定 ───────────────────────────────────────────

    def _bind_events(self) -> None:
        self.canvas.bind("<Motion>", self._on_canvas_hover)
        self.canvas.bind("<Configure>", self._on_resize)
        self.root.bind("<Key>", self._on_key)

    def _on_key(self, event: tk.Event) -> None:
        key = event.keysym
        if key in ("plus", "equal"):
            self.vid.set(min(50.0, self.vid.get() + 1.0))
        elif key == "minus":
            self.vid.set(max(2.0, self.vid.get() - 1.0))
        elif key == "bracketright":
            self.h_fov.set(min(30.0, self.h_fov.get() + 1.0))
        elif key == "bracketleft":
            self.h_fov.set(max(0.0, self.h_fov.get() - 1.0))
        elif key.lower() == "r":
            self._reset_defaults()
        elif key in ("q", "Escape"):
            self.root.destroy()
        else:
            return
        self._on_param_change()

    def _on_lane_preset(self, _event=None) -> None:
        key = self.lane_preset_key.get()
        if key in LANE_WIDTH_PRESETS:
            self.lane_width.set(LANE_WIDTH_PRESETS[key])
            self._on_param_change()

    # ─── 参数变更 ───────────────────────────────────────────

    def _on_param_change(self, *args) -> None:
        if self._updating:
            return
        self._updating = True
        try:
            self._compute_metrics()
            self._update_info_labels()
            self._schedule_redraw()
        finally:
            self._updating = False

    def _update_info_labels(self) -> None:
        self.lbl_width.configure(text=f"{self.view_width:.1f} m")
        self.lbl_height.configure(text=f"{self.view_height:.1f} m")
        self.lbl_lanes.configure(text=f"{self.lanes_visible:.1f}")
        lanes_int = max(1, round(self.lanes_visible))
        coverage = (self.view_width / (self.lane_width.get() * lanes_int) * 100) if lanes_int > 0 else 0
        self.lbl_coverage.configure(text=f"{coverage:.0f}%")
        self.lbl_display_fov.configure(text=f"{self.display_fov:.1f} deg")

    def _reset_defaults(self) -> None:
        self._updating = True
        try:
            for name, val in DEFAULTS.items():
                getattr(self, name).set(val)
            self.aspect_key.set("16:9")
            self._compute_metrics()
            self._update_info_labels()
        finally:
            self._updating = False
        self._schedule_redraw()

    # ─── 延迟重绘 ───────────────────────────────────────────

    def _schedule_redraw(self) -> None:
        if self._redraw_pending is not None:
            self.root.after_cancel(self._redraw_pending)
        self._redraw_pending = self.root.after(30, self._redraw)

    def _on_resize(self, _event=None) -> None:
        self._schedule_redraw()

    # ─── 透视坐标变换 ──────────────────────────────────────

    def _world_to_screen(self, lateral_m: float, dist_m: float,
                         canvas_w: int, canvas_h: int,
                         horizon_y: float) -> tuple[float, float]:
        """
        将真实世界坐标 (横向偏移, 纵向距离) 映射到 Canvas 像素坐标。
        horizon_y: 地平线在 canvas 上的 Y 坐标 (越远越靠近)。
        """
        max_dist = max(self.vid.get() * 1.8, 80.0)
        y_norm = dist_m / max_dist
        y_norm = max(0.0, min(1.0, y_norm))

        screen_y = canvas_h - (canvas_h - horizon_y) * y_norm

        road_half_w = canvas_w * 0.42
        perspective = 1.0 - y_norm * 0.7
        screen_x = canvas_w / 2 + lateral_m * (road_half_w * perspective) / (self.lane_width.get() * 3)

        return screen_x, screen_y

    # ─── 绘制 ──────────────────────────────────────────────

    def _redraw(self) -> None:
        self._redraw_pending = None
        c = self.canvas
        c.delete("all")

        w = c.winfo_width()
        h = c.winfo_height()
        if w < 10 or h < 10:
            return

        self._draw_sky_ground(c, w, h)
        self._draw_road_perspective(c, w, h)
        self._draw_lane_markings(c, w, h)
        self._draw_virtual_image(c, w, h)
        self._draw_vehicle(c, w, h)
        self._draw_annotations(c, w, h)

    def _draw_sky_ground(self, c: tk.Canvas, w: int, h: int) -> None:
        horizon_y = h * 0.28
        c.create_rectangle(0, 0, w, horizon_y, fill=BG_SKY, outline="")
        c.create_rectangle(0, horizon_y, w, h, fill=COLOR_ROAD, outline="")

    def _draw_road_perspective(self, c: tk.Canvas, w: int, h: int) -> None:
        horizon_y = h * 0.28
        bottom_y = h
        road_w_bottom = w * 0.84
        road_w_top = w * 0.06

        x1 = w / 2 - road_w_bottom / 2
        x2 = w / 2 + road_w_bottom / 2
        x3 = w / 2 + road_w_top / 2
        x4 = w / 2 - road_w_top / 2

        c.create_polygon(x1, bottom_y, x4, horizon_y, x3, horizon_y, x2, bottom_y,
                         fill="#2a2a2a", outline="#3a3a3a", width=1)

        shoulder = 8
        c.create_line(x1 + shoulder, bottom_y, x4 + shoulder / 4, horizon_y,
                      fill=COLOR_LANE, width=2)
        c.create_line(x2 - shoulder, bottom_y, x3 - shoulder / 4, horizon_y,
                      fill=COLOR_LANE, width=2)

    def _draw_lane_markings(self, c: tk.Canvas, w: int, h: int) -> None:
        horizon_y = h * 0.28
        bottom_y = h
        lane_w = self.lane_width.get()
        lanes_int = max(1, int(self.lanes_visible) + 1)

        for lane_idx in range(-lanes_int, lanes_int + 1):
            if lane_idx == 0:
                continue
            lateral = lane_idx * lane_w
            segments = 20
            for i in range(segments):
                t1 = i / segments
                t2 = (i + 0.55) / segments
                if (i % 2) == 0:
                    continue
                sx1, sy1 = self._world_to_screen(lateral, t1 * self.vid.get() * 1.8, w, h, horizon_y)
                sx2, sy2 = self._world_to_screen(lateral, t2 * self.vid.get() * 1.8, w, h, horizon_y)
                c.create_line(sx1, sy1, sx2, sy2, fill=COLOR_LANE, width=1, dash=(6, 4))

        sx0_b, _ = self._world_to_screen(0, 0, w, h, horizon_y)
        sx0_t, _ = self._world_to_screen(0, self.vid.get() * 1.8, w, h, horizon_y)
        c.create_line(sx0_b, bottom_y, sx0_t, horizon_y, fill=COLOR_ORANGE, width=2, dash=(8, 6))

    def _draw_virtual_image(self, c: tk.Canvas, w: int, h: int) -> None:
        horizon_y = h * 0.28
        vid = self.vid.get()
        half_w = self.view_width / 2.0
        half_h = self.view_height / 2.0

        corners = [
            (-half_w, vid - half_h),
            ( half_w, vid - half_h),
            ( half_w, vid + half_h),
            (-half_w, vid + half_h),
        ]
        screen_pts = []
        for lx, dist in corners:
            sx, sy = self._world_to_screen(lx, dist, w, h, horizon_y)
            screen_pts.extend([sx, sy])

        c.create_polygon(screen_pts, fill="#00bfff", outline=COLOR_CYAN,
                         stipple="gray25", width=2, tags="vi_rect")
        c.create_polygon(screen_pts, fill="", outline=COLOR_CYAN,
                         width=2, tags="vi_outline")

        cx = (screen_pts[0] + screen_pts[2]) / 2
        cy = (screen_pts[1] + screen_pts[5]) / 2
        c.create_text(cx, cy,
                      text=f"{self.view_width:.1f}m x {self.view_height:.1f}m",
                      fill="#ffffff", font=("Consolas", 11, "bold"), tags="vi_label")

    def _draw_vehicle(self, c: tk.Canvas, w: int, h: int) -> None:
        vw = self.vehicle_width.get()
        vx1, vy1 = self._world_to_screen(-vw / 2, 2, w, h, h * 0.28)
        vx2, vy2 = self._world_to_screen(vw / 2, 6, w, h, h * 0.28)
        c.create_rectangle(vx1, vy1, vx2, vy2, outline=COLOR_RED, width=2, tags="vehicle")
        c.create_text((vx1 + vx2) / 2, (vy1 + vy2) / 2,
                      text="CAR", fill=COLOR_RED, font=("Consolas", 8, "bold"),
                      tags="vehicle")

    def _draw_annotations(self, c: tk.Canvas, w: int, h: int) -> None:
        vid = self.vid.get()
        half_w = self.view_width / 2.0

        sx, sy = self._world_to_screen(half_w, vid, w, h, h * 0.28)
        c.create_text(sx + 10, sy, text=f"R: {half_w:.1f}m",
                      fill=COLOR_ORANGE, font=("Consolas", 9), anchor="w", tags="annot")

        sx_l, sy_l = self._world_to_screen(-half_w, vid, w, h, h * 0.28)
        c.create_text(sx_l - 10, sy_l, text=f"L: {half_w:.1f}m",
                      fill=COLOR_ORANGE, font=("Consolas", 9), anchor="e", tags="annot")

        sx_vid, sy_vid = self._world_to_screen(0, vid, w, h, h * 0.28)
        c.create_text(sx_vid, sy_vid - 12, text=f"VID: {vid:.1f}m",
                      fill=COLOR_GREEN, font=("Consolas", 10, "bold"),
                      anchor="s", tags="annot")

        lane_w = self.lane_width.get()
        lanes_int = max(1, round(self.lanes_visible))
        for i in range(-lanes_int, lanes_int + 1):
            lx = i * lane_w
            sx_i, sy_i = self._world_to_screen(lx, vid + half_w * 0.3, w, h, h * 0.28)
            txt = f"{i:+d}" if i != 0 else "0"
            c.create_text(sx_i, sy_i + 14, text=txt,
                          fill=COLOR_DIM, font=("Consolas", 8), tags="annot")

        c.create_text(w / 2, h * 0.28 - 10, text="Horizon",
                      fill=COLOR_DIM, font=("Consolas", 9), anchor="s", tags="annot")

    # ─── 鼠标悬停 ──────────────────────────────────────────

    def _on_canvas_hover(self, event: tk.Event) -> None:
        c = self.canvas
        w = c.winfo_width()
        h = c.winfo_height()
        horizon_y = h * 0.28

        vid = self.vid.get()
        max_dist = max(vid * 1.8, 80.0)
        y_norm = (h - event.y) / (h - horizon_y)
        y_norm = max(0.0, min(1.0, y_norm))
        dist = y_norm * max_dist

        road_half_w = w * 0.42
        perspective = 1.0 - y_norm * 0.7
        if perspective > 0.01:
            lateral = (event.x - w / 2) * (self.lane_width.get() * 3) / (road_half_w * perspective)
        else:
            lateral = 0.0

        if horizon_y <= event.y <= h:
            in_vi = (abs(lateral) <= self.view_width / 2.0 and
                     abs(dist - vid) <= self.view_height / 2.0)
            marker = " [IN VI]" if in_vi else ""
            self.hover_label.configure(
                text=f"Pos: {lateral:+.1f}m lateral, {dist:.1f}m ahead{marker}")
        else:
            self.hover_label.configure(text="Hover over road for coordinates")


def main() -> None:
    root = tk.Tk()
    HudOpticalSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
