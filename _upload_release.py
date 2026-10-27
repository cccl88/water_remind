"""创建 GitHub Release 并上传 exe（复用本机 Git 凭据，token 不打印）"""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

REPO = "cccl88/water_remind"
API = "https://api.github.com"


def get_cred():
    p = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True,
        text=True,
    )
    user = token = None
    for line in (p.stdout or "").splitlines():
        if line.startswith("username="):
            user = line.split("=", 1)[1]
        elif line.startswith("password="):
            token = line.split("=", 1)[1]
    return user, token


def api(path, token, method="GET", data=None):
    req = urllib.request.Request(API + path, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "water-reminder-release")
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, body) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


def main():
    user, token = get_cred()
    if not token:
        print("NO_CREDENTIAL: 无法从本机 Git 凭据获取 token")
        return 1
    print("credential user:", user)

    st, me = api("/user", token)
    print("auth status:", st, "login:", me.get("login", "?"))
    if st != 200:
        print("AUTH_FAIL", me)
        return 1

    st, rels = api(f"/repos/{REPO}/releases", token)
    print("list releases:", st, [r.get("tag_name") for r in rels] if isinstance(rels, list) else rels)

    exe = "dist/WaterReminder.exe"
    if not os.path.exists(exe):
        print("EXE_NOT_FOUND", exe)
        return 1
    size_mb = round(os.path.getsize(exe) / 1048576, 1)

    body = (
        "## 喝水提醒 WaterReminder v1.0.0\n\n"
        "Windows 桌面喝水提醒：静默无提示音，提醒从屏幕顶部滑入。\n\n"
        "### 下载\n"
        f"- `WaterReminder.exe`（{size_mb} MB，单文件，无需安装 Python，Windows 10/11）\n\n"
        "### 功能\n"
        "- 提醒间隔 5~180 分钟可调，改完立即生效\n"
        "- 静默提醒：自绘弹窗，不播放任何声音\n"
        "- 可设提醒时段、稍后顺延、一键暂停\n"
        "- 饮水统计：今日进度环、近 7 天柱状图、连续达标天数\n"
        "- 系统托盘常驻、开机自启、浅色/深色主题\n\n"
        "### 使用\n"
        "双击运行，托盘出现水滴图标；关窗口只是最小化到托盘，右键可打卡 / 暂停 / 退出。\n"
        "首次运行若被 SmartScreen 拦截，点「更多信息 → 仍要运行」（个人项目未做代码签名）。\n\n"
        "### 数据与设置\n"
        "保存在 `%APPDATA%\\WaterReminder\\`，不在程序目录，重装不丢。\n"
    )

    st, rel = api(
        f"/repos/{REPO}/releases", token, method="POST",
        data={"tag_name": "v1.0.0", "name": "v1.0.0 喝水提醒", "body": body, "draft": False, "prerelease": False},
    )
    if st not in (200, 201):
        print("CREATE_FAIL", st, rel)
        return 1
    rel_id = rel["id"]
    print("release created:", rel["html_url"])

    # 上传 exe
    up = f"https://uploads.github.com/repos/{REPO}/releases/{rel_id}/assets?name=WaterReminder.exe"
    with open(exe, "rb") as f:
        data = f.read()
    req = urllib.request.Request(up, method="POST", data=data)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Content-Type", "application/octet-stream")
    req.add_header("User-Agent", "water-reminder-release")
    try:
        with urllib.request.urlopen(req) as r:
            res = json.loads(r.read().decode())
            print("uploaded:", res.get("name"), res.get("size"), "bytes")
            print("download:", res.get("browser_download_url"))
    except urllib.error.HTTPError as e:
        print("UPLOAD_FAIL", e.code, e.read().decode()[:300])
        return 1

    print("RELEASE_OK:", rel["html_url"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
