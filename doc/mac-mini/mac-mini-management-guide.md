# Mac Mini 管理手册 — SSH 免密登录与代理服务

> 最后更新：2026-08-20 | 状态：✅ 全部部署完成并验证
>
> 本文档整合：SSH 远程登录实现方式、mihomo 代理部署现状、日常管理命令。

---

## 一、机器信息

| 项目 | 值 |
|------|-----|
| 主机名 | macdeMac-mini.local |
| 局域网 IP | **172.16.105.139**（DHCP 动态分配，重启路由器后可能变化） |
| 系统 | macOS 26.2 (Build 25C56) |
| 芯片 | Apple Silicon (arm64) |
| 用户名 | `mac` |
| 活跃网络 | **Wi-Fi (en1)** — Ethernet (en0) 未接线 |

---

## 二、SSH 免密登录实现方式

### 2.1 连接方式（Windows → Mac）

```bash
# 已配置别名，一条命令直连
ssh mac-mini

# 远程执行命令
ssh mac-mini "sw_vers"

# 传文件
scp 本地文件 mac-mini:~/目标路径/
scp mac-mini:~/远程文件 ./本地路径
```

### 2.2 实现原理

```
Windows (C:\Users\wuyan\.ssh\)                Mac Mini
├─ config  ── Host mac-mini ──────────────▶ 172.16.105.139:22 (OpenSSH_10.0)
│              User mac
│              IdentityFile id_ed25519
├─ id_ed25519 (私钥) ── 配对 ──▶ ~/.ssh/authorized_keys (含对应公钥)
└─ id_rsa_mac (备用私钥) ── 配对 ──▶ authorized_keys (Mac 侧生成的 RSA 公钥)
```

认证流程：`ssh mac-mini` → config 解析出 IP/用户/密钥 → ed25519 公钥认证 → 免密登录。

### 2.3 关键文件位置

| 文件 | 位置 | 说明 |
|------|------|------|
| SSH 配置 | `C:\Users\wuyan\.ssh\config` | Host 别名定义（改 IP 只改这里） |
| 主私钥 | `C:\Users\wuyan\.ssh\id_ed25519` | Windows 原生生成 |
| 备用私钥 | `C:\Users\wuyan\.ssh\id_rsa_mac` | Mac 侧生成后传回，双保险 |
| Mac 公钥列表 | Mac: `~/.ssh/authorized_keys` | 含上述两个公钥 |

### 2.4 踩坑记录（排障参考）

部署时认证反复失败的根因是 **IP 指向了路由器**（172.16.105.1 是 TP-LINK 网关，不是 Mac）。
识别"连错主机"的 4 个特征：

1. ping TTL=254（网络设备默认 255；macOS 默认 64）
2. `ssh -v` 显示 `remote software version -`（无版本号）
3. KEX 只有 SHA1 老算法但 host key 是 ECDSA（异常组合）
4. `arp -a` 查 MAC 地址 OUI 是网络设备厂商而非 Apple

**金标准**：远程连接的 host key 指纹与 Mac 本机 `ssh localhost` 显示的指纹一致才是真机。

**IP 变化应对**：Mac 是 DHCP，IP 变了先扫子网再找真机：

```bash
# Windows Git Bash 扫 22 端口
for i in $(seq 1 254); do (timeout 0.4 bash -c "echo > /dev/tcp/172.16.105.$i/22" 2>/dev/null && echo "172.16.105.$i OPEN") & done; wait
# 确认后改 ~/.ssh/config 的 HostName
```

---

## 三、代理部署现状

### 3.1 架构

```
Mac Mini 浏览器/应用
  → 系统代理 127.0.0.1:7891 (Wi-Fi 服务已启用)
  → mihomo v1.19.30 (darwin arm64)
  → 分流: 国内直连 / 国外走 Trojan
  → Trojan over TLS :443
  → 阿里云新加坡 47.237.28.48 (proxy.fh-lease.com)
  → 国外网站
```

