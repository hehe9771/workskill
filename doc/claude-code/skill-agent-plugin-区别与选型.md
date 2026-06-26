# Skill vs Agent vs Plugin — 区别与选型指南

## 一句话区分

| | 一句话 | 类比 |
|---|---|---|
| **Skill（技能）** | 给 Claude 的一段指令，告诉它"遇到X事时按Y方式做" | 员工手册里的一章操作规程 |
| **Agent（智能体）** | 一个带角色定义的可复用执行者，有独立工具集和模型 | 一个专职岗位（审计员、测试员） |
| **Plugin（插件）** | 把 Skill + Agent + Hook + MCP 打包的分发容器 | 一个 npm 包 / Docker 镜像 |

---

## 三要素对比

| 维度 | Skill | Agent | Plugin |
|------|-------|-------|--------|
| **本质** | 一段 prompt 指令 | 一个角色定义文件 | 一个可分发的包 |
| **最小文件** | `SKILL.md`（1 个文件） | `xxx.md`（1 个文件，含 frontmatter） | 目录（含 `CLAUDE.md` + 子组件） |
| **运行方式** | 在当前 Claude 进程中加载，不产生新进程 | 启动独立 Claude 子进程，有隔离上下文 | 安装后，其内部组件各自按原方式运行 |
| **激活方式** | `/skill-name` 或自动匹配 | 主 Claude/Agent 通过 `Agent` 工具启动 | 安装后其内部 Skill/Agent/Hook 各自注册 |
| **自动加载** | ✅ 放到 `.claude/skills/` 即生效 | ✅ 放到 `.claude/agents/` 即生效 | Skill/Agent 自动，**Hook 必须手动注册** |
| **独立性** | 低，依附主进程 | 中，独立上下文但受主 Claude 管理 | 无，本身不运行，只承载组件 |
| **成本** | 无额外 token（指令在 prompt 里） | 有额外 token（子进程独立推理） | 取决于内含组件 |
| **模型选择** | 无法指定，跟随当前模型 | 可指定 `model: sonnet/opus/haiku` | 无，取决于内含 Agent |
| **工具限制** | 无法限制，使用当前可用工具 | 可通过 `tools: [...]` 限定可用工具 | 无，取决于内含组件 |

---

## 补充：Hook 是唯一的"非自动加载"组件

### 关键差异

| 组件 | 放进目录就生效？ | 还需要做什么？ |
|------|-----------------|---------------|
| Skill | ✅ 是 | 无 |
| Agent | ✅ 是 | 无 |
| **Hook** | **❌ 否** | **必须在 `settings.json` 的 `hooks` 段显式注册** |

### Hook 注册格式

```json
// ~/.claude/settings.json 中的 hooks 段
{
  "hooks": {
    "PostToolUse": [           ← 事件类型
      {
        "matcher": "Write",    ← 匹配条件（* 表示全部，或指定工具名）
        "hooks": [
          {
            "command": "bash ~/.claude/skills/my-plugin/hooks/auto-format.sh",
            "type": "command",
            "timeout": 5       ← 超时秒数
          }
        ]
      }
    ],
    "SessionStart": [          ← 另一个事件类型
      {
        "matcher": "*",
        "hooks": [
          {
            "command": "node ~/.claude/skills/my-plugin/hooks/init.mjs",
            "type": "command"
          }
        ]
      }
    ]
  }
}
```

**可用事件类型**：`SessionStart`、`SessionEnd`、`PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`Stop`、`UserPromptSubmit`、`PreCompact`、`SubagentStart`、`SubagentStop`、`Notification`、`PermissionRequest`。

**matcher 的用法**：
- `"*"` — 所有该类型事件都触发
- 具体工具名如 `"Write"`、`"Bash"` — 只有该工具执行时才触发
- 空字符串 `""` — 同 `"*"`

### 实际例子

你当前 `settings.json` 中 `claude-notifications-go` 插件的 Hook 注册：

```json
"Notification": [
  {
    "hooks": [
      {
        "command": "bash -c 'dir=$(for d in ~/.claude/plugins/cache/claude-notifications-go/.../; do ...); \"${dir}bin/claude-notifications-windows-amd64.exe\" handle-hook Notification'",
        "type": "command"
      }
    ],
    "matcher": ""
  }
]
```

注意：即使是插件安装的 Hook，也是通过 `claude plugin install` **自动写入 settings.json**，而不是 Claude 自动发现的。**Hook 永远不会自动加载。**

---

### 不使用 `claude plugin install`，如何注册 Hook？

v2.1.157 之后，Skill 和 Agent 可以不经市场安装直接放目录生效。但 Hook 仍然需要注册。有两种方式：

#### 方式 1：手动编辑 settings.json（推荐，最可控）

把插件的 Hook 脚本复制到 `.claude/skills/` 下，然后在 `settings.json` 的 `hooks` 段添加注册：

```bash
# 1. 把 Hook 脚本放进来
cp ~/downloads/some-plugin/hooks/auto-format.sh \
   ~/.claude/skills/some-plugin/hooks/auto-format.sh

