# Windows SSH 遥控 Mac Mini 实施方案

## 目标

Windows Claude Code 通过 SSH 遥控局域网 Mac Mini，实现免密登录和远程命令执行。

## 当前状态（2026-08-20 部署完成 ✅）

| 检查项 | 状态 | 说明 |
|--------|------|------|
| Windows SSH 密钥 | ✅ 已存在 | `~/.ssh/id_ed25519` (ed25519) |
| SSH config | ✅ 已配置 | Host 别名 `mac-mini` → 172.16.105.139 |
| Mac Mini SSH 服务 | ✅ 已开启 | OpenSSH_10.0，macOS 26.2 |
| 公钥已部署到 Mac | ✅ 已验证 | 免密登录成功 |
| 备用密钥 | ✅ 保留 | `~/.ssh/id_rsa_mac`（Mac 生成，pubkey 也在 authorized_keys） |

## ⚠️ 部署踩坑记录（重要）

**故障现象**：密码正确、公钥正确，但认证反复被拒（`Permission denied`）

**根因**：IP 地址错误——`172.16.105.1` 是**网关路由器**（TP-LINK），不是 Mac。所有认证都在往路由器的 SSH 管理接口打。

**识别路由器伪装 SSH 服务的 4 个特征**：
1. ping TTL=254（路由器默认 255；macOS/Linux 默认 64）
2. SSH banner 无版本号（`remote software version -`）
3. KEX 只提供 SHA1 老算法但 host key 是 ECDSA（组合异常）
4. ARP 查 MAC OUI 是网络设备厂商而非 Apple

**验证"这是不是真 Mac"的金标准**：对比 SSH host key 指纹与 Mac 本机 `ssh localhost` 显示的指纹是否一致。

---

## 第一阶段：Mac Mini 端操作（需物理接触，一次性）

> 以下操作需要在 Mac Mini 上直接执行（接键鼠显示器），或通过 Mac 当前可用的任何远程方式完成。

### 步骤 1.1：开启远程登录（SSH 服务）

**GUI 方式：**
```
系统设置 → 通用 → 共享 → 远程登录 → 打开
允许访问：仅限这些用户 → 添加 wuyan
```

**终端方式（如果能访问 Mac 终端）：**
```bash
# 开启 SSH 服务
sudo systemsetup -setremotelogin on

# 或通过 launchctl
sudo launchctl load -w /System/Library/LaunchDaemons/ssh.plist
```

**验证 SSH 服务已开启：**
```bash
# 在 Mac 上执行
sudo launchctl list | grep ssh
# 应看到 com.openssh.sshd
```

### 步骤 1.2：确认 Mac Mini 网络连通性

Mac Mini 需要接入局域网（网线或 WiFi），不需要互联网。

```bash
# 在 Mac 上查看 IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# 记录 en0（通常是以太网）或 en1 的 IP，例如 192.168.x.x
```

**关于 `.local` 域名：**
- macOS 默认支持 mDNS（Bonjour），`计算机名.local` 在局域网内可直接解析
- 确认 Mac 的计算机名：
  ```bash
  scutil --get ComputerName
  scutil --get LocalHostName
  ```
- 如果计算机名是 `Mac-mini`，则可通过 `Mac-mini.local` 访问
- 如果是其他名字（如 `wuyandeMac-mini`），对应调整

### 步骤 1.3：部署 Windows 公钥到 Mac

**方式 A：Mac 上手动添加（推荐，只需一次）**

在 Mac 终端执行：
```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 将以下内容追加到 authorized_keys
cat >> ~/.ssh/authorized_keys << 'EOF'
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDnQ2wGrBOgccz8TMU2d+Zr3nVABBkr5+cVbD4SrSec+ wuyan@DESKTOP-88P12D3
EOF

chmod 600 ~/.ssh/authorized_keys
```

**方式 B：Windows 通过 ssh-copy-id 复制（需知道 Mac IP 和密码）**

```bash
# Git Bash 中执行（如果 Mac 已接入局域网且知道密码）
ssh-copy-id -i ~/.ssh/id_ed25519.pub wuyan@<MAC_IP>

# 或手动方式
cat ~/.ssh/id_ed25519.pub | ssh wuyan@<MAC_IP> "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

---

## 第二阶段：Windows 端准备

### 步骤 2.1：创建 SSH config（简化连接）

在 Windows 上创建 `~/.ssh/config` 文件：

```bash
# PowerShell 中执行
@"
Host mac-mini
    HostName Mac-mini.local
    User wuyan
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
"@ | Out-File -Encoding utf8 "$env:USERPROFILE\.ssh\config"
```

或用 Git Bash：
```bash
cat > ~/.ssh/config << 'EOF'
Host mac-mini
    HostName Mac-mini.local
    User wuyan
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
EOF
chmod 600 ~/.ssh/config
```

> **注意：** 如果 `.local` 域名不通，把 `HostName` 改为 Mac 的实际 IP（如 `192.168.1.100`），或在 `C:\Windows\System32\drivers\etc\hosts` 中添加静态映射。

### 步骤 2.2：配置 known_hosts（避免首次连接确认）

如果 Mac IP 固定，可以预添加 host key：

```bash
# 先获取 Mac 的 host key（在能连通后执行一次）
ssh-keyscan -H Mac-mini.local >> ~/.ssh/known_hosts 2>/dev/null
# 或指定 IP
ssh-keyscan -H 192.168.x.x >> ~/.ssh/known_hosts 2>/dev/null
```

### 步骤 2.3：验证 SSH 免密连接

```bash
# 简短测试
ssh mac-mini "echo ok"

