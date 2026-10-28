# 喝水提醒 WaterReminder

一个安静、好看的 Windows 桌面喝水提醒工具——现在由一只 **Q 版桌宠**亲自盯着你喝水。全程**不发出任何声音**。

![桌宠提醒](assets/pet_preview.png)

## 桌宠「凛」

白发双马尾的 Q 版小人，常驻桌面角落。到点了她会跳起来、冒出气泡催你喝水；平时会呼吸浮动、偶尔眨眼，可以随便拖动，点她一下还会害羞。

**三种性格随意切换**（设置里随时改，台词全套不同）：

| 性格 | 风格 | 提醒时她会说 |
| --- | --- | --- |
| 傲娇（默认） | 口是心非 | "你该不会打算一直不喝水吧？真是拿你没办法……快去喝！" |
| 温柔 | 轻声细语 | "工作久了别忘了喝水哦，对身体好。" |
| 撒娇 | 软磨硬泡 | "呐呐～一起喝水好不好嘛～" |

![三种性格](assets/personas.png)

- **拖动**：按住左键拖到桌面任意位置，自动记住
- **点击**：她会应你一句（每种性格反应不同）
- **右键**：喝了 / 稍后再说 / 暂停 / 打开设置 / 藏起来 / 退出
- **提醒气泡**自带按钮：喝了 / 稍后 / 跳过，不用打开主窗口
- 也可以关掉桌宠、只保留传统的顶部卡片提醒（或两个都要）

> 角色为**原创形象**（仅使用白发、红发夹、双马尾、呆毛等通用二次元元素），代码全程程序化绘制，不含任何第三方素材，与任何现有作品角色无关，可放心使用与分发。

## 主界面与提醒卡片

![主界面](assets/preview_main.png)
![提醒弹窗](assets/preview_popup.png)

<details>
<summary>深色模式效果</summary>

![深色主界面](assets/preview_main_dark.png)
![深色弹窗](assets/preview_popup_dark.png)

</details>

## 特性

- **桌宠提醒**：原创 Q 版角色「凛」，傲娇 / 温柔 / 撒娇三种性格全套台词，可改名、可拖动、可互动
- **间隔自由可调**：5 ~ 180 分钟滑块随便调，改完立即生效
- **绝对静音**：全部界面自绘，不走系统通知通道，不加载任何音频文件
- **不打扰**：可设提醒时段（默认 08:00–22:00），深夜自动静默
- **饮水统计**：今日进度环、最近 7 天柱状图、连续达标天数，支持打卡与撤销
- **系统托盘常驻**：关闭窗口只是最小化到托盘，右键可打卡、暂停、退出
- **开机自启**：一键写入注册表（不写也完全不影响使用）
- **浅色 / 深色主题**
- **单实例**：重复启动只会唤醒已有窗口

## 快速开始

### 方式一：直接运行 exe（推荐）

1. 到本仓库 [Releases](../../releases) 下载 `WaterReminder.exe`；或自己打包（见下方「打包 exe」）
2. 双击运行，桌宠会出现在桌面右下角，托盘出现水滴图标

> exe 体积约 40~60 MB（内含 Qt 运行库），Windows 10/11 可用。首次运行若被 SmartScreen 拦截，点「更多信息 → 仍要运行」即可（个人项目未做代码签名）。

### 方式二：源码运行

```bat
安装依赖.bat      :: 首次运行：创建 .venv 并安装 PySide6（国内走腾讯云镜像）
启动喝水提醒.bat  :: 之后每次双击这个即可
```

也可以手动执行：

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\pythonw.exe main.py
```

## 使用说明

| 区域 | 说明 |
| --- | --- |
| 提醒间隔 | 5~180 分钟滑块，默认 45 分钟 |
| 提醒时段 | 默认 08:00–22:00，超出时段不提醒 |
| 稍后再说顺延 | 点「稍后」后 N 分钟再提醒（默认 10 分钟） |
| 每杯水量 / 每日目标 | 默认 250 ml / 2000 ml |
| 启用桌宠 | 关闭后退回传统的顶部卡片提醒 |
| 性格 | 傲娇 / 温柔 / 撒娇，切换后全部台词生效 |
| 昵称 | 给桌宠起名字（默认「凛」） |
| 同时弹出卡片提醒 | 桌宠气泡之外，再弹一张顶部卡片（默认关） |
| 我喝了一杯 | 手动补记一杯，右侧「撤销」可删除最后一次记录 |
| 暂停提醒 | 临时关闭计时，再点一次恢复 |
| 测试提醒 | 立刻预览一次提醒效果 |

## 打包 exe

```bat
打包exe.bat
```

产物在 `dist\WaterReminder.exe`。等价于：

```bash
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --noconsole ^
    --name WaterReminder --icon app.ico --hidden-import PySide6.QtNetwork main.py
```

> `dist/`、`build/`、`*.spec` 已在 `.gitignore` 中忽略，不会推到 GitHub。

一键发版（复用本机 Git 凭据，无需手填 token）：

```bash
.venv\Scripts\python.exe _upload_release.py   # 创建 Release 并上传 dist\WaterReminder.exe
```

## 数据存放位置

配置与饮水记录保存在（不在项目目录，重装/移动项目都不丢）：

```
%APPDATA%\WaterReminder\config.json     # 设置项
%APPDATA%\WaterReminder\history.json    # 每日饮水记录
```

## 目录结构

```
main.py              入口：调度、系统托盘、单实例、桌宠总控
core/config.py       配置项读写、开机自启（注册表）
core/store.py        饮水记录与统计（JSON）
pet/character.py     桌宠角色程序化绘制（表情/双马尾/呆毛/呼吸浮动）
pet/personality.py   三种性格台词库（原创文案）
pet/bubble.py        桌宠台词气泡（可带操作按钮）
pet/pet_window.py    桌宠窗口：拖动/眨眼/跳跃/点击区域穿透/右键菜单
ui/theme.py          浅色/深色配色与 QSS
ui/widgets.py        进度环、柱状图、水滴图标、开关（自绘）
ui/main_window.py    主窗口
ui/popup.py          顶部提醒卡片（桌宠关闭时的备用提醒）
_smoke.py            自测脚本（离屏渲染截图 + 逻辑校验）
_render_char.py / _render_pet.py / _render_personas.py / _render_settings.py   截图工具
_make_icon.py        生成 app.ico
_upload_release.py   一键创建 GitHub Release 并上传 exe
安装依赖.bat / 启动喝水提醒.bat / 打包exe.bat
```

## 常见问题

**Q：会有声音吗？**
不会。桌宠、气泡、卡片全是普通 Qt 窗口，不播放音频；但托盘气泡走的是 Windows 通知通道，若系统开了通知声音，建议在系统通知设置里静音，或忽略该气泡。

**Q：桌宠会挡住我点别的东西吗？**
不会。桌宠窗口做了轮廓遮罩，只有点在角色身上才有响应，透明区域鼠标直接穿透。

**Q：关了窗口程序还在吗？**
在，最小化到托盘了，桌宠也还在。托盘图标右键 →「退出」才是真正退出。

**Q：为什么 exe 这么大？**
PySide6/Qt 运行库体积所致，正常现象。

## 许可证

[MIT](LICENSE)
