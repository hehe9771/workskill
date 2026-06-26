# Claude Code v2.1.154 到 v2.1.187 完整更新总结

## 版本总览表

| 版本 | 日期 | 亮点 |
|------|------|------|
| 2.1.154 | 5/28 | Opus 4.8、动态工作流、快速模式2x |
| 2.1.157 | 5/29 | .claude/skills 自动加载、claude plugin init |
| 2.1.158 | 5/30 | Auto 模式支持 Bedrock/Vertex/Foundry |
| 2.1.160 | 6/2 | Shell 启动文件写入前提示、ultracode 触发关键字 |
| 2.1.162 | 6/3 | claude agents --json 增强、安静启动 |
| 2.1.163 | 6/4 | 版本范围托管设置、/plugin list、Hook additionalContext |
| 2.1.166 | 6/6 | fallbackModel 设置、通配符拒绝规则、跨会话消息加固 |
| 2.1.169 | 6/8 | --safe-mode、/cd、post-session runner hook |
| 2.1.170 | 6/9 | Claude Fable 5 模型发布 |
| 2.1.172 | 6/10 | 嵌套子agent(5层深度)、Bedrock ~/.aws 区域读取 |
| 2.1.175 | 6/12 | 企业模型强制 enforceAvailableModels |
| 2.1.176 | 6/12 | 会话标题自动使用对话语言、Bedrock 凭证缓存优化 |
| 2.1.178 | 6/15 | Agent团队简化、Tool(param:value) 权限语法 |
| 2.1.181 | 6/17 | /config key=value、Apple Events沙盒、30+ bug修复 |
| 2.1.183 | 6/19 | Auto模式安全(阻止破坏性git/基础设施命令) |
| 2.1.186 | 6/22 | claude mcp login/logout、bash自动响应 |
| 2.1.187 | 6/23 | 沙盒凭证保护、组织模型限制、鼠标点击支持 |

---

## 六大主题分类

### 1. 模型更新

- **Opus 4.8** (v2.1.154): 默认高effort, 新增xhigh级别, 快速模式2x速率
- **Claude Fable 5** (v2.1.170): Mythos级别模型, 能力超越此前所有模型

### 2. Agent与子Agent系统

- **嵌套子agent** (v2.1.172): 子agent可再生成子agent, 最深5层
- **Agent团队简化** (v2.1.178): 移除TeamCreate/TeamDelete, 每个会话一个隐式团队, 直接通过Agent工具的name参数生成队友
- **后台子agent权限提示** (v2.1.186): 改为在主会话中显示权限提示, 而非自动拒绝
- 前台子agent遵守5层深度限制 (v2.1.181)
- 空闲子agent 30秒后自动隐藏 (v2.1.181)
- 子agent深度跟踪修复 (v2.1.187)
- 泄漏的agent worktree注册自动清理 (v2.1.187)

### 3. 安全与沙盒

- **sandbox.credentials** (v2.1.187): 阻止沙盒命令读取凭证文件和秘密环境变量
- **sandbox.allowAppleEvents** (v2.1.181): macOS上Apple Events opt-in
- **enforceAvailableModels** (v2.1.175): 企业管理员可强制模型允许列表
- **Auto模式安全** (v2.1.183): 阻止破坏性git命令(git reset --hard等), terraform/pulumi/cdk destroy
- **Shell启动文件写入前提示** (v2.1.160): .zshenv/.bash_login等写入前确认
- **组织模型限制** (v2.1.187): 在模型选择器中显示组织限制提示
- **跨会话消息加固** (v2.1.166): SendMessage中继消息不再携带用户权限
- **通配符拒绝规则** (v2.1.166): "*"拒绝所有工具, allow规则拒绝非MCP通配符

### 4. MCP改进

- **claude mcp login/logout** (v2.1.186): CLI认证MCP服务器, 支持--no-browser用于SSH
- **MCP工具空闲超时** (v2.1.187): 远程MCP工具调用不再挂起5分钟, 可配置CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT
- **MCP OAuth改进** (v2.1.181): 浏览器页面匹配Claude Code视觉风格, 成功后自动关闭

### 5. 企业/组织功能

- **版本范围托管** (v2.1.163): requiredMinimumVersion/requiredMaximumVersion
- **fallbackModel** (v2.1.166): 最多三个回退模型在过载时尝试
- **--safe-mode** (v2.1.169): 禁用所有自定义化以排查问题
- **post-session hook** (v2.1.169): 自托管runner在会话结束后、workspace删除前运行
- **会话标题语言** (v2.1.176): 自动以对话语言生成标题

### 6. UI/UX与开发者体验

- **动态工作流** (v2.1.154): 跨数百个后台agent编排, /workflows查看
- **/config key=value** (v2.1.181): 从提示直接设置任何配置
- **Tool(param:value)权限语法** (v2.1.178): 匹配工具输入参数
- **鼠标点击支持** (v2.1.187): 全屏模式选择菜单支持鼠标
- **会话标题自动语言** (v2.1.176)
- **bash自动响应** (v2.1.186): ! bash命令触发Claude自动响应
- **嵌套skills加载** (v2.1.178): .claude/skills嵌套目录自动加载
- **.claude/skills自动加载** (v2.1.157): 无需市场安装
- **claude plugin init** (v2.1.157): 脚手架新插件
- **流式传输改进** (v2.1.181): 长段落逐行显示
- **CJK修复** (v2.1.187): 粘贴的韩语/CJK文本不再乱码

---

## 重要破坏性/行为变更汇总

1. **v2.1.154**: 弃用CLAUDE_CODE_OPUS_4_6_FAST_MODE_OVERRIDE; /effort标签改名; 工作流触发关键字改为ultracode
2. **v2.1.160**: 工作流触发关键字从workflow改为ultracode; 移除JetBrains插件安装建议
3. **v2.1.166**: MAX_THINKING_TOKENS=0现在通过API禁用thinking; Claude Code在回退模型上重试一次非重试错误
4. **v2.1.178**: 工作流触发关键字改为明确短语如"run a workflow"或"workflow:"
5. **v2.1.186**: 后台子agent改为在主会话显示权限提示; /review改用/code-review medium引擎; CLAUDE_CODE_MAX_RETRIES上限15

---

## 稳定性修复亮点(跨版本)

- 1M上下文无积分会话永久卡住 -> 自动压缩 (v2.1.172)
- OOM崩溃(陈旧websocket/OAuth文件描述符) (v2.1.178)
- 启动回归120ms已修复 (v2.1.181)
- 网络降级启动阻塞15秒已修复 (v2.1.181)
- Write/Edit在网络驱动器生成0字节文件 (v2.1.181)
- 流式请求唤醒后失败 (v2.1.186)
- Remote MCP工具调用挂起5分钟 (v2.1.187)
- Windows Terminal全屏TUI损坏 (v2.1.183)
- VSCode恢复大会话无响应 (v2.1.187)

---

## 数据来源

- 官方changelog: https://code.claude.com/docs/en/changelog
- GitHub releases: https://github.com/anthropics/claude-code/releases
- 调研时间: 2026/06/24
