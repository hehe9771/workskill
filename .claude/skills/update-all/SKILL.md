---
name: update-all
description: 一键更新所有 Claude Code 环境组件 — 市场、插件、npm 全局工具、uv 工具、skills。每个步骤都有验证机制确保更新成功。
version: 1.4.0
source: project-init
allowed-tools: Bash(claude:*) Bash(npm:*) Bash(npx:*) Bash(uv:*) Bash(playwright-cli:*) Bash(specify:*)
---

# 一键更新所有环境组件

## 触发条件

当用户说"更新环境"、"更新所有插件"、"update all"、"升级组件"时，直接执行下方全部命令，无需确认。

## 黑名单（跳过更新）

以下组件已拉黑，**禁止更新**：

| 组件 | 原因 |
|------|------|
| `@anthropic-ai/claude-code` | 自动更新可能导致兼容性问题，需手动控制版本 |
| `claude-mem@thedotmack` | 更新后修复脚本需重跑，手动控制更新时机 |
| `claude-notifications-go@claude-notifications-go` | 1.40.0 上游发布缺 Windows exe(残缺版),需手动控制版本 |
| `claude-mem@thedotmack` | 本地有未上游的 mcp-server.cjs dirname 补丁,自动更新会丢失补丁 |

> 如需更新黑名单中的组件，请手动执行对应命令。

### ⚠️ 重要：技能黑名单挡不住 daemon 自动更新

本技能的黑名单只阻止下方第 6 类的 `claude plugins update` 命令，**挡不住 Claude Code daemon 自身的插件自动更新机制**。实测：黑名单中的 `claude-notifications-go` 仍被 daemon 偷偷升级到残缺的 1.40.0，`understand-anything` 也被升级后留下残缺（缺 dist/node_modules）。

**根治配置**（已在 `~/.claude/settings.json` 的 `env` 段设置）：

```json
{
  "env": {
    "DISABLE_AUTOUPDATER": "1"
  }
}
```

此为总开关，**同时禁用 CLI 本体 + 所有插件的自动更新**。此后插件只在执行本技能第 6 类或手动 `claude plugin update <plugin>` 时更新。注意：仅靠 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` 的等价关系不够（子进程可能未继承），必须显式设 `DISABLE_AUTOUPDATER=1`。改后需重启 daemon 生效。

## 执行原则

**每个更新步骤都必须：**
1. 执行更新命令
2. 立即验证更新结果
3. 验证失败时记录错误但继续后续步骤
4. 最后汇总所有更新结果

## 验证框架

每次执行 update-all 时，**必须先初始化以下变量和函数**，然后所有步骤通过 `record_result` 记录结果。

```bash
# ===== 验证框架初始化（每次 update-all 开头运行） =====
FAILURES=""
PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0
LOG_FILE="$HOME/.claude/update-all.log"
START_TIME=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$START_TIME] ===== update-all 开始 =====" >> "$LOG_FILE"

record_result() {
  local step="$1" status="$2" desc="$3"
  case $status in
    PASS) PASS_COUNT=$((PASS_COUNT+1)); echo "  PASS [$step] $desc" ;;
    FAIL) FAIL_COUNT=$((FAIL_COUNT+1)); FAILURES="$FAILURES $step"; echo "  FAIL [$step] $desc" ;;
    SKIP) SKIP_COUNT=$((SKIP_COUNT+1)); echo "  SKIP [$step] $desc" ;;
  fi
  echo "[$(date '+%H:%M:%S')] [$status] [$step] $desc" >> "$LOG_FILE"
}
```

---

## 更新清单

### 1. npm 全局工具

```bash
# 更新
npm update -g html-to-react-components 2>&1
npm install -g @playwright/cli@latest 2>&1
# [黑名单] npm install -g @anthropic-ai/claude-code@latest

# 验证
if npm list -g html-to-react-components 2>&1 | grep -q html-to-react-components; then
  record_result "1a" "PASS" "html-to-react-components 已更新"
