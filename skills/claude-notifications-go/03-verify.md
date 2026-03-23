---
description: 验证 claude-notifications-go 插件是否正确安装并正常工作
allowed-tools: Bash
---

# 验证 claude-notifications-go 安装

按顺序执行以下检查，确认插件完整安装。

---

## 检查 1：插件配置目录

```bash
ls -la ~/.claude/claude-notifications-go/
# 预期：看到 config.json
```

---

## 检查 2：Go 二进制文件

```bash
ls ~/.claude/plugins/cache/claude-notifications-go/claude-notifications-go/1.33.0/bin/
# 预期（Windows）：
# claude-notifications-windows-amd64.exe
# claude-notifications.bat
# list-devices-windows-amd64.exe
# list-sounds-windows-amd64.exe
# sound-preview-windows-amd64.exe
```

```bash
# 测试二进制可执行
~/.claude/plugins/cache/claude-notifications-go/claude-notifications-go/1.33.0/bin/claude-notifications-windows-amd64.exe --version 2>&1 || echo 'Binary test complete'
```

---

## 检查 3：settings.json 中插件启用状态

```bash
grep 'claude-notifications-go' ~/.claude/settings.json
# 预期："claude-notifications-go@claude-notifications-go": true
```

---

## 检查 4：hooks 是否注册

```bash
grep -l 'claude-notifications' ~/.claude/settings.json ~/.claude/hooks/hooks.json 2>/dev/null
```

---

## 检查 5：配置文件有效性

```bash
# 检查 JSON 格式是否有效
node -e "JSON.parse(require('fs').readFileSync(process.env.HOME + '/.claude/claude-notifications-go/config.json', 'utf8')); console.log('Config JSON valid')"
```

---

## 检查 6：触发测试通知

在 Claude Code 中执行一个简单任务后，应收到 Windows 桌面 Toast 通知：
- 标题：`✅ Task Completed`
- 如配置了飞书 Webhook，飞书机器人也会发送消息

也可通过运行以下命令初始化并测试：
```
/claude-notifications-go:init
```

---

## 常见问题排查

| 问题 | 解决方案 |
|---|---|
| 二进制不存在 | 重新运行 `install.sh`，参考 [01-install.md](./01-install.md) Step 2 |
| 插件未启用 | 检查 `settings.json`，手动添加插件 key |
| 无桌面通知 | 检查 Windows 通知设置，确认「终端/Claude」应用通知未被屏蔽 |
| 无飞书通知 | 检查 `config.json` 中 webhook.url 是否正确，参考 [04-webhook-feishu.md](./04-webhook-feishu.md) |