# 2. 手动在 settings.json 的 hooks 段加一条注册
```

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "command": "bash ~/.claude/skills/some-plugin/hooks/auto-format.sh",
            "type": "command",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

#### 方式 2：用 `/config` 命令添加

```
/config hooks.PostToolUse.push { "matcher": "Write", "hooks": [{ "command": "bash ~/.claude/skills/some-plugin/hooks/auto-format.sh", "type": "command" }] }
```

#### 两种方式的对比

| | 手动编辑 settings.json | /config 命令 |
|--|----------------------|-------------|
| 可控性 | 高，可以看完整结构再改 | 中，语法不熟容易写错 |
| 批量操作 | 方便，一次改多条 | 逐条执行 |
| 风险 | 改错 JSON 会导致启动失败 | 语法错误会直接拒绝 |
| 推荐场景 | 一次性注册多条 Hook | 只加一条，不想打开文件 |

#### 完整流程示例

假设你从 GitHub 克隆了一个包含 Hook 的插件，想不经安装直接使用：

```bash
# 第 1 步：克隆到 skills 目录
git clone https://github.com/xxx/auto-format-plugin.git \
  ~/.claude/skills/auto-format-plugin

# 第 2 步：此时 Skill 和 Agent 已自动生效（如果插件里有）
# 但 Hook 还没注册

# 第 3 步：打开 settings.json，在 hooks 段添加
# （或者用 /config 命令）

# 第 4 步：重启 Claude Code，Hook 生效
```

**核心结论**：v2.1.157 的"自动加载"只覆盖 Skill 和 Agent，**Hook 的注册方式没有变化**。不管插件是否通过市场安装，Hook 都必须出现在 `settings.json` 的 `hooks` 段才能生效。

---

## 文件结构对比

---

## 文件结构对比

### Skill — 最小
```
.claude/skills/
└── code-review/
    └── SKILL.md              ← 就一个文件，YAML frontmatter + 指令
