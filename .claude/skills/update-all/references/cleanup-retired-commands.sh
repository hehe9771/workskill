#!/usr/bin/env bash
# 坑 7b：退役命令副本自动清理（update-all v2.4.0，由 SKILL.md Phase 2 对账块挂载）
# 语义：用户级 ~/.claude/commands/<n>.md 的名字出现在某 marketplace 克隆的
#       legacy-command-shims/commands/ 中 = 上游已退役该命令（功能收编为技能）。
# 处置：与上游"退役前最后版本"（commands/<n>.md 的删除提交的父版本）逐字节一致
#       → 纯未自定义副本，自动移除并记日志；不一致 → 疑含自定义，仅 WARN 留人工。
# 日志：所有输出由调用方重定向进 $LOG_FILE，行格式与对账块一致（[WARN] [P*]）。
set -u
CMD_DIR="$HOME/.claude/commands"
removed=0; kept=0
shopt -s nullglob
for mp in "$HOME"/.claude/plugins/marketplaces/*/; do
  [ -d "$mp/legacy-command-shims/commands" ] || continue
  for shim in "$mp"/legacy-command-shims/commands/*.md; do
    n=$(basename "$shim")
    u="$CMD_DIR/$n"
    [ -f "$u" ] || continue
    dcommit=$(git -C "$mp" log --diff-filter=D --format=%H -1 -- "commands/$n" 2>/dev/null)
    if [ -n "$dcommit" ] && git -C "$mp" show "${dcommit}^:commands/$n" 2>/dev/null | cmp -s - "$u"; then
      rm -f "$u" && echo "[$(date '+%H:%M:%S')] [WARN] [P*] 已自动移除退役命令副本 $n（与上游退役前版本逐字节一致，功能由插件技能承接，坑7b）" && removed=$((removed+1))
    else
      echo "[$(date '+%H:%M:%S')] [WARN] [P*] 检测到退役命令副本 $n（内容与上游退役前版本不一致，疑含自定义，未动，人工核对，坑7b）" && kept=$((kept+1))
    fi
  done
done
echo "[$(date '+%H:%M:%S')] [P*] 坑7b 退役命令清理完成：自动移除 $removed，留人工 $kept"
