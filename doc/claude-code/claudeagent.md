# Claude Code Agent Type 完整参考手册

> 生成时间：2026/06/12
> 本文档列出 Claude Code 支持的所有 agent type，包括来源、作用和应用场景

---

## 一、Agent 管理机制概述

### 1.1 管理方式

子智能体通过 **Agent 工具**创建和管理：

```
主 Agent (Orchestrator)
├── spawn Agent A → 返回结果
├── spawn Agent B → 返回结果  
└── spawn Agent C → 返回结果
```

**关键特性：**
- 每个子智能体是**独立进程**，有自己独立的 context window
- 子智能体完成后返回**最终文本结果**给主 Agent
- 主 Agent 负责整合所有子智能体的输出
- 子智能体无法直接访问主 Agent 的对话历史

### 1.2 子智能体间的交互

**子智能体之间没有直接交互**

```
❌ 错误理解：子智能体 A → 子智能体 B
✅ 正确模型：子智能体 A → 主 Agent ← 子智能体 B
```

交互模式是 **Hub-and-Spoke（中心辐射型）**：
- 主 Agent 是中心节点
- 子智能体只能通过主 Agent 间接"通信"
- 如需传递信息，主 Agent 需要在 prompt 中显式传入

### 1.3 拆分标准

| 维度 | 拆分子智能体的条件 |
|------|------------------|
| **独立性** | 任务可独立执行，无强依赖 |
| **专业性** | 需要特定领域知识（如 code-reviewer、security-reviewer） |
| **上下文隔离** | 避免单个 context window 过载 |
| **并行价值** | 多任务并行能显著减少总时间 |
| **对抗验证** | 需要独立视角交叉验证（如 adversarial verify） |

### 1.4 并行 vs 串行决策

```javascript
// 并行：无依赖关系
parallel([
  agent("安全分析"),
  agent("性能审查"),
  agent("代码质量检查")
])

// 串行：有依赖关系
resultA = agent("阶段1: 需求分析")
resultB = agent("阶段2: 基于A的结果设计方案", {context: resultA})

// 混合：DAG 依赖
parallel([
  agent("前端设计"),
  agent("后端设计")
])
// 等上面都完成后
agent("集成设计", {context: [前端结果, 后端结果]})
```

---

## 二、Agent 来源说明

