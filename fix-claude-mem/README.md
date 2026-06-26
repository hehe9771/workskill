# claude-mem 安装后修复脚本

## 问题背景

claude-mem 插件在以下场景会出问题：

1. **更新/重新安装后**：插件文件被覆盖，所有修复丢失
2. **Windows 环境**：cmd.exe 对 `<` 等特殊字符的处理与 Unix 不同
3. **非官方 Claude API**：使用 DashScope 等代理时，模型名/认证方式不兼容

## 修复内容

### 1. Hook 容错（防止 Claude Code 被阻塞）

**问题**：worker 不可达时 hook 执行 `exit 1`，Claude Code 认为操作被拒绝，所有用户输入被阻塞。

**修复**：
- 清空 `UserPromptSubmit` hook（最大阻塞源）
- 所有 worker hook 在不可达时输出 `{"continue":true}` 而非 `exit 1`

### 2. Chroma 向量搜索（Windows cmd.exe 兼容）

**问题**：`--with "protobuf<7"` 在 cmd.exe 中 `<` 被解释为文件重定向，即使包在双引号里也无效。

**修复**：patch `bie()` 函数，用 `^` 转义 cmd.exe 特殊字符（`protobuf^<7`）而非双引号包裹。

### 3. 模型覆盖（适配 DashScope 等代理）

**问题**：`CLAUDE_MEM_MODEL` 默认值为 `claude-haiku-4-5-20251001`，DashScope 不支持。

**修复**：强制设置所有模型 tier 为 `qwen3.7-plus`（或你在 Claude Code 里配置的模型）。

### 4. 动态同步（模型/URL/密钥自动跟随）

**问题**：worker 作为独立进程启动，不继承 Claude Code 的环境变量。

**修复**：
- 创建 `sync-env-from-claude.mjs`，从 Claude Code 的 `settings.json` 读取配置
- SessionStart hook 每次启动时自动运行同步
- 你改 Claude Code 的模型，claude-mem 自动跟随

## 使用方式

```bash
# 安装/更新 claude-mem 插件后运行
python fix-claude-mem.py
```

然后**重启 Claude Code** 使修复生效。

## 文件说明

```
fix-claude-mem/
├── fix-claude-mem.py   # 一键修复脚本
└── README.md           # 本文档
```

脚本修改的目标文件：

| 文件 | 位置 | 说明 |
|------|------|------|
| hooks.json | `~/.claude/plugins/cache/thedotmack/claude-mem/<version>/hooks/` | hook 容错 + sync-env |
| worker-service.cjs | `~/.claude/plugins/cache/thedotmack/claude-mem/<version>/scripts/` | cmd.exe 转义修复 |
| sync-env-from-claude.mjs | `~/.claude-mem/` | 动态同步脚本（用户数据，不会被覆盖） |
| settings.json | `~/.claude-mem/` | claude-mem 配置（模型覆盖） |
| .env | `~/.claude-mem/` | 从 Claude Code 同步的认证信息 |

## 根因分析

### 为什么每次更新都有问题？

claude-mem 的架构有三个设计缺陷：

1. **Hook 没有 graceful degradation**：worker 不可达应该降级而非阻塞。这是插件作者的疏忽——在非 Windows 环境下可能不明显，但 Windows 上进程管理差异会导致 zombie 端口占用更频繁。

2. **Windows cmd.exe 转义不完整**：`bie()` 函数用双引号包裹特殊字符，但 cmd.exe 的 `<` 重定向不受双引号保护（这是 Windows 和 Unix shell 的根本差异）。

3. **模型硬编码**：`CLAUDE_MEM_MODEL` 默认值是 `claude-haiku-4-5-20251001`，假设用户用官方 Claude API。使用代理的用户必须手动覆盖。

### 修复的脆弱性

| 修复 | 存储位置 | 更新后 |
|------|----------|--------|
| hooks.json 容错 | 插件 cache 目录 | ❌ 被覆盖 |
| worker-service.cjs patch | 插件 cache 目录 | ❌ 被覆盖 |
| sync-env-from-claude.mjs | `~/.claude-mem/`（用户数据） | ✅ 存活 |
| settings.json 模型覆盖 | `~/.claude-mem/`（用户数据） | ⚠️ 部分存活 |

**结论**：每次插件更新后需要重新运行 `fix-claude-mem.py`。

## 长期方案建议

1. **向上游提 PR**：修复 `bie()` 函数的 Windows 转义、添加 hook 容错
2. **写 Claude Code hook**：监听插件安装事件，自动运行修复
3. **Fork 插件**：如果上游不合并，维护一个 Windows/代理兼容的 fork

## 故障排查

```bash
# 检查 worker 状态
cd ~/.claude/plugins/cache/thedotmack/claude-mem/13.4.2
node scripts/bun-runner.js scripts/worker-service.cjs status

# 查看日志
tail -20 ~/.claude-mem/logs/claude-mem-$(date +%Y-%m-%d).log

# 检查端口占用
netstat -ano | findstr 37777

# 手动同步 .env
node ~/.claude-mem/sync-env-from-claude.mjs
```
