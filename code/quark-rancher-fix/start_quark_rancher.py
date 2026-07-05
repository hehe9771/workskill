"""
启动夸克浏览器并自动修复 Rancher 登录页密码自动填充问题。
用法：运行此脚本即可启动夸克浏览器，修复会自动注入。
"""
import subprocess, time, requests, json, websocket, sys, os

RANCHER_URL = "https://rancher.nbmarket.cn/dashboard/auth/login"
QUARK_EXE = r"C:\Program Files\Quark\quark.exe"
CDP_PORT = 9222

FIX_SCRIPT = """
(function() {
    'use strict';
    const observer = new MutationObserver(() => fixInputs());

    function fixInputs() {
        const isLoginPage = window.location.href.includes('auth/login');
        if (!isLoginPage) return;

        document.querySelectorAll('input[type="text"][autocomplete="off"]').forEach(input => {
            input.setAttribute('autocomplete', 'username');
            if (!input.name) input.setAttribute('name', 'username');
        });

        document.querySelectorAll('input[type="password"][autocomplete="off"]').forEach(input => {
            input.setAttribute('autocomplete', 'current-password');
            if (!input.name) input.setAttribute('name', 'password');
        });

        document.querySelectorAll('form[autocomplete="off"]').forEach(form => {
            form.setAttribute('autocomplete', 'on');
        });
    }

    if (document.body) fixInputs();
    observer.observe(document.documentElement || document, {
        childList: true, subtree: true, attributes: true,
        attributeFilter: ['autocomplete', 'type']
    });
    document.addEventListener('DOMContentLoaded', fixInputs);
    setTimeout(fixInputs, 500);
    setTimeout(fixInputs, 1500);
    setTimeout(fixInputs, 3000);
})();
"""

def wait_for_cdp(timeout=15):
    """等待 CDP 可用"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"http://localhost:{CDP_PORT}/json/version", timeout=2)
            if r.status_code == 200:
                return True
        except:
            pass
        time.sleep(0.5)
    return False

def inject_fix():
    """注入修复脚本到所有 Rancher 相关页面"""
    try:
        pages = requests.get(f"http://localhost:{CDP_PORT}/json").json()
        for page in pages:
            if page.get("type") != "page":
                continue
            try:
                ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=5)
                msg_id = 1
                ws.send(json.dumps({
                    "id": msg_id,
                    "method": "Page.addScriptToEvaluateOnNewDocument",
                    "params": {"source": FIX_SCRIPT}
                }))
                # 等待响应
                t = time.time()
                while time.time() - t < 3:
                    try:
                        ws.settimeout(1)
                        r = json.loads(ws.recv())
                        if r.get("id") == msg_id:
                            print(f"[OK] 已注入修复到: {page.get('url', '?')[:60]}")
                            break
                    except:
                        break
                ws.close()
            except Exception as e:
                pass
    except Exception as e:
        print(f"[WARN] 注入失败: {e}")

def main():
    # 1. 启动夸克浏览器（带远程调试）
    print("启动夸克浏览器...")
    subprocess.Popen([
        QUARK_EXE,
        f"--remote-debugging-port={CDP_PORT}",
        "--remote-allow-origins=*"
    ])

    # 2. 等待 CDP 就绪
    print("等待浏览器启动...")
    if not wait_for_cdp():
        print("[ERROR] 浏览器启动超时")
        sys.exit(1)
    print("浏览器已启动")

    # 3. 注入修复脚本
    time.sleep(2)
    inject_fix()

    # 4. 打开 Rancher 登录页
    time.sleep(1)
    subprocess.Popen([QUARK_EXE, RANCHER_URL])

    print("\n[DONE] 夸克浏览器已启动，修复已注入")
    print("打开 Rancher 登录页后，点击用户名框即可看到密码建议")

if __name__ == "__main__":
    main()