### 3.2 部署清单

| 项目 | 位置/值 |
|------|---------|
| 二进制 | `/usr/local/bin/mihomo`（v1.19.30，已去 Gatekeeper 隔离属性） |
| 配置与数据 | `~/mihomo-proxy/`（config.yaml、geoip.metadb、cache.db） |
| 部署脚本副本 | `~/mihomo-install/`（verify/restart/setup-system-proxy 等） |
| 自启配置 | `~/Library/LaunchAgents/com.mihomo.proxy.plist` |
| 日志 | `/tmp/mihomo-stdout.log`、`/tmp/mihomo-stderr.log` |
| 代理端口 | 7891（HTTP/SOCKS5 混合）、9091（API）、1053（DNS） |

### 3.3 自启机制

- **LaunchAgent**：`RunAtLoad: true`（登录即启动）+ `KeepAlive`（崩溃 5 秒内自动拉起）
- **自动登录已开启**（autoLoginUser=mac）——重启后自动进桌面，代理随之拉起
- **已实测**：整机重启后 mihomo 自动运行，验证 6 项全过

### 3.4 分流规则要点

- 国内域名（百度/腾讯/阿里系等）+ GEOIP CN → 直连
- 国外域名（Google/GitHub/OpenAI 等）+ 其余全部 → PROXY
- 防路由循环三层保险：`DOMAIN,proxy.fh-lease.com,DIRECT` + `hosts` 硬编码 IP + `IP-CIDR,47.237.28.48/32,DIRECT`

### 3.5 验证标准（部署后实测通过）

```
✅ 进程运行  ✅ 7891/9091 监听  ✅ 百度 200（直连）
✅ Google 200（代理）  ✅ 出口 IP 47.237.28.48 (SG)  ✅ 系统代理启用 (Wi-Fi)
```

---

## 四、代理管理命令

### 4.1 Mac 本机操作（Mac 终端）

| 操作 | 命令 |
|------|------|
| **重启代理**（推荐，不断网） | `bash ~/mihomo-install/restart-mihomo.sh` |
| **停止代理** | `bash ~/mihomo-install/setup-system-proxy.sh off && launchctl unload ~/Library/LaunchAgents/com.mihomo.proxy.plist` |
| **启动代理** | `launchctl load ~/Library/LaunchAgents/com.mihomo.proxy.plist && bash ~/mihomo-install/setup-system-proxy.sh on` |
| **只关系统代理**（进程保留，浏览器临时直连） | `bash ~/mihomo-install/setup-system-proxy.sh off` |
| **只开系统代理** | `bash ~/mihomo-install/setup-system-proxy.sh on` |
| **完整健康检查** | `bash ~/mihomo-install/verify-proxy.sh` |
| 进程状态 | `pgrep -lx mihomo` |
| 端口状态 | `lsof -nP -i :7891` |
| 实时日志 | `tail -f /tmp/mihomo-stderr.log` |
| 修改配置后热重载 | `kill -HUP $(pgrep -x mihomo)` |

以上命令均**不需要 sudo**（macOS 26 实测 admin 用户可直接操作 networksetup）。

### 4.2 Windows 远程操作（本机 Git Bash / Claude Code）

```bash
# 重启代理
ssh mac-mini "bash ~/mihomo-install/restart-mihomo.sh"

# 健康检查
ssh mac-mini "bash ~/mihomo-install/verify-proxy.sh"

# 快速确认代理是否活着
ssh mac-mini "pgrep -lx mihomo && curl -s -o /dev/null -w '%{http_code}' --max-time 10 -x http://127.0.0.1:7891 https://www.google.com"

# 看日志
ssh mac-mini "tail -30 /tmp/mihomo-stderr.log"

# 关/开系统代理
ssh mac-mini "bash ~/mihomo-install/setup-system-proxy.sh off"
ssh mac-mini "bash ~/mihomo-install/setup-system-proxy.sh on"
```