# 完整测试
ssh mac-mini "hostname && whoami && pwd"
```

预期输出：
```
Mac-mini.local
wuyan
/Users/wuyan
```

---

## 第三阶段：Claude Code 遥控用法

### 基础命令模式

在 Claude Code 对话中这样指示：

```
请通过 SSH 在 Mac Mini 上执行以下操作：
1. 检查系统版本
2. 列出用户目录
3. 检查磁盘空间
```

Claude Code 会转换为：
```bash
ssh mac-mini "sw_vers && ls ~ && df -h"
```

### 文件传输

```bash
# Windows → Mac
scp local_file.txt mac-mini:~/Desktop/

# Mac → Windows
scp mac-mini:~/remote_file.txt ./

# 传目录
scp -r ./local_dir mac-mini:~/target_dir/
```

### 批量部署脚本

```bash
# 1. 传文件
scp install.sh verify.sh mac-mini:~/

# 2. 远程执行
ssh mac-mini "bash ~/install.sh"
ssh mac-mini "bash ~/verify.sh"
```

### 长时间任务

```bash
# 使用 nohup 防止 SSH 断开中断
ssh mac-mini "nohup long_running_task.sh > ~/task.log 2>&1 &"

# 或使用 tmux/screen（如果 Mac 上已安装）
ssh -t mac-mini "tmux new -s deploy 'bash ~/deploy.sh'"
```

---

## 第四阶段：网络不通时的备选方案

如果 Mac Mini 暂时无法接入局域网，以下是离线准备选项：

### 选项 A：USB 传输公钥

1. Windows 导出公钥：`cat ~/.ssh/id_ed25519.pub`
2. 复制到 U 盘（文本文件 `authorized_keys`）
3. Mac 上插入 U 盘，执行：
   ```bash
   mkdir -p ~/.ssh && chmod 700 ~/.ssh
   cp /Volumes/USBDRIVE/authorized_keys ~/.ssh/
   chmod 600 ~/.ssh/authorized_keys
   ```

### 选项 B：Mac 上生成交叉密钥

在 Mac 终端生成新密钥对，私钥传到 Windows：
```bash
# Mac 上
ssh-keygen -t ed25519 -C "mac-mini-remote" -f ~/.ssh/mac_key
cat ~/.ssh/mac_key.pub >> ~/.ssh/authorized_keys
# 把 mac_key（私钥）通过 USB 传到 Windows ~/.ssh/
```

---

## 常见问题排查

### 连接被拒绝
```bash
# 检查 Mac SSH 服务是否开启
ssh mac-mini "sudo launchctl list | grep ssh"

# 检查防火墙
ssh mac-mini "sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate"
```

### `.local` 域名解析失败
```bash
# Windows 上测试 mDNS
ping Mac-mini.local

# 不通则用 IP
# 1. 在 Mac 上查 IP：ifconfig | grep "inet "
# 2. 修改 ~/.ssh/config 的 HostName 为 IP
# 3. 或添加 hosts 文件映射
```

### 免密登录不生效
```bash
# 检查权限
ssh mac-mini "ls -la ~/.ssh/ && cat ~/.ssh/authorized_keys"

# 正确权限：
# ~/.ssh/ → 700
# ~/.ssh/authorized_keys → 600
# ~ (home) → 不能是 777
```

### 连接频繁断开
```bash
# 已在 SSH config 配置保活：
# ServerAliveInterval 60
# ServerAliveCountMax 3

# 或在命令行指定
ssh -o ServerAliveInterval=60 mac-mini "command"
```

---

## 执行清单

### 现在可做（Windows 端）
- [x] SSH 密钥已存在
- [ ] 创建 `~/.ssh/config`（步骤 2.1）
- [ ] 准备 host key 预添加命令（步骤 2.2，等 Mac 联网后执行）

### 需要物理接触 Mac 时做
- [ ] 开启远程登录（步骤 1.1）
- [ ] 确认/记录 Mac 计算机名和 IP（步骤 1.2）
- [ ] 部署公钥到 Mac（步骤 1.3）
- [ ] 验证连接（步骤 2.3）

### Mac 接入局域网后
- [ ] 从 Windows 测试 `ssh mac-mini "echo ok"`
- [ ] 执行 `ssh-keyscan` 添加 host key
- [ ] 开始 Claude Code 遥控操作

---

## 安全备注

- SSH 密钥仅存储在 Windows 本机，不要通过网盘/邮件传输私钥
- 如 Mac 需要暴露到公网，务必修改默认端口（22）并禁用密码登录
- 定期轮换密钥：`ssh-keygen -t ed25519 -C "claude-remote-2026" -f ~/.ssh/id_ed25519_new`
