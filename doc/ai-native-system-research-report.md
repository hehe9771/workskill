# AI 原生系统综合研究报告

> 调研时间：2026年7月 | 覆盖维度：热门项目、架构模式、核心组件、最佳实践、新兴趋势

---

## 一、执行摘要

AI 原生系统在 2025-2026 年完成了从"实验性工具"到"生产基础设施"的跃迁。本报告基于五个维度的深度调研（GitHub 热门项目、架构模式、核心组件、工程最佳实践、新兴趋势），提炼出以下核心结论：

**第一性原理**：AI 原生系统的本质约束是**上下文窗口有限**和**模型输出不确定**。所有架构选择、工程实践、协议设计都围绕这两个约束展开。

### 五大关键发现

1. **协议标准化是最大基础设施变革**。MCP（工具连接）+ A2A（代理协作）形成双层基础架构，已成为事实标准。学术界已指出当前协议不够——潜空间通信、语义帧等下一代协议在探索中。

2. **从单代理到多代理编排是不可逆趋势**。Top 10 项目中 7 个涉及多代理。AutoGen 进入维护模式、Microsoft Agent Framework 统一方向、OpenAI Swarm 被 Agents SDK 替代——行业正收敛到标准化多代理架构。

3. **评估驱动开发取代"感觉测试"**。Hamel Husain 方法论（二元判断 + 人类校准 + CI 集成）和 AgentBeats 框架标志着从"跑几个例子看看"到"系统化评估管线"的范式转变。

4. **从简单开始是唯一正确的起点**。Anthropic 的核心建议：简单 prompt → workflow → agent，只在指标改善时才增加复杂度。能用 workflow 解决的不上 agent。

5. **安全从"对齐问题"扩展为"系统工程问题"**。沙箱隔离、行为审计、记忆安全、通信同质化风险——安全覆盖五个层级（输入→工具→执行→输出→审计）。

### Stars 排行榜 Top 10

| 排名 | 项目 | Stars | 类别 |
|------|------|-------|------|
| 1 | n8n | 197k | 工作流编排 |
| 2 | AutoGPT | 186k | Agent 框架 |
| 3 | Dify | 149k | 工作流编排 |
| 4 | LangChain | 142k | Agent 框架 |
| 5 | Claude Code | 138k | AI 开发工具 |
| 6 | MCP Servers | 88.5k | 工具集成 |
| 7 | OpenHands | 81k | AI 开发工具 |
| 8 | Flowise | 54.7k | 可视化构建 |
| 9 | LlamaIndex | 50.9k | 数据框架 |
| 10 | AutoGen | 59.8k | 多代理框架 |

---

## 二、核心发现

### 发现一：协议层——MCP + A2A 双层架构已成事实标准

**MCP（Model Context Protocol）** 是 AI 应用的"USB-C 接口"：
- Anthropic 发起，Claude/ChatGPT/VS Code/Cursor 原生支持
- 架构：Host → Client → Server，JSON-RPC 2.0 通信
- 三大原语：Tools（可执行函数）、Resources（数据源）、Prompts（复用模板）
- 传输层：Stdio（本地）/ Streamable HTTP（远程 + SSE）
- 88.5k Stars 的 MCP Servers 仓库证明生态已成熟

**A2A（Agent-to-Agent Protocol）** 与 MCP 互补：
- Google 2025年4月发起，50+ 企业参与
- MCP 解决"代理→工具"，A2A 解决"代理→代理"
- 基于 HTTP/SSE/JSON-RPC，Agent Card 服务发现

**学术界已指出不足**（2026年密集产出）：
- 潜空间通信（Beyond Tokens）：绕过文本生成的连续向量通信
- 身份感知协议（LDP）：语义帧减少 37% token 消耗
- 异构协作（tap）：不同模型通过文件系统协作
- 表征耦合风险（BOUNDARY_SYNC）：文本通信导致代理表征同质化

### 发现二：Agent 框架收敛到三大范式

| 范式 | 代表 | 核心设计 |
|------|------|---------|
| 图状态机 | LangGraph | Pregel/Beam 概念，有状态持久工作流，子图嵌套 |
| 角色协作 | CrewAI | 角色扮演团队编排，持久执行，全面记忆 |
| 对话驱动 | AutoGen | 分层架构（Core + AgentChat + Extensions），多进程运行时 |