else
  record_result "1a" "FAIL" "html-to-react-components 更新失败"
fi

if npm list -g @playwright/cli 2>&1 | grep -q playwright; then
  record_result "1b" "PASS" "@playwright/cli 已更新"
else
  record_result "1b" "FAIL" "@playwright/cli 更新失败"
fi
```

### 2. gstack 技能包

```bash
# 备份旧版本（可选）
if [ -d ~/.claude/skills/gstack ]; then
  rm -rf ~/.claude/skills/gstack.bak
  mv ~/.claude/skills/gstack ~/.claude/skills/gstack.bak
fi

# 更新
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack 2>&1
cd ~/.claude/skills/gstack && ./setup 2>&1

# 验证
if [ -f ~/.claude/skills/gstack/.git/HEAD ] && [ -f ~/.claude/skills/gstack/setup ]; then
  record_result "2" "PASS" "gstack 已安装且完整"
else
  record_result "2" "FAIL" "gstack 安装不完整"
fi
```

### 2.5. superpowers 用户级副本清理

> **问题根因**：`npx skills@latest add mattpocock/skills` 会在 `~/.claude/skills/superpowers/` 创建静态副本，与 plugin cache（`claude plugins update superpowers@claude-plugins-official`）完全独立。两套同时存在导致 Claude Code 可能加载旧版。
>
> **解决**：删除用户级副本，让 plugin cache 通过 plugin.json 自动加载。

```bash
if [ -d ~/.claude/skills/superpowers ]; then
  USER_VER=$(cat ~/.claude/skills/superpowers/VERSION 2>/dev/null || echo "unknown")
  CACHE_VER=$(ls -td ~/.claude/plugins/cache/claude-plugins-official/superpowers/*/ 2>/dev/null | head -1 | xargs basename)
  if [ "$USER_VER" != "$CACHE_VER" ]; then
    rm -rf ~/.claude/skills/superpowers
    record_result "2.5" "PASS" "superpowers 过期副本已清理 (v$USER_VER -> plugin cache v$CACHE_VER)"
  else
    record_result "2.5" "PASS" "superpowers 版本一致 (v$USER_VER)"
  fi
else
  record_result "2.5" "PASS" "superpowers 无用户级副本（plugin cache 直接生效）"
fi
```

### 2.6. ui-ux-pro-max symlink 退化修复

> **问题根因**：Windows `core.symlinks=false` 下，`claude plugins update` 检出时把 symlink 变成含目标路径的文本文件（30-40B），导致 `search.py` 等不可达。

```bash
UI_CACHE=$(ls -td ~/.claude/plugins/cache/ui-ux-pro-max-skill/ui-ux-pro-max/*/ 2>/dev/null | head -1)
UI_SKILL=~/.claude/skills/ui-ux-pro-max
if [ -d "$UI_CACHE" ] && [ -d "$UI_SKILL" ]; then
  DEGRADED=0
  for item in scripts data; do
    [ -f "$UI_SKILL/$item" ] && [ ! -d "$UI_SKILL/$item" ] && DEGRADED=1
  done
  if [ "$DEGRADED" -eq 1 ]; then
    rm -f "$UI_SKILL/scripts" "$UI_SKILL/data"
    cp -r "$UI_CACHE/src/ui-ux-pro-max/scripts" "$UI_SKILL/scripts"
    cp -r "$UI_CACHE/src/ui-ux-pro-max/data" "$UI_SKILL/data"
    if test -f "$UI_SKILL/scripts/search.py"; then
      record_result "2.6" "PASS" "ui-ux-pro-max symlink 已修复"
    else
      record_result "2.6" "FAIL" "ui-ux-pro-max symlink 修复失败"
    fi
  else
    record_result "2.6" "PASS" "ui-ux-pro-max scripts/data 正常"
  fi
else
  record_result "2.6" "SKIP" "ui-ux-pro-max 未安装"
fi
```

### 3. Playwright Skills

```bash
# 更新
playwright-cli install --skills 2>&1

