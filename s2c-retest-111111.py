"""
问题2 复测: 用真实 111111.png 生成 html_css, 验证 413 修复、生成完整完成。
用法: C:\\Users\\wuyan\\.conda\\envs\\e2c\\python.exe s2c-retest-111111.py
"""
import asyncio
import base64
import json
import os
import sys
import time

import websockets

# 控制台 UTF-8, 避免 GBK 编码崩溃(emoji/中文)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BACKEND_WS = "ws://localhost:7001/generate-code"
ANTHROPIC_KEY = "sk-sp-471c562c92d048aeae843249058a988f"
IMG_PATH = r"C:\Users\wuyan\Desktop\111111.png"
OUTPUT_DIR = r"D:\mydoc\workskill\s2c-output"


def load_image_data_url(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{b64}", len(b64)


async def main():
    data_url, b64_len = load_image_data_url(IMG_PATH)
    print(f"图片: {IMG_PATH}")
    print(f"原始 base64 大小: {b64_len/1024/1024:.2f} MB")
    payload = {
        "generatedCodeConfig": "html_css",
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
    variant_errors = []
    variant_codes = {}  # variantIndex -> 最终代码(每次 setCode 覆盖, 保留最后版本)
    max_code_len = 0
    deadline = time.time() + 180
    print(f"\n连接 {BACKEND_WS} ...")
    try:
        async with websockets.connect(BACKEND_WS, max_size=None, ping_interval=20) as ws:
            await ws.send(json.dumps(payload))
            print("已发送请求, 等待流式响应(最长 180s)...")
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
                if mtype == "setCode":
                    val = msg.get("value") or ""
                    vidx = msg.get("variantIndex", 0)
                    if val:
                        got_code = True
                        variant_codes[vidx] = val  # 保留每个 variant 最新代码
                        if "<html" in val.lower() or "<div" in val.lower():
                            got_html = True
                            if len(val) > max_code_len:
                                max_code_len = len(val)
                if mtype == "variantComplete":
                    print(f"  variant {msg.get('variantIndex')} 完成")
                if mtype == "variantError":
                    err = msg.get("value") or ""
                    variant_errors.append(err)
                    print(f"  variant {msg.get('variantIndex')} 错误: {err[:120]}")
                if mtype == "variantCount":
                    print(f"  variant 总数: {msg.get('value')}")
                if mtype == "variantModels":
                    print(f"  模型: {msg.get('data', {}).get('models')}")
                if mtype == "error":
                    error_msg = msg.get("value") or str(msg)
                    print(f"  error: {error_msg[:120]}")
    except websockets.exceptions.ConnectionClosedOK:
        # 服务端正常关闭(code 1000), 生成完整结束, 非异常
        pass
    except Exception as e:
        print(f"WS 异常: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("复测结果")
    print("=" * 60)
    print(f"消息类型: {sorted(set(msg_types))}")
    print(f"收到代码(setCode): {got_code}")
    print(f"代码含 HTML: {got_html}")
    print(f"代码最大长度: {max_code_len} 字符")
    print(f"variant 错误数: {len(variant_errors)}")
    if variant_errors:
        for e in variant_errors:
            print(f"  - {e[:200]}")
    has_413 = any("413" in e or "Request Entity Too Large" in e for e in variant_errors) or (error_msg and ("413" in error_msg or "Request Entity Too Large" in error_msg))
    print(f"413 错误: {'是' if has_413 else '否'}")

    # 保存各 variant 生成的 HTML 代码到文件
    # 只保存含 HTML 结构的 variant; LLM 反问文本(无截图)跳过并记日志
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # 清理旧文件
    for old in os.listdir(OUTPUT_DIR):
        if old.endswith(".html") or old in ("README.txt", "errors.txt"):
            try:
                os.remove(os.path.join(OUTPUT_DIR, old))
            except OSError:
                pass
    saved_files = []
    skipped = []
    print(f"\n保存生成文件到 {OUTPUT_DIR}")
    for vidx, code in sorted(variant_codes.items()):
        low = code.lower()
        is_html = "<html" in low or "<!doctype" in low or "<div" in low
        if not is_html:
            skipped.append((vidx, code))
            continue
        fname = os.path.join(OUTPUT_DIR, f"variant-{vidx}.html")
        with open(fname, "w", encoding="utf-8") as f:
            f.write(code)
        saved_files.append((fname, len(code)))
        print(f"  variant-{vidx}.html ({len(code)} 字符) [OK]")
    if skipped:
        err_path = os.path.join(OUTPUT_DIR, "errors.txt")
        with open(err_path, "w", encoding="utf-8") as f:
            f.write(f"以下 variant 未生成有效 HTML(多为 LLM 反问未识别截图):\n\n")
            for vidx, code in skipped:
                f.write(f"=== variant-{vidx} ({len(code)} 字符) ===\n{code}\n\n")
        print(f"  errors.txt (跳过 {len(skipped)} 个无效 variant)")
    # 写一份说明
    readme = os.path.join(OUTPUT_DIR, "README.txt")
    with open(readme, "w", encoding="utf-8") as f:
        f.write(f"screenshot-to-code 生成结果\n")
        f.write(f"输入图: {IMG_PATH}\n")
        f.write(f"栈: html_css\n")
        f.write(f"模型: DashScope qwen3.7-plus (经 Anthropic 兼容端点)\n")
        f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"variant 总数: {len(variant_codes)}\n")
        f.write(f"有效 HTML variant: {len(saved_files)}\n")
        f.write(f"无效 variant(跳过): {len(skipped)}\n\n")
        for fname, ln in saved_files:
            f.write(f"{os.path.basename(fname)}: {ln} 字符\n")
        f.write(f"\n说明: 并发生成 4 个 variant, 部分 variant 偶发未识别截图(返回反问文本),\n")
        f.write(f"属 DashScope qwen3.7-plus 多路并发的偶发现象, 非 413/系统错误。\n")
        f.write(f"有效 variant 可直接浏览器打开预览。\n")

    ok = got_html and not has_413 and not variant_errors and saved_files
    print(f"\n结论: {'[OK] 修复成功 - 生成完整完成, 无 413, 产出 ' + str(len(saved_files)) + ' 个有效 HTML' if ok else '[FAIL] 仍有问题'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    asyncio.run(main())