| 来源标识 | 说明 |
|----------|------|
| **内置** | Claude Code 核心功能，系统提示中直接定义 |
| **ecc** | [ECC Universal](https://github.com/affaan-m/ECC) 插件 (v2.0.0-rc.1) |
| **understand-anything** | Understand-Anything 插件 (v2.7.6)，知识图谱分析 |
| **用户自定义** | 位于 `~/.claude/agents/` 目录 |
| **omc** | Oh-My-ClaudeCode 扩展，位于 `~/.claude/omc/agents/` |

---

## 三、核心通用 Agents

| Agent Type | 来源 | 作用 | 应用场景 |
|------------|------|------|----------|
| **claude** | 内置 | 默认通用 agent，FleetView 的 catch-all | 没有更专业 agent 匹配时的默认选择 |
| **general-purpose** | 内置 | 通用任务执行，工具全开 | 复杂多步骤任务、代码搜索、不确定用什么 agent 时 |
| **Explore** | 内置 | 只读搜索 agent，广撒网式探索（breadth: medium/very thorough） | 大规模文件搜索、命名规范扫描、只需结论不需审计时 |

---

## 四、规划与设计 Agents

| Agent Type | 来源 | 作用 | 应用场景 |
|------------|------|------|----------|
| **architect** | 内置 + ecc | 软件架构专家 | 系统设计、可扩展性分析、技术决策、新功能规划 |
| **planner** | 内置 + ecc | 实现规划专家 | 复杂功能拆分、重构规划、自动生成 step-by-step 计划 |
| **Plan** | 内置 | 架构规划 agent | 需要实现策略设计时，返回分步计划、关键文件、架构权衡 |

---

## 五、代码审查 Agents

| Agent Type | 来源 | 作用 | 应用场景 |
|------------|------|------|----------|
| **code-reviewer** | 内置 + ecc | 通用代码审查 | 主要项目步骤完成后，审查是否符合计划和编码标准 |
| **security-reviewer** | 内置 + ecc | 安全漏洞检测 | 处理用户输入、认证、API 端点、敏感数据后的安全检查 |

---

## 六、语言专用 Review Agents

### 6.1 内置语言 Reviewers

| Agent Type | 来源 | 作用 | 应用场景 |
|------------|------|------|----------|
| **python-reviewer** | 内置 + ecc | Python 代码审查 | PEP 8、类型提示、安全性、性能（Python 项目必用） |
| **go-reviewer** | 内置 + ecc | Go 代码审查 | 惯用 Go、并发模式、错误处理、性能（Go 项目必用） |
| **rust-reviewer** | 内置 + ecc | Rust 代码审查 | 所有权、生命周期、错误处理、unsafe 使用（Rust 项目必用） |
| **java-reviewer** | 内置 + ecc | Java/Spring Boot 审查 | 分层架构、JPA 模式、安全性、并发（Spring Boot 必用） |
| **kotlin-reviewer** | 内置 + ecc | Kotlin/Android 审查 | 协程安全、Compose 最佳实践、Clean Architecture |
| **cpp-reviewer** | 内置 + ecc | C++ 代码审查 | 内存安全、现代 C++ 惯用法、并发、性能 |

### 6.2 ECC 插件扩展 Reviewers

| Agent Type | 来源 | 作用 | 应用场景 |
|------------|------|------|----------|
| **typescript-reviewer** | ecc | TypeScript/JavaScript 审查 | 类型安全、React/Vue 模式、异步处理 |
| **react-reviewer** | ecc | React 代码审查 | Hooks、组件设计、性能优化 |
| **swift-reviewer** | ecc | Swift/iOS 审查 | Actor、并发、SwiftUI 模式 |
| **php-reviewer** | ecc | PHP 代码审查 | Laravel 模式、安全性 |
| **django-reviewer** | ecc | Django 审查 | ORM、视图、安全性 |
| **fastapi-reviewer** | ecc | FastAPI 审查 | 异步路由、Pydantic 模型 |
| **fsharp-reviewer** | ecc | F# 代码审查 | 函数式模式、类型提供程序 |
| **csharp-reviewer** | ecc | C# 审查 | .NET 模式、异步 |
| **dart-build-resolver** | ecc | Dart/Flutter 构建 | Flutter 构建错误 |
| **flutter-reviewer** | ecc | Flutter 审查 | Widget 设计、状态管理 |
| **mle-reviewer** | ecc | ML 工程审查 | 模型训练、数据管道 |

---

## 七、构建错误修复 Agents

### 7.1 内置构建修复

| Agent Type | 来源 | 作用 | 应用场景 |
|------------|------|------|----------|
| **build-error-resolver** | 内置 + ecc | TypeScript/通用构建错误 | 构建失败、类型错误时快速修复（最小 diff） |
| **go-build-resolver** | 内置 + ecc | Go 编译/vet 错误 | Go 构建失败、vet 问题、linter 警告 |
| **rust-build-resolver** | 内置 + ecc | Cargo 构建错误 | 编译、依赖、borrow checker 问题 |
| **java-build-resolver** | 内置 + ecc | Java/Maven/Gradle 错误 | 编译、依赖、构建配置问题 |
| **kotlin-build-resolver** | 内置 + ecc | Kotlin/Gradle 错误 | 编译、依赖、Gradle 配置问题 |
| **cpp-build-resolver** | 内置 + ecc | C++/CMake 编译错误 | CMake、链接、模板错误 |

### 7.2 ECC 插件扩展构建修复

| Agent Type | 来源 | 作用 | 应用场景 |
|------------|------|------|----------|
| **pytorch-build-resolver** | ecc | PyTorch 构建错误 | CUDA、依赖、编译问题 |
| **react-build-resolver** | ecc | React 项目构建 | Next.js/Vite 构建错误 |
| **django-build-resolver** | ecc | Django 构建错误 | 配置、迁移问题 |

---

## 八、测试与质量 Agents

| Agent Type | 来源 | 作用 | 应用场景 |
|------------|------|------|----------|
| **tdd-guide** | 内置 + ecc | TDD 专家 | 强制 write-tests-first 方法论，确保 80%+ 覆盖率 |
| **e2e-runner** | 内置 + ecc | 端到端测试 | 使用 Vercel Agent Browser/Playwright 测试关键用户流程 |
| **qa-tester** | omc | QA 测试专家 | 功能测试、回归测试 |
| **test-engineer** | omc | 测试工程师 | 单元测试、集成测试编写 |
| **verifier** | omc | 验证专家 | 代码变更验证、结果确认 |

---

## 九、文档与知识 Agents

| Agent Type | 来源 | 作用 | 应用场景 |
|------------|------|------|----------|
| **doc-updater** | 内置 + ecc | 文档/codemap 专家 | 更新 codemap、生成文档、更新 README |
| **docs-lookup** | 内置 + ecc | 文档查询 agent | 查询库/框架/API 的当前文档和使用示例 |
| **claude-code-guide** | 内置 | Claude Code 使用指南 | 解答 Claude Code 功能、配置、MCP、SDK 等问题 |
| **document-specialist** | omc | 文档专家 | 技术文档撰写、API 文档生成 |
| **writer** | omc | 写作助手 | 通用文本撰写、内容优化 |

---

## 十、重构与维护 Agents

| Agent Type | 来源 | 作用 | 应用场景 |
|------------|------|------|----------|
| **refactor-cleaner** | 内置 + ecc | 死代码清理 | 移除未使用代码、重复代码，运行 knip/depcheck/ts-prune |
| **code-simplifier** | omc | 代码简化 | 降低复杂度、提取函数 |
| **code-architect** | ecc | 代码架构分析 | 现有架构分析、重构建议 |
| **code-explorer** | ecc | 代码探索 | 代码库导航、模式识别 |

---

## 十一、数据库专用 Agent

| Agent Type | 来源 | 作用 | 应用场景 |
|------------|------|------|----------|
| **database-reviewer** | 内置 + ecc | PostgreSQL 专家 | 查询优化、schema 设计、安全性、Supabase 最佳实践 |

---

## 十二、运维与配置 Agents

| Agent Type | 来源 | 作用 | 应用场景 |
|------------|------|------|----------|
| **chief-of-staff** | 内置 + ecc | 个人通讯参谋长 | 分类 email/Slack/LINE/Messenger 消息，生成回复草稿 |
| **harness-optimizer** | 内置 + ecc | 本地 agent harness 优化 | 提高可靠性、降低成本、提升吞吐量 |
| **loop-operator** | 内置 + ecc | 自主 agent 循环操作 | 运行自主循环、监控进度、安全干预 |
| **statusline-setup** | 内置 | 状态栏配置 | 配置用户 Claude Code 状态栏设置 |
| **performance-optimizer** | ecc | 性能优化专家 | 性能瓶颈分析、优化建议 |
| **git-master** | omc | Git 专家 | 复杂 Git 操作、冲突解决 |

---

## 十三、领域专用 Agents (ECC 扩展)

| Agent Type | 来源 | 作用 | 应用场景 |
|------------|------|------|----------|
| **homelab-architect** | ecc | 家庭实验室架构 | 网络设计、服务器配置 |
| **network-architect** | ecc | 网络架构师 | 企业网络设计、拓扑规划 |
| **network-config-reviewer** | ecc | 网络配置审查 | 路由器/交换机配置审计 |
| **network-troubleshooter** | ecc | 网络故障排除 | 网络问题诊断、修复 |
| **healthcare-reviewer** | ecc | 医疗软件审查 | HIPAA 合规、医疗数据处理 |
| **seo-specialist** | ecc | SEO 专家 | 搜索引擎优化、元数据 |
| **marketing-agent** | ecc | 营销代理 | 内容营销、用户获取 |
| **a11y-architect** | ecc | 无障碍架构师 | WCAG 合规、无障碍设计 |

---

## 十四、Understand-Anything 知识图谱 Agents

> 来源：understand-anything 插件 (v2.7.6)

| Agent Type | 来源 | 作用 | 应用场景 |
|------------|------|------|----------|
| **understand-anything:architecture-analyzer** | understand-anything | 架构层分析 | 分析文件结构、导入关系，识别逻辑架构层 |
| **understand-anything:article-analyzer** | understand-anything | 文章知识提取 | 从 markdown 提取知识图谱节点和边 |
| **understand-anything:domain-analyzer** | understand-anything | 业务域分析 | 提取业务域知识、业务流程、处理步骤 |
| **understand-anything:file-analyzer** | understand-anything | 文件分析 | 批量分析源文件，提取函数/类/关系 |
| **understand-anything:project-scanner** | understand-anything | 项目扫描 | 生成项目清单：语言、框架、导入图、复杂度 |
| **understand-anything:tour-builder** | understand-anything | 学习路径构建 | 设计 5-15 步引导式学习路径 |
| **understand-anything:knowledge-graph-guide** | understand-anything | 知识图谱导航 | 理解、查询、操作知识图谱 |
| **understand-anything:graph-reviewer** | understand-anything | 图谱验证 | 验证知识图谱的正确性和完整性 |
| **understand-anything:assemble-reviewer** | understand-anything | 图谱组装审查 | 合并批处理图谱，填充跨批次空白 |

---

## 十五、Oh-My-ClaudeCode (OMC) 扩展 Agents

> 来源：`~/.claude/omc/agents/` 用户自定义

| Agent Type | 来源 | 作用 | 应用场景 |
|------------|------|------|----------|
| **oh-my-claudecode:executor** | omc | 执行者 | 代码实现、任务执行（支持 haiku/sonnet/opus 模型分级） |
| **oh-my-claudecode:architect** | omc | 架构师 | 设计验证、架构决策 |
| **oh-my-claudecode:planner** | omc | 规划师 | 任务分解、实现计划 |
| **oh-my-claudecode:critic** | omc | 批评者 | 代码批评、质量审查 |
| **oh-my-claudecode:scientist** | omc | 科学家 | 研究分析、文献综述 |
| **oh-my-claudecode:analyst** | omc | 分析师 | 数据分析、问题诊断 |
| **oh-my-claudecode:debugger** | omc | 调试专家 | 复杂 bug 定位、修复 |
| **oh-my-claudecode:designer** | omc | 设计师 | UI/UX 设计、架构设计 |

---

## 十六、使用决策树

```
需要分析架构/做设计决策？
├── 是 → architect 或 Plan

需要规划实现步骤？
├── 是 → planner

代码刚写完？
├── 是 → code-reviewer
├── 涉及安全 → security-reviewer
├── 特定语言 → {language}-reviewer

构建失败？
├── 是 → {language}-build-resolver

需要写测试？
├── 新功能 → tdd-guide
├── E2E 测试 → e2e-runner

需要查文档？
├── 库/框架/API → docs-lookup
├── Claude Code 本身 → claude-code-guide

需要更新文档？
├── 是 → doc-updater

需要理解大型代码库？
├── 是 → understand-anything 系列

需要网络/基础设施相关？
├── 是 → network-architect 或 network-troubleshooter

默认情况
├── 广撒网搜索 → Explore
├── 复杂多步骤 → general-purpose
└── 其他 → claude
```

---

## 十七、subagent_type 精确调用规范（重要）

### 17.1 参数名称

启动子智能体必须使用 `subagent_type` 参数：

```javascript
Agent({
  subagent_type: "code-reviewer",  // ← 必须用这个参数名
  prompt: "..."
})
```

### 17.2 匹配规则

| 规则 | 说明 | 示例 |
|------|------|------|
| **大小写不敏感** | `Code-Reviewer` = `code-reviewer` | ✅ `"Code Reviewer"` → `code-reviewer` |
| **分隔符不敏感** | 空格/连字符/下划线等效 | ✅ `"code_reviewer"` = `"code-reviewer"` |
| **必须存在** | type 必须对应实际存在的 agent | ❌ `"non-existent-agent"` → 报错 |

### 17.3 常见错误

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `Agent type not found` | type 拼写错误或不存在 | 检查下方精确 type 列表 |
| `Agent type ... not found` | 混淆了 skill 和 agent | skill 用 `Skill()` 调用，不是 `Agent()` |
| 静默失败 | type 正确但 agent 内部错误 | 检查 agent prompt 和工具权限 |

### 17.4 带命名空间的 type（插件 agents）

插件提供的 agents 需要带命名空间前缀：

```javascript
// Understand-Anything 插件
Agent({ subagent_type: "understand-anything:architecture-analyzer", ... })
Agent({ subagent_type: "understand-anything:project-scanner", ... })

// Oh-My-ClaudeCode 插件
Agent({ subagent_type: "oh-my-claudecode:executor", ... })
Agent({ subagent_type: "oh-my-claudecode:architect", ... })
Agent({ subagent_type: "oh-my-claudecode:planner", ... })
Agent({ subagent_type: "oh-my-claudecode:critic", ... })
```

### 17.5 精确 type 名称速查表

#### 内置 Agents（直接使用）

```
claude                    general-purpose         Explore
architect                 planner                 Plan
code-reviewer             security-reviewer       tdd-guide
e2e-runner                doc-updater             docs-lookup
claude-code-guide         refactor-cleaner        database-reviewer
chief-of-staff            harness-optimizer       loop-operator
statusline-setup          build-error-resolver

# 语言专用 reviewers
python-reviewer           go-reviewer             rust-reviewer
java-reviewer             kotlin-reviewer         cpp-reviewer

# 语言专用 build resolvers
go-build-resolver         rust-build-resolver     java-build-resolver
kotlin-build-resolver     cpp-build-resolver
```

#### Understand-Anything 插件（带前缀）

```
understand-anything:architecture-analyzer
understand-anything:article-analyzer
understand-anything:assemble-reviewer
understand-anything:domain-analyzer
understand-anything:file-analyzer
understand-anything:graph-reviewer
understand-anything:knowledge-graph-guide
understand-anything:project-scanner
understand-anything:tour-builder
```

#### Oh-My-ClaudeCode 插件（带前缀）

```
oh-my-claudecode:executor
oh-my-claudecode:architect
oh-my-claudecode:planner
oh-my-claudecode:critic
oh-my-claudecode:scientist
oh-my-claudecode:analyst
oh-my-claudecode:debugger
oh-my-claudecode:designer
oh-my-claudecode:qa-tester
oh-my-claudecode:test-engineer
oh-my-claudecode:verifier
oh-my-claudecode:code-simplifier
oh-my-claudecode:explore
oh-my-claudecode:document-specialist
oh-my-claudecode:writer
oh-my-claudecode:git-master
oh-my-claudecode:tracer
oh-my-claudecode:code-reviewer
oh-my-claudecode:security-reviewer
```

#### ECC 插件扩展（可直接使用，无需前缀）

```
# 额外 reviewers
typescript-reviewer       react-reviewer          swift-reviewer
php-reviewer              django-reviewer         fastapi-reviewer
fsharp-reviewer           csharp-reviewer         flutter-reviewer
mle-reviewer              performance-optimizer

# 额外 build resolvers
pytorch-build-resolver    react-build-resolver    django-build-resolver
dart-build-resolver

# 领域专用
homelab-architect         network-architect       network-config-reviewer
network-troubleshooter    healthcare-reviewer     seo-specialist
marketing-agent           a11y-architect
```

### 17.6 Skill vs Agent 区分

| 类型 | 调用方式 | 示例 |
|------|----------|------|
| **Agent** | `Agent({ subagent_type: "..." })` | `code-reviewer`, `executor` |
| **Skill** | `Skill("skill-name")` | `ai-slop-cleaner`, `browse` |

⚠️ **常见陷阱**：`ai-slop-cleaner` 是 **skill**，不是 agent！

```javascript
// ❌ 错误 - 会报 "Agent type not found"
Agent({ subagent_type: "oh-my-claudecode:ai-slop-cleaner", ... })

// ✅ 正确
Skill("ai-slop-cleaner")
```

### 17.7 调试技巧

调用失败时的排查步骤：

1. **检查拼写**：确认 type 名称完全匹配上表
2. **检查命名空间**：插件 agents 需要 `plugin:agent-name` 格式
3. **检查 skill vs agent**：如果报错 "not found"，可能是 skill 不是 agent
4. **查看可用 agents**：在 Claude Code 中询问 "列出所有可用的 agent types"

---

## 十八、关键特性总结

| 特性 | 说明 |
|------|------|
| **工具集** | 每个 agent 有特定工具子集（如 Explore 只读，e2e-runner 有浏览器） |
| **并行执行** | 独立任务可并行 spawn 多个 agent（上限 min(16, CPU-2)） |
| **上下文隔离** | 每个 agent 有独立 context window |
| **结果返回** | agent 最终文本返回给主 agent 整合 |
| **模型覆盖** | 可通过 `model` 参数指定特定模型（haiku/sonnet/opus） |
| **Worktree 隔离** | `isolation: "worktree"` 让 agent 在独立 git worktree 工作 |
| **后台运行** | `run_in_background: true` 异步执行 agent |
| **命名寻址** | `name` 参数让 agent 可通过 SendMessage 继续对话 |
| **Schema 强制** | `schema` 参数强制 agent 输出结构化 JSON |

---

## 十九、调用示例

```javascript
// 基础调用
Agent({
  subagent_type: "code-reviewer",
  prompt: "审查 src/auth.ts 的安全性"
})

// 并行多 agent
parallel([
  () => Agent({ subagent_type: "security-reviewer", prompt: "..." }),
  () => Agent({ subagent_type: "performance-optimizer", prompt: "..." }),
  () => Agent({ subagent_type: "python-reviewer", prompt: "..." })
])

// Worktree 隔离（并行修改文件时避免冲突）
Agent({
  subagent_type: "general-purpose",
  prompt: "重构用户模块",
  isolation: "worktree"
})

// 后台运行
Agent({
  subagent_type: "e2e-runner",
  prompt: "运行登录流程 E2E 测试",
  run_in_background: true,
  name: "e2e-login-test"
})

// 模型覆盖
Agent({
  subagent_type: "planner",
  prompt: "设计微服务架构",
  model: "opus"  // 使用最强推理模型
})

// 结构化输出
Agent({
  subagent_type: "Explore",
  prompt: "查找所有认证相关代码",
  schema: {
    type: "object",
    properties: {
      files: { type: "array", items: { type: "string" } },
      summary: { type: "string" }
    }
  }
})
```

---

## 二十、Agent 统计

| 来源 | 数量 |
|------|------|
| Claude Code 内置 | ~35 |
| ECC 插件扩展 | ~70+ |
| Understand-Anything | 9 |
| Oh-My-ClaudeCode | ~18 |
| **总计** | **130+** |

---

## 二十一、参考资料

- [ECC Universal](https://github.com/affaan-m/ECC) - 跨平台 agent 框架
- [Understand-Anything](https://github.com/understand-anything) - 代码知识图谱工具
- [Claude Code 官方文档](https://docs.anthropic.com/claude-code)
