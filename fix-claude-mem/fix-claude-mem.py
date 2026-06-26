#!/usr/bin/env python3
"""
fix-claude-mem.py — claude-mem 插件安装后一键修复脚本

解决的问题：
1. hook 阻塞 Claude Code（worker 不可达时 exit 1 而非 continue:true）
2. Chroma 向量搜索在 Windows 上失败（cmd.exe 不识别双引号内的 < 重定向）
3. 模型硬编码为 claude-haiku-4-5-20251001（DashScope 不支持）
4. 认证信息不同步（worker 读不到 Claude Code 的 token/url/model）
5. mcp-server.cjs dirname 解析失败（import.meta 在 CommonJS .cjs 中无效）

使用方式：
  python fix-claude-mem.py

每次 claude-mem 插件重新安装/更新后运行一次即可。
"""

import sys

from fixers import (
    find_latest_cache_version,
    fix_hooks,
    fix_mcp_server_script,
    fix_worker_script,
    create_sync_script,
    update_mem_settings,
    run_sync,
)


def main():
    print("=" * 60)
    print("  claude-mem 安装后修复脚本")
    print("=" * 60)
    print()

    cache_dir = find_latest_cache_version()
    if not cache_dir:
        print("[ERROR] claude-mem cache not found!")
        print("        Please install the plugin first:")
        print("        /plugin marketplace add thedotmack/claude-mem")
        print("        /plugin install claude-mem")
        sys.exit(1)

    print(f"[1/6] Found cache: {cache_dir.name}")

    print(f"\n[2/6] Fixing hooks (continue:true fallback + sync-env)...")
    hooks_path = cache_dir / "hooks" / "hooks.json"
    fix_hooks(hooks_path)

    print(f"\n[3/6] Fixing mcp-server.cjs (dirname resolution for CommonJS)...")
    mcp_server_path = cache_dir / "scripts" / "mcp-server.cjs"
    fix_mcp_server_script(mcp_server_path)

    print(f"\n[4/6] Fixing worker (cmd.exe < escaping)...")
    worker_path = cache_dir / "scripts" / "worker-service.cjs"
    fix_worker_script(worker_path)

    print(f"\n[5/6] Setting up dynamic sync...")
    create_sync_script()
    update_mem_settings()

    print(f"\n[6/6] Generating .env from Claude Code settings...")
    run_sync()

    print()
    print("=" * 60)
    print("  Done! 请重启 Claude Code 使修复生效。")
    print("=" * 60)


if __name__ == "__main__":
    main()
