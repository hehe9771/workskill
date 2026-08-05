# -*- coding: utf-8 -*-
"""统计 Claude Code 本地会话的 token 用量。

数据源: ~/.claude/projects/*/*.jsonl
口径: 与 ccusage 一致, 按 (message.id, requestId) 去重, 避免会话续接/压缩导致的重复计数。
"""
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECTS_DIR = Path(os.environ["USERPROFILE"]) / ".claude" / "projects"
FIELDS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")


def parse_ts(ts):
    """ISO 时间戳 -> 本地日期 (YYYY-MM-DD)。"""
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return dt.astimezone().date().isoformat()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    seen = set()  # (message_id, request_id) 去重键
    grand = defaultdict(int)
    daily = defaultdict(lambda: defaultdict(int))
    files = 0
    bad_lines = 0

    for proj in PROJECTS_DIR.iterdir():
        if not proj.is_dir():
            continue
        for f in proj.rglob("*.jsonl"):
            files += 1
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if '"usage"' not in line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        bad_lines += 1
                        continue
                    msg = rec.get("message") or {}
                    usage = msg.get("usage")
                    if not usage:
                        continue
                    key = (msg.get("id"), rec.get("requestId"))
                    if key != (None, None) and key in seen:
                        continue
                    seen.add(key)
                    ts = rec.get("timestamp")
                    if not ts:
                        continue
                    day = parse_ts(ts)
                    for fld in FIELDS:
                        val = usage.get(fld) or 0
                        grand[fld] += val
                        daily[day][fld] += val

    total = sum(grand.values())
    print(f"扫描文件: {files}, 跳过坏行: {bad_lines}, 去重后记录: {len(seen)}")
    print("=" * 92)
    print("总计 (全部历史):")
    print(f"  输入 input:                 {grand['input_tokens']:>16,}")
    print(f"  缓存创建 cache_creation:    {grand['cache_creation_input_tokens']:>16,}")
    print(f"  缓存读取 cache_read:        {grand['cache_read_input_tokens']:>16,}")
    print(f"  输出 output:                {grand['output_tokens']:>16,}")
    print(f"  ── 合计:                    {total:>16,}")
    print("=" * 92)

    today = datetime.now().astimezone().date()
    cutoff = (today - timedelta(days=9)).isoformat()
    print(f"最近 10 天每日用量 (截止 {today.isoformat()}):")
    print(f"{'日期':<12}{'input':>12}{'cache_create':>14}{'cache_read':>14}{'output':>12}{'合计':>14}")
    ten_day_total = 0
    for i in range(10):
        day = (today - timedelta(days=9 - i)).isoformat()
        d = daily.get(day)
        if d:
            day_sum = sum(d.values())
            ten_day_total += day_sum
            print(f"{day:<12}{d['input_tokens']:>12,}{d['cache_creation_input_tokens']:>14,}"
                  f"{d['cache_read_input_tokens']:>14,}{d['output_tokens']:>12,}{day_sum:>14,}")
        else:
            print(f"{day:<12}{'0':>12}{'0':>14}{'0':>14}{'0':>12}{'0':>14}")
    print("-" * 92)
    print(f"{'10天合计':<12}{ten_day_total:>66,}")


if __name__ == "__main__":
    sys.exit(main())
