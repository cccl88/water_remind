# AGENTS.md — 喝水提醒 / WaterReminder 交接说明

> 给后续接手的人（或 AI 编码代理）读的项目上下文。改代码前请先读完「必须遵守的约束」和「踩过的坑」。
> 仓库：https://github.com/cccl88/water_remind · 当前版本 v1.1.0

## 1. 这是什么

一个 Windows 桌面喝水提醒工具。核心差异化：**有个 Q 版桌宠「凛」亲自催你喝水**，全程**不出声**，提醒走自绘气泡/卡片，不碰系统通知音。

三种性格（傲娇/温柔/撒娇）各有全套原创台词，用户可切换、可给桌宠改名、可拖动、可点击互动。

技术栈：Python 3.13 + PySide6-Essentials（Qt Widgets，**纯 QPainter 手绘，零图片素材**）+ PyInstaller 单文件打包。

## 2. 常用命令

```bash
# 依赖（首次）
安装依赖.bat                     # 建 .venv + 装 PySide6-Essentials（腾讯云镜像）

# 运行
启动喝水提醒.bat                  # pythonw 无控制台启动
.venv\Scripts\pythonw.exe main.py

# 自检（会真的开窗渲染，需要桌面会话）
.venv\Scripts\python.exe main.py --selftest        # 逻辑校验 + 真实数据截图
.venv\Scripts\python.exe main.py --selftest=demo   # 伪造演示数据截图（README 用）

# 打包 / 发版
打包exe.bat
.venv\Scripts\python.exe _upload_release.py v1.2.0
```

`--selftest` 是当前**唯一**的验证手段：它会渲染两种主题的主界面、触发一次提醒（断言必须触发）、写 `_selftest.log`，退出码 0 表示通过。

## 3. 架构

```
main.py  Controller（唯一状态中心）
  ├─ Config.load()          %APPDATA%\WaterReminder\config.json
  ├─ Store()                %APPDATA%\WaterReminder\history.json
  ├─ MainWindow(self)       ui/main_window.py   设置 + 进度环 + 7 日柱状图
  ├─ Personality(key)       pet/personality.py  台词库
  ├─ PetWindow(self)        pet/pet_window.py   桌宠窗口（可选，pet_enabled）
  ├─ QSystemTrayIcon        托盘菜单：显示/暂停/打卡/桌宠开关/退出
  ├─ QTimer(1s) → tick()    到点判定 + 每秒刷新界面
  └─ QLocalServer           单实例锁（SINGLE_KEY）
```

**提醒数据流**：`tick()` 每秒跑 → `in_active(now)` 判断提醒时段 → `now >= next_remind` → `show_reminder()`
→ 若 `pet_enabled` 走 `pet.remind(台词)`（跳跃 + 气泡带三个按钮）；若 `show_card` 或桌宠关闭，额外/改为 `ReminderPopup`（屏幕顶部滑入卡片）。
→ 用户点「喝了」→ `drink()` → `store.add(cup_ml)` → `schedule_next()` → `refresh_ui()` → 桌宠 `react("drink")`。

**状态一致性要点**：`_reminding()` 是"正在提醒中"的唯一判据（卡片或桌宠气泡可见），`show_reminder()` 开头会挡重复提醒。

## 4. 模块职责

| 文件 | 行数 | 职责 |
| --- | --- | --- |
| `main.py` | ~480 | Controller 全体调度、托盘、单实例、`--selftest` |
| `core/config.py` | ~118 | dataclass 配置、JSON 读写、注册表开机自启 |
| `core/store.py` | ~94 | 按日期存杯数/总量、undo、近 N 天、连续达标 |
| `pet/character.py` | ~335 | 角色绘制：头/发/双马尾/呆毛/身体/发饰/表情/影子 |
| `pet/personality.py` | ~104 | 三性格 × 8 场景（greet/remind/drink/snooze/skip/click/idle/pause）台词 |
| `pet/bubble.py` | ~112 | 台词气泡，可带「喝了/稍后/跳过」，支持自动关闭 |
| `pet/pet_window.py` | ~241 | 透明置顶窗口、跳动/眨眼/呼吸、拖动、右键菜单、轮廓 mask 穿透 |
| `ui/theme.py` | ~152 | 浅/深两套调色板 + QSS |
| `ui/widgets.py` | ~231 | RingProgress、BarChart、水滴图标、Switch（全自绘） |
| `ui/main_window.py` | ~441 | 主窗口：进度环、统计、各设置卡片（含「桌宠」区） |
| `ui/popup.py` | ~136 | 顶部滑入提醒卡片（桌宠关闭时的备用提醒） |

