# Mac Mini 远程使用 Claude Code 落地文档

> 落地日期：2026-09-04
> 环境：Mac Mini（macOS 26.2，ARM，`ssh mac-mini` = 172.16.105.139，用户 `mac`）+ Windows 工作机 + 安卓手机
> 目标：手机（在家局域网 / 外出 Tailscale）远程接入 Mac Mini 上持久运行的 Claude Code

---

## 一、架构总览

```
手机 Termius/Blink ──┐
                     ├─ SSH ──> Mac Mini sshd ──> tmux 会话「claude」──> claude (GLM flash)
Windows 工作机 ──────┘              │
                                Tailscale（外网）/ 局域网 WiFi（在家）
```

- tmux 会话断连不退出：手机断开、App 被杀，Claude Code 继续在 Mac 上跑
- 两套入口地址（SSH 全部走 22 端口）：

| 场景 | 地址 |
|---|---|
| 在家（同 WiFi） | `172.16.105.139` |
| 在外（手机开 Tailscale） | `100.114.87.19` |
| 用户名 / 密码 | `mac` / Mac 开机登录密码 |

---

## 二、阶段一：Claude Code 模型配置切换（qwen → GLM flash）

### 做了什么
- 备份旧配置：`~/.claude/settings.json` → `~/.claude/settings.json.bak-qwen-20260904`
- 新 `settings.json` 的 `env` 块与 Windows 侧 `C:\Users\wuyan\.claude\setting\settings-glm-flash.json` 完全一致（token、`dashscope.aliyuncs.com/apps/anthropic` 端点、全模型映射 `ZHIPU/GLM-5.3-Flash[1M]` / NAME `A006`），仅去掉 `CLAUDE_CODE_USE_POWERSHELL_TOOL`
- 保留 Mac 本地项：`permissions.defaultMode: bypassPermissions`、`theme`、`includeCoAuthoredBy`
- 删除旧配置顶层无效残留 `"CLAUDE_MODEL"`（放顶层不生效）
- 未带入 Windows 专属块：`hooks`（notifications 插件脚本 Mac 没有）、`statusLine`（claude-hud 未装）、`extraKnownMarketplaces`/`enabledPlugins`（插件体系两端独立管理）

### 验证
```bash
# Mac 上真实调用一次（走新网关）
zsh -ic "claude -p \"Reply with exactly: OK\""
```
- 启动时的 `[claude-code:unrecognized_model]` 警告无害（模型名不在 CLI 内置目录），请求正常走通
- 证据链：警告回显的模型名来自新 env（旧的是 qwen）+ 成功返回 = 新配置生效

### 回滚
```bash
cp ~/.claude/settings.json.bak-qwen-20260904 ~/.claude/settings.json
```

---

## 三、阶段二：SSH + tmux 持久会话

| 项 | 状态/命令 |
|---|---|
| SSH 远程登录 | 原本已开启（系统设置 → 通用 → 共享 → 远程登录），sshd `passwordauthentication yes` |
| tmux | `brew install tmux` → 3.7c，装在 `/opt/homebrew/bin/tmux` |
| 持久会话 | `tmux new-session -d -s claude -c ~`（detached，起始目录 home） |
| 休眠 | `sudo -n pmset -a sleep 0`（免密 sudo 可用；显示器休眠本来就是 0） |

验证会话内 claude 可用：
```bash
tmux send-keys -t claude "which claude && claude --version" Enter
tmux capture-pane -t claude -p | tail -3
# → /opt/node-v22.12.0-darwin-arm64/bin/claude，2.1.258 ✅
```

---

## 四、阶段三：Tailscale 外网访问

```bash
# 1. 安装 CLI 版（非 App Store/cask 版，便于远程无 GUI 管理）
brew install tailscale          # → 1.102.3

# 2. 守护进程设为开机自启（root LaunchDaemon）
sudo brew services start tailscale

# 3. 发起登录授权（⚠️ 必须后台跑，否则 SSH 会挂住等授权）
nohup sudo tailscale up --hostname=mac-mini > /tmp/ts-up.log 2>&1 &
cat /tmp/ts-up.log               # 取出 https://login.tailscale.com/a/xxx 授权链接

# 4. 用户在浏览器打开链接登录/注册（手机与 Mac 必须同一账号），授权后：
tailscale ip -4                  # → 100.114.87.19
```

- 账号 `wuyan9771@`，tailnet 内设备：`mac-mini` 100.114.87.19、安卓手机 `node` 100.85.242.12
- 登录有效期默认 **180 天**，到期连接失败时重跑第 3 步重新授权
- `tailscale ping <对端IP>` 可测隧道连通性（本次实测走 DERP 香港中继）

