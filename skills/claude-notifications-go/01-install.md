---
description: 安装 claude-notifications-go 插件到 Claude Code 全局环境（Windows/macOS/Linux）
allowed-tools: Bash
---

# 安装 claude-notifications-go

> 插件版本：v1.33.0 | 仓库：https://github.com/777genius/claude-notifications-go

## 前置条件

```bash
# 确认 claude CLI 可用
claude --version

# 确认 curl 可用
curl --version | head -1
```

---

## Step 1：运行 bootstrap 脚本

```bash
curl -fsSL https://raw.githubusercontent.com/777genius/claude-notifications-go/main/bin/bootstrap.sh > /tmp/bootstrap.sh
bash /tmp/bootstrap.sh > /tmp/bootstrap_out.txt 2>&1
cat /tmp/bootstrap_out.txt
```

> **注意**：bootstrap.sh 存在版本检测 bug（`vunknown` 问题），脚本会报错退出，但插件实际上已安装成功。继续执行 Step 2 手动下载 Go 二进制即可。

---

## Step 2：手动下载 Go 二进制

boostrap.sh 版本检测失败后，需手动运行 install.sh 下载 Go 通知二进制：

```bash
# 找到插件安装目录（通常为以下路径）
PLUGIN_ROOT="$HOME/.claude/plugins/cache/claude-notifications-go/claude-notifications-go/1.33.0"

# 下载并运行 install.sh
curl -fsSL https://raw.githubusercontent.com/777genius/claude-notifications-go/main/bin/install.sh > /tmp/install.sh
INSTALL_TARGET_DIR="${PLUGIN_ROOT}/bin" bash /tmp/install.sh 2>&1
```

**预期输出**：
```
✓ Binary executes correctly
✓ Created wrapper claude-notifications.bat → claude-notifications-windows-amd64.exe
✓ Installation Complete!
```

---

## Step 3：确认插件已启用

```bash
# 检查 settings.json 中插件是否启用
grep -c 'claude-notifications-go' ~/.claude/settings.json && echo 'Plugin enabled' || echo 'Plugin NOT found'
```

如果未启用，手动编辑 `~/.claude/settings.json`，在 `enabledPlugins` 中添加：
```json
"claude-notifications-go@claude-notifications-go": true
```

---

## Step 4：重启 Claude Code

重启 Claude Code 后插件 hooks 生效。

---

## Step 5（可选）：更新插件

```bash
# 重新运行 bootstrap.sh 即可，配置文件不会被覆盖
curl -fsSL https://raw.githubusercontent.com/777genius/claude-notifications-go/main/bin/bootstrap.sh | bash
```

---

## 安装路径说明

| 路径 | 说明 |
|---|---|
| `~/.claude/plugins/cache/claude-notifications-go/` | 插件脚本缓存 |
| `~/.claude/plugins/cache/.../bin/*.exe` | Go 通知二进制 |
| `~/.claude/claude-notifications-go/config.json` | 通知配置文件 |
| `~/.claude/settings.json` | 插件启用状态 |
