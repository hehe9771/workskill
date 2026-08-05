# AI-Native 系统架构模式研究

> 生成日期: 2026-07-16
> 数据来源: Anthropic, OpenAI, Microsoft AutoGen, LangChain/LangGraph, CrewAI, ReAct, Lilian Weng 博客, arXiv 论文

---

## 目录

1. [Agent 编排模式](#1-agent-编排模式)
2. [记忆与上下文管理模式](#2-记忆与上下文管理模式)
3. [工具使用与函数调用模式](#3-工具使用与函数调用模式)
4. [多 Agent 通信模式](#4-多-agent-通信模式)
5. [Human-in-the-Loop 模式](#5-human-in-the-loop-模式)
6. [工作流组合模式](#6-工作流组合模式)
7. [评估与反馈循环模式](#7-评估与反馈循环模式)

---

## 1. Agent 编排模式

### 1.1 顺序编排 (Sequential / Prompt Chaining)

**描述**: 将复杂任务分解为固定的线性步骤链，每个步骤的输出作为下一步的输入。可在步骤之间设置检查点用于质量控制。

**适用场景**:
- 任务步骤可预定义且顺序固定
- 每步输出质量可验证
- 翻译 -> 审核 -> 发布 等多阶段流水线

**实现要点**:
```
[步骤1] → [检查点] → [步骤2] → [检查点] → [步骤3] → 输出
```

**示例**: 内容生成流水线 —— 研究 → 大纲 → 写作 → 编辑 → 发布

**来源**: Anthropic Building Effective Agents

---

### 1.2 路由模式 (Routing)

**描述**: 将输入分类后路由到专门的下游处理流程。一个分类模型负责判断输入类型，然后将请求分发到对应的专家处理链。

**适用场景**:
- 输入类型多样化
- 不同类别需要不同处理逻辑
- 需要隔离关注点，各自优化

**实现要点**:
```
                    ┌── 专家链A (代码问题)
输入 → [路由器] ───┼── 专家链B (数学问题)
                    └── 专家链C (知识问答)
```

**示例**: 客服系统中，路由器将问题分为"技术支持"、"账单查询"、"产品咨询"三类，分别交给不同专家链处理。

**来源**: Anthropic Building Effective Agents

---

### 1.3 并行化模式 (Parallelization)

**描述**: 同时执行多个子任务，结果汇总。两种变体:
- **切片 (Sectioning)**: 将任务拆分为独立子任务并行执行
- **投票 (Voting)**: 同一任务多次独立执行，取最优结果

**适用场景**:
- 子任务之间无依赖关系
- 需要多样性结果或冗余验证
- 加速整体执行时间

**实现要点**:
```
         ┌── [子任务A] ──┐
输入 ────┼── [子任务B] ──┼── [聚合器] → 输出
         └── [子任务C] ──┘
```

**示例**: 代码审查场景中，安全审查、性能审查、代码风格审查并行执行后汇总结果。

**来源**: Anthropic Building Effective Agents

---

### 1.4 编排者-工作者模式 (Orchestrator-Workers)

**描述**: 一个中央编排模型动态分解任务，分配给工作模型执行，然后汇总结果。区别于顺序链的关键在于编排者**动态决定**任务分配。

**适用场景**:
- 任务不可预测，无法预定义步骤
- 需要灵活的任务分解
- 复杂搜索、代码生成等开放性问题

**实现要点**:
```
                    ┌── [工作者A: 搜索]
[编排者] ── 分配 ──┼── [工作者B: 计算]── 汇总 ──→ 输出
                    └── [工作者C: 写作]
```

**来源**: Anthropic Building Effective Agents

---

### 1.5 评估者-优化者模式 (Evaluator-Optimizer)

**描述**: 一个生成模型产生输出，一个独立评估模型提供反馈，形成迭代改进循环。

**适用场景**:
- 输出质量需要反复打磨
- 有明确的评估标准
- 翻译、写作、代码生成等需要迭代优化的场景

**实现要点**:
```
[生成器] → [评估器] → 反馈 → [生成器] → ... → 满足标准 → 输出
```

**示例**: 翻译任务中，生成器产出翻译，评估器检查准确性和流畅性，不合格则带反馈重新生成。

**来源**: Anthropic Building Effective Agents

---

### 1.6 自主 Agent 模式 (Autonomous Agent)

**描述**: Agent 动态控制自身执行流程，不依赖预定义工作流。Agent 自主决定使用哪些工具、何时停止。

**适用场景**:
- 开放式探索任务
- 多步骤交互式任务
- 需要环境反馈的迭代任务

**实现要点**:
```
[感知环境] → [推理] → [行动] → [观察结果] → [推理] → ... → 完成
```

**关键论文**: ReAct (Yao et al., 2022) —— 将推理与行动交织在一起

**来源**: Anthropic, ReAct

---

## 2. 记忆与上下文管理模式

### 2.1 三层记忆架构

**描述**: 借鉴人类认知科学，将记忆分为三类:

| 记忆类型 | 对应组件 | 特点 |
|---------|---------|------|
| 感觉记忆 (Sensory) | 输入嵌入 | 原始多模态输入的处理 |
| 短期记忆 (Short-term) | 上下文窗口 | 受 context window 限制，用于 in-context learning |
| 长期记忆 (Long-term) | 外部向量数据库 | 跨会话持久存储，通过 ANN 检索 |

**来源**: Lilian Weng, "LLM Powered Autonomous Agents" (2023)

---

### 2.2 统一记忆系统 (Unified Memory)

**描述**: CrewAI 采用的模式 —— 单一 Memory 类管理所有记忆类型，LLM 自动推断上下文、标签和重要性。检索时使用复合指标: **语义相似度 + 时间衰减 + 重要性评分**。

**关键特性**:
- **层级分区**: 树形目录结构组织记忆
- **记忆切片**: 跨多个不相连分支同时读取
- **隐私与溯源**: 标记来源 ID，私有数据仅同源可见
- **检索深度**: 快速向量搜索 / 深度多步 LLM 分析
- **去重机制**: 相似度阈值自动合并/删除重复项
- **异步批量保存**: 后台线程处理，不阻塞主流程

**来源**: CrewAI Memory Documentation

---

### 2.3 反思机制 (Reflection)

**描述**: Agent 审视自身过去的行为和输出，生成更高层次的摘要。用于从经验中学习和改进。

**实现要点**:
- 存储历史事件 (observations)
- 通过 LLM 合成高层摘要 (summaries)
- 结合 **相关性、时效性、重要性** 三个维度评分检索

**示例**: 生成式 Agent 模拟中，Agent 记录观察 -> 触发反思 -> 形成新认知 -> 影响后续规划。

**来源**: Lilian Weng, Generative Agents paper (Park et al., 2023)

---

### 2.4 上下文窗口管理策略

**关键挑战**: 上下文窗口有限，需要智能管理。

**常见策略**:
- **摘要压缩**: 将长对话历史压缩为摘要
- **滑动窗口**: 保留最近 N 轮对话
- **选择性检索**: 只检索与当前任务相关的历史片段
- **分层存储**: 关键信息保持在上下文中，次要信息存入长期记忆

---

## 3. 工具使用与函数调用模式

### 3.1 ReAct 模式 (Reasoning + Acting)

**描述**: 将推理与行动交织执行的框架。Agent 交替产生推理轨迹 (thought) 和执行动作 (action)，从外部环境获取信息。

**核心循环**:
```
Thought: 我需要查找XX的信息
Action: search("XX")
Observation: [搜索结果]
Thought: 根据搜索结果，...
Action: ...
```

**关键设计**:
- LLM 决定何时思考 (think) vs 何时行动 (act)
- 通过 API 接口与外部知识库交互
- 支持异常处理和计划更新

**来源**: Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models" (2022)

---

### 3.2 工具自动模式匹配 (Auto Schema Generation)

**描述**: OpenAI Agents SDK 的模式 —— 将 Python 函数自动转换为工具定义，自动生成参数 schema。

**关键特性**:
- 函数签名 -> 工具 schema 自动生成
- 原生支持 MCP (Model Context Protocol) 服务器工具调用
- `tool_choice` 控制: `required` / `auto` / `none`
- `tool_use_behavior`: 是否在工具执行后让模型重新处理结果

**来源**: OpenAI Agents SDK

---

### 3.3 工具编排流水线 (Tool Orchestration Pipeline)

**描述**: HuggingGPT 等系统采用的多阶段工具编排:

```
请求解析 → 模型选择 → 任务执行 → 结果汇总
```

**阶段说明**:
1. **请求解析**: LLM 理解用户意图，拆解为子任务
2. **模型选择**: 为每个子任务选择合适的专家模型/工具
3. **任务执行**: 按依赖关系顺序执行
4. **结果汇总**: 整合多个工具的输出为最终答案

**来源**: HuggingGPT (Shen et al., 2023)

---

### 3.4 工具缓存模式 (Tool Result Caching)

**描述**: 缓存工具执行结果避免重复调用。

**实现要点**:
- 按工具名 + 参数哈希缓存
- 设置 TTL 过期时间
- 区分可缓存/不可缓存的工具调用

**来源**: CrewAI Documentation

---

## 4. 多 Agent 通信模式

### 4.1 协作模式 (Collaboration / Shared Scratchpad)

**描述**: 所有 Agent 共享一个消息板 (scratchpad)，每个步骤对所有参与者可见。规则路由器检查工具调用或最终答案来决定流转。

**实现要点**:
```
[Agent A] ──┐
            ├── [共享消息板] ── [路由器] ── 决定下一个 Agent
[Agent B] ──┘
```

**适用场景**: 需要透明协作、所有步骤可追溯的场景

**来源**: LangGraph Multi-Agent Workflows

---

### 4.2 主管模式 (Supervisor)

**描述**: 每个 Agent 有独立的 scratchpad，只有最终响应共享。一个主管 Agent 负责任务分配和结果汇总 —— "主管的工具就是其他 Agent"。

**实现要点**:
```
           ┌── [Agent A] (独立 scratchpad)
[主管] ───┼── [Agent B] (独立 scratchpad)
           └── [Agent C] (独立 scratchpad)
              ↑ 只有最终结果回到主管
```

**适用场景**: 任务可明确分工、需要中央协调的场景

**来源**: LangGraph Multi-Agent Workflows

---

### 4.3 层级团队模式 (Hierarchical Teams)

**描述**: 多层层级结构，节点包含嵌套的图对象而非简单执行器。主管连接子团队，子团队内部再进一步协作。

**实现要点**:
```
[顶层主管]
    ├── [团队A 主管]
    │     ├── [Worker A1]
    │     └── [Worker A2]
    └── [团队B 主管]
          ├── [Worker B1]
          └── [Worker B2]
```

**适用场景**: 大型复杂项目，需要多层次分工

**来源**: LangGraph, AutoGen

---

### 4.4 交接模式 (Handoffs)

**描述**: OpenAI Agents SDK 的去中心化模式 —— Agent 之间直接交接控制权，接收方继承完整对话历史。

**实现要点**:
```
[Agent A] ──handoff──→ [Agent B] ──handoff──→ [Agent C]
                         (继承完整历史)
```

**两种变体**:
- **集中式**: Agent 作为工具被调用，主 Agent 保持控制
- **去中心化**: Peer Agent 直接交接控制权

**来源**: OpenAI Agents SDK

---

### 4.5 混合专家模式 (Mixture of Agents)

**描述**: 多个 Agent 独立处理同一问题，通过辩论或投票机制产生最优答案。

**示例**: Multi-Agent Debate —— 多个 Agent 就同一问题给出不同观点，通过辩论达成共识。

**来源**: AutoGen, CrewAI

---

### 4.6 Agent 委托模式 (Delegation)

**描述**: CrewAI 的 `allow_delegation: true` 模式 —— Agent 可以将任务委托给其他 Agent 处理。

**来源**: CrewAI

---

## 5. Human-in-the-Loop 模式

### 5.1 工具执行审批 (Tool Execution Approval)

**描述**: Agent 在执行敏感工具前需要人类审批。AutoGen 通过 "Intervention Handler" 实现。

**实现要点**:
```
Agent 决定调用工具 → [拦截器] → 请求人类审批 → 批准/拒绝 → 执行/跳过
```

**适用场景**: 金融交易、数据删除、外部 API 调用等高风险操作

**来源**: AutoGen Intervention Handler

---

### 5.2 检查点恢复 (Checkpoint & Resume)

**描述**: CrewAI 在工作流关键节点保存状态，允许人类介入后从中断处恢复。

**实现要点**:
- 工作流在关键事件后自动保存状态
- 人类可以查看、修改中间结果
- 从中断处恢复执行

**来源**: CrewAI

---

### 5.3 交互式澄清 (Interactive Clarification)

**描述**: 系统在启动前提示用户填补缺失参数，在执行中请求人类确认模糊决策。

**来源**: CrewAI, AutoGen

---

### 5.4 反馈注入 (Feedback Injection)

**描述**: 人类反馈直接注入 Agent 的上下文或长期记忆，影响后续决策。

**实现要点**:
- 人类评价 Agent 输出质量
- 反馈存入记忆系统
- 后续类似任务中检索并参考

---

## 6. 工作流组合模式

### 6.1 有向无环图 (DAG / Graph-Based Workflows)

**描述**: LangGraph 的核心模式 —— 将工作流建模为图，Agent 是节点，连接是边。边定义控制流，节点执行计算。

**核心概念**:
- **节点 (Node)**: 每个 Agent 或处理步骤
- **边 (Edge)**: 定义流转条件
- **状态 (State)**: 图的全局状态对象，节点通过修改状态通信
- **条件边 (Conditional Edge)**: 基于状态动态决定下一个节点

**实现要点**:
```python
# 类比状态机
# Agent 节点 = 状态
# 连接 = 转移矩阵
# 通信 = 向图状态添加数据
```

**来源**: LangGraph Documentation

---

### 6.2 状态机模式 (State Machine)

**描述**: 将 Agent 编排建模为有限状态机，每个状态对应一个 Agent 或处理步骤，转移条件决定流转。

**关键要素**:
- 状态集合 (States)
- 初始状态 (Initial State)
- 转移函数 (Transition Function)
- 终止状态 (Terminal States)

**与 DAG 的关系**: DAG 是状态机的特例 (无环)。LangGraph 支持有环图，允许 Agent 循环执行。

---

### 6.3 子图嵌套模式 (Nested Graphs)

**描述**: 将复杂工作流拆分为子图，主图编排子图的执行顺序。实现模块化和可复用。

**实现要点**:
```
[主图]
  ├── [子图A: 数据处理流水线]
  ├── [子图B: 分析流水线]
  └── [子图C: 报告生成流水线]
```

**来源**: LangGraph Hierarchical Teams

---

### 6.4 流模式 (Flow-Based Patterns)

**描述**: 数据驱动的工作流，数据在管道中流动，每个节点处理并传递。

**变体**:
- **线性流**: A → B → C
- **分支流**: A → (B | C) → D
- **循环流**: A → B → C → (条件: 回到 A 或结束)

---

## 7. 评估与反馈循环模式

### 7.1 自动化评估框架 (Automated Evaluation)

**描述**: WildBench 等框架使用自动指标评估 Agent 输出质量。

**关键指标**:
- **WB-Reward**: 基于细粒度成对比较的相对评分
- **WB-Score**: 独立单点评分，更快更经济
- **任务特定清单**: 系统化的结构化评估标准

**防偏机制**:
- 多基线模型 (非单一基线)
- 长度偏差校正: 优胜答案超过阈值时转为平局
- 与人类 Elo 评分高度相关 (Pearson 0.98)

**来源**: WildBench (Lin et al., 2024)

---

### 7.2 反思-改进循环 (Reflection Loop)

**描述**: Agent 自我评估输出质量，发现问题后迭代改进。

**实现要点**:
```
[执行] → [自我评估] → 不满意? → [带反馈重新执行]
              ↓ 满意
           [输出]
```

**来源**: Anthropic Evaluator-Optimizer pattern

---

### 7.3 外部验证 (External Verification)

**描述**: 使用外部工具验证 Agent 输出的准确性。

**常见方法**:
- **搜索验证**: Agent 发起搜索查询验证事实
- **代码执行验证**: 运行代码验证逻辑正确性
- **多模型交叉验证**: 不同模型独立验证同一输出

**来源**: WildBench paper

---

### 7.4 追踪与可观测性 (Tracing & Observability)

**描述**: OpenAI Agents SDK 的内置追踪系统 —— 可视化调试工作流，连接到评估、微调和蒸馏工具链。

**关键功能**:
- 完整的 Agent 执行轨迹记录
- 每次工具调用的输入/输出追踪
- 决策过程的可视化
- 与下游评估/微调管线集成

**来源**: OpenAI Agents SDK

---

### 7.5 监控与指标 (Usage Metrics)

**描述**: 持续监控 Agent 执行效率和质量。

**关键指标**:
- Token 使用量追踪
- 任务完成时间
- 工具调用成功率
- 任务回调: 每次任务完成后触发分析函数

**来源**: CrewAI

---

## 附录: 主要框架模式对照表

| 模式类别 | Anthropic | OpenAI SDK | LangGraph | AutoGen | CrewAI |
|---------|-----------|-----------|-----------|---------|--------|
| 顺序编排 | Prompt Chaining | - | Sequential | Sequential Workflow | Sequential Process |
| 并行化 | Parallelization | - | Fan-out/Fan-in | Concurrent Agents | - |
| 路由 | Routing | - | Conditional Edge | - | - |
| 编排者-工作者 | Orchestrator-Workers | - | Supervisor | - | Hierarchical Process |
| 评估优化 | Evaluator-Optimizer | - | - | Reflection | - |
| 多 Agent 协作 | - | Handoffs | Collaboration | Group Chat | Delegation |
| 层级结构 | - | Agents-as-tools | Nested Graphs | Nested Chat | Manager Agent |
| 记忆 | - | Context Object | State | - | Unified Memory |
| 工具使用 | Tool Use | Function + MCP | Tool Node | - | Tool + Cache |
| 人类介入 | - | Guardrails | Interrupt | Intervention Handler | - |
| 追踪 | - | Built-in Tracing | LangSmith | - | Usage Metrics |

---

## 参考文献

1. **Anthropic** - "Building Effective Agents" (2024) - https://www.anthropic.com/engineering/building-effective-agents
2. **Lilian Weng** - "LLM Powered Autonomous Agents" (2023) - https://lilianweng.github.io/posts/2023-06-23-agent/
3. **Yao et al.** - "ReAct: Synergizing Reasoning and Acting in Language Models" (2022) - https://react-lm.github.io/
4. **OpenAI** - Agents SDK Documentation - https://openai.github.io/openai-agents-python/
5. **LangChain** - LangGraph Multi-Agent Workflows - https://langchain-ai.github.io/langgraph/
6. **Microsoft** - AutoGen Design Patterns - https://microsoft.github.io/autogen/stable/
7. **CrewAI** - Documentation - https://docs.crewai.com/
8. **Lin et al.** - "WildBench: Automatic Evaluation of LLMs" (2024) - https://arxiv.org/abs/2406.04770
9. **Wang et al.** - "A Survey on Large Language Model based Autonomous Agents" (2023) - https://arxiv.org/abs/2308.11432
10. **Park et al.** - "Generative Agents: Interactive Simulacra of Human Behavior" (2023)