---

## 五、手机端操作卡（最终可用版）

1. **装 App**：iOS 用 Blink Shell / Termius；安卓用 Termius
2. **手机装 Tailscale** 并登录同一账号（wuyan9771），在外面打开连接开关
3. **新建 SSH 主机**：

| 字段 | 在外 | 在家 |
|---|---|---|
| 地址 | `100.114.87.19` | `172.16.105.139` |
| 端口 | 22 | 22 |
| 用户名 | `mac` | `mac` |
| 密码 | Mac 开机密码 | 同左 |

4. **日常口诀**：
   - 接入：`tmux attach -t claude` → `claude --resume`（恢复上次对话；首次直接 `claude`）
   - 离开：`Ctrl+b` 松开再按 `d`（会话后台继续跑）
   - Mac 重启后会话丢失：`tmux new -s claude` 重建 → `claude --resume` 恢复对话

---

## 六、踩坑实录（最有价值的部分）

| # | 坑 | 根因与解法 |
|---|---|---|
| 1 | 非交互 SSH 下 `claude not found` | claude 装在 `/opt/node-v22.12.0-darwin-arm64/bin/`，PATH 只在交互式 zsh（`.zshrc`）里配。远程跑 claude 必须 `zsh -ic "..."`；tmux 内是交互 shell 所以没问题 |
| 2 | Windows 配置不能整份照搬到 Mac | PowerShell 工具开关、hooks（notifications 脚本不存在会报错）、statusLine（claude-hud 未装）、插件块都是 Windows 侧环境依赖，只同步 `env` 模型块 |
| 3 | `tailscale up` 挂死 SSH | 它会阻塞等待浏览器授权，必须 `nohup ... &` 后台跑再从日志抓授权 URL |
| 4 | **手机连不上 22 端口 + 浏览器 502**（本次最隐蔽） | 手机上的代理 App（Clash 类）全局接管后，把发往 `100.114.87.19` 的流量当公网请求转发到海外节点，海外节点够不到 CGNAT 段 → 22 超时、HTTP 502。而 Tailscale 自己的 UDP 心跳没被拦，`tailscale ping` 依然通，极具迷惑性。**解法：断开代理 App**；共存需在 Clash 配置加 `IP-CIDR,100.64.0.0/10,DIRECT` |
| 5 | 判断请求是否到达 Mac | 临时 `python3 -m http.server 8000` 起测试页 + 看 `/tmp/http-test.log` 有无访问记录。502 响应本身即证明请求被中间代理截胡（Mac 的 http.server 不会回 502） |
| 6 | Mac 端自检被干扰 | Mac 本机 `ssh mac@100.x` 报 Too many authentication failures：本机 ssh-agent 密钥过多逐个尝试超限，外部连接（如手机）不受影响，勿误判为服务故障 |
| 7 | 诊断顺序口诀 | 先 `tailscale status`（对端在不在线）→ `tailscale ping`（隧道通不通）→ 服务端日志（请求到没到）→ 客户端填写（IP/密码），由网络层向应用层收敛 |

---

## 七、故障排查速查表

| 症状 | 排查 |
|---|---|
| 手机连不上 22 | ① Tailscale App 开关开了没 ② **代理 App 断了没**（坑 4）③ IP/用户名/密码 ④ Mac 端 `sudo sshd -T \| grep passwordauth` |
| 浏览器/SSH 出现 502、超时但 Mac 端无访问日志 | 中间有代理截胡，见坑 4 |
| Tailscale 连不上/要重新登录 | Mac 端 `tailscale status` 看 logged out → `nohup sudo tailscale up` 重授权（坑 3） |
| `tmux attach` 报 no session | Mac 重启后会话丢了 → `tmux new -s claude` |
| `claude --resume` 没有历史 | 换了目录或首次使用；在 tmux 会话内对应项目目录下执行 |
| Mac 端 claude 不在 PATH | 用 `zsh -ic "claude ..."`（坑 1） |

## 八、关键路径备忘

```
Mac: ~/.claude/settings.json            # GLM flash 配置（token 完整值在此，文档脱敏）
Mac: ~/.claude/settings.json.bak-qwen-20260904   # 旧 qwen 配置备份
Windows: C:\Users\wuyan\.claude\setting\settings-glm-flash.json   # 配置源头模板
tailscaled: sudo brew services（root LaunchDaemon，开机自启）
```