`pet/character.py` 已支持表情：`idle / happy / angry / shy / surprised / sleepy`（+ `blink` 眨眼参数）。
主题色键：`bg card panel border text sub primary primary2 primary_soft success warn track hover shadow`。

## 5. 配置字段（`config.json`）

| 字段 | 默认 | 说明 |
| --- | --- | --- |
| `interval_min` | 45 | 提醒间隔（5–180） |
| `cup_ml` / `goal_ml` | 250 / 2000 | 单杯水量 / 每日目标 |
| `enabled` | true | 提醒总开关 |
| `active_from` / `active_to` | 08:00 / 22:00 | 提醒时段，支持跨午夜（`in_active` 已处理） |
| `snooze_min` | 10 | 「稍后」顺延分钟 |
| `silent` | true | 历史字段，保留不使用（本应用根本不加载音频） |
| `auto_start` | false | 注册表 HKCU Run |
| `theme` | light | light / dark |
| `pet_enabled` | true | 关掉则退回卡片提醒 |
| `personality` | tsundere | tsundere / gentle / coquettish |
| `pet_name` | 凛 | 8 字以内 |
| `pet_pos` | [] | 桌宠屏幕坐标（拖动后保存） |
| `show_card` | false | 桌宠气泡之外是否再弹卡片 |

## 6. 必须遵守的约束

1. **绝对不出声**。不加载音频文件、不调 `QSound`、不弹系统通知来提醒（托盘 `showMessage` 仅用于"已记录 xx ml"轻量回执，不要用于提醒本身）。
2. **不引入任何第三方美术素材**。角色是原创形象，只用"白发 / 双马尾 / 红发夹 / 呆毛"这类通用元素，靠 QPainter 绘制。加贴图/立绘等于引入版权风险，会破坏这个项目的合规前提。
3. **中文界面 + 中文注释**，文案风格口语化。台词要保持性格一致性（傲娇口是心非、温柔轻声、撒娇软磨硬泡）。
4. **不要动用户的真实数据**：`%APPDATA%\WaterReminder\config.json` 和 `history.json` 是真人数据，测试时不要在代码里清空；`--selftest` 已设计为不写记录。
5. 自绘控件统一走 `ui/theme.py` 的调色板，不要在控件里硬编码颜色，否则深色模式会崩。

## 7. 踩过的坑（血泪，别重复）

- **打包会静默失败**：PyInstaller 覆盖 `dist/WaterReminder.exe` 时，若旧 exe 被占用/被安全策略拦截，会抛 `OSError: [safe-delete] ... trash operation` 并退出码 1。**必须**看 `_build.log` 里的 `EXIT=0`，并校验 exe mtime 与体积；更稳的做法是打包前先 `rm -f dist/WaterReminder.exe`。本项目曾因此把旧 exe 发到新 Release 上。
- **自检会覆盖演示截图**：`--selftest`（非 demo）用真实数据渲染，会把 `assets/preview_*.png` 写脏。提交前要补跑 `--selftest=demo`。
- **问候气泡会抢截图**：`Controller` 启动后 1.4s 会弹 `greet` 气泡。写截图脚本必须先等 ≥1.8s 再 `close_bubble()`，否则抓到的是问候而不是想测的那条。
- **`QTimeEdit` 设 `NoButtons` 后内容显示空白**，已改回默认箭头按钮 + 固定宽度 88。
- **气泡长文本**：`QLabel` 需要 `setWordWrap(False)` + `setFixedWidth`，否则换行被裁；气泡整体尺寸改动后要同步 `paintEvent` 里手绘背景的矩形。
- **PyInstaller onefile 会出现两个同名进程**（引导器 + 子进程），任务管理器里看到两个是正常的，不是重复启动。
- **`QApplication.setHighDpiScaleFactorRoundingPolicy(PassThrough)`** 是刻意保留的，别删，否则高分屏缩放下布局会抖。

## 8. 已知问题 / 待办（按优先级）

