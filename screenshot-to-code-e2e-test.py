"""
screenshot-to-code 部署端到端测试
验证: 容器健康 + DashScope qwen3.7-plus 通路 + 前后端连通

用法:
  C:\\Users\\wuyan\\.conda\\envs\\e2c\\python.exe screenshot-to-code-e2e-test.py
"""
import asyncio
import base64
import io
import json
import subprocess
import sys
import time
import urllib.request

import websockets
from PIL import Image, ImageDraw, ImageFont

BACKEND_HTTP = "http://localhost:7001"
BACKEND_WS = "ws://localhost:7001/generate-code"
FRONTEND_HTTP = "http://localhost:5174"
ANTHROPIC_KEY = "sk-sp-471c562c92d048aeae843249058a988f"

results = []


def record(name, ok, detail=""):
    results.append((name, ok, detail))
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {name} {('- ' + detail) if detail else ''}")


def http_get(url, timeout=5):
    """返回状态码。用 curl 子进程(与浏览器验证一致), urllib 对 Vite dev 会误判 404。"""
    try:
        r = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             "-H", "User-Agent: Mozilla/5.0", "--max-time", str(timeout), url],
            capture_output=True, text=True, timeout=timeout + 5)
        code = r.stdout.strip()
        return int(code) if code.isdigit() else f"ERR: {r.stderr.strip()}"
    except Exception as e:
        return f"ERR: {e}"


def make_test_image_data_url():
    """生成 480x300 白底黑字 'Hello World' 测试图，返回 data URL。"""
    img = Image.new("RGB", (480, 300), color="white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 48)
    except Exception:
        font = ImageFont.load_default()
    draw.text((60, 120), "Hello World", fill="black", font=font)
    draw.rectangle([40, 40, 440, 260], outline="blue", width=3)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


async def test_ws_codegen():
    """核心: 连 WS /generate-code, 发截图, 验证 DashScope 返回 HTML 代码。"""
    data_url = make_test_image_data_url()
    payload = {
        "generatedCodeConfig": "html_tailwind",
        "inputMode": "image",
        "openAiApiKey": None,
        "anthropicApiKey": ANTHROPIC_KEY,
        "geminiApiKey": None,
        "openAiBaseURL": None,
        "isImageGenerationEnabled": False,
        "generationType": "create",
        "prompt": {"type": "image", "content": data_url},
        "history": [],
        "fileState": None,
        "optionCodes": [],
        "designSystem": None,
    }
    msg_types = []
    got_code = False
    got_html = False
    error_msg = None
    deadline = time.time() + 120
    try:
        async with websockets.connect(BACKEND_WS, max_size=None, ping_interval=20) as ws:
            await ws.send(json.dumps(payload))
            while time.time() < deadline:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=10)
                except asyncio.TimeoutError:
                    if got_code:
                        break
                    continue
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                mtype = msg.get("type")
                if mtype:
                    msg_types.append(mtype)
                if mtype in ("status",):
                    continue
                if mtype == "setCode":
                    val = msg.get("value") or ""
                    if val:
                        got_code = True
                        if "<html" in val.lower() or "<div" in val.lower():
                            got_html = True
                if mtype in ("variantComplete", "variantStatus"):
                    got_code = True
                if mtype in ("error",) or "error" in str(mtype).lower():
                    error_msg = msg.get("value") or msg.get("message") or str(msg)
    except Exception as e:
        record("WS 连接 /generate-code", False, f"异常: {e}")
        return
    uniq = sorted(set(msg_types))
    record("WS 连接 /generate-code", True, f"消息类型: {uniq}")
    record("DashScope 返回代码(setCode)", got_code, f"got_code={got_code} error={error_msg}")
    record("返回内容含 HTML", got_html, "含 <html>/<div> 标签")
    if error_msg:
        record("无错误消息", False, error_msg[:200])
    else:
        record("无错误消息", True)


async def main():
    print("=" * 60)
    print("screenshot-to-code E2E 测试")
    print("=" * 60)
    # Phase 1: 容器健康
    print("\n--- Phase 1: 容器健康 ---")
    b = http_get(BACKEND_HTTP)
    record("backend HTTP 7001", b == 200, f"status={b}")
    f = http_get(FRONTEND_HTTP)
    record("frontend HTTP 5174", f == 200, f"status={f}")
    # Phase 2: DashScope 通路(核心)
    print("\n--- Phase 2: DashScope qwen3.7-plus 通路 ---")
    await test_ws_codegen()
    # Phase 3: 前端页面可达
    print("\n--- Phase 3: 前后端连通配置 ---")
    try:
        r = subprocess.run(
            ["curl", "-s", "-H", "User-Agent: Mozilla/5.0", "--max-time", "5", FRONTEND_HTTP],
            capture_output=True, text=True, timeout=10)
        html = r.stdout
        has_root = "<div id=\"root\"" in html or "id=root" in html or "<html" in html.lower()
        record("前端 index.html 可达", has_root, f"len={len(html)}")
    except Exception as e:
        record("前端 index.html 可达", False, f"ERR: {e}")
    # 报告
    print("\n" + "=" * 60)
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"结果: {passed}/{total} PASS")
    print("=" * 60)
    failed = [n for n, ok, _ in results if not ok]
    if failed:
        print("失败项:")
        for n in failed:
            print(f"  - {n}")
        sys.exit(1)
    else:
        print("全部通过 ✅ 安装验证成功")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
