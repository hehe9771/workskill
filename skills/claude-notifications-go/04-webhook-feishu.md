---
description: 配置飞书（Lark）Webhook 机器人接收 Claude Code 任务通知
allowed-tools: Bash
---

# 飞书 Webhook 通知配置

claude-notifications-go 支持飞书（Lark）Webhook，任务完成、有问题等事件会自动推送消息到飞书群。

---

## 当前配置

```json
{
  "notifications": {
    "webhook": {
      "enabled": true,
      "preset": "lark",
      "url": "https://open.feishu.cn/open-apis/bot/v2/hook/090c54b4-cdc9-4b01-8093-5d01728156d8"
    }
  }
}
```

---

## 创建飞书机器人（如需新建）

1. 打开飞书群 → 设置 → 机器人 → 添加机器人
2. 选择「自定义机器人」
3. 设置名称（如 `Claude Code 通知`）
4. 复制生成的 Webhook URL
5. 格式：`https://open.feishu.cn/open-apis/bot/v2/hook/<UUID>`

---

## 更新 Webhook URL

```bash
# 方式一：直接编辑 config.json
CONFIG="$HOME/.claude/claude-notifications-go/config.json"
NEW_URL="https://open.feishu.cn/open-apis/bot/v2/hook/<你的新UUID>"

# 用 node 更新（避免手动编辑 JSON 出错）
node -e "
  const fs = require('fs');
  const c = JSON.parse(fs.readFileSync('$CONFIG', 'utf8'));
  c.notifications.webhook.url = '$NEW_URL';
  c.notifications.webhook.preset = 'lark';
  c.notifications.webhook.enabled = true;
  fs.writeFileSync('$CONFIG', JSON.stringify(c, null, 2));
  console.log('Webhook URL updated');
"
```

```bash
# 方式二：交互式配置（在 Claude Code 内运行）
# /claude-notifications-go:settings
```

---

## 测试 Webhook 是否正常

```bash
# 手动发送一条测试消息到飞书
WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/090c54b4-cdc9-4b01-8093-5d01728156d8"
curl -X POST "$WEBHOOK_URL" \
  -H 'Content-Type: application/json' \
  -d '{"msg_type":"text","content":{"text":"Claude Code 通知测试 ✅"}}'
# 预期响应：{"StatusCode":0,"StatusMessage":"success",...}
```

---

## 飞书通知格式

claude-notifications-go 发送的飞书消息包含：
- 通知类型标题（如 `✅ Task Completed`）
- git 分支名（如 `main [cat]`）
- 触发时间

---

## 禁用 Webhook（仅保留桌面通知）

```bash
CONFIG="$HOME/.claude/claude-notifications-go/config.json"
node -e "
  const fs = require('fs');
  const c = JSON.parse(fs.readFileSync('$CONFIG', 'utf8'));
  c.notifications.webhook.enabled = false;
  fs.writeFileSync('$CONFIG', JSON.stringify(c, null, 2));
  console.log('Webhook disabled');
"
```

---

## 支持的 Webhook Preset 类型

| Preset | 服务 |
|---|---|
| `lark` | 飞书 / Lark |
| `slack` | Slack |
| `discord` | Discord |
| `telegram` | Telegram Bot |
| `ntfy` | ntfy.sh |
| `teams` | Microsoft Teams |
| `pagerduty` | PagerDuty |
| `custom` | 自定义格式 |