Anthropic 定义了 6 种 Agent 编排模式，按复杂度递增：
1. **Prompt 链式**：顺序步骤 + 检查点 → 确定性任务
2. **路由**：分类器分发到专家链 → 已知输入类型
3. **并行化**：切片并行 / 投票并行 → 独立子任务
4. **编排者-工作者**：动态分解 + 分配 + 汇总 → 不可预测任务
5. **评估者-优化者**：生成-评估迭代循环 → 质量迭代
6. **自主 Agent**：工具调用循环 + 环境反馈 → 开放式探索

**选择原则**：能用 1-3 解决的不用 4-6。Workflow 比 Agent 更可预测、可调试、成本可控。

### 发现三：记忆系统分三层，统一记忆是终极目标

| 层级 | 类比 | 实现 | 生命周期 |
|------|------|------|---------|
| 感觉记忆 | 输入嵌入 | 当前请求上下文 | 单次请求 |
| 短期记忆 | 上下文窗口 | 对话缓冲区 + 滑动窗口 | 单次会话 |
| 长期记忆 | 向量数据库 | 向量存储 + 实体链接 | 跨会话持久 |

**领先实现**：
- **Mem0**：三步管线（发送 → 提取事实+实体链接 → 查询召回），支持 user/agent/run/session 四维度
- **CrewAI**：复合检索指标 = 语义相似度 + 时间衰减 + 重要性
- **LangGraph Checkpointing**：状态持久化，支持断点恢复与时间旅行

**上下文窗口管理**是最稀缺资源的优化：
- 子代理分离上下文（调研任务在 subagent 中执行，只返回汇总）
- 自动摘要压缩（token 超限时触发）
- 精简系统提示（每行问"删掉会导致犯错吗？"不会就删）

### 发现四：成本优化的三个杠杆

**杠杆一：Prompt Caching（最高 ROI）**
- 缓存读取成本仅为基础价的 0.1x（90% 折扣）
- 关键陷阱：`cache_control` 必须放在所有请求中保持不变的最后一个 block 上
- 变更工具定义会级联失效整个缓存层级
- 最低阈值：Opus 4.8/Sonnet 5 为 1,024 tokens

**杠杆二：模型路由**
- 简单任务（FAQ/格式化/分类）→ Haiku/轻量模型
- 复杂任务（推理/规划/代码）→ Sonnet/Opus
- 可静态路由（按任务类型）或动态路由（分类器判断复杂度）

**杠杆三：Token 管理**
- 上下文窗口填满后模型性能下降
- 给模型足够的"思考空间"（extended thinking / 足够 max_tokens）
- 两次纠正失败后，清理上下文重新开始

### 发现五：安全纵深防御五层模型

| 层级 | 措施 | 实现 |
|------|------|------|
| L1 输入层 | Prompt 注入检测 | 独立模型实例审查用户输入 |
| L2 工具层 | 权限最小化 | allowlist 参数，防呆设计（Poka-yoke） |
| L3 执行层 | 沙箱隔离 | Docker/firecracker 容器，限制文件系统和网络 |
| L4 输出层 | 输出验证 | LLM 输出使用前必须验证 |
| L5 审计层 | 全量日志 | 记录所有工具调用和输入输出 |

**OWASP LLM Top 3 风险**：
1. Prompt 注入（最高优先级）
2. 不安全的输出处理
3. 过度代理（unchecked autonomy）

### 发现六：评估从"单任务"走向"系统级"

**Hamel Husain 分层评估框架**：

| 层级 | 方法 | 频率 |
|------|------|------|
| L1 | 快速断言 + 代码检查 | 每次提交 |
| L2 | 人工 + 模型评估 | 每个版本 |
| L3 | A/B 测试 + 用户行为 | 成熟产品 |

**关键原则**：
- 用二元判断（pass/fail）替代模糊评分（1-10）
- 用人类专家的文字批评作为 few-shot 示例构建自动化评估器
- 验证优先：给 AI 一个可以运行的检查（测试/构建/截图），而非让它"声称完成"

**2026年评估框架爆发**：
- AgentBeats：基于 A2A+MCP 的通用评估接口
- AgentCompass：统一评估基础设施
- Terminal-Bench 2.0：持续学习场景下复合增益测试

### 发现七：Microsoft 生态重组信号

| 项目 | 状态 |
|------|------|
| AutoGen | 进入维护模式 |
| Semantic Kernel | 正向 Microsoft Agent Framework 演进 |
| OpenAI Swarm | 已被 OpenAI Agents SDK 替代 |