# 验证
if playwright-cli --version 2>&1 | grep -q "version"; then
  record_result "3" "PASS" "playwright-cli 可用"
else
  record_result "3" "FAIL" "playwright-cli 不可用"
fi
```

### 4. uv 工具 (specify-cli)

```bash
# 清理残留文件（防止 ModuleNotFoundError）
rm -f ~/.local/bin/specify.exe 2>/dev/null || true

# 更新
uv tool install specify-cli --from "git+https://github.com/github/spec-kit.git" --reinstall 2>&1

# 验证
if uv tool list 2>&1 | grep -q specify-cli; then
  record_result "4" "PASS" "specify-cli 已安装"
else
  record_result "4" "FAIL" "specify-cli 安装失败"
fi
```

### 5. Claude Code 市场 (全部)

```bash
# 更新
claude plugins marketplace update 2>&1

# 验证
if claude plugins marketplace list 2>&1 | grep -q "claude-plugins-official"; then
  record_result "5" "PASS" "Claude 市场已更新"
else
  record_result "5" "FAIL" "Claude 市场更新失败"
fi
```

### 6. Claude Code 插件 (逐个更新)

```bash
# 更新（逐个执行，记录每个结果）
PLUGINS_TO_UPDATE="claude-hud@claude-hud ecc@ecc superpowers@claude-plugins-official understand-anything@understand-anything ui-ux-pro-max@ui-ux-pro-max-skill jobs-to-be-done@pm-skills"
STEP6_FAIL=0
for plugin in $PLUGINS_TO_UPDATE; do
  if claude plugins update "$plugin" 2>&1; then
    record_result "6-$plugin" "PASS" "$plugin 已更新"
  else
    record_result "6-$plugin" "FAIL" "$plugin 更新失败"
    STEP6_FAIL=1
  fi
done
# [黑名单] claude plugins update claude-mem@thedotmack
# [黑名单] claude plugins update claude-notifications-go@claude-notifications-go

# 整体验证
if claude plugins list 2>&1 | grep -q "ecc"; then
  record_result "6v" "PASS" "插件列表正常"
else
  record_result "6v" "FAIL" "插件列表异常"
