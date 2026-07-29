# First

基于 Python 的汽车 HUD 光学参数仿真与可视化工具。

## 工具

### hud_optical_sim.py — 光学参数可视化

基于 VID/FOV 等光学参数，生成可交互的第一人称透视道路可视化，展示虚像尺寸和车道线覆盖情况。

支持的光学参数：

| 参数 | 说明 | 范围 |
|------|------|------|
| VID | 虚像距离 | 2-50 m |
| H-FOV | 水平视场角 | 0-30° |
| V-FOV | 垂直视场角 | 0-10° |
| Lane Width | 车道宽度 | 2.5-4.5 m |
| Display Size | HUD 显示屏尺寸 | 4-20 inch |
| Eye-box Distance | 眼睛到 HUD 距离 | 0.3-1.5 m |

所有参数均支持滑块拖动和手动输入。

交互方式：
- 鼠标悬停在透视道路查看真实世界坐标
- 键盘：`+`/`-` 调整 VID，`[`/`]` 调整 FOV，`R` 重置，`Q`/`Esc` 退出

```bash
python hud_optical_sim.py
```

### hud_sim.py — HUD 仪表盘仿真

车速、燃油、方向、档位、RPM 等仪表盘元素的动态仿真，同时支持 VID/FOV 参数输入。

```bash
python hud_sim.py
```