### P0 真实缺陷（建议先修）
1. **多显示器气泡定位错误**：`PetWindow._reposition_bubble` 和 `ReminderPopup.show_at_top` 都用 `QApplication.primaryScreen()`。桌宠被拖到副屏时，气泡会跑到主屏去。应改用 `self.screen()` / 坐标所在屏的 `availableGeometry()`。
2. **跳跃会撞 mask**：`_build_mask()` 按静止姿态算轮廓，而 `paintEvent` 里 `translate(0, bob_offset())` 最多上移 16px，头部会被裁掉一点。要么把 mask 上边界留出余量，要么改成动画时重算。
3. **`tick()` 的守卫用 `self.popup is None`**，没复用 `_reminding()`，桌宠气泡在显示时仍会每秒进一次 `show_reminder()`（虽被内部挡住，但属于逻辑不一致）。
4. **`_smoke.py` 已废弃且有害**：它的逻辑早被 `main.py --selftest` 取代，而且它会直接 `ctrl.store.add(...)` 往**真实** `history.json` 里写假记录（9:00 / 11:00 / 14:00 各若干杯），跑一次就污染用户数据；断言也还是旧卡片弹窗版本。建议直接删掉，需要回归就用 `--selftest`。

### P1 体验增强
5. **喝水/提醒动作动画**：目前 `drink` 只切 happy 表情 + 气泡。可加"举杯""喝一口"的分段绘制（`character.py` 已有参数化的 `t`，加一个 `action` 参数即可）。
6. **桌宠空闲自言自语**：`personality` 里已经有 `idle` 台词但没人调用。可加 8–15 分钟随机定时器，气泡自动消失。
7. **睡眠唤醒后立即提醒**：`next_remind` 用的是墙钟时间，电脑睡眠两小时后唤醒会立刻弹提醒。可在 `tick()` 里检测"距上次 tick 超过 N 秒"视为休眠，顺延间隔。
8. **提醒气泡加倒计时**：现在 `remind()` 的 `auto_close_ms=0` 永不自动关，用户不处理就一直挂着。可加"30 秒后自动收起（不记录）"。

### P2 功能扩展
9. **多角色 / 换装**：`character.py` 的发色、裙色、发饰已是常量，抽成 `palette` 参数就能做皮肤；`personality.py` 的台词可外置成 `%APPDATA%` 下的 JSON 让用户自定义。
10. **数据导出 / 周报**：`Store.last_days()` 已有数据，可加 CSV 导出和"一周喝水报告"。
11. **单杯记录编辑**：目前只能 add/undo，不能改某一条。

### P3 工程化
12. **单元测试 + CI**：`store.py`、`config.py`、`in_active()` 边界（跨午夜）纯逻辑，容易测。可加 GitHub Actions 跑 `pytest` + `--selftest`（需 `QT_QPA_PLATFORM=offscreen`，但注意 offscreen 平台中文会变豆腐块，只断言逻辑不截图）。
13. **打包健壮化**：把"先删旧 exe + 校验 EXIT + 校验体积"固化进 `打包exe.bat`。
14. **依赖固定版本**：`requirements.txt` 建议锁 `PySide6-Essentials==x.y.z`，避免上游更新导致打包体积/行为漂移。

## 9. 给编码代理的工作约定

- 改完必须跑 `--selftest`，且**看日志内容**而不是只看命令退出码（历史上出过"命令成功但打包失败"）。
- 修 UI 布局要顺手用 `_render_*.py` 截图看一眼（`_render_pet.py` / `_render_personas.py` / `_render_settings.py`），别凭想象改像素。
- 提交信息用中文 `feat: / fix: / docs: / refactor:` 前缀，一句话说清做了什么。
- **不要**：改用户 `%APPDATA%` 下的真实数据；引入音频；引入图片素材；为"好看"而重写成 QML/Web 技术栈（当前 QPainter 方案体积小、无外部依赖，是有意选择）。
- 发版流程：改版本 → `打包exe.bat` → `_upload_release.py vX.Y.Z`（脚本已支持复用同 tag 并替换同名资产）。

## 10. 环境备注（本次交接时的机器状态）

- 项目在 `D:\gitPRO\my_project\喝水提醒`，`.venv` 已建好，PySide6-Essentials 已装。
- pip 源用**腾讯云**（`mirrors.cloud.tencent.com/pypi/simple`）：清华源解析异常、阿里源不可用时验证过可用。
- 本机上 `gh` CLI 未安装；发版靠 `_upload_release.py` 复用 Git 凭据调 GitHub API。
- 若在沙箱/自动化环境里启动 GUI：**进程会在命令结束时被回收**，别以为程序崩了——同一命令内观测是稳定的。真实常驻必须由用户在桌面上双击启动。
