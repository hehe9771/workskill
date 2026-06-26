"""
fix-claude-mem 修复逻辑
"""

import json
import os
import subprocess
from pathlib import Path

HOME = Path.home()
CLAUDE_DIR = HOME / ".claude"
PLUGIN_CACHE = CLAUDE_DIR / "plugins" / "cache" / "thedotmack" / "claude-mem"
MEM_DATA_DIR = HOME / ".claude-mem"
SETTINGS_JSON = CLAUDE_DIR / "settings.json"
MEM_SETTINGS = MEM_DATA_DIR / "settings.json"
SYNC_SCRIPT = MEM_DATA_DIR / "sync-env-from-claude.mjs"
ENV_FILE = MEM_DATA_DIR / ".env"

# 必须强制覆盖的模型配置
_MODEL_KEYS = {
    "CLAUDE_MEM_MODEL", "CLAUDE_MEM_TIER_FAST_MODEL",
    "CLAUDE_MEM_TIER_SIMPLE_MODEL", "CLAUDE_MEM_TIER_SMART_MODEL",
    "CLAUDE_MEM_TIER_SUMMARY_MODEL", "CLAUDE_MEM_TIER_ROUTING_ENABLED",
    "ANTHROPIC_MODEL", "ANTHROPIC_DEFAULT_HAIKU_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL", "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "ANTHROPIC_REASONING_MODEL",
}

_M = "qwen3.7-plus"
_DEFAULTS = {
    "CLAUDE_MEM_PROVIDER": "claude", "CLAUDE_MEM_CLAUDE_AUTH_METHOD": "cli",
    "CLAUDE_MEM_WORKER_PORT": "37777", "CLAUDE_MEM_WORKER_HOST": "127.0.0.1",
    "CLAUDE_MEM_DATA_DIR": str(MEM_DATA_DIR), "CLAUDE_MEM_LOG_LEVEL": "INFO",
    "CLAUDE_MEM_MODE": "code", "CLAUDE_MEM_CONTEXT_OBSERVATIONS": "50",
    "CLAUDE_MEM_TIER_ROUTING_ENABLED": "false", "CLAUDE_MEM_CHROMA_ENABLED": "true",
    "CLAUDE_MEM_CHROMA_MODE": "local", "CLAUDE_MEM_FOLDER_CLAUDEMD_ENABLED": "false",
    "CLAUDE_MEM_TRANSCRIPTS_ENABLED": "true",
    "CLAUDE_MEM_MODEL": _M, "CLAUDE_MEM_TIER_FAST_MODEL": _M,
    "CLAUDE_MEM_TIER_SIMPLE_MODEL": _M, "CLAUDE_MEM_TIER_SMART_MODEL": _M,
    "CLAUDE_MEM_TIER_SUMMARY_MODEL": _M,
    "ANTHROPIC_MODEL": _M, "ANTHROPIC_DEFAULT_HAIKU_MODEL": _M,
    "ANTHROPIC_DEFAULT_SONNET_MODEL": _M, "ANTHROPIC_DEFAULT_OPUS_MODEL": _M,
    "ANTHROPIC_REASONING_MODEL": _M,
}


def find_latest_cache_version():
    """找到最新版本的 cache 目录"""
    if not PLUGIN_CACHE.exists():
        return None
    versions = sorted(
        [d for d in PLUGIN_CACHE.iterdir() if d.is_dir() and d.name[0].isdigit()],
        key=lambda d: d.name, reverse=True,
    )
    return versions[0] if versions else None