```

### Agent — 独立
```
.claude/agents/
└── security-reviewer.md      ← 一个 .md 文件，含 frontmatter 定义角色和工具
```

### Plugin — 容器
```
my-plugin/
├── CLAUDE.md                 ← 插件入口，元信息
├── skills/                   ← 可含 0~N 个 Skill
│   ├── lint-check/
│   │   └── SKILL.md
│   └── deploy-guide/
│       └── SKILL.md
├── agents/                   ← 可含 0~N 个 Agent
│   ├── builder.md
│   └── tester.md
└── package.json              ← 发布用元数据
```

---

## 什么时候建什么

### 建 Skill 最合适（90% 的场景）

**判断标准**：只需要"告诉 Claude 怎么做"，不需要独立上下文、不需要限定工具/模型。

**典型场景**：

| 场景 | 为什么选 Skill |
|------|---------------|
| 编码规范（命名、缩进、注释风格） | 只是一段规则，当前 Claude 遵守即可 |
| 工作流指南（"先建 PR 再发通知"） | 操作流程，不需要独立进程 |
| 审查清单（"检查这 10 项"） | 指令式，在当前对话里执行 |
| 团队约定（"数据库表前缀统一用 t_"） | 共享知识，当前 Claude 记住就行 |
| 特殊处理指南（"遇到报错按这三步排查"） | 经验沉淀，一段文字即可 |

**不要建 Skill 的场景**：
- 需要限定可用工具集 → 建 Agent
- 需要指定不同模型（如用 Opus 做深度推理） → 建 Agent
- 需要独立上下文避免污染主对话 → 建 Agent
- 要分享给别人安装使用 → 建 Plugin

---

### 建 Agent 最合适

**判断标准**：需要**独立执行上下文**、**限定工具权限**、**指定模型**，或者这个任务需要**反复被主 Claude 委托**。

**典型场景**：

| 场景 | 为什么选 Agent |
|------|---------------|
| 专职代码审查员 | 需要独立上下文，不能影响主对话；需要限定工具（只读+grep） |
| 构建错误修复专家 | 需要独立子进程处理，修复完返回结果 |
| 安全审计员 | 需要限定工具集（不让它写文件，只让它读和分析） |
| 测试执行者 | 需要运行测试命令，有独立 stdout/stderr |
| 文档更新专员 | 需要指定 haiku 模型（便宜且够用） |
| 多层嵌套任务（审查者再派生子审查者） | 只有 Agent 支持嵌套调用，Skill 不行 |

**不要建 Agent 的场景**：
- 只是一段知识/规范 → 建 Skill（Agent 的 prompt 本质和 Skill 一样，但多了进程开销）
- 想打包分发给别人 → 建 Plugin（Agent 只能放 `.claude/agents/`，不能单独分发）

---

### 建 Plugin 最合适

**判断标准**：需要**打包分发**、**一键安装**、**包含多个组件**（Skill + Agent + Hook 组合）。

**典型场景**：

| 场景 | 为什么选 Plugin |
|------|---------------|
| 团队共享开发规范（含 Skill + 自定义 Agent） | 一条 `claude plugin install` 全员安装 |
| 完整开发工作流包（Skill + Hook + MCP 配置） | 多组件打包，安装即全套就绪 |
| 第三方工具集成（如 gstack、claude-mem） | 有版本号、可更新、可卸载 |
| 企业级标准化包 | 统一版本、统一组件、统一分发 |
| 开源项目提供 Claude 集成 | 用户 git clone 或 install 即可使用 |

**不要建 Plugin 的场景**：
- 只是自己用的一段规范 → 建 Skill（放 `.claude/skills/` 下就行）
- 只是一个自定义角色 → 建 Agent（放 `.claude/agents/` 下就行）
- 不需要安装/更新/版本管理 → 不需要 Plugin 的容器能力

---

## 决策树

```
你想做什么？
│
├─ 只是沉淀一段"怎么做"的知识/规范/清单？
│   └─ YES → 建 Skill
│
├─ 需要一个"专职角色"，要独立上下文/限定工具/指定模型？
│   └─ YES → 建 Agent
│
├─ 需要把多个 Skill + Agent + Hook 打包在一起，分发给别人？
│   └─ YES → 建 Plugin
│
└─ 以上都不是？
    └─ 可能只需要改 CLAUDE.md 或 settings.json
```

---

## 常见组合模式

### 模式 1：纯 Skill（最常见）
```
.claude/skills/
└── coding-standards/
    └── SKILL.md
```
场景：个人/团队的编码规范沉淀。无需额外组件。

### 模式 2：Skill + Agent（插件内部）
```
code-quality-plugin/
├── CLAUDE.md
├── skills/
│   └── review-checklist/
│       └── SKILL.md          ← 审查知识清单
└── agents/
    └── reviewer.md            ← 专职审查者，会引用上面的 checklist
```
场景：一个完整的代码质量工具包。Agent 是执行者，Skill 是它的知识来源。

### 模式 3：Skill + Agent + Hook
```
auto-format-plugin/
├── CLAUDE.md
├── skills/
│   └── format-guide/
│       └── SKILL.md          ← 格式化规范
├── agents/
│   └── formatter.md           ← 格式化 Agent
└── hooks/
    └── post-write.sh          ← 写入后自动触发格式化
```
场景：全自动格式化。Hook 监听写入事件 → 触发 Agent → Agent 参考 Skill 执行。

### 模式 4：Agent 嵌套
```
.claude/agents/
├── code-generator.md          ← 主 Agent（协调者）
├── frontend-reviewer.md       ← 子 Agent
└── backend-reviewer.md        ← 子 Agent
```
场景：代码生成 + 双重审查。主 Agent 生成代码后自动派生两个子 Agent。
不需要 Skill，因为每个 Agent 的 prompt 已自带审查逻辑。

---

## 成本考量

| 方案 | Token 成本 | 适用频率 |
|------|-----------|---------|
| Skill | 极低（指令在 prompt 里，不额外推理） | 每天多次 |
| Agent | 中~高（每次启动 = 一次完整推理） | 按需启动 |
| Plugin | 取决于内含组件 | 一次性安装 |

**省钱建议**：
- 高频、轻量的操作 → Skill
- 低频、重度的操作 → Agent（用 haiku 模型降低成本）
- 需要深度推理的 Agent → 指定 opus，但限制调用频率
