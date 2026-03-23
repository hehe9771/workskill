---
description: 查看和修改 claude-notifications-go 通知配置（桌面通知、Webhook、声音等）
allowed-tools: Bash
---

# claude-notifications-go 配置说明

配置文件路径：`~/.claude/claude-notifications-go/config.json`

---

## 当前配置（本机实际值）

```json
{
  "notifications": {
    "desktop": {
      "enabled": true,
      "sound": true,
      "volume": 1.0,
      "audioDevice": "",
      "appIcon": ""
    },
    "webhook": {
      "enabled": true,
      "preset": "lark",
      "url": "https://open.feishu.cn/open-apis/bot/v2/hook/090c54b4-cdc9-4b01-8093-5d01728156d8"
    },
    "suppressQuestionAfterTaskCompleteSeconds": 7
  },
  "statuses": {
    "task_complete": {
      "enabled": true,
      "title": "✅ Task Completed",
      "sound": "~/.claude/plugins/cache/claude-notifications-go/claude-notifications-go/1.33.0/sounds/task-complete.mp3"
    },
    "review_complete": {
      "enabled": true,
      "title": "🔍 Review Completed",
      "sound": "~/.claude/plugins/cache/claude-notifications-go/claude-notifications-go/1.33.0/sounds/review-complete.mp3"
    },
    "question": {
      "enabled": true,
      "title": "❓ Claude Has Questions",
      "sound": "~/.claude/plugins/cache/claude-notifications-go/claude-notifications-go/1.33.0/sounds/question.mp3"
    },
    "plan_ready": {
      "enabled": true,
      "title": "📋 Plan Ready for Review",
      "sound": "~/.claude/plugins/cache/claude-notifications-go/claude-notifications-go/1.33.0/sounds/plan-ready.mp3"
    }
  }
}
```

---

## 配置项说明

### notifications.desktop

| 字段 | 类型 | 说明 |
|---|---|---|
| `enabled` | bool | 是否启用桌面通知 |
| `sound` | bool | 是否播放声音 |
| `volume` | float | 音量（0.0 ~ 1.0）|
| `audioDevice` | string | 指定音频设备（空=默认）|
| `appIcon` | string | 自定义通知图标路径（空=默认）|

> **Windows 注意**：不支持 `clickToFocus`，点击通知不会聚焦终端窗口。

### notifications.webhook

| 字段 | 类型 | 说明 |
|---|---|---|
| `enabled` | bool | 是否启用 Webhook 通知 |
| `preset` | string | 预设类型：`slack`、`discord`、`telegram`、`ntfy`、`teams`、`lark`、`custom` |
| `url` | string | Webhook 推送地址 |

### notifications.suppressQuestionAfterTaskCompleteSeconds

任务完成后，若在此秒数内出现 Question 通知，则抑制（避免重复打扰）。

### statuses.*

每种通知状态可单独配置：
- `enabled`：是否启用该类型通知
- `title`：通知标题
- `sound`：声音文件路径（支持 MP3/WAV/FLAC/OGG）

---

## 查看当前配置

```bash
cat ~/.claude/claude-notifications-go/config.json
```

## 交互式配置（需要 Claude Code 内运行）

```
/claude-notifications-go:settings
```

## 手动编辑配置

```bash
# Windows Git Bash
notepad ~/.claude/claude-notifications-go/config.json

# 或直接用编辑器
code ~/.claude/claude-notifications-go/config.json
```