**行业收敛方向**：标准化多代理架构 + MCP/A2A 互操作。

### 发现八：自改进代理进入"约束期"

不再追求"无限自我提升"，而是研究有效条件：
- Mimosa 框架：科研代理动态调整流程
- 角色演化（Roles with Rails）：合约约束下的角色池自演化
- Do Agent Optimizers Compound?：终端学习任务上增益有限

---

## 三、重点 GitHub 项目清单

### A. Agent 框架

| 项目 | Stars | 链接 | 适用场景 | 推荐度 |
|------|-------|------|---------|--------|
| LangChain | 142k | [github.com/langchain-ai/langchain](https://github.com/langchain-ai/langchain) | 最广泛集成的 LLM 应用框架 | ★★★★★ |
| LangGraph | 37.4k | [github.com/langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | 复杂有状态 Agent 工作流 | ★★★★★ |
| CrewAI | 37.4k | [github.com/crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) | 角色驱动多代理协作 | ★★★★☆ |
| AutoGen | 59.8k | [github.com/microsoft/autogen](https://github.com/microsoft/autogen) | 对话驱动多代理（维护模式） | ★★★☆☆ |
| AutoGPT | 186k | [github.com/Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) | 自主任务规划与执行 | ★★★★☆ |
| OpenAI Agents SDK | 27.9k | [github.com/openai/openai-agents-python](https://github.com/openai/openai-agents-python) | 生产级多代理框架 | ★★★★☆ |
| Semantic Kernel | 28.3k | [github.com/microsoft/semantic-kernel](https://github.com/microsoft/semantic-kernel) | 企业级多代理，C#/Python | ★★★★☆ |

### B. 工作流编排

| 项目 | Stars | 链接 | 适用场景 | 推荐度 |
|------|-------|------|---------|--------|
| n8n | 197k | [github.com/n8n-io/n8n](https://github.com/n8n-io/n8n) | AI 原生自动化，可视化+代码双模 | ★★★★★ |
| Dify | 149k | [github.com/langgenius/dify](https://github.com/langgenius/dify) | LLMOps 全栈平台 | ★★★★★ |
| Dagster | 27.9k | [github.com/dagster-io/dagster](https://github.com/dagster-io/dagster) | 云原生数据管线编排 | ★★★★☆ |
| Temporal | 21.7k | [github.com/temporalio/temporal](https://github.com/temporalio/temporal) | 持久执行分布式系统 | ★★★★☆ |

### C. 数据与检索

| 项目 | Stars | 链接 | 适用场景 | 推荐度 |
|------|-------|------|---------|--------|
| LlamaIndex | 50.9k | [github.com/run-llama/llama_index](https://github.com/run-llama/llama_index) | 文档代理与数据索引 | ★★★★★ |
| Haystack | 25.9k | [github.com/deepset-ai/haystack](https://github.com/deepset-ai/haystack) | 模块化管道 RAG | ★★★★☆ |
| ChromaDB | — | [github.com/chroma-core/chroma](https://github.com/chroma-core/chroma) | 开源向量存储 | ★★★★☆ |
| Instructor | 13.5k | [github.com/jxnl/instructor](https://github.com/jxnl/instructor) | LLM 结构化输出 | ★★★★☆ |

### D. 开发工具

| 项目 | Stars | 链接 | 适用场景 | 推荐度 |
|------|-------|------|---------|--------|
| Claude Code | 138k | [github.com/anthropics/claude-code](https://github.com/anthropics/claude-code) | 终端 AI 代理 + IDE 集成 | ★★★★★ |
| MCP Servers | 88.5k | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | MCP 协议服务器集合 | ★★★★★ |
| OpenHands | 81k | [github.com/All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands) | 开源 AI 编码代理 | ★★★★☆ |
| Flowise | 54.7k | [github.com/FlowiseAI/Flowise](https://github.com/FlowiseAI/Flowise) | 可视化拖拽构建 AI 代理 | ★★★★☆ |
| SWE-agent | 19.8k | [github.com/princeton-nlp/SWE-agent](https://github.com/princeton-nlp/SWE-agent) | 自主解决仓库问题 | ★★★☆☆ |
| GPT Researcher | 28.3k | [github.com/assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher) | 开源深度研究代理 | ★★★★☆ |

### E. 评估与监控

| 项目 | Stars | 链接 | 适用场景 | 推荐度 |
|------|-------|------|---------|--------|
| AgentOps | 5.7k | [github.com/AgentOps-AI/agentops](https://github.com/AgentOps-AI/agentops) | 代理监控与调试 | ★★★★☆ |
| Vercel AI SDK | 25.6k | [github.com/vercel/ai](https://github.com/vercel/ai) | TypeScript AI 工具库 | ★★★★☆ |

---

## 四、架构模式图谱

### 4.1 AI 原生系统总体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI Native System                            │
├──────────────┬──────────────┬───────────────────────────────────┤
│  Agent 框架   │  记忆系统      │  提示管理                          │
│  (LangGraph, │  (Mem0,      │  (DSPy,                          │
│   CrewAI,    │   Checkpoint, │   PromptTemplate,                │
│   AutoGen)   │   Vector DB)  │   Few-shot)                      │
├──────────────┼──────────────┼───────────────────────────────────┤
│  工具集成      │  向量存储      │  评估框架                          │
│  (MCP,       │  (ChromaDB,  │  (LangSmith,                     │
│   LangChain   │   FAISS,     │   Ragas,                         │
│   Tools)     │   Pinecone)  │   AgentBench)                    │
├──────────────┴──────────────┴───────────────────────────────────┤
│  规划与推理 (ReAct / CoT / ToT / Plan-and-Execute)               │
├─────────────────────────────────────────────────────────────────┤
│  观察-行动空间 (环境反馈 / 工具调用结果 / 沙盒测试)                  │
├─────────────────────────────────────────────────────────────────┤
│  协议层 (MCP 工具连接 + A2A 代理协作)                              │
├─────────────────────────────────────────────────────────────────┤
│  LLM 层 (OpenAI / Anthropic / Local Models)                      │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 六大 Agent 编排模式对照

| 模式 | 控制流 | 适用场景 | 复杂度 | 代表框架 |
|------|--------|---------|--------|---------|
| Prompt 链式 | 线性 A→B→C | 确定性步骤 | 低 | LangChain |
| 路由 | 分类→专家链 | 已知输入类型 | 低 | LangGraph |
| 并行化 | 扇出→汇聚 | 独立子任务 | 中 | LangGraph |
| 编排者-工作者 | 动态分解→分配→汇总 | 不可预测任务 | 中 | AutoGen |
| 评估者-优化者 | 生成↔评估迭代 | 质量迭代 | 中高 | DSPy |
| 自主 Agent | 工具循环+环境反馈 | 开放式探索 | 高 | CrewAI |

### 4.3 记忆架构分层

```
┌─────────────────────────────────────────────┐
│              长期记忆 (跨会话)                 │
│  向量数据库 + 知识图谱 + 实体链接              │
│  实现: Mem0, ChromaDB, Pinecone              │
├─────────────────────────────────────────────┤
│              短期记忆 (会话内)                 │
│  上下文窗口 + 对话缓冲区 + 检查点              │
│  实现: LangGraph Checkpointer                │
├─────────────────────────────────────────────┤
│              感觉记忆 (请求内)                 │
│  输入嵌入 + 当前消息                           │
│  实现: Embedding 模型                         │
└─────────────────────────────────────────────┘
```

### 4.4 MCP 协议架构

```
MCP Host (AI 应用)
├── MCP Client 1 ─── MCP Server A (本地: 文件系统)
├── MCP Client 2 ─── MCP Server B (本地: 数据库)
├── MCP Client 3 ─── MCP Server C (远程: API)
└── MCP Client 4 ─── MCP Server C (同一服务器多连接)

协议栈:
┌──────────────────────────────────┐
│  应用层: Tools / Resources / Prompts │
├──────────────────────────────────┤
│  数据层: JSON-RPC 2.0              │
├──────────────────────────────────┤
│  传输层: Stdio / Streamable HTTP   │
└──────────────────────────────────┘
```

### 4.5 五大框架模式对照表

| 模式 | Anthropic SDK | OpenAI SDK | LangGraph | AutoGen | CrewAI |
|------|--------------|------------|-----------|---------|--------|
| 顺序链式 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 路由 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 并行化 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 编排者-工作者 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 评估者-优化者 | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |
| 自主 Agent | ✅ | ✅ | ✅ | ✅ | ✅ |
| MCP 支持 | ✅ 原生 | ✅ | ✅ | ✅ | ✅ |
| 人机协作 | ✅ | ✅ | ✅ 内置 | ✅ | ✅ |
| 状态持久化 | ⚠️ | ⚠️ | ✅ 核心 | ✅ | ✅ |

---

## 五、最佳实践清单

### 5.1 错误处理与重试

- [ ] 每步从环境获取"地面真相"，不盲目重试
- [ ] 设计防呆工具（Poka-yoke）：强制绝对路径、枚举值
- [ ] 设置终止条件：最大迭代次数上限
- [ ] 分级重试：API限流→指数退避；网络超时→最多3次；格式错误→结构化输出+重试；认证错误→不重试
- [ ] 优雅降级：模型路由降级 → 功能降级 → 缓存兜底

### 5.2 成本优化

- [ ] 启用 Prompt Caching：系统提示和工具定义加 `cache_control: ephemeral`
- [ ] 避免"变化后缀陷阱"：`cache_control` 放在不变的最后一个 block 上
- [ ] 模型路由：简单任务用小模型，复杂任务用大模型
- [ ] 子代理分离上下文，避免主会话膨胀
- [ ] 监控 `cache_read_input_tokens`，全为 0 说明缓存未生效

### 5.3 安全

- [ ] 五层防御：输入审查 → 权限最小化 → 沙箱隔离 → 输出验证 → 审计日志
- [ ] Prompt 注入防御：分离系统指令与用户输入，用 XML 标签区分
- [ ] 沙箱隔离：Docker/firecracker 容器，限制文件系统和网络
- [ ] 不信任外部数据：API/文件/网页内容视为不可信
- [ ] 用独立模型实例做安全审查

### 5.4 可观测性

- [ ] 全链路追踪：记录每次 LLM 调用的输入/输出/token/延迟
- [ ] 结构化日志：JSON 格式，包含 trace_id/span_id/model/tokens/latency/cost
- [ ] 监控指标：延迟(p99)、Token消耗、缓存命中率(>60%)、工具成功率(>95%)、成本/请求
- [ ] 消除数据查看摩擦：构建领域特定可视化
- [ ] 避免重抽象框架：保持底层 prompt 可见

### 5.5 测试与评估

- [ ] 分层评估：L1 快速断言(每次提交) → L2 人工+模型(每版本) → L3 A/B(成熟产品)
- [ ] 二元判断（pass/fail）替代模糊评分
- [ ] 验证优先：给 AI 可运行的检查，而非让它声称完成
- [ ] 测试数据集覆盖：分解功能维度，覆盖多样性
- [ ] CI 集成：每次代码变更运行评估

### 5.6 部署

- [ ] 从简单开始：prompt → workflow → agent
- [ ] 减少抽象层：直接基于 LLM API 构建
- [ ] 渐进式放权：先限制权限和迭代次数
- [ ] 生产就绪检查：超时重试、错误分类、成本告警、追踪接入、安全审查

### 5.7 Prompt 与版本控制

- [ ] Prompt 视为代码：Git 管理，版本化
- [ ] CLAUDE.md 只放"删掉会导致犯错"的内容
- [ ] 用 hook 替代指令（确定性保证执行）
- [ ] 评估器版本化：变更关联指标变化
- [ ] 工作流即代码：声明式配置 + 回滚机制

### 5.8 人机协作

- [ ] 四阶段分离：探索 → 计划 → 实现 → 提交
- [ ] 让 AI 面试你：对复杂功能让 AI 提问
- [ ] 两次纠正失败后清理上下文重新开始
- [ ] 独立审查：用 subagent 审查 diff
- [ ] 展示证据而非声称成功

---

## 六、未来展望

### 6.1 短期（2026 下半年）

1. **Microsoft Agent Framework 正式发布**：统一 AutoGen + Semantic Kernel，成为企业多代理标准
2. **MCP/A2A 互操作成熟**：生产版本落地，AgentBeats 类评估框架普及
3. **评估基础设施标准化**：从单任务成功率到系统级综合评估

### 6.2 中期（2027）

4. **下一代通信协议落地**：潜空间通信、语义帧等学术成果转化为工程实践
5. **异构代理协作成为常态**：不同模型/成本/能力的代理混合编排
6. **企业记忆基底**：Oracle Agent Memory 等方案成为企业标配

### 6.3 长期趋势

7. **自改进代理的工程化**：不是"无限自我提升"，而是在约束条件下持续优化
8. **安全系统工程化**：沙箱隔离、行为审计、记忆安全、通信安全成为基础设施
9. **AI 原生开发成为默认**：人类角色从"编码者"转向"审查者+规划者"

### 6.4 需要持续关注的风险

| 风险 | 说明 |
|------|------|
| 协议碎片化 | 学术论文提出的新协议可能加剧碎片化 |
| 表征同质化 | BOUNDARY_SYNC 发现文本通信导致代理表征趋同 |
| 自改进退化 | Do Agent Optimizers Compound? 证明复合增益有限 |
| 企业部署失败率 | Semantic Consensus 指出 41%-86.7% 失败率 |
| 上下文窗口瓶颈 | 所有优化都受限于有限上下文窗口 |

---

## 七、参考资源

### 核心文献

1. Anthropic, "Building Effective Agents" — [anthropic.com/engineering/building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents)
2. Anthropic, "Claude Code Best Practices" — [code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices)
3. Anthropic, "Prompt Caching Documentation" — [platform.claude.com/docs/en/docs/build-with-claude/prompt-caching](https://platform.claude.com/docs/en/docs/build-with-claude/prompt-caching)
4. Hamel Husain, "Your AI Product Needs Evals" — [hamel.dev/blog/posts/evals](https://hamel.dev/blog/posts/evals)
5. Hamel Husain, "Building an LLM Judge" — [hamel.dev/blog/posts/llm-judge](https://hamel.dev/blog/posts/llm-judge)
6. OWASP, "Top 10 for LLM Applications" — [owasp.org/www-project-top-10-for-large-language-model-applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
7. Latent Space, "Why MCP Won" — [latent.space/p/why-mcp-won](https://latent.space/p/why-mcp-won)

### 2026 年关键学术论文

8. "Self-Improvements in Modern Agentic Systems: A Survey" (arXiv 2026.7)
9. "A Technical Taxonomy of LLM Agent Communication Protocols" (arXiv 2026.6)
10. "Beyond Tokens: Latent Communication" (arXiv 2026.6)
11. "BOUNDARY_SYNC" (arXiv 2026.7)
12. "Semantic Consensus: Process-Aware Conflict Detection" (arXiv 2026.4)
13. "Do Agent Optimizers Compound?" (arXiv 2026.7)
14. "Roles with Rails" (arXiv 2026.5)
15. "LDP: Identity-Aware Protocol" (arXiv 2026.3)

### 项目链接汇总

| 类别 | 项目 | 链接 |
|------|------|------|
| Agent | AutoGPT | https://github.com/Significant-Gravitas/AutoGPT |
| Agent | LangChain | https://github.com/langchain-ai/langchain |
| Agent | AutoGen | https://github.com/microsoft/autogen |
| Agent | CrewAI | https://github.com/crewAIInc/crewAI |
| Agent | LangGraph | https://github.com/langchain-ai/langgraph |
| Agent | GPT Researcher | https://github.com/assafelovic/gpt-researcher |
| Agent | OpenAI Swarm | https://github.com/openai/swarm |
| Agent | OpenAI Agents SDK | https://github.com/openai/openai-agents-python |
| 编排 | n8n | https://github.com/n8n-io/n8n |
| 编排 | Dify | https://github.com/langgenius/dify |
| 编排 | Dagster | https://github.com/dagster-io/dagster |
| 编排 | Prefect | https://github.com/prefecthq/prefect |
| 编排 | Temporal | https://github.com/temporalio/temporal |
| 数据 | LlamaIndex | https://github.com/run-llama/llama_index |
| 数据 | Haystack | https://github.com/deepset-ai/haystack |
| 数据 | Vercel AI SDK | https://github.com/vercel/ai |
| 数据 | Instructor | https://github.com/jxnl/instructor |
| 工具 | Claude Code | https://github.com/anthropics/claude-code |
| 工具 | OpenHands | https://github.com/All-Hands-AI/OpenHands |
| 工具 | Flowise | https://github.com/FlowiseAI/Flowise |
| 工具 | Continue | https://github.com/continuedev/continue |
| 工具 | SWE-agent | https://github.com/princeton-nlp/SWE-agent |
| 工具 | MCP Servers | https://github.com/modelcontextprotocol/servers |
| 监控 | AgentOps | https://github.com/AgentOps-AI/agentops |
| 多代理 | Semantic Kernel | https://github.com/microsoft/semantic-kernel |

---

> 报告生成时间：2026-07-16 | 基于五维度综合调研（热门项目、架构模式、核心组件、最佳实践、新兴趋势）
