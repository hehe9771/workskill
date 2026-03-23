# claude-notifications-go Skills

> 适用于 `777genius/claude-notifications-go` v1.33.0 的安装与配置 Skills 集合

## 插件简介

claude-notifications-go 是一个 Claude Code 插件，通过 Claude Code 的 Hook 系统触发桌面通知和 Webhook，用 Go 编写，零依赖。

### 6 种通知类型

| 类型 | 触发条件 |
|---|---|
| Task Complete | Stop hook，检测到活跃工具 |
| Review Complete | Stop hook，只读工具 + 长响应 |
| Question | PreToolUse (AskUserQuestion) 或 Notification hook |
| Plan Ready | PreToolUse (ExitPlanMode) |
| Session Limit Reached | Stop hook，检测到限额文本 |
| API Error | Stop hook，检测 JSONL 中的错误字段 |

### 平台支持

| 平台 | 桌面通知 | 点击聚焦 |
|---|---|---|
| macOS | 支持 | 支持 |
| Linux | 支持 | 支持 |
| Windows 10+ | 支持 | 不支持 |

---

## 本机已安装信息（Windows 11 x64）

| 项目 | 值 |
|---|---|
| 插件版本 | v1.33.0 |
| 插件目录 | `~/.claude/plugins/cache/claude-notifications-go/claude-notifications-go/1.33.0/` |
| Go 二进制 | `...1.33.0/bin/claude-notifications-windows-amd64.exe` |
| 配置文件 | `~/.claude/claude-notifications-go/config.json` |
| Webhook | 飞书 Lark（已配置）|

---

## Skills 文件索引

| 文件 | 说明 | 用途 |
|---|---|---|
| [01-install.md](./01-install.md) | 完整安装步骤 | 全新安装或更新插件 |
| [02-config.md](./02-config.md) | 配置文件说明 | 查看/修改通知配置 |
| [03-verify.md](./03-verify.md) | 验证安装 | 确认插件正常工作 |
| [04-webhook-feishu.md](./04-webhook-feishu.md) | 飞书 Webhook 配置 | 配置飞书机器人通知 |

---

## 快速上手

1. 按 [01-install.md](./01-install.md) 完成安装
2. 重启 Claude Code
3. 按 [03-verify.md](./03-verify.md) 验证
4. 如需飞书通知，参考 [04-webhook-feishu.md](./04-webhook-feishu.md)