在 Claude Code 中直接说"重启 Mac 上的代理"即可，会自动转换为上述 SSH 命令。

### 4.3 源仓库位置（Windows，修改配置的源头）

`D:\mydoc\proxy\install-files\mac\` — 改完配置后同步：

```bash
# 例：改了 config.yaml 的分流规则后下发
scp /d/mydoc/proxy/install-files/mac/config.yaml mac-mini:~/mihomo-proxy/config.yaml
ssh mac-mini "kill -HUP \$(pgrep -x mihomo)"   # 热重载，不断连
```

---

## 五、常见故障速查

### 5.1 浏览器打不开 Google，但 curl 走代理正常

**根因**：系统代理设到了未接线的 Ethernet，实际走 Wi-Fi。
**修复**（已固化到脚本，按默认路由接口自动定位）：

```bash
ssh mac-mini "bash ~/mihomo-install/setup-system-proxy.sh on"
```

### 5.2 重启 Mac 后代理没起来

```bash
# 查 LaunchAgent 是否在列
ssh mac-mini "launchctl list | grep mihomo"

# 不在则手动加载
ssh mac-mini "launchctl load ~/Library/LaunchAgents/com.mihomo.proxy.plist"
```

前提：自动登录必须保持开启（系统设置→用户与群组→自动登录 = mac）。

### 5.3 国外网站全挂、国内正常

代理链路问题（服务器/证书/网络），按顺序查：

```bash
# 1. 进程和日志
ssh mac-mini "pgrep -lx mihomo; tail -20 /tmp/mihomo-stderr.log"

# 2. 服务器 443 可达性
ssh mac-mini "nc -zv 47.237.28.48 443 2>&1"

# 3. 证书有效期（2026-12-27 到期）
ssh mac-mini "openssl s_client -connect 47.237.28.48:443 -servername proxy.fh-lease.com 2>&1 | openssl x509 -noout -dates"
```

### 5.4 SSH 连不上 Mac

```bash
# 1. 网络通不通
ping 172.16.105.139    # TTL=64 才是 Mac

# 2. IP 是否变了（DHCP 重分配）→ 扫子网找 22 端口
for i in $(seq 1 254); do (timeout 0.4 bash -c "echo > /dev/tcp/172.16.105.$i/22" 2>/dev/null && echo "172.16.105.$i OPEN") & done; wait

# 3. IP 变了就改 C:\Users\wuyan\.ssh\config 的 HostName
```

### 5.5 mihomo 启动失败

```bash
# 手动前台跑看报错
ssh mac-mini "/usr/local/bin/mihomo -d ~/mihomo-proxy"

# 只校验配置语法
ssh mac-mini "/usr/local/bin/mihomo -d ~/mihomo-proxy -t"
```

---

## 六、卸载（完整回滚）

```bash
ssh mac-mini "
bash ~/mihomo-install/setup-system-proxy.sh off
launchctl unload ~/Library/LaunchAgents/com.mihomo.proxy.plist 2>/dev/null
pkill -x mihomo 2>/dev/null
rm ~/Library/LaunchAgents/com.mihomo.proxy.plist
echo '密码' | sudo -S rm /usr/local/bin/mihomo
rm -rf ~/mihomo-proxy ~/mihomo-install
echo '卸载完成'
"
```

---

## 七、相关文档

| 文档 | 位置 |
|------|------|
| 本手册 | `workskill/doc/mac-mini/mac-mini-management-guide.md` |
| SSH 部署方案（含踩坑全过程） | `workskill/doc/mac-mini/mac-mini-ssh-remote-control-plan.md` |
| 代理项目与 Mac 部署手册（已修复） | `D:\mydoc\proxy\docs\mac-mini-deploy.md` |
| 服务器端部署指南 | `D:\mydoc\proxy\proxy-deployment-guide.md` |
| 代理故障排查大全 | `D:\mydoc\proxy\troubleshooting.md` |