fi
```

### 6.5. ECC 资源同步（plugins update 后必做）

> **问题根因**：`claude plugins update ecc@ecc` 只更新 plugin cache（`~/.claude/plugins/cache/ecc/`），**不会自动同步** rules/agents/skills/commands 到用户级目录。ECC 升级后，本地 rules/agents 仍是旧版（如缺少 Prompt Defense 安全层），新 agent 不生效。
>
> **解决**：每次 ECC 插件更新后，跑 `install.sh --profile full` 重新同步。同时清理旧顶层重复 rules（`rules/common`、`rules/python` 等），避免与新的 `rules/ecc/` 结构双重注入。

```bash
# 定位当前 ECC plugin cache 目录
ECC_DIR=$(ls -td ~/.claude/plugins/cache/ecc/ecc/*/ 2>/dev/null | head -1)
if [ -n "$ECC_DIR" ] && [ -f "$ECC_DIR/install.sh" ]; then
  (cd "$ECC_DIR" && bash install.sh --target claude --profile full 2>&1) | tail -5

  # 清理旧顶层重复 rules（防止与 rules/ecc/ 双重注入）
  for d in common cpp golang kotlin perl php python swift typescript; do
    [ -d "$HOME/.claude/rules/$d" ] && rm -rf "$HOME/.claude/rules/$d"
  done

  # 验证
  AGENTS_N=$(ls ~/.claude/agents/*.md 2>/dev/null | wc -l)
  RULES_N=$(ls ~/.claude/rules/ecc/ 2>/dev/null | grep -v README | wc -l)
  CACHE_AGENTS=$(ls "$ECC_DIR/agents/"*.md 2>/dev/null | wc -l)
  if [ "$AGENTS_N" -ge "$CACHE_AGENTS" ] && [ "$RULES_N" -ge 20 ]; then
    record_result "6.5" "PASS" "ECC 同步完成 (agents=$AGENTS_N rules/ecc=$RULES_N)"
  else
    record_result "6.5" "FAIL" "ECC 同步不完整 (agents=$AGENTS_N/$CACHE_AGENTS rules=$RULES_N)"
  fi
else
  record_result "6.5" "SKIP" "ECC plugin cache 未找到"
fi
```

### 7. Skills 包更新（全量重装）

```bash
# 更新
npx skills@latest add mattpocock/skills 2>&1

# ⚠️ 关键：mattpocock/skills 会把 superpowers 复制到 ~/.claude/skills/superpowers/
# 这与 plugin cache (claude-plugins-official/superpowers) 冲突，产生过期静态副本
if [ -d ~/.claude/skills/superpowers ]; then
  rm -rf ~/.claude/skills/superpowers
  record_result "7" "PASS" "Skills 包已更新 + superpowers 冲突副本已清理"
else
  record_result "7" "PASS" "Skills 包已更新"
fi
```

---

## 更新后汇总 + 自动健康检查

以下步骤在所有更新步骤完成后**自动执行**，不需要手动触发：

```bash
# ===== H1: understand-anything 构建产物 =====
UA=~/.claude/plugins/cache/understand-anything/understand-anything
CUR=$(ls -td $UA/*/ 2>/dev/null | while read d; do [ -f "$d/.orphaned_at" ] || { echo "$d"; break; }; done)
if [ -n "$CUR" ] && [ ! -f "$CUR/packages/core/dist/index.js" ]; then
  (cd "$CUR" && pnpm install && pnpm -r build) 2>&1 >/dev/null
  test -f "$CUR/packages/core/dist/index.js" && record_result "H1" "PASS" "understand-anything dist 已构建" || record_result "H1" "FAIL" "understand-anything 构建失败"
else
  record_result "H1" "PASS" "understand-anything dist 正常"
fi

# ===== H2: (已在步骤 2.6 覆盖，此处验证最终状态) =====
UI_SKILL=~/.claude/skills/ui-ux-pro-max
if [ -d "$UI_SKILL" ]; then
  DEGRADED=0
  for item in scripts data; do
    [ -f "$UI_SKILL/$item" ] && [ ! -d "$UI_SKILL/$item" ] && DEGRADED=1
  done
  [ "$DEGRADED" -eq 0 ] && record_result "H2" "PASS" "ui-ux-pro-max symlink 正常" || record_result "H2" "FAIL" "ui-ux-pro-max symlink 仍退化"
else
  record_result "H2" "SKIP" "ui-ux-pro-max 未安装"
fi

# ===== H3: claude-notifications-go exe 检查 =====
NG=~/.claude/plugins/cache/claude-notifications-go/claude-notifications-go
for v in $NG/*/; do
  [ ! -f "$v/.orphaned_at" ] && [ ! -f "$v/bin/claude-notifications-windows-amd64.exe" ] && rm -rf "$v"
done
DIR=$(ls -td $NG/*/ 2>/dev/null | head -1)
test -f "${DIR}bin/claude-notifications-windows-amd64.exe" && record_result "H3" "PASS" "claude-notifications-go exe 存在" || record_result "H3" "FAIL" "claude-notifications-go 无可用 exe"

# ===== H4: claude-mem 版本监控 =====
CM=~/.claude/plugins/cache/thedotmack
NON_ORPH=$(ls -d $CM/*/*/ 2>/dev/null | while read d; do [ -f "$d/.orphaned_at" ] || echo "$d"; done | wc -l)
[ "$NON_ORPH" -le 1 ] && record_result "H4" "PASS" "claude-mem 单版本（补丁在位）" || record_result "H4" "FAIL" "claude-mem 多版本（补丁可能丢失）"

# ===== H5: temp_git 清理 =====
rm -rf ~/.claude/plugins/cache/temp_git_* 2>/dev/null
record_result "H5" "PASS" "temp_git 残留已清理"