def fix_hooks(hooks_path: Path) -> bool:
    """修复 hooks.json：容错 + 清空 UserPromptSubmit + sync-env"""
    if not hooks_path.exists():
        print(f"  [SKIP] hooks.json not found: {hooks_path}")
        return False

    with open(hooks_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    hooks = data.get("hooks", {})
    changed = False

    if hooks.get("UserPromptSubmit") != []:
        hooks["UserPromptSubmit"] = []
        changed = True

    for hook_type in ["Setup", "SessionStart", "PostToolUse", "PreToolUse", "Stop"]:
        for entry in hooks.get(hook_type, []):
            for h in entry.get("hooks", []):
                cmd = h.get("command", "")
                if "worker-service" not in cmd and "bun-runner" not in cmd:
                    continue
                if "exit 1" in cmd and '"continue"' not in cmd:
                    cont = (
                        '{"continue":true,"suppressOutput":true}'
                        if "context" in cmd else '{"continue":true}'
                    )
                    h["command"] = cmd.replace("exit 1; ", f"echo '{cont}'; exit 0; ")
                    changed = True

    sync_cmd = (
        'node "$HOME/.claude-mem/sync-env-from-claude.mjs" 2>/dev/null; '
        'echo \'{"continue":true,"suppressOutput":true}\''
    )
    has_sync = any(
        "sync-env-from-claude" in h.get("command", "")
        for entry in hooks.get("SessionStart", [])
        for h in entry.get("hooks", [])
    )
    if not has_sync:
        hooks.setdefault("SessionStart", []).insert(0, {
            "matcher": "startup|clear|compact",
            "hooks": [{"type": "command", "shell": "bash", "command": sync_cmd, "timeout": 10}],
        })
        changed = True

    if changed:
        with open(hooks_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Fixed hooks: {hooks_path}")
    else:
        print(f"  [OK] Hooks already fixed: {hooks_path}")
    return True


def fix_mcp_server_script(mcp_server_path: Path) -> bool:
    """修复 mcp-server.cjs 的 dirname 解析 bug

    问题：原始代码使用 import.meta.url（ES module 语法），但在 .cjs (CommonJS) 中无效
    解决：改用 __dirname -> __filename -> process.cwd() 回退链，移除 import.meta

    原始代码特征：typeof __dirname<"u" 后跟 fileURLToPath(MP.url) 或类似 import.meta 引用
    修复后代码：__dirname -> __filename -> process.cwd() 三层回退
    """
    if not mcp_server_path.exists():
        print(f"  [SKIP] mcp-server.cjs not found: {mcp_server_path}")
        return False

    content = mcp_server_path.read_text(encoding="utf-8")

    # 已修复的特征：包含 __filename 回退
    fixed_marker = '__dirname<"u"&&__dirname)return __dirname;if(typeof __filename<"u"&&__filename)'

    if fixed_marker in content:
        print(f"  [OK] dirname resolution already patched: {mcp_server_path}")
        return True

    # 原始有问题的代码特征：使用 fileURLToPath 和 MP.url (import.meta 的混淆)
    old_pattern = 'fileURLToPath(MP.url)'
    if old_pattern in content:
        # 找到 dirname 解析函数并替换
        # 原始模式：if(typeof __dirname<"u")return __dirname;try{if(typeof MP<"u"&&MP)return tt.dirname(fileURLToPath(MP.url))}catch{}return process.cwd()
        new_pattern = '__dirname<"u"&&__dirname)return __dirname;if(typeof __filename<"u"&&__filename)return tt.dirname(__filename);C_=!0;return process.cwd()'

        # 替换整个 dirname 解析逻辑
        content = content.replace(
            'if(typeof __dirname<"u")return __dirname;try{if(typeof MP<"u"&&MP)return tt.dirname(fileURLToPath(MP.url))}catch{}return process.cwd()',
            new_pattern
        )
        mcp_server_path.write_text(content, encoding="utf-8")
        print(f"  [OK] Patched dirname resolution in: {mcp_server_path}")
        return True

    # 检查是否有其他变体
    if 'import.meta' in content and '__filename' not in content:
        print(f"  [WARN] Found import.meta reference but pattern not matched")
        print("         Manual inspection may be needed")
        return False

    print(f"  [OK] dirname resolution pattern not found (may be fixed or version changed)")
    return True


def fix_worker_script(worker_path: Path) -> bool:
    """修复 worker-service.cjs 的 bie() cmd.exe 转义"""
    if not worker_path.exists():
        print(f"  [SKIP] worker not found: {worker_path}")
        return False

    content = worker_path.read_text(encoding="utf-8")
    old = (
        r'yie=/[<>|&^()]/;function bie(t)'
        r'{return yie.test(t)?`"${t.replace(/"/g,\'\\\"\')}"`:t}'
    )
    new = r'yie=/[<>|&^()]/;function bie(t){return t.replace(/[<>|&^()]/g,"^$&")}'

    if old in content:
        content = content.replace(old, new)
        worker_path.write_text(content, encoding="utf-8")
        print(f"  [OK] Patched bie() in: {worker_path}")
        return True
    elif new in content:
        print(f"  [OK] bie() already patched: {worker_path}")
        return True
    else:
        print(f"  [WARN] bie() pattern not found in: {worker_path}")
        return False


def create_sync_script():
    """创建 sync-env-from-claude.mjs"""
    MEM_DATA_DIR.mkdir(parents=True, exist_ok=True)
    if SYNC_SCRIPT.exists():
        print(f"  [OK] Sync script exists: {SYNC_SCRIPT}")
        return
    # 从当前 Claude Code settings 动态读取，写入 .env
    script = (
        "#!/usr/bin/env node\n"
        "import { readFileSync, writeFileSync, existsSync } from 'fs';\n"
        "import { join } from 'path';\n"
        "import { homedir } from 'os';\n"
        "const home = homedir();\n"
        "const cfg = join(process.env.CLAUDE_CONFIG_DIR||join(home,'.claude'),'settings.json');\n"
        "const out = join(process.env.CLAUDE_MEM_DATA_DIR||join(home,'.claude-mem'),'.env');\n"
        "if(!existsSync(cfg)){process.exit(0)}\n"
        "let s;try{s=JSON.parse(readFileSync(cfg,'utf-8'))}catch{process.exit(0)}\n"
        "const e=s.env||{};\n"
        "const c={ANTHROPIC_AUTH_TOKEN:e.ANTHROPIC_AUTH_TOKEN||'',ANTHROPIC_API_KEY:e.ANTHROPIC_API_KEY||'',\n"
        "ANTHROPIC_BASE_URL:e.ANTHROPIC_BASE_URL||'',ANTHROPIC_MODEL:e.ANTHROPIC_MODEL||'',\n"
        "ANTHROPIC_DEFAULT_SONNET_MODEL:e.ANTHROPIC_DEFAULT_SONNET_MODEL||'',\n"
        "ANTHROPIC_DEFAULT_HAIKU_MODEL:e.ANTHROPIC_DEFAULT_HAIKU_MODEL||'',\n"
        "ANTHROPIC_DEFAULT_OPUS_MODEL:e.ANTHROPIC_DEFAULT_OPUS_MODEL||''};\n"
        "const l=[`# Synced: ${new Date().toISOString()}`];\n"
        "for(const[k,v]of Object.entries(c))if(v)l.push(`${k}=${v}`);\n"
        "writeFileSync(out,l.join('\\n')+'\\n','utf-8');\n"
        "console.error(`[sync-env] Done -> ${out}`);\n"
    )
    SYNC_SCRIPT.write_text(script, encoding="utf-8")
    print(f"  [OK] Sync script created: {SYNC_SCRIPT}")


def update_mem_settings():
    """更新 claude-mem settings.json（模型覆盖）"""
    MEM_DATA_DIR.mkdir(parents=True, exist_ok=True)
    existing = {}
    if MEM_SETTINGS.exists():
        with open(MEM_SETTINGS, "r", encoding="utf-8") as f:
            existing = json.load(f)
    merged = {**_DEFAULTS, **existing}
    for key in _MODEL_KEYS:
        merged[key] = _DEFAULTS[key]
    with open(MEM_SETTINGS, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    print(f"  [OK] claude-mem settings: {MEM_SETTINGS}")


def run_sync():
    """运行同步脚本生成 .env"""
    if not SYNC_SCRIPT.exists():
        print("  [SKIP] Sync script not found")
        return
    result = subprocess.run(
        ["node", str(SYNC_SCRIPT)],
        capture_output=True, text=True, cwd=str(HOME),
    )
    if result.returncode == 0:
        print(f"  [OK] .env generated: {ENV_FILE}")
    else:
        print(f"  [WARN] Sync failed: {result.stderr.strip()}")