# ===== H6: ECC 漂移检查 =====
ECC_DIR=$(ls -td ~/.claude/plugins/cache/ecc/ecc/*/ 2>/dev/null | head -1)
if [ -n "$ECC_DIR" ]; then
  CACHE_AGENTS=$(ls "$ECC_DIR/agents/"*.md 2>/dev/null | wc -l)
  INSTALLED_AGENTS=$(ls ~/.claude/agents/*.md 2>/dev/null | wc -l)
  [ "$INSTALLED_AGENTS" -ge "$CACHE_AGENTS" ] && record_result "H6" "PASS" "ECC 无漂移 (agents=$INSTALLED_AGENTS)" || record_result "H6" "FAIL" "ECC 漂移 (cache=$CACHE_AGENTS installed=$INSTALLED_AGENTS)"
  # 清理旧顶层重复 rules
  for d in common cpp golang kotlin perl php python swift typescript; do
    [ -d "$HOME/.claude/rules/$d" ] && rm -rf "$HOME/.claude/rules/$d"
  done
else
  record_result "H6" "SKIP" "ECC 未安装"
fi

# ===== H7: orphaned + temp_git 清理 =====
find ~/.claude/plugins/cache -name ".orphaned_at" -exec dirname {} \; 2>/dev/null | while read d; do rm -rf "$d"; done
rm -rf ~/.claude/plugins/cache/temp_git_* 2>/dev/null
record_result "H7" "PASS" "orphaned + temp_git 已清理"

# ===== H8: 全插件用户级副本漂移 =====
[ -d ~/.claude/skills/superpowers ] && { rm -rf ~/.claude/skills/superpowers; record_result "H8" "PASS" "superpowers 副本已清理"; } || record_result "H8" "PASS" "无用户级副本漂移"

# ===== 最终汇总表 =====
echo ""
echo "============================================================"
echo "           update-all 执行汇总"
echo "============================================================"
echo ""
echo "  开始时间: $START_TIME"
echo "  结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "  PASS: $PASS_COUNT"
echo "  FAIL: $FAIL_COUNT"
echo "  SKIP: $SKIP_COUNT"
echo ""
if [ -n "$FAILURES" ]; then
  echo "  失败步骤:$FAILURES"
  echo "  请检查上述失败项并手动修复"
else
  echo "  所有步骤通过 ✅"
fi
echo ""
echo "  日志: ~/.claude/update-all.log"
echo "  提示: 更新完成后需重启 Claude Code daemon 使插件生效"
echo "============================================================"

echo "[$(date '+%H:%M:%S')] ===== update-all 完成: PASS=$PASS_COUNT FAIL=$FAIL_COUNT SKIP=$SKIP_COUNT =====" >> "$LOG_FILE"
[ -n "$FAILURES" ] && echo "[$(date '+%H:%M:%S')] 失败步骤:$FAILURES" >> "$LOG_FILE"
```

---

## 故障排查

### specify-cli 报错 `ModuleNotFoundError: No module named 'specify_cli'`

**原因**：`~/.local/bin/specify.exe` 是残留文件，实际 Python 包未安装。

**修复**：
```bash
rm -f ~/.local/bin/specify.exe
uv tool install specify-cli --from "git+https://github.com/github/spec-kit.git" --reinstall
```

### claude plugins update 报 "not found"

**原因**：上游市场已重构，插件名称变更。

**修复**：运行 `claude plugins list` 确认新名称后重新安装。

### gstack 更新后命令不可用

**原因**：setup 脚本未正确执行。

**修复**：
```bash
cd ~/.claude/skills/gstack && ./setup
```

---

## 注意事项

- 更新完成后需**重启 Claude Code daemon** 使插件生效
- `specify-cli` 始终从 `github/spec-kit` 主分支安装最新开发版
- `everything-claude-code` 已重构为 `ecc@ecc`，旧名不可用
- 每个步骤的验证失败不会中断整体流程，但最终汇总会显示所有问题
