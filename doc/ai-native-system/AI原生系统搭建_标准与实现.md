# AI 原生系统如何搭建：定义、标准与实现路径

## 一、执行摘要

本文基于对全网研究资料的对抗式核验，回答四个根本问题：什么是真正的 AI 原生系统、如何衡量一个系统是否达到了 AI 原生标准、从 0 到 1 该如何搭建、以及哪些反模式会让"AI 原生"沦为营销话术。在初稿之上，本文补入六个此前缺失的维度——成本与经济模型、安全与对齐纵深、多模态架构、边缘与端侧部署、合规与监管、组织与团队结构——使"标准"从架构/数据/Agent/产品/业务/评估六维扩展为十二维。

核心结论可浓缩为五条判据。第一，AI 原生的存在性判据是"移除测试"：抽掉 AI 后核心流程是否崩溃——若崩溃则为 AI 原生，若仅丢失增强则为 AI 赋能（来源：Aicadium）。第二，AI 原生的逻辑本质是"概率性逻辑为核心"而非"确定性逻辑为核心"，AI 是心脏而非点缀（来源：虎嗅）。第三，从第一性原理看，AI 原生意味着假设 AI 能力（而非人类吞吐量）为基线约束，从零重建运营模型，而非在现有流程里找地方塞 AI（来源：Custom AI Studio）。第四，架构上模型须直接位于请求路径上充当推理引擎与决策路由器，遵循"模型推理、框架治理"原则（来源：ittech-pulse、SAP）。第五，数据闭环集成是最强护城河，"最佳 AI 公司把数据当作结果而非输入"（来源：aitech365）。

补研新增的五条判据：第六，"可辩护的 cost-per-query"必须显式声明四大约束与六行成本分解，省略 embedding/eval/observability 会让真实成本被低估 20-40%（来源：SfaiLabs）。第七，安全纵深远不止 prompt injection——OWASP 2025 已把过度代理权（LLM06）与供应链（LLM03）单列为顶级风险，NIST AI 100-2 建立了覆盖 evasion/poisoning/extraction/backdoor 的对抗性 ML 分类（来源：OWASP、NIST）。第八，多模态重塑上下文工程——大块二进制应外置为 artifact 而非塞进 prompt，按需工具加载配合稳定前缀缓存（来源：Google ADK）。第九，云-边-端三层是端侧场景下"模型位于请求路径"的标准落地范式，路由层是混合架构中最高杠杆组件（来源：MEI4LLM、tianpan）。第十，组织拓扑即架构——水平工作归平台团队、垂直工作归产品团队，放反则结构性失能（来源：CTAIO）。

本文共核验与引用 98 条关键声明（初稿 61 条 + 补研 37 条），其中初稿经对抗式独立核验的为 18 条（16 条确认、1 条证伪、1 条存疑），补研声明均附真实 source_url 与 credibility 字段但未及全部独立复核。证伪与存疑的声明均以"争议/待考证"方式标注，不作为肯定结论使用。

## 二、定义与本质：什么是 AI 原生系统

### 2.1 AI 原生 vs AI 赋能：本质判据

判别一个系统是否 AI 原生，最尖锐的工具是"移除测试"：如果今晚从产品中移除 AI，用户是否会察觉到产品工作方式的根本变化？若核心流程崩溃，则属 AI 原生；若仅丢失某个增强功能而核心流程照常运行，则仅是 AI 赋能。Aicadium 将此表述为"Without AI, it wouldn't exist"（没有 AI 它就不会存在），而 AI 赋能则是"AI is an add-on"（AI 是附加物）（来源：Aicadium）。

虎嗅给出中文镜像判据并进一步从逻辑本质上二分：AI 增强的逻辑核心是确定性的，AI 是"点缀"，用来提高某个环节的效率（如文档软件加个"续写"按钮）；AI 原生的逻辑核心是概率性的，AI 是"心脏"，没有了 AI，产品的核心流程根本跑不通（来源：虎嗅）。这一区分不是程度的差异，而是架构类的差异——一个是"对同一架构的改进"，另一个是"不同的架构"（来源：Arco）。

**如何衡量**：对目标系统执行移除测试。逐一关闭所有 AI 调用路径，观察核心业务流程（非边缘功能）是否仍可端到端完成。若可完成，则系统至多为 AI 赋能；若无法完成，则通过存在性判据。

### 2.2 与 AI-First / AI-Driven 的层次关系

AI 成熟度存在递增的三层次：AI-Enabled（AI 作为附加物增强现有产品）→ AI-First（转型以 AI 为核心使能技术）→ AI-Native（自构思起即以 AI 为基、从底层构建）。三者常被混淆但本质不同。Aicadium 的关键区分原文是："AI-native means conceived with in mind and built on AI from the ground up. AI-First means based on AI, but not originally built on it"（来源：Aicadium）。

Aicadium 用汽车类比阐明三者差异：AI-Enabled 是"给现有车加涡轮增压器"，AI-First 是"围绕智能重设计仪表盘"，AI-Native 是"围绕新电动引擎重新设计整车"（来源：Aicadium）。ThoughtSpot 另给出 AI-enabled → Embedded AI → AI-native 的三层次，其中 Embedded AI 介于两者之间，指 AI 集成进特定模块（如电商推荐）（来源：ThoughtSpot）。

Jimmy Song 白皮书定义 AI 原生应用为"以大模型为认知基础，以 Agent 为编排和执行单元，以数据作为决策和个性化基础，通过工具感知和执行的智能应用"，并指出开发者"通过 Prompt 等自然语言方式完成业务逻辑的构建与配置"，模型能"自主生成和调整业务执行逻辑"。其架构含 11 大要素：模型、应用开发框架、提示词、RAG、记忆、工具、网关、运行时、可观测、评估、安全（来源：Jimmy Song）。

> **争议/待考证**：研究包中有一项声明称"必须 clean-sheet 新建而非改造现有架构"，并称 AI 赋能的现有企业"无法渐进跨越此鸿沟"。经核验，该声明将 Arco 的观点错误归因于 Jimmy Song 源页——Jimmy Song 第 1 章页面并无"clean-sheet"或"无法渐进跨越"的表述，反而明确指出 AI 原生应用"建立在云原生的基础之上"。clean-sheet 的论断实际来自 Arco（另一独立来源），但该 Arco 声明本身未及独立核验，故此处仅作为 Arco 的观点引用，不作肯定结论。

**如何衡量**：追问系统的起源——它是"在既有确定性架构上叠加 AI 功能"（AI-Enabled），还是"转型使 AI 成为核心使能技术"（AI-First），还是"从第一行代码起即以 AI 模型为逻辑核心构建"（AI-Native）？关键判别点在于：系统的核心应用逻辑是通过传统规则编程表达，还是通过 AI 模型表达。

### 2.3 第一性原理视角的根本特征

从第一性原理出发，AI 原生与 AI 赋能问的是两个根本不同的问题。AI 赋能/bolt-on 问的是"哪里能用 AI 帮忙"（where can I use AI to help）；AI 原生问的是"如果容量不再是约束，运营该是什么样"（if the capacity is no longer the constraint, what does the operation look like），并导向"完全不同的架构"（completely different architecture）（来源：Custom AI Studio）。

Custom AI Studio 提出奠基性的第一性原理问题："If you were building this business today, from scratch, knowing what AI can do — how would you build it?"。根本原则是"human throughput is no longer a given constraint"。运营方法遵循"Constraint → Remove → New constraint → Remove → Repeat"的持续复利循环，每一轮"复合累积——更好利润、更多容量、更高人均收入"（来源：Custom AI Studio）。

Arco 同样定义 AI 原生公司为"engineered from first principles rather than automated from existing processes"。两者产出"不同资产类"：AI 赋能公司是"better margins 的服务业务"，AI 原生公司成为"a software-like entity with service-level revenue"，成本基础"deflationary rather than inflationary"（来源：Arco）。

**如何衡量**：审视系统的成本结构与人机比例。Arco 给出量化判据：Intervention Threshold（1:100，即百次自治执行仅一次人工干预）、Headcount Decoupling（增加一单位工作的成本趋近算力成本而非人力成本）、10:1 Revenue-to-Headcount Advantage、Inverse Complexity Scaling（规模越大越盈利）。若增加收入仍需线性增加人力，则未达 AI 原生。

## 三、核心标准

### 3.1 架构标准

**标准 1：模型位于请求路径上（Intelligence-First）**。AI 原生架构的核心原则是"intelligence is not an add-on, but the foundation"——模型直接位于请求路径上，充当用户与系统之间的主要接口，通过 prompt 解释用户意图、动态生成响应、调用 API 与工具。编排层负责"Tasks are broken down / Models are selected / Workflows are executed"，使推理本身成为路由机制而非静态分发器（来源：ittech-pulse）。

**标准 2：模型推理，框架治理（Model reasons, harness governs）**。SAP 架构中心明确将模型智能与治理/平台基础设施显式分离："The model reasons. The harness governs."以及"The harness, not the model, determines the ceiling"。平台层提供托管 agent 运行时（标准化 SDK、agent 沙箱、容器化执行、agent skills 注册表、持续评估、持久记忆、基于 OpenTelemetry 的端到端可观测性）（来源：SAP）。

**标准 3：概率性逻辑为核心，推理即计算**。传统架构请求流经确定性路由（rule-based logic、static workflows、deterministic outputs）；AI 原生中路由决策由模型推理而非固定规则做出。状态从"存于表中（显式可查）"变为"weights/memory/context 中的潜态"；分解单元从"按服务"变为"按带 intent 的自治 agent"；反馈从"事后监控"变为"in-the-loop 的架构要求"（来源：Catio）。

**如何衡量**：
- 检查请求路径：是否每次核心请求都经过模型推理？是否存在绕过模型的确定性快捷路径承担核心逻辑？
- 检查治理分离：模型推理与安全/审计/限流是否由独立组件负责，而非全部塞进单次 LLM 调用？
- 检查控制流可预测性：系统能否保证关键业务流程（审批、回滚、审计轨迹）的确定性，而非完全依赖模型"近似"执行？

### 3.2 数据与知识标准

**标准 1：数据飞轮闭环**。数据飞轮是"用户使用→数据→模型改进→更好体验"的自我强化闭环，由六步循环构成：数据处理（抽取多模态原始数据并过滤噪声/PII/毒性）→ 模型定制（DAPT、LoRA、SFT 注入领域知识）→ 模型评估（对照应用需求迭代直到达标）→ 护栏实现（叠加安全/隐私/合规护栏）→ 定制模型部署（RAG 保持与最新上下文连接）→ 企业数据精炼（推理日志与人类/AI 反馈回流到第一步重启循环）（来源：NVIDIA）。NVIDIA 的 NVInfo bot 案例显示，8B 模型经反馈微调后路由准确率超 96%，匹配 70B 模型性能，单 GPU 即可运行，延迟改善超 70%，推理成本节省最高 98%（来源：NVIDIA Developer）。

**标准 2：上下文工程而非仅提示工程**。上下文工程区别于提示工程：后者聚焦于编写组织 LLM 指令（主要是系统提示）用于单次任务；前者涵盖"在推理时策展和维护最优 token 集合"的策略，包括系统指令、工具、MCP 连接、外部数据、消息历史。核心约束是"上下文腐化"（context rot）——随 token 增长召回准确率下降，源于 transformer 每 token 关注所有其他 token 产生 n² 关系在规模上被稀释。指导哲学：找到"最大化期望结果可能性的最小高信号 token 集合"。上下文应被视为"有衰减边际收益的有限资源"，每个 token 消耗一个"注意力预算"（来源：Anthropic）。

**标准 3：检索范式按查询复杂度动态选择**。即时 agentic 搜索优于全量预嵌入：agent 维护轻量标识符（文件路径、存储查询、链接），运行时用工具动态加载数据而非预处理全量数据为嵌入。混合策略最有效——预加载部分数据保证速度 + 运行时自主探索保证相关性（来源：Anthropic）。RAG 与长上下文的实证表明：资源充足时长上下文平均性能优于 RAG，但 RAG 成本显著更低；Self-Route 混合路由（基于模型自反思将查询路由到 RAG 或长上下文）是性价比最优解（来源：arXiv EMNLP 2024）。Agentic RAG 把检索包成控制循环（检索→推理→决策），而 Classic RAG 是线性管道；选择按查询复杂度与错误容忍度决定——低复杂度+高错误容忍用 Classic RAG，高复杂度+低错误容忍用 Agentic RAG（来源：Towards Data Science）。

**标准 4：数据是核心差异化壁垒**。基础模型正在商品化，价值迁移到专有数据和运营智能（来源：Axel Tombereau）。四层数据壁垒中闭环集成是最强护城河：(1) 专有/暗数据（法律独占、竞争对手无法访问）；(2) 刷新速度（实时摄入管道使 AI 操作于当前信号）；(3) 行为智能（用户行为模式比人口统计更揭示真相）；(4) 闭环集成（每次交互成为系统新燃料）。"最佳 AI 公司把数据当作结果而非输入"，"未来 AI 赢家未必有最大数据集，而是有最快学习系统"（来源：aitech365）。

**如何衡量**：
- 数据飞轮：是否每条用户交互（接受/拒绝推荐、编辑 AI 输出、完成/放弃步骤）都被结构化捕获并回流为训练信号？闭环延迟（从交互到模型更新）是多长？
- 上下文工程：是否对每次推理都策展最小高信号 token 集？是否监控了上下文腐化导致的召回下降？
- 数据壁垒：是否拥有竞争对手无法获取的运营生成数据？刷新速度是否实时？是否形成闭环？

### 3.3 Agent 系统标准

**标准 1：Agent 本质是 agentic loop**。Agent 是"LLM 在一个反馈循环中基于环境反馈调用工具"的系统，核心循环为：接收任务→规划→执行工具调用→用环境的 ground truth（如工具结果、代码执行）评估进展→决定继续/暂停人工介入/终止。这与 workflow（按预定义代码路径编排 LLM、可预测）是两种不同架构（来源：Anthropic）。

**标准 2：简洁性第一原则**。"寻找尽可能简单的方案，仅在确有需要时才增加复杂度"——很多场景"优化单次 LLM 调用 + 检索 + 上下文示例就足够了"。Agent 适用于"难以预测所需步骤数量的开放式问题"，但伴随"更高成本与复合错误风险"，须"在沙箱环境中充分测试并配以适当 guardrails"。三大核心原则：简洁性、透明性（显式展示规划步骤）、Toolcraft/ACI（精心设计与文档化工具接口）（来源：Anthropic）。

**标准 3：工具接口（ACI）应与整体 prompt 工程同等投入**。工具定义和规范应得到与整体 prompt 同等的 prompt 工程关注。具体实践包括：给模型足够 token 在行动前推理、参数描述像给初级开发者写优秀 docstring、包含示例用法与边界情况、应用 poka-yoke 防错（如从相对路径改为绝对路径）。Anthropic 构建 SWE-bench agent 时"花在优化工具上的时间比整体 prompt 还多"（来源：Anthropic）。

**标准 4：规划模式按任务特性选择**。三大主流规划模式各有失败模式与缓解手段：①ReAct（think→act→observe→repeat）适用于下一步依赖上一步的交互任务，失败模式是 verifier stall（反复用改写参数调用验证工具），需 per-tool 调用上限 + max_steps 边界；②Plan-and-Execute（planner 一次性产出步骤列表，executor 逐步执行）成本约 1×强模型 + N×便宜模型，N>3 时优于 ReAct，失败模式是 brittle plan，需 re-plan gate；③Reflection（生成→批评→修正→至批评通过）失败模式是 self-bias（同模型批评倾向认可自己输出），需用不同模型族或外部信号锚定批评。生产中常组合：Plan-and-Execute 外层 + 每步内 ReAct + 整体包 Reflection（来源：dev.to）。

**标准 5：可靠性是分布式系统问题**。多 agent 系统等同经典分布式系统（节点失效、网络分区、消息丢失、级联错误）。可靠性手段：timeout 与重试、graceful degradation、暴露错误而非隐藏、传给下一 agent 前校验输出、circuit breaker、agent 间隔离避免共享单点故障、用 SDK checkpoint 从中断恢复。Guardrails 应在用户输入、工具调用、工具响应、最终输出多点布防（来源：Azure）。

**如何衡量**：
- 是否为每个 agent 设置了最大迭代次数等停止条件？
- 是否每步都从环境获取 ground truth 评估进展，而非盲信模型自述？
- ACI 投入：工具文档的完整度是否达到"初级开发者可独立使用"标准？
- 是否有 per-tool 调用上限防止 verifier stall？

### 3.4 产品设计标准

**标准 1：意图驱动交互（Intent-driven）**。这是 60 年来首个新 UI 范式：命令式交互下用户"点击每个图标逐步产出想要的东西"，意图式系统中用户"告诉它要达成什么目标，它自行决定其余"。系统从指定"如何做"转向指定"做什么"，用户角色从操作者变为监督者。一个可用意图必须包含三要素：期望结果、约束条件、委托边界（来源：Jakob Nielsen / UX Tigers）。

**标准 2：可用性指标全面重写**。从确定性转向概率性系统，指标迁移为：可发现性→意图捕获（系统能否将模糊请求映射为结构化动作）；错误预防→澄清质量（系统是否问对后续问题）；学习时间→委托容易度；执行效率→验证效率（用户多快能验证 AI 输出）；系统状态可见性→执行透明度；用户满意度→信任校准（用户既不过度信任也不低用）。"纠正时间（time-to-correct）成为核心指标"取代传统任务耗时（来源：Jakob Nielsen / UX Tigers）。

**标准 3：渐进式委托而非二元的人控/全自动**。通过可见的自主度滑块和分级信任机制实现：Suggest（代理建议、用户逐步批准）→ Co-pilot（常规动作自动执行、重要动作需许可）→ Autopilot（完全自主并报告）。原则："默认采用最保守设置，让用户随信任建立而提升自主度"（来源：Mantlr、Microsoft）。

**标准 4：可纠错性与可撤销性**。动作预览（对昂贵/不可逆动作渲染实际结果预览而非模糊确认框，且预览应可编辑）；活动日志（每个代理动作、决策、结果的持久时间线日志，每条含撤销选项）；优雅错误恢复（承认错误、用通俗语言解释、提供修复、并从纠正中学习）（来源：Mantlr、Microsoft）。

**标准 5：刻意认知摩擦而非一味消除摩擦**。copilot 是概率性系统易犯错，需在保存、分享、复制、粘贴等关键时刻加摩擦让用户慢下来审阅。按风险分级施加防护栏：低风险自动执行并记录、中风险快速预览一键批准、高风险详细预览+显式确认+撤销窗口（来源：Microsoft、Mantlr）。

**标准 6：拒绝默认套壳聊天框**。产品团队必须避免匆忙采用聊天界面，除非它们满足真实的用户需求。另一反模式是"以 AI 为卖点"——公司应以 AI 实现提供的价值来引领，而非指望 AI 本身创造价值。建议收窄范围："范围收窄的 AI 功能更易理解、用户采用率更高"（来源：NNGroup）。

**如何衡量**：
- 意图捕获率：系统能否将模糊自然语言请求映射为结构化动作？映射失败时是否问对澄清问题？
- 纠正时间：从 AI 输出错误到用户完成纠正的平均耗时。
- 信任校准：用户对 AI 输出的信任度是否与实际准确率匹配（是否存在过度信任或低用）？
- 自主度可调：用户是否能显式设定 agent 的独立运行程度？

### 3.5 业务流程标准

**标准 1：AI 放在价值交付关键路径上自主执行**。判别标准是"任务是否同时需要对话与行动、有清晰成功标准、有反馈回路、且可接入人类监督"。AI 作为主驱动者的典型领域：客户支持（聊天界面+工具集成如检索数据/发放退款，成功可由用户定义的解决标准衡量）和编码 agent（代码可通过自动化测试验证、agent 可用测试反馈迭代）。对可分解为固定子任务或可分类为已知类型的任务，LLM 在受控管道内辅助而非自主驱动（来源：Anthropic）。

**标准 2：人机协同模式按问题域选择**。HITL（人作为 AI 决策管道中的验证器）与 AITL（AI 作为人类工作流中的增强层）是方向相反的两种架构。根本判据是问题域是否良好定义：良好定义域适合自动化（HIL，AI 主导决策，人提供修正），未定义/不可定义域适合协作（AI²L，人保留完全控制与决策权，AI 做感知/推理/行动的支持）。域是"嵌套而非分离"的（来源：arXiv、IBM）。HITL 延迟分钟到小时、吞吐瓶颈是认知能力；AITL 近实时、瓶颈是算力（来源：IBM）。

**标准 3：headcount decoupling**。收入增长不再线性依赖人力。量化基准：Valve $46.3M/人、Netflix $4.15M/人、Cursor $3.3M/人、Basecamp $1.64M/人，中位私有 SaaS $12.97 万/人；"优秀"新基准是 $50 万 ARR/人（来源：Pepper Effect）。Gartner 数据支撑：到 2028 年 33% 企业软件含 agentic AI、15% 日常工作决策自主做出，麦肯锡称 57% 美国工作时间可被现有技术自动化（来源：Pepper Effect）。

**标准 4：从 0 到 1 重设计而非叠加 AI**。叠加 AI 等于增量效率非变革（重蹈数字化转型早期"纸质转电子"覆辙）；重设计是以"AI 是队友"为前提重新构想流程。核心重构问题："如果 AI 从一开始就是队友，这个流程会是什么样？哪些步骤会消失，哪些新步骤会出现？"四步框架：审计摩擦（映射最高频工作流）、审计抽象（找出讨论多于行动处）、探索新协作面、从零开始（完全搁置现有流程）（来源：Grammarly）。

**标准 5：为 AI 增强员工而非裁人**。Gartner 调研 350 家年收≥$10 亿公司：80% 报告 AI 采用后减员，但减员率在高 ROI 与低 ROI 公司间几乎相等——裁人与财务回报无有意义相关。高 ROI 公司用 AI 做"people amplification"（销售团队生产力提升 2-3 倍、支持处理时长降 40%、合同审阅从 4 小时降至 30 分钟——均保留人工）。裁人是"成本转移而非成本消除"（来源：Beri / Gartner）。

**如何衡量**：
- AI 是否在价值交付关键路径上自主执行（而非仅辅助）？移除 AI 后价值交付是否中断？
- 人机协同模式是否按问题域良好定义性正确选择？是否识别了哪些决策点需人工、是可选还是强制？
- 人均收入（ARR/人）是否随 AI 采用而提升？收入增长是否快于团队规模增长？
- 流程是否从零重设计（而非在既有流程上叠加 AI）？

### 3.6 评估与可观测性标准

**标准 1：Eval 结构化**。Eval 由 task（带输入与成功判据的单个测试）、trial（一次尝试，因模型非确定性需多次）、grader（对某方面打分的逻辑）、transcript（trial 完整记录）、outcome（trial 后最终环境状态）构成。关键区分：capability eval（问"agent 擅长什么"，应从低通过率起步）与 regression eval（问"agent 是否仍能完成以前能完成的"，应接近 100% 通过率，下降即意味有东西坏了）（来源：Anthropic）。

**标准 2：三类 grader 组合**。Code-Based Graders（字符串匹配/二进制测试/静态分析/outcome 验证，快/便宜/客观但对合法变体脆弱）；Model-Based Graders/LLM-as-Judge（rubric 打分/成对比较，灵活但非确定性/需与人工校准）；Human Graders（金标准但贵/慢）。原则："能用确定性 grader 就用，必要时用 LLM grader，谨慎用人工"。重要告诫：应评 agent 产出了什么而非走了什么路径——检查精确工具调用顺序"太刚性、导致过脆测试"（来源：Anthropic）。

**标准 3：用 pass@k 与 pass^k 衡量可靠性**。pass@k（k 次尝试中至少一次正确的似然，k 增大分数升，适合一次成功即可的工具）；pass^k（k 次全部成功的概率，k 增大分数降，关乎面向客户 agent 的可靠性）。k=1 时两者相同；k=10 时 pass@k 趋近 100% 而 pass^k 趋近 0。这解释了为何"实验室能力分"与"生产可靠性"是两回事（来源：Anthropic）。

**标准 4：LLM-as-Judge 生产化**。需 persona + few-shot + CoT + 结构化输出 + 低置信度转人工，且不可替代人工评估。每次产出 5 项：0-100 分、二值/类别判定、置信度、CoT 推理、附加注释。明确局限：LLM judge 是"收集到足够数据前的强起点"而非人工替代，幻觉风险要求按"何时失败而非是否失败"设计（来源：Towards Data Science）。

**标准 5：以 trace 为核心的可观测性**。Langfuse trace 包含所有 LLM 与非 LLM 调用（含检索、embedding、API 调用），基于 OpenTelemetry 降低厂商锁定；多轮对话追踪为 sessions，agent 可视化为 graphs。成本监控按 userId 追踪人均成本，延迟用 timeline view 分解各操作。质量评估支持 LLM-as-a-judge、代码 evaluator、用户反馈、人工标注（来源：Langfuse）。

**标准 6：幻觉检测三层架构 + 持续评估闭环**。三层架构：(1) 预部署测试套件（对带 ground truth 数据集做受控评估，可 A/B 对比 prompt 变体）；(2) 模拟环境（persona 用户模型复现边界 case）；(3) 生产可观测（live 流量持续 auto-eval + 分布式追踪 + 告警）。五层粒度：Session/Trace/Span/Generation/Retrieval。关键指标：Faithfulness/Groundedness（产出声明被检索上下文支持的比例）、Context Relevance/Recall/Precision。生产失败案例被采样回流为离线测试集，配合 CI/CD 在指标退化时阻塞部署——形成"生产→离线→部署"闭环（来源：Maxim AI、Anthropic）。Anthropic 将多种评估方法比作安全工程"瑞士奶酪模型"——无单层评估能捕获所有问题（来源：Anthropic）。

**标准 7：Prompt injection 纵深防御**。指令与数据分离（结构化 prompt 明确标注用户输入为"待分析数据而非待执行指令"）；输入/输出/动作三重筛查（部署独立分类器模型在三处筛查）；dual-LLM 模式（特权模型持工具但不读不可信内容、隔离模型读不可信内容但不能行动）；HITL 风险评分（按高风险关键词算分，达阈值转人工）。已知局限：研究显示 BoN 攻击"GPT-4o 89%、Claude 3.5 Sonnet 78% 成功率"，"对持续攻击的稳健防御可能需根本性架构创新而非增量改进"（来源：OWASP）。注意：prompt injection 只是安全纵深的一个维度，完整的对齐与对抗性安全见 3.8 节。

**如何衡量**：
- 是否区分 capability eval 与 regression eval，并设置了不同的通过率基线？
- 是否同时追踪 pass@k（能力）与 pass^k（可靠性）？
- 是否有五层粒度的分布式追踪覆盖 Session/Trace/Span/Generation/Retrieval？
- 生产失败案例是否回流为离线测试集形成闭环？CI/CD 是否将 AI 质量作为部署门禁？
- 是否对 prompt injection 做了输入/输出/动作三重筛查与 HITL 风险评分？

### 3.7 成本与经济模型标准

补研发现，初稿将"成本"仅作为部署运维的附属项，缺乏可辩护的单位经济标准、推理 TCO 模型与 API/自托管迁移门禁。这一缺口是规模化失败的硬约束——MIT NANDA（2025-08，150 访谈+350 员工+300 部署）证实 95% 企业 GenAI 试点失败、仅 5% 实现收入加速，主因之一即"资源错配：超半数 GenAI 预算投向销售营销，但最大 ROI 在后台自动化；外购成功率 67% vs 自建 ~22%"（来源：Drivetrain / Fortune）。

**标准 1：可辩护的 cost-per-query 须显式声明四约束 + 六行成本分解**。一个可辩护的单位经济必须同时声明：(1) 输入 token 区间（如 500–2000，RAG 系统简单/复杂查询差 3-5x）；(2) 输出 token 中位数与 P95 双值（P95 可达中位数 4x）；(3) eval-pass 质量门槛（如 eval≥87）；(4) 延迟 P95 目标（如 ≤5s，防止用慢配置压成本）。六行成本：输入 token、输出 token、embedding 摊销、检索（按 P95 chunk 数）、eval 摊销、可观测性摊销。省略 embedding/eval/observability 会让真实成本被低估 20-40%；同一系统无约束 vs 可辩护 cost-per-query 之间约 30% 缺口——"这正是销售 Deck 与三季后毛利之间的差"。示例：Claude 4.7 级 RAG 客服、12M 月查询，中位数 $0.00665/query、P95 $0.0116/query。规则：买方按输入付费用 cost-per-query，按结果付费用 cost-per-action。envelope 须季度重置，输入分布偏移>15% 立即重置（来源：SfaiLabs）。

**标准 2：推理 TCO 三组件模型 + 不可能三角**。核心经济模型：Intelligence = f(Cost, Model)。每小时 GPU 成本三部分：折旧 = P/(Y×8760×u)、功耗 = kW×PUE×E、维护 = (P×m)/8760。A800 80G 基线：折旧 ~$0.64/hr、功耗 ~$0.08/hr、维护 ~$0.06/hr，合计 ~$0.79/hr（范围 $0.51–0.99）；对比云 AWS P4de $5.08/hr、阿里云 gn7e $4.80/hr，云溢价 3.6–7.1x。推理生产前沿三原则：(1) 边际成本递减（并发 8→48 使完成时间 2034s→774s）；(2) 规模报酬递减（超过最优并发吞吐骤降、TTFT 飙升）；(3) 最优性价比区间。同一基准集各模型成本差达 31x（最便宜 $0.11 vs 最贵 $3.47），输出 token 数是成本主驱动（思考型模型生成 token 多致成本高）。限制：该模型明确排除 fine-tune/持续训练成本与 GPU 集群前期 CapEx（来源：arXiv）。

**标准 3：API vs 自托管迁移决策有明确预算分级拐点**。三档决策阈值：年 API 花费 <5 万美元 → 留在 GPT-4o Mini；5 万-50 万 → 混合（80% 走 Mini，其余自托管 7B）；>50 万 → 高利用率 GPU 集群 + LoRA fine-tune 几乎总赢。私有 LLM 在日 token 量超 200 万或需 HIPAA/PCI 合规时开始回本，典型回收期 6-12 个月。TCO 关键事实：芯片+人员占 LLM 部署总成本 70-80%，一名中级 MLOps 工程师对应 4-6 块 GPU 是现实配比，需加 10-15% 冗余。成本敏感于利用率：H100 spot 节点 70% 利用率时 ~$0.013/1K tokens，利用率降到 10% 时每 token 成本翻 10 倍至 $0.13。真实案例：FinTech 客服月成本 7 个月内从 $47k 攀升（3.2B→12.4B tokens），用三层混合路由（Haiku FAQ/Mini 复杂/自托管 7B 批量摘要）后降至 $8k/月（降 83%），响应时间 310→280ms，CSAT 维持 4.2，基础设施 ~4 个月回本。降本手段：LoRA fine-tune 7B 降本 60-80%、RAG 缓存省 20-40% token、4-bit 量化降 30% 运行成本、spot GPU 降 40-70% 时价（来源：Ptolemay）。

**标准 4：AI agent ROI 框架须做敏感性测试**。TCO = 实施 + 运营 + 培训变更 + 维护监控（12-36 个月视野），四维成本：(1) 模型与用量（推理费/编排订阅）；(2) 基础设施与集成（云、数据传输、存储、CRM/ERP 集成）；(3) 人员与运营（监督、编排、持续改进）；(4) 治理与风控（安全、审计、合规、可观测性）。ROI = (收益-TCO)/TCO，收益四类：降本、增收、生产力提升、风险缓释。Payback = 初始投入/月净收益，12-18 个月视为强。中型部署样本：一次性 3 万-7.5 万、月度 1.8 万-4.8 万、12 个月总计 25.5 万-65 万美元。敏感性：基础情形（50% 自动化）ROI 575%；自动化 ±10pp 或量 ±20% → ROI 在 ~680% 与 ~440% 间摆动约 230pp，故必须做敏感性测试。CapEx（一次性，差异化/合规驱动）vs OpEx（经常性，占长期支出主体）。build-vs-buy：需领域调优/合规/复杂集成→自建（CapEx 高）；标准流程→买平台。麦肯锡数据：AI 销售代理增 3-15% 收入、10-20% 生产力；但 78% 公司用 AI 仍"无实质底线影响"（来源：Acropolium）。

**标准 5：AI SaaS 毛利压缩与三类预算框架**。三大根本转变：(1) COGS 从按用户变为按用量（推理随 prompt 长度/响应/并发上涨，"下一条请求边际成本非零"）；(2) 毛利压缩（传统 SaaS 60-80% → AI SaaS 50-60%，a16z 2020）；(3) 成本波动加剧。开源对比：Llama 2 同等输出 ~$0.0007 vs GPT-4 ~$0.084/500 词（超 100x）。三类预算框架：预付消耗（固定额度封顶，早期）、滚动/变量预算（月度更新，成长期）、单位经济锚定（按 cost-per-workflow 而非裸 token，成熟期，如"每次合规报告花 $0.07 token+基础设施"）。三阶段成本治理：与工程协作识别成本→优化（GPU、prompt、commitment 折扣、降级模型）→控制（预算/阈值/告警/限流/按客户配额）。向投资人沟通须把裸 token 花费翻译为单位经济（来源：Drivetrain）。

**标准 6：标准化推理 TCO 测算六步法**。NVIDIA 给出跨配置对比的行业基准方法：(1) 定约束（如平均 TTFT≤250ms、峰值 RPS）；(2) 在 Pareto 前沿上按延迟上限筛出最高吞吐点（Pareto 最优：没有其他配置能在同延迟下吞吐更高）；(3) 实例数 = 峰值 RPS / 单实例可达 RPS；(4) 服务器数 = (实例数×每实例 GPU)/(每服务器 GPU)；(5) 单服务器年成本 = (初始成本/折旧期) + 年软件费 + 年托管费；(6) 总成本 = 服务器数×单服务器年成本。单位成本：cost-per-1M-tokens = cost-per-1K-prompts×1000/(ISL+OSL)。关键度量：TTFT、ITL、TPS、RPS，跨配置须用相同 GPU 数或归一化到 RPS/GPU（来源：NVIDIA Developer）。

**如何衡量**：
- cost-per-query 是否声明了四约束与六行成本分解？是否同时给中位数与 P95？省略 embedding/eval/observability 是否会让成本被低估 20-40%？
- 推理 TCO 是否用三组件模型（折旧+功耗+维护）而非只看 API 单价？利用率是否在 70% 以上（否则每 token 成本翻 10 倍）？
- 是否按年 API 花费分级（5 万/50 万阈值）决策迁移与 fine-tune？私有 LLM 是否达回本点（日 200 万 token / 合规需求）？
- ROI 是否做了 ±10pp 自动化敏感性测试？Payback 是否 ≤18 个月？
- 是否把毛利预期从 60-80% 下调到 50-60%？是否按 cost-per-workflow 而非裸 token 锚定预算？

### 3.8 安全与对齐纵深标准

补研发现，初稿的"安全"维度仅覆盖 prompt injection 单点，遗漏模型对齐、对抗性 ML、模型供应链与 agent 权限滥用四个独立纵深。OWASP Top 10 for LLM 2025 已把过度代理权（LLM06:2025 Excessive Agency）与供应链（LLM03:2025 Supply Chain）单列为顶级风险，证明仅防 prompt injection 不足（来源：OWASP）。

**标准 1：模型对齐采用 RLAIF/Constitutional AI**。Anthropic Constitutional AI 核心是"让 AI 协助监督其他 AI"，无需人类标注识别有害输出，人类输入仅通过"一份规则/原则清单"（即"宪法"）。两阶段：(1) 监督学习阶段——从初始模型采样，生成"自我批判与修订"，再在修订后回答上微调；(2) 强化学习阶段——从微调模型采样，用一个模型评估两样本优劣训练偏好模型，再以该偏好模型作为奖励信号做 RL（即 RL from AI Feedback / RLAIF）。两阶段均可借助 chain-of-thought 推理提升透明度。结果是"无害但不回避"的助手——对有害查询解释其反对理由而非简单拒绝。这是填补"模型对齐"缺口的直接方法（来源：Anthropic Constitutional AI）。

**标准 2：对抗性 ML 分类须覆盖 prompt injection 之外的攻击类型**。NIST AI 100-2e2023（2024 年 1 月，作者 Apostol Vassilev 等）围绕"ML 方法类型/攻击生命周期阶段/攻击者目标/攻击者能力与知识"建立概念层次。明确命中的攻击类型：Evasion（扰动输入致误分类）、Data Poisoning（污染训练数据操纵模型行为）、Privacy Breach（从模型提取敏感信息，对应 model extraction/inversion）、Trojan/Backdoor Attack（在模型中植入隐藏触发器）。分类同时覆盖生成式模型、大语言模型与 chatbot。报告声明其目的是"为评估和管理 AI 系统安全的其他标准与未来实践指南提供输入"——即对抗性 ML 应作为标准独立维度（来源：NIST）。

**标准 3：红队演练制度化**。Google SAIF 六要素中第 5 要素明确要求"组织应进行定期红队演练以提升 AI 产品的安全保证"，并按事件与用户反馈更新训练数据/微调模型应对攻击。SAIF 同时显式列出对抗性威胁："stealing the model（模型窃取/提取）""data poisoning of the training data""prompt injection""extracting confidential information"。OWASP GenAI 项目 8 大议题中第 7 项"Red Teaming & Evaluation——用对抗性红队方法测试 GenAI 系统"，第 2 项"AI Threat Intelligence and Response——追踪攻击者对 GenAI 的滥用与新兴威胁模式"（来源：Google SAIF、OWASP GenAI）。

**标准 4：过度代理权防护**。OWASP 2025 版 LLM06 定义：基于 LLM 的系统常被授予超出安全边界的自主权，当连接工具/API/自动执行路径时，过度权限会导致真实世界的损害。OWASP GenAI 项目 8 大议题中专设第 5 项"Agentic App Security——保障自主 agent 与多步 AI 工作流"，并发布《OWASP Top 10 for Agentic Applications》（其中 ASI06 为记忆与上下文投毒 Memory & Context Poisoning）。agent 自主权滥用需独立纵深，而非 prompt injection 单点（来源：OWASP）。

**标准 5：模型供应链安全**。OWASP 2025 版把供应链单列为 LLM03，指出 LLM 供应链在多阶段易受攻击：预训练模型、微调数据、第三方组件、部署基础设施；风险包括被篡改的模型权重、被污染的训练数据集、AI/ML 管道中不安全的依赖。OWASP GenAI 项目另设 AIBOM Generator（AI SBOM 生成器）议题。SAIF 借鉴其联合开发的 SLSA（软件构件供应链级别）框架，将供应链完整性延伸到模型构建软件。仅防 prompt injection 无法覆盖权重投毒与依赖篡改（来源：OWASP、Google SAIF）。

**标准 6：Prompt injection 纵深防御**（见 3.6 标准 7，此处为完整安全纵深的一环而非全部）。

**如何衡量**：
- 是否采用 RLAIF/Constitutional AI 或等效对齐方法，而非仅靠系统提示拒答？
- 是否针对 evasion/data poisoning/model extraction/backdoor 四类对抗性 ML 攻击建立了检测与防护？
- 是否有制度化的定期红队演练（而非仅在发布前做一次越狱测试）？
- agent 的工具/API 自主权是否遵循最小权限？是否对"过度代理权"做了独立审计？
- 是否有 AI SBOM 覆盖预训练模型、微调数据、第三方组件、部署基础设施？是否对模型权重与依赖做完整性校验？

### 3.9 多模态架构标准

补研发现，初稿通篇以文本 LLM 为隐含假设，完全未覆盖视觉/音频/文档处理、多模态嵌入、多模态 agent 与多模态对上下文工程及成本的改变。

**标准 1：多模态按视觉 token 计费，多轮 agent 须用 Files API 引用**。Claude 把图像切成 28×28 像素 patch，每 patch 一个视觉 token，即 ⌈width/28⌉×⌈height/28⌉ 个 token。一般模型上限 1568 token/1568px 长边；Opus 4.7+/Fable 5 等高分辨率模型上限 4784 token/2576px。按 Sonnet 4.6 每百万输入 token $3 计：1MP 图像约 1296 token≈$0.0039/张，4K 图像因降采样封顶仅约 $0.0047/张。单请求最多 100（200k 窗模型）或 600 张图，每张最大 10MB base64。关键 agent 模式：多轮对话每轮重发全部历史，若图用 base64 则每轮重传全图字节，显著放大请求体与延迟，应改用 Files API 上传一次后以 file_id 引用，让请求体随图数累积保持小体积（来源：Anthropic Claude Vision）。

**标准 2：多模态重塑上下文工程——大二进制外置为 artifact**。Google ADK 把上下文重构为编译视图：会话/记忆/artifact 是源，流与处理器是编译管线，working context 是发给 LLM 的编译产物。四层：working context（按调用重建、临时）→ session（持久真相、强类型事件流）→ memory（跨会话可检索）→ artifacts。对多模态关键：artifacts 管理与会话/用户关联的大二进制或文本（文件/日志/图像），按名称+版本寻址而非粘贴进 prompt；用 handle 模式——大数据只放 artifact store，agent 默认只看轻量引用（名+摘要），需用时 LoadArtifactsTool 才装入，调用后即卸载，把每条 prompt 5MB 噪声变成按需精确检索。三大压力证明朴素塞上下文失败：成本/TTFT 随上下文暴涨、信号退化（无关日志/陈旧工具输出分散注意力）、物理上限。多 agent 用 include_contents 控制 handoff 范围防止上下文爆炸，并做会话翻译（把前一个 assistant 消息重铸为叙事上下文）以正确归因角色（来源：Google ADK）。

**标准 3：五种可复用架构模式按场景选型**。(1) 独立编码器+文本枢纽——视觉模型先出图说，图说作为文本进入编排器，LLM 纯文本推理；关注点解耦、成本可预测、故障局部化，2025-2026 企业最常见。(2) 统一多模态模型（GPT-4o/Claude 3.7/Gemini 1.5/Qwen-VL）同窗原生跨模态推理，能注意 caption 会丢弃的低层图像特征，适合图表推理+OCR，但成本高、延迟可变、故障混合。(3) 文档预处理管线（企业文档密集主流）：格式检测→布局解析（DiT/LayoutLMv3）→OCR→表格抽取→布局感知语义切块→嵌入索引→检索时重排。(4) 模态专属检索：用 CLIP 式嵌入检索图像、音频嵌入检索音频。(5) 多模态输出（图表/TTS/文档/图像生成）各有独立阶段与评估面。反模式：把所有模态都塞进最大的多模态模型对常规案例昂贵、慢且无必要（来源：Compel Framework）。

**标准 4：统一 decoder-only 多模态是前沿路线**。字节 BAGEL 是统一 decoder-only 模型，在万亿级 token 交错文本/图像/视频/web 数据上预训练，原生支持理解与生成，发展出自由图像编辑、未来帧预测、3D 操作、世界导航等涌现推理。Seed1.5-VL 由 532M 视觉编码器 + 20B 激活参数的 MoE LLM 组成，在 60 个公开 VLM 基准的 38 个上 SOTA，且在 GUI 控制、游戏等 agent 任务上超越 OpenAI CUA 和 Claude 3.7。四条原则：统一优于专用、MoE 提效、交错多模态预训练带来跨模态涌现、粗-细解耦提升生成保真（来源：字节跳动 Seed-Multimodal）。

**标准 5：多模态分词与 Dense vs MoE 权衡**。2025-2026 主流多模态模型存在两条可行分词路线——统一共享 token 空间（GPT-5 把文本/图像 patch/音频映射到同一共享 token 空间）vs 模态专属分词（Gemini 用针对每个模态优化的分层分词 + 跨模态注意力层把文本概念锚定到视觉内容；SAM 3 用 ViT 图像编码器+提示编码器+轻量 mask 解码器，靠 cross-attention 进行多模态提示融合）。架构上 Dense（GPT-5/Gemini Pro，重推理深度、延迟高，GPT-5 达 26s）vs MoE（Gemini Flash，2x 更快）是当前主要速度/能力权衡。Gemini 上下文窗达 200 万 token 支持整篇论文/法律/科学数据分析（来源：Roboflow）。

**标准 6：多模态成本/延迟/评估/治理按模态设门**。相对文本基线：视觉+文本模型调用 2-5x；音频转写+模型调用额外 +1-3s 预处理，转写约 $0.006/分钟；20 页 PDF 文档管线端到端 5-30s，且总成本由文档管线而非模型调用主导。各模态评估面：视觉（ChartQA/DocVQA/MMMU、OCR 精度）、音频（WER、说话人分离、MOS）、文档（布局检测 F1、表抽取 P/R、端到端 QA）、跨模态一致性。安全：图内可藏 prompt 注入、CSAM/PII（车牌人脸）；音频有声纹生物特征/录音合规；文档敏感数据浓度更高需先脱敏；图像输出有深度伪造/版权、音频输出有语音克隆与披露法规。治理：EU AI Act 第 10/15 条覆盖所有模态，生物特征处理（声/脸）触发第 5 条/附件 III。Anthropic 官方也指出视觉模型会幻觉物体计数、误读图表、从模糊图像臆造文本，agent 高风险用例必须人工复核（来源：Compel Framework）。

**如何衡量**：
- 多轮多模态 agent 是否用 Files API/artifact handle 引用大二进制而非每轮重传 base64？
- 是否按场景在五种架构模式中选型，而非默认把所有模态塞进最大统一模型？
- 多模态成本/延迟是否按模态单独预算（视觉 2-5x、文档管线主导成本）？
- 各模态是否有独立评估面（ChartQA/WER/布局 F1/跨模态一致性）？是否按模态设人工复核门？

### 3.10 边缘与端侧部署标准

补研发现，初稿的架构标准隐含"模型单一位于云端"，完全未覆盖边缘 AI、端侧推理、联邦学习与云-边-端混合——而这恰是 Cursor p50<100ms、Copilot p95 190ms 等延迟敏感场景的落地答案。

**标准 1：云-边-端三层是端侧场景下"模型位于请求路径"的落地范式**。IEEE Communications Surveys & Tutorials 接收的 MEI4LLM 综述将移动边缘智能（MEI）定位为云端与端侧之间的中间层：端侧 LLM 相比云端"更具成本效益、延迟更低、更保护隐私"但受设备资源限制，MEI 通过将重计算卸载到近端边缘服务器解决。架构含三大子系统：边缘 LLM 缓存与投递（模型就近存储分发）、边缘 LLM 训练（边缘微调）、边缘 LLM 推理（边缘服务器运行推理）。核心原则是"云-边-端协作"——按资源可用性与延迟要求跨层切分 LLM 工作负载。模型不再单一位于云端，而是按延迟/隐私/成本分布到三层（来源：MEI4LLM）。

**标准 2：延迟-隐私-成本三角**。该文将每次推理决策建模为延迟-隐私-成本三角权衡（优化其中两个必牺牲第三个）。延迟：云端往返在首 token 前增加 200-500ms，端侧短上下文每 token <20ms，人类延迟感知阈值约 100ms——云端超阈值、边缘远低于阈值。隐私：数据不离设备则无法被截获/记录/传唤，本地推理自动满足数据驻留要求，是结构性保证而非策略性保证。成本：云端推理在高频场景（自动补全、摘要）成本复利累积，端侧将成本转移到用户已有的硬件。这直接对应 Cursor p50<100ms、Copilot p95 190ms 延迟敏感场景——这些延迟恰好落在端侧可满足、云端难以稳定满足的区间。"可在本地服务的查询占比两年内从 23% 跃升到 80% 以上"（来源：tianpan）。

**标准 3：路由层是混合架构中最高杠杆组件**。路由层模式包括：(1) 复杂度路由——轻量分类器按估计难度分流，研究显示可实现 85% 成本削减同时保持 95% 前沿模型性能；(2) 置信度级联——边缘模型先处理每个查询，token 级熵或校准概率低于阈值时升级到云端，无需单独分类器，模型自身不确定性即路由信号；(3) 分层升级含人工回退（边缘→云→专家，用于电信/医疗/法律）。三种架构：边优先+云升级（60%+查询在边缘能力内时最佳）、入口分流（分类器在推理前路由，避免浪费边缘算力）、推测式边缘+云端异步校验（乐观并发控制的 UX 等价物）。关键约束：路由器必须轻量——若增加 50ms 就消耗掉边缘推理本要节省的延迟预算的 1/4，应是小型分类器或启发式规则而非又一次 LLM 调用（来源：tianpan）。

**标准 4：端侧技术栈已成熟**。(1) 量化——GPTQ 用二阶信息误差补偿降到 3-4bit/权重，AWQ 保护 0.1%-1% 关键权重，TinyChat 比 FP16 桌面/移动 GPU 加速达 3x；训练 16 位部署量化 4 位为标准配方；经验法则 3B 以下模型不要量化到 Q4 以下（Llama 3.2 1B 在 Q3_K 掉约 40% 精度）。(2) MobileLLM 挑战"越宽越好"假设，125M 参数精度提升 2.7%、350M 提升 4.3%。(3) MoE——JetMoE-8B 总 8B 但每 token 仅激活 2B，比 Llama2-7B 推理计算减约 70%；EdgeMoE 专家预加载推理加速达 2.78x。(4) 协同分层——EdgeShard 将 LLM 分片分布到边缘与云端，动态规划最优分片放置实现 50% 延迟降低/2 倍吞吐；LLMCad"生成后验证"（小模型生成+大模型校验）加速达 9.3x 无精度损失。(5) 硬件——三星 PIM/PNM 内存内计算实现 4.5x 性能提升与 71% 能耗降低。模型示例：Gemini Nano（7B,4-bit,离线可用）、Octopus v2（2B,函数调用 1.1-1.7s）、Phi-3-mini（3.8B,69% MMLU）。端侧 AI 市场预计从 152 亿美元（2022）增至 1436 亿美元（2032），CAGR 25.9%（来源：On-Device Language Models Review）。

**标准 5：联邦学习是隐私敏感场景的标准答案**。云边协作架构含三层（云计算中心/边缘服务器/IoT 设备）与上层六种协作：资源协作、数据协作、智能协作、应用协作、服务协作、业务协作。边缘 FL 工作流：云端下发初始全局模型到边缘服务器，边缘设备从所属边缘服务器下载参数，本地更新先在边缘服务器聚合（而非直接云端），再在边缘服务器与中心云间做全局聚合——层级聚合减少通信轮次与延迟。通信效率三策略：端计算（IID 数据上增加本地计算可减少通信轮次 30 倍以上）、聚合控制（异步聚合避免滞后客户端）、模型压缩（Batchcrypt 实现 >20% 训练加速与 >60% 通信削减）。隐私两条路：差分隐私（加噪到客户端参数）、同态加密（密文上直接计算但"最短密钥长度可达平均梯度长度几十倍"，跨设备 FL 不实用但高隐私工业 FL 可行）。模型训练本身可分布到边缘而不集中数据（来源：PMC Federated learning）。

**标准 6：边缘原生运行时优先 C++/离线**。NVIDIA TensorRT-Edge-LLM 自述为"面向物理 AI 的高性能轻量 C++ LLM 与 VLM 推理软件"，明确面向"资源受限设备如 NVIDIA Jetson 与 NVIDIA DRIVE 平台"。关键架构决策："引擎构建与端到端推理完全在边缘平台运行"——与许多需远程构建步骤的框架不同，编译与运行时均无云依赖。语言构成反映优先级：Python 42%（工具/量化/导出脚本）、C++ 40.8%（核心推理运行时）、CUDA 16.2%（自定义 GPU 内核）——运行时无 Python。用例清单强化边缘优先：车内 AI 助手、隐私保护 AI、离线语言处理、低延迟推理——这些场景云端往返延迟不可接受。Apache 2.0 许可（汽车/工业部署关键）（来源：NVIDIA TensorRT-Edge-LLM）。

**如何衡量**：
- 延迟敏感场景（<100ms）是否将模型下沉到边缘/端侧，而非依赖云端往返？
- 路由层是否轻量（<50ms）且按复杂度/置信度路由？是否实现 85% 成本削减同时保持 95% 性能？
- 端侧模型是否用 AWQ/GPTQ 4-bit 量化与 MoE 稀疏激活？是否避免 3B 以下量化到 Q4 以下？
- 隐私敏感场景是否用联邦学习把训练分布到边缘而非集中数据？是否用 DP/HE 保护参数？
- 边缘运行时是否 C++ 原生、完全离线、无云依赖？

### 3.11 合规与监管标准

补研发现，初稿仅把"合规"作为治理横切层的一句提及，缺乏 EU AI Act 风险分级、GDPR/HIPAA/SOC2、数据驻留、跨境数据流、审计轨迹与行业专属（医疗/金融）考量的可操作标准。

**标准 1：EU AI Act 四级风险分级**。四级：不可接受风险（2025 年 2 月起 8 类被禁，含社会评分、职场情绪识别、实时远程生物识别）；高风险（信贷评分、招聘筛选、关键基础设施、教育考试评分、司法辅助、移民边境）；有限风险（透明度披露，2026 年 8 月生效）；最小风险（无规则）。高风险系统上市前必须：充分的风险评估与缓解系统、高质量数据集以最小化歧视性结果、活动日志记录以确保结果可追溯、详细文档提供系统及目的的全部信息、向部署者提供清晰充分信息、适当的人类监督措施、高稳健性/网络安全/准确性。上市后提供商须维护监控系统，提供商和部署者须报告严重事件和故障。GPAI 模型规则 2025 年 8 月生效，系统性风险模型须评估并缓解风险。高风险 AI 系统规则（生物识别/关键基础设施/教育/就业/移民）2027 年 12 月 2 日适用（来源：欧盟委员会）。

**标准 2：GDPR 跨境数据流 + Article 22 自动化决策约束**。Article 45 充分性决定允许向认定国家自由传输；Article 46 在无充分性决定时须 SCCs/BCRs/行为准则等适当保障；Article 47 BCRs 用于集团内部传输；Article 49 例外（明示同意、合同必要、重大公共利益等）。Article 22：个人有权不受仅基于自动化处理（含画像）且产生法律或类似重大影响的决策约束，例外须提供人类干预和可争议权——直接影响 AI 自动决策架构。Article 25 须在数据处理手段确定时和处理期间内嵌隐私（数据最小化、目的限制）。Article 35 对高风险处理（大规模画像、敏感数据、系统监控）须做 DPIA。Article 5 六原则：合法公平透明、目的限制、数据最小化、准确性、存储限制、完整性与机密性。Article 9 限制敏感数据（健康/生物识别）处理（来源：GDPR）。

**标准 3：HIPAA BAA + 共享责任模型**。PHI 涵盖广泛可识别健康数据。Security Rule 要求通过三类防护保护 PHI 的机密性、完整性和可用性：行政控制（策略、风险管理、培训、监督流程）、物理控制（设施和系统访问保护）、技术控制（访问控制、审计控制、完整性控制、传输安全）。任何创建/接收/维护/传输 PHI 的供应商（含云/AI 服务商）须签 BAA。无 CSP 的 HIPAA 认证，AWS 将控制对齐 NIST 800-53 和 FedRAMP，HITRUST CSF 统一联邦法/州法/非政府框架。客户须仅在 BAA 覆盖的 HIPAA-eligible 服务中处理存储传输 PHI，共享责任模型下客户负责其部署的 AI/ML 工作负载安全。AI/ML 服务须先获得 HIPAA-eligible 资格才可处理 PHI（来源：AWS HIPAA）。

**标准 4：NIST AI RMF 四函数（GOVERN/MAP/MEASURE/MANAGE）**。GOVERN（跨切函数，融入其他三函数）要求：1.1 法律法规要求须理解、管理、文档化；1.6 AI 系统清单机制；1.7 安全退役；2.1 角色责任文档化清晰；6.1 第三方含知识产权侵权；6.2 高风险第三方故障应急。MAP（建上下文）5 类含用途/法律/规范文档化、系统分类、组件风险含第三方、影响特征化。MEASURE（量化评估）4 类含评估七个可信特征（2.5 有效可靠、2.6 安全、2.7 安全弹性、2.8 透明问责、2.9 可解释、2.10 隐私、2.11 公平无偏、2.12 环境影响）。MANAGE（处置）4 类含按影响/可能性/资源排序处置（缓解/转移/规避/接受）、4.3 事件和错误须沟通给相关 AI 行为者包括受影响社区。GOVERN 1.2 要求可信 AI 特征内嵌到组织政策流程（来源：NIST AI RMF）。

**标准 5：SOC 2 与跨境数据流框架**。SOC 2 基于 AICPA 五个 Trust Services Criteria（安全、可用性、处理完整性、机密性、隐私）对外包服务组织进行审计，是采购方评估 AI/SaaS 供应商数据安全与处理可靠性的关键 assurance 报告；审计师须按专业标准执业、参加同行评审并持证。另有 SOC for Supply Chain（同样五准则应用于生产/制造/分销系统）。欧盟委员会 2023 年 7 月 10 日通过 EU-US Data Privacy Framework 充分性决定，使个人数据可在无额外保障（如 SCCs）下从欧盟流向美国，是继 Safe Harbor、Privacy Shield 被废止后的新框架。U.S. 组织须通过该框架认证并遵守相应原则（通知、选择、可问责性、安全、数据完整性、访问与救济、执法）。此框架是 AI 系统跨境数据流（如 EU 训练数据流向美国模型服务）的关键合规路径之一（来源：AICPA、欧盟委员会）。

**标准 6：行业专属——金融 adverse action 可解释性**。CFPB 2023 年 9 月 19 日发布消费者保护通告：ECOA 与 Regulation B 要求采取 adverse action 的信贷方提供"具体"且含"主要拒绝原因"的陈述，原因须"与信贷方实际考虑或评分的因素相关并准确描述"。CFPB 明确"ECOA 和 Regulation B 不允许信贷方在使用黑箱承保技术导致无法提供具体准确原因时使用该技术"——信贷方不能以技术过于复杂或不透明为由不合规，必须理解自身决策系统。AI 模型使用替代数据时仍须披露实际拒绝原因，即使该因素与信用度的关系对申请人不明显。须对齐银行业模型风险管理（SR 11-7 类）指引。这直接约束金融 AI 原生系统的可解释性架构选择（来源：MoFo / CFPB）。

**如何衡量**：
- 系统是否按 EU AI Act 定级？若为高风险是否满足风险评估/数据质量/日志记录/人类监督/文档化/稳健性六项强制义务？
- 自动决策是否受 GDPR Article 22 约束？是否提供人类干预和可争议权？是否做 DPIA？
- 处理 PHI 是否签 BAA？是否仅在 HIPAA-eligible 服务中处理？是否用 HITRUST CSF 统一框架？
- 是否用 NIST AI RMF 四函数组织治理？GOVERN 是否横切且文档化问责与第三方风险？
- 金融场景是否满足 ECOA adverse action 可解释性？黑箱模型是否被禁用？
- 跨境数据流是否用充分性决定/SCCs/BCRs/EU-US DPF 合法化？

### 3.12 组织与团队结构标准

补研发现，初稿通篇谈技术架构与流程，完全未覆盖团队结构、关键角色、团队拓扑与康威定律——而"AI 放大康威定律"意味着组织拓扑直接塑造 AI 系统架构。

**标准 1：水平工作归平台团队，垂直工作归产品团队**。CTAIO 提出 ML Engineer 与 ML Platform Engineer 的工作是水平的（训练/微调基础模型、构建共享 ML 平台：serving=Triton/vLLM/TGI、feature store、registry、monitoring），应置于 centralized 或 platform team；AI Engineer 的工作是垂直的（集成预训练模型、RAG、agent 框架、prompt pipeline），应嵌入产品团队。原文警告：把两者放反——把本应嵌入的 AI Engineer 中心化、或把本应中心化的 platform engineer 嵌入——会造成结构性失能。4 种拓扑模型：Centralized CoE、Embedded、Platform ML、Hybrid Hub-and-Spoke，按成熟度选型（0-2 模型→Centralized；3-5→Embedded；6-10→Hub-and-Spoke；10+→Platform+Embedded；AI-Native→从第一天起即 stream-aligned AI 团队）。企业把 AI 当 feature 而非 platform 是共同错误，结果产出 fragile ecosystem（prompts/models/vector stores/agents 各建不同、治理不一致、无法规模化），需如云时代 DevOps/Platform Engineering 一样设专职 AI 平台团队（来源：CTAIO）。

**标准 2：AI 放大康威定律，AI context 文件成为新沟通通道**。Team Topologies（Skelton & Pais 2019）四类团队三类交互仍成立，但 AI 改变认知负荷方程："less implementation load, more integration load"。具体：stream-aligned 团队从 7-9 人缩到 3-5 人；platform team 从支持角色升为"重心"（传统标准化省 10-15% 基础设施开销，AI 时代使 AI 有效性提升 20-30%/团队，"The ROI roughly doubles"）；enabling team 从临时变为常设；complicated-subsystem team 大幅消解（AI 吸收 60-70% 专家实现工作）。康威定律下，AI context files（CLAUDE.md、cursor rules）、API specs（OpenAPI、proto）成为向 AI agent 传达架构决策的新沟通通道；Inverse Conway Maneuver 更强——边界清晰时 AI 产出尊重契约的代码，边界模糊时"AI agents take the ambiguity at face value and produce code that does not respect the intended separation"。"The topology you choose is the architecture you'll get"——孤立 AI 团队→功能像"bolted on"、handoff 成"JSON blob thrown over a wall"；碎片化团队→三个不同 vector DB、两套不兼容 eval 框架（来源：prommer）。

**标准 3：关键角色 taxonomy，prompt engineer 退化为技能**。六类角色：ML Engineer（从头训练/微调基础模型，需 GPU 集群，水平工作，居平台/中心化团队）；AI Engineer（集成预训练模型尤其 LLM，建 RAG/agent/prompt pipeline，垂直工作，嵌入产品团队）；ML Platform Engineer（建运营共享 ML 平台，不建模型，居平台团队）；AI Product Manager（与普通 PM 不同——AI 产品非确定性行为、需不同评估方法、需上线后持续监控）；Prompt Engineer（争议角色——到 2026 多数组织把 prompting 当作 AI engineer 拥有的技能而非独立岗位，仅在有系统化 prompt 管理/版本化/A-B 测试共享 registry 时才成立专职）；AI Safety/Red Team（测 prompt injection/有害输出/偏差/数据泄露/jailbreak，关键原则"Should NOT report to the same team that built the system being tested"）。a16z 补充：in-context learning"effectively reduces an AI problem to a data engineering problem"，"You don't need a specialized team of ML engineers"，prompt 策略正成为产品差异化来源。招聘 MLE 过早是浪费，须"domain expert at all times"（来源：CTAIO、a16z、applied-llms.org）。

**标准 4：Eval 所有权跨多角色，须"评估评估器"**。applied-llms.org 称"evaluation and measurement are crucial for scaling a product beyond vibe checks. The skills for effective evaluation align with some of the strengths traditionally seen in machine learning engineers"，但主张民主化——让全员学 prompt 基础以鼓励实验，eval 以"unit tests of samples of inputs/outputs with expectations"起步，成熟后才引入 MLE。Martin Fowler 文章给三类测试：example-based（结构化 JSON 输出做确定性断言）、auto-evaluator（LLM 评 LLM，"a type of property-based test"）、adversarial（prompt injection/PII 泄露）。关键要求："it's not enough for a test to pass or fail"——须产出可视化调试产物；"evaluate the Evaluator to check for false positives and false negatives"；"decouple inference and testing"避免重复昂贵 LLM 调用；prompt 当代码做 red-green-refactor；引入 Threat Modelling 与 OWASP Top 10 for LLM Applications（来源：Martin Fowler、applied-llms.org）。

**标准 5：context engineering 是分布式职能而非独立岗位**。prommer.net 明确不把"eval engineers""prompt engineers""context engineers""AI architects"命名为独立岗位——context/prompt engineering 工作分布在 enabling team 的职责（"context engineering standards"：维护 CLAUDE.md 模板、spec 格式、prompt libraries），evaluation 工作落在 platform team 范围（"evaluation frameworks"）。专属 AI enabling team（2-4 人）负责：工具评估（每月控制试点新 AI 编码工具）、context engineering 标准、培训、effectiveness 测量、成本优化（"when to use Opus vs Sonnet vs Haiku"）。平台团队扩展范围含 LLM API gateway（限流/成本追踪/model routing/fallback）、context engineering 模板、evaluation 框架、成本监控仪表盘（来源：prommer）。

**标准 6：比例、反模式与迁移路径**。平台工程师对 stream-aligned 从传统 1:10-15 收紧到约 1:8-10。具体配比：Centralized CoE 约 4 人、5+ 请求团队即成瓶颈；at-scale 平台团队 8-15 人、每产品团队 0-2 个 AI engineer；Hub-and-Spoke 实例（Series D fintech 300 工程师、40 在 AI/ML、8 产品团队、中心平台 12 人、每产品团队 2-4 AI engineer）；Series B startup 3-5 人最优。反模式：AI Center of Bottleneck（按"最吵的轮子"排优先级、拖延数月）、Lone Wolf（单一嵌入 AI engineer，离开后两月内功能坏）、Platform for Nobody（华丽基础设施无人能用、团队仍用 Jupyter 部署）、Research Lab（为发论文而非生产影响优化）、Stealth AI Team（暗中堆积模型无监控/成本/安全审查直至事故）。重组触发器：AI 队列超 4-6 周、shadow AI 基础设施出现、各团队模型质量差异大、top AI engineer 因孤立离职。迁移：Month1-3 试点缩一个团队 7-9→4-5；Month2-4 平台投资须领先 stream-aligned 迁移 1-2 月；Month4-9 每月 2-3 团队；Month9-12 拓扑精修（来源：CTAIO、prommer）。

**如何衡量**：
- 水平工作（模型/共享基建）是否归平台团队？垂直工作（RAG/agent/prompt）是否嵌入产品团队？两者是否放反？
- stream-aligned 团队是否已从 7-9 人缩到 3-5 人？platform team 是否升为重心（ROI 翻倍）？
- 是否区分 ML Engineer/AI Engineer/ML Platform Engineer/AI PM/AI Safety-Red Team 六类角色？AI Safety 是否独立于被测系统团队汇报？
- eval 所有权是否从共享起步、系统成熟后引入专职 MLE？是否"评估评估器"并解耦推理与测试？
- 是否避免了五大组织反模式（Bottleneck/Lone Wolf/Platform for Nobody/Research Lab/Stealth Team）？平台:stream 比例是否在 1:8-10？

## 四、参考架构

### 4.1 分层架构总览

Indium 提出一套 6 层 AI 原生参考架构（经核验逐字确认）：

1. **AI-Powered Experience Layer**（会话 UI / 个性化引擎 / 预测 UX / 全渠道智能）
2. **AI Intelligence & Decision Layer**（LLM 编排、AI Agent 框架、知识图谱引擎、实时 ML 管道、计算机视觉、预测分析）
3. **Intelligent Application Layer**（自适应微服务、智能工作流、AI 增强 API 网关、事件驱动智能、文档智能）
4. **AI-Enhanced Data Platform**（智能数据编织、特征存储、向量库、模型注册表、数据质量 AI、语义数据层）
5. **Autonomous Infrastructure Layer**（GPU/TPU 算力、预测式自动扩缩、容器编排、边缘 AI 节点、自愈系统）
6. **AI Governance & Security 横切层**（伦理框架、模型可解释性、智能安全、隐私合规、MLOps、风险管理）（来源：Indium）

ittech-pulse 的分层为 Frontend → LLM → RAG → AI Microservices → Orchestration → Data，同样把"模型层、编排/agent 层、数据/知识层"作为核心（来源：ittech-pulse）。a16z 的 LLM 应用栈分解为 11 层（Data Pipelines、Embedding Model、Vector Database、Orchestration、LLM APIs、LLM Cache、APIs/Plugins、Logging/LLMops、Validation & Security、App Hosting、Playground），主导模式为 in-context learning 而非 fine-tuning（来源：a16z）。AWS Well-Architected ML Lens 给出 5 层 ML 架构（Data → Feature Engineering → Model → Inference → Application）与 7 项设计原则（来源：AWS）。

> **争议/待考证**：研究包中一项声明称"多家厂商参考架构高度一致"。经核验，Indium 的 6 层架构本身逐字确认，但 Indium 文章并未做跨厂商对比或"高度一致"的论断；detail 中引用的 First Line Software 6 层模型无法定位核实。故"多家厂商高度一致"这一结论存疑。可以确认的是：Indium、ittech-pulse、a16z、AWS 各自独立提出的分层均把"模型层、编排/agent 层、数据/知识层、基础设施层、应用层"作为核心分层，呈现方向性趋同，但尚不足以断言"高度一致"。

### 4.2 核心组件与职责

**数据基础设施层**。向量数据库存储嵌入并提供相似性搜索，是 RAG 管道核心。标准数据流范式为离线批摄入（领域数据分块→经嵌入模型转为高维向量→向量连同元数据写入向量库）+ 实时在线查询（用户输入向量化→最近邻查询→检索的语义块作为上下文接地追加到提示→FM 生成）。关键技术考量：分块策略、维度选择、规模、数据治理、混合读写模式（来源：AWS）。

**编排/Agent 层**。Anthropic 的 agent 系统分层：Layer 0 = 增强 LLM（检索+工具+记忆）为基础构建块；Layer 1 = 5 种组合式工作流模式：Prompt Chaining（顺序+门控）、Routing（分类分流到专用 prompt/模型）、Parallelization（sectioning 并行聚合 / voting 多次投票）、Orchestrator-Workers（中央 LLM 动态拆解任务委派 worker 再综合）、Evaluator-Optimizer（生成-评估反馈循环）；Layer 2 = 自治 agent，在"a loop of tool use and environmental feedback"中运行（来源：Anthropic）。多 agent 编排有五种基础模式（sequential/concurrent/group-chat/handoff/magentic），按协调方式与路由确定性区分，可混合使用（来源：Azure）。

**治理与安全横切层**。SAP 的"模型推理、框架治理"原则要求平台同时承载确定性应用与自适应 agent，"agent lifecycle, identity, routing, and governance are built in from the start"。四种扩展模式：MCP 工具扩展、可复用 skills、pre/post 扩展钩子、指令式行为调节（来源：SAP）。该横切层须扩展为完整安全纵深（见 3.8），涵盖模型对齐、对抗性 ML、红队、过度代理权与供应链。

### 4.3 Agent 系统设计要点

**记忆系统**。Agent 记忆分为短期（工作记忆，维护当前交互上下文，用 checkpoint 机制按线程存储，会话结束即重置）、长期（跨会话持久，通过提取管道识别有意义信息→整合→存为向量嵌入，用近似 k-NN 语义检索）、情景记忆（捕获带时间细节的过去经历，用向量库做语义检索 + 事件日志做不可变审计轨迹）。四阶段架构：Encoding（切块+嵌入）→ Storage（向量索引 HNSW/IVF/FLAT）→ Retrieval（相似度搜索）→ Integration（格式化注入 prompt）。设计建议：先做线程级短期 + 跨会话长期，其余按运营价值增量添加（来源：Redis）。

值得注意的是，主流框架中 agent 记忆常退化为"上下文窗口即工作记忆"。Claude Agent SDK 用文件系统作为持久记忆、用 agentic search（grep/tail 等 bash 工具直接搜文件）优于语义搜索、用 Compaction 在上下文接近上限时自动摘要历史消息。对 ReAct/Plan-and-Execute/Reflection 三模式的分析表明，三者均只靠上下文窗口做工作记忆，没有内建长期/情景记忆机制——这正是 ReAct 的 verifier stall 失败模式根因（来源：Claude Agent SDK）。

**协议层选型**。MCP（Model Context Protocol）适合一个编排器对工具/API/数据源的强控制；A2A（Linux Foundation Agent2Agent）适合 agent 间相互 opaque（如分属不同工程团队）的场景。推荐：用 MCP 做工具与数据访问（含企业级安全/认证/审计），用 A2A 做跨平台 agent 通信。核心原则：最小权限、简洁性、可审计性、强治理（来源：Microsoft Learn）。

### 4.4 云-边-端参考架构

补研新增。端侧场景下"模型位于请求路径"标准（3.1 标准 1）的落地范式为云-边-端三层（见 3.10 标准 1）：云端数据中心负责集中训练与复杂推理、边缘服务器负责近端推理与缓存投递、终端设备负责低延迟/隐私敏感的本地推理。路由层（复杂度路由/置信度级联/分层升级）是三层间的最高杠杆组件（来源：MEI4LLM、tianpan）。隐私敏感训练场景用联邦学习的层级聚合（边缘服务器先聚合再全局聚合）替代集中数据（来源：PMC）。边缘运行时优先 C++ 原生、完全离线、无云依赖（来源：NVIDIA TensorRT-Edge-LLM）。

### 4.5 多模态参考架构

补研新增。多模态场景下上下文工程标准（3.2 标准 2）的落地范式为四层上下文架构（working context/session/memory/artifacts），大二进制外置为 artifact 并用 handle 模式按需加载（见 3.9 标准 2，来源：Google ADK）。五种可复用架构模式按场景选型：独立编码器+文本枢纽（企业最常见）、统一多模态模型（图表推理）、文档预处理管线（企业文档密集主流）、模态专属检索（CLIP）、多模态输出（来源：Compel Framework）。前沿路线为统一 decoder-only 多模态 + MoE + 交错多模态预训练（来源：字节跳动 Seed-Multimodal）。

## 五、从 0 到 1 实现路径

### 5.1 阶段划分

**第一优先级：设计数据模型与反馈闭环**。从零构建的第一优先级是设计数据模型——记录产品将产生的每个事件、要预测的每个结果，从第一天起就构建能捕获训练信号的 schema，并选择对 embedding 友好的数据库架构；在集成第一个模型之前先集成 AI 可观测性工具。代价是开始时 2-3 周设计工作，否则后期返工需 3-6 个月工程时间。判别 AI 原生 vs AI 增强的标准是："如果今晚从产品中移除 AI，用户是否会注意到产品工作方式的根本变化？"（来源：apidots）

**阶段演进**。三种 AI 集成方式：API-based（2-6 周，低前期成本，低差异化，适合快速 MVP）→ 预训练模型嵌入/自部署+微调（6-16 周，中等成本/差异化，适合领域特定/隐私数据）→ 自定义模型训练（6-18 月，高成本，最高差异化）。成本交叉点："约 10000 用户以上，嵌入式模型比 API 集成更具成本效益"（来源：apidots）。

**成本经济门禁**（补研新增）。迁移决策须按年 API 花费分级（见 3.7 标准 3）：<5 万美元留在 GPT-4o Mini；5 万-50 万混合（80% 走 Mini，其余自托管 7B）；>50 万高利用率 GPU 集群 + LoRA fine-tune。私有 LLM 在日 token 量超 200 万或需 HIPAA/PCI 合规时开始回本，典型回收期 6-12 个月。FinTech 客服案例：三层混合路由（Haiku FAQ/Mini 复杂/自托管 7B 批量摘要）使月成本从 $47k 降至 $8k（降 83%），CSAT 维持 4.2，基础设施 ~4 个月回本（来源：Ptolemay）。须在做迁移决策前先用可辩护的 cost-per-query 四约束 + 六行成本分解建立基线（见 3.7 标准 1），否则会重蹈 MIT NANDA 证实的 95% 试点失败覆辙（来源：Drivetrain / Fortune）。

### 5.2 技术栈选型

**核心模式：用现成 LLM + 上下文条件化**。主流模式是"原样使用 LLM（不做 fine-tune）"，通过提示和私有上下文数据控制行为，"有效把 AI 问题降维为大多数公司已知道如何解决的数据工程问题"。三阶段流水线：(1) 数据预处理/Embedding（文档分块→过 embedding 模型→存向量库）；(2) 提示构建/检索（编译提示=硬编码模板+few-shot+外部 API+向量库相关文档）；(3) 提示执行/推理。即使上下文窗口扩大，成本和推理时间"随提示长度二次方扩展"，单次 GPT-4 查询 10000 页成本数百美元（来源：a16z）。这也意味着不需要专职 ML 团队（见 3.12 标准 3，来源：a16z）。

**模型选型演进**。原型阶段用最强模型（GPT-4）；成本敏感的规模化阶段降级到 GPT-3.5-turbo（比 GPT-4 便宜约 50 倍且显著更快）；高流量 B2C 分诊场景用开源模型。2026 多模型路由框架：简单任务(60%请求)→GPT-4o-mini；中等(30%)→Claude Haiku3.5/Gemini2.5Pro；复杂(10%)→GPT-5.5/Claude Sonnet4，并用便宜分类器做路由决策（来源：a16z、lushbinary）。

**多模态与端侧技术栈**（补研新增）。多模态多轮 agent 须用 Files API 引用图像而非每轮重传 base64（见 3.9 标准 1）。端侧模型用 AWQ/GPTQ 4-bit 量化为默认配方，MoE 稀疏激活（JetMoE-8B 每 token 仅激活 2B）；协同分层用 EdgeShard（降延迟 50%/吞吐 2x）与 LLMCad"生成后验证"（加速 9.3x 无精度损失）；经验法则 3B 以下模型不要量化到 Q4 以下（见 3.10 标准 4，来源：On-Device Language Models Review）。边缘运行时优先 C++ 原生、完全离线（来源：NVIDIA TensorRT-Edge-LLM）。

### 5.3 关键工程决策

**优先 in-context learning/RAG 而非 fine-tune**。理由：特定信息需在训练集出现至少约 10 次模型才能记住；in-context 可近实时纳入新数据；无需专门 ML 工程师；对相对小数据集通常优于 fine-tune。fine-tune 仅在特定条件（10K+用户/专有数据/需差异化/高流量需特定领域精度）才迁移（来源：a16z）。迁移的经济门禁见 3.7 标准 3。

**从 prompt engineering 演进到 context engineering**。随用例从一次性分类/生成演进到多轮长周期 agent，需从 prompt engineering 转向 context engineering——策展推理时整个 token 集。三大约束使上下文成为稀缺资源：context rot（token 增多则召回精度下降）、attention budget（transformer 的 n² 成对注意力）、训练分布偏差（模型主要训练于短序列）。长周期任务用三技术：压缩（Compaction）、结构化笔记（Agentic Memory）、子 agent 架构（专用子 agent 处理聚焦任务并只返回浓缩摘要）（来源：Anthropic）。多模态场景下大二进制须外置为 artifact（见 3.9 标准 2，来源：Google ADK）。

**何时上 agent**。沿"增强 LLM → 提示链 → 路由 → 并行 → 编排者-工作者 → 评估者-优化器 → 自主 agent"谱系按需升级。决策判据：任务可干净分解为固定子任务→用 workflow；步骤数不可预测/需模型驱动决策→用 agent。何时不用 agent：任务定义明确、需可预测性、需跨运行一致性、需固定路径时用 workflow。何时用 agent：问题开放式、灵活性关键、步骤数不可预测（来源：Anthropic）。

### 5.4 MVP 与验证

**先窄后宽**。MVP 核心原则："先窄、证明闭环、再扩展"。选 AI 能创造最明显价值的单一工作流，构建最小反馈捕获机制（记录用户接受/拒绝推荐、编辑 AI 输出、完成/放弃 AI 建议步骤），在该工作流发布窄 AI 功能，衡量留存影响而非参与度，闭环证明后再扩展。为何单任务深度重要：反馈闭环只在先在一个领域端到端跑通时才形成护城河，把 AI 薄摊到多个功能而闭环在任何地方都没跑通意味着没有功能复利。反模式："在拥有 100 个付费用户之前不要构建自定义 agent 框架、向量库或评估管道"（来源：apidots、lushbinary）。

**部署运维：把 AI 质量评估当作部署门禁**。评估栈：50-100 个带期望输出的黄金样例自动测试套件（每次模型更新/提示变更都跑）；LLM-as-judge（评估主观质量）；用户反馈信号（赞/踩、编辑追踪、重生成率）；成本监控（按用户/功能/模型追踪，超利润阈值告警）；延迟监控（P95 超 3 秒告警）。CI/CD 原则："像对待测试覆盖率一样对待 AI 质量——它是部署门禁。"成本降低模式：语义缓存（新查询与缓存相似度>0.95 则返回缓存，减少 30-50% LLM 调用）、多模型路由、提供商故障转移。关键安全规则："永远不要信任 LLM 输出做授权决策——LLM 是建议引擎，不是授权层。"（来源：lushbinary）

eval 所有权须从共享起步、系统成熟后引入专职 MLE，且须"评估评估器"并解耦推理与测试（见 3.12 标准 4，来源：Martin Fowler、applied-llms.org）。

### 5.5 边缘与端侧部署路径

补研新增。端侧场景的部署决策遵循延迟-隐私-成本三角（见 3.10 标准 2）：云端 TTFT 200-500ms 超人类感知阈值约 100ms，端侧每 token <20ms 远低于阈值，故延迟敏感场景须下沉到边缘/端侧。路由层是最高杠杆组件——复杂度路由可实现 85% 成本削减同时保持 95% 前沿模型性能，但路由器必须轻量（<50ms），应是小型分类器或启发式规则而非又一次 LLM 调用（来源：tianpan）。三种可交付架构模式按查询分布选型：60%+ 查询在边缘能力内用"边优先+云升级"；分类器在推理前路由用"入口分流"；乐观并发用"推测式边缘+云端异步校验"（来源：tianpan）。隐私敏感训练场景用联邦学习层级聚合（边缘服务器先聚合再全局聚合），DP/HE 保护参数（来源：PMC）。

### 5.6 组织与团队搭建

补研新增。AI 原生系统的"从 0 到 1"不仅是技术栈搭建，更是组织拓扑搭建。核心原则：水平工作（模型/共享基建）归平台团队，垂直工作（RAG/agent/prompt）嵌入产品团队，放反则结构性失能（见 3.12 标准 1）。按成熟度选型：0-2 模型→Centralized CoE；3-5→Embedded；6-10→Hub-and-Spoke；10+→Platform+Embedded；AI-Native→从第一天起即 stream-aligned AI 团队（来源：CTAIO）。团队规模：stream-aligned 从 7-9 人缩到 3-5 人，平台:stream 从 1:10-15 收紧到 1:8-10；Series B startup 3-5 人最优（1 senior ML + 1 ML platform/ops + 1 AI PM + 1-2 第二模型阈值时）（来源：prommer、CTAIO）。迁移路径：Month1-3 试点缩一个团队；Month2-4 平台投资须领先 stream-aligned 迁移 1-2 月；Month4-9 每月 2-3 团队；Month9-12 拓扑精修（来源：prommer）。须避免五大反模式：AI Center of Bottleneck、Lone Wolf、Platform for Nobody、Research Lab、Stealth AI Team（来源：CTAIO）。

## 六、案例研究

### 6.1 Cursor：把代码库索引做进基础设施层

Cursor 的 AI 原生设计体现在快慢双路径模型路由：补全走自研小模型（Fireworks 上 INT8 量化 1-7B 微调模型，目标 p50<100ms/p95<200ms）；复杂任务（Chat/Agent）路由到前沿模型 API（来源：collabnix）。该 p50<100ms 延迟目标恰好落在端侧可满足、云端难以稳定满足的区间（见 3.10 标准 2），是"模型位于请求路径"在延迟敏感场景的落地。

代码库索引采用 Merkle 树做增量同步：客户端扫描工作目录、构建文件/分块的 Merkle 哈希树，启动时把根哈希发给服务器做握手，服务器据此判断哪些子树需要同步，每 10 分钟检查一次哈希不一致以增量上传（来源：Engineer's Codex）。跨用户索引复用用 simhash + content proofs 做隐私隔离：新用户打开代码库时算出 simhash 上传，服务器做相似搜索，高于阈值的索引直接作为新库初始索引（同组织内同一代码库克隆平均 92% 相似度）。隐私模型：客户端上传完整 Merkle 树作为"内容证明"，搜索时服务器用客户端的树过滤结果，客户端证明不了的文件结果被丢弃。优化后中位索引时间从 7.87s 降到 525ms，p99 从 4.03 小时降到 21 秒（来源：Cursor 官方博客）。

### 6.2 Perplexity：检索质量而非 LLM 能力是首要瓶颈

核心论断是"检索质量是首要瓶颈而非 LLM 能力"，每次查询都触发全新检索，无静态答案缓存。六阶段 RAG 管线：查询意图解析 → pplx-embed 向量化（自研嵌入模型，INT8 量化使每 GB 可索引页面数提升 4 倍）→ 混合检索（BM25+dense+hybrid）→ 多层排序 L1-L3（L3 用 XGBoost，约 0.7 质量阈值，仅前约 30% 存活）→ 结构化 prompt 组装（引用标记在生成前嵌入）→ 约束式 LLM 合成（只在证据范围内生成并挂引用号）（来源：ziptie）。INT8 量化降本与 3.7 节成本标准一致。

Deep Research 是 agentic RAG 循环而非单次检索：decompose→逐子主题检索→部分合成→更新 scratchpad→识别缺口→细化子查询→重检索→跨源验证→最终合成，跑数十次搜索、扫描数百源、2-5 分钟（来源：gist）。

### 6.3 Devin：递归认知架构 + 持久沙箱

四阶段递归循环：Planning（CoT 生成结构化计划，执行中发现新信息会动态重规划）→ Action（shell/代码编辑器/浏览器三工具）→ Observation（捕获 stdout/stderr/编译日志/浏览器渲染）→ Correction（失败回灌上下文自愈）。沙箱用 Firecracker microVM（独立最小内核做更强隔离）而非 Docker，VM 跨会话持久（保留已装库等环境状态）。2025 末 SWE-1.5 联合 Cerebras 达 950 token/s，引入多轮 RL。已知坑：Death Loop（反复尝试同一失败修复烧钱直到预算上限）、任务耗时分钟到小时（来源：mmntm）。Death Loop 是 3.3 标准 4 中 ReAct verifier stall 失败模式的实例，须用 per-tool 调用上限 + max_steps 边界缓解。

Devin 用双 agent 系统（编码 agent + Devin Review 审查 agent）闭合反馈环：一 agent 写码，另一 pressure-tests，监听任意 GitHub bot 的 PR 评论命中即自动拾取修复并回灌 PR，循环直至通过所有检查。宣称"systems compound, tools don't"（来源：Cognition 官方）。

### 6.4 GitHub Copilot：延迟优先的无状态架构

Wave1 内联补全是延迟优先的无状态架构：约 6B 量化模型 + 约 350M 排序模型，p95 约 190ms、缓存命中 99.5%。上下文提取用 Tree-sitter 取相邻三个函数体+当前签名+最近 5 行 import，硬截断 4096 token，把约 50KB 编辑器状态压到约 2KB。缓存键 {user_id}:{project_hash}:{cursor_offset}，命中 99.5%（仅 0.5% 到 GPU）。与 chat agent 根本不同：无多轮状态、无工具/agent 推理、延迟优先（<200ms vs chat 1-5s）（来源：markaicode）。p95 190ms 同样落在端侧可满足区间（见 3.10 标准 2），高缓存命中率是端侧"成本转移到用户硬件"的实例。

### 6.5 FinTech 客服：三层混合路由降本 83%

补研新增。FinTech 客服月成本 7 个月内从 $47k 攀升（3.2B→12.4B tokens），用三层混合路由（Haiku FAQ/Mini 复杂/自托管 7B 批量摘要）后降至 $8k/月（降 83%），响应时间 310→280ms，CSAT 维持 4.2，基础设施 ~4 个月回本。这是 3.7 标准 3（API vs 自托管迁移门禁）与 5.2 模型选型演进（多模型路由）的直接实证（来源：Ptolemay）。

### 6.6 共同特征：AI 渗入栈中层成为一等公民

AI 赋能（bolt-on）把 AI 当偶尔调用的分类/摘要特性；AI 原生意味着 AI"不只活在栈顶，而是渗入栈中层"，成为与数据库、消息队列并列的基础层。关键差异：LLM 状态以权重/记忆/上下文"隐式烘焙"而非存表；暴露的是 intent/inference/actions/tools 而非 CRUD；控制流可动态路由甚至生成逻辑本身。核心原则："不能把一个 LLM 调用包进 API 网关就完事"——需要 prompt 路由器、记忆层、护栏、反馈评估器等新基础设施（来源：Catio）。

## 七、反模式与陷阱

### 7.1 AI 洗（AI Washing）

AI 洗的本质是用 buzzword 夸大 AI 能力、把边缘性 AI（如一个聊天框）宣传为 AI 驱动，且缺乏算法/训练数据/指标等技术细节。典型症状：使用 AI 流行词吸引客户但 AI 非核心；仅添加小元素却宣传为"AI powered"；无 AI 对决策/绩效影响证据；组织基础设施不足；营销语言超前于实际技术落地（来源：CFA Institute）。

规模性失败案例：逆向分析 200 家已融资 AI 初创公司，73% 是 API 套壳，成本溢价最高达 1000 倍，仅 7% 真正从零训练模型。三种套壳模式：伪专属模型（实际调 OpenAI API，溢价约 75 倍）、RAG 架构套壳（42 家技术栈完全一致，溢价 250-1000 倍）、微调模型（仅 7% 从零训练）。12 家把 API 密钥暴露在前端代码（来源：InfoQ）。

**30 秒识别法**：F12 开发者工具→网络面板→触发 AI 功能，看到 api.openai.com 等域名即为封装公司；响应稳定在 200-350 毫秒大概率调 OpenAI；代码包溯源搜 openai/anthropic/sk-proj 等关键词；模糊流行词（如"先进 AI"）可能在隐瞒（来源：InfoWorld）。

### 7.2 Bolt-on AI 的架构锁定

Bolt-on AI 把智能当附加功能：静态架构（底层产品不变，AI 只在旁边"按需帮忙"）；只优化所触瞬间而非重塑流程，天花板是旧产品略改；工作仍压在用户身上；架构锁定（因"架构为人手工操作设计"，再多 AI 功能也无法克服该基本假设）；无复利（各 AI 功能相互孤立，产品会衰退而非累积）。判据：bolt-on 改进曲线在初始跃升后趋平，AI-native 跨所有界面复利。"The foundation compounds. The bolt-on decays."本季度的架构选择决定未来十年轨迹，无中间地带（来源：Justin Bartak）。

### 7.3 把 AI 当 if-else

用智能体替换可控可审计的业务流程图是核心反模式。业务流程需要强制转移、分支条件、回滚、审计轨迹，而智能体没有原生状态机概念，它"近似流程而非执行流程"。基准表明指令遵循准确率随约束数稳定下降——"5 个及以上同时约束的 prompt 准确率远低于 50%"。解决：用专用工作流引擎保证确定性流程图，智能体仅在特定节点做推理，不应"成为"工作流（来源：Allen Chan）。

### 7.4 巨型 mega-prompt

把数百行程序性指令塞进单个智能体并期望每次精确顺序执行。问题：LLM 压缩上下文并按意图而非严格执行优化；研究显示长上下文中靠后信息检索准确率显著下降——"20 文档上下文中第 10 位置信息检索准确率降到约 55%"。即使每步 95% 准确率，跨数百步复合后端到端成功率很低。解决：分解为多智能体+supervisor 路由，或把确定性步骤卸载到工作流引擎；先直接用 LLM API（来源：Allen Chan、Anthropic）。

### 7.5 忽视 evals 与无视成本

基准（IFEval、FollowBench、Berkeley Function-Calling Leaderboard）表明模型远未达到完美合规，跳过评估的团队只在生产中发现失败。引用 2025 MIT/HBR 报告："95% 的生成式 AI 投资产生了零可测回报"，主因是缺少架构基础（来源：Allen Chan）。补研进一步证实：MIT NANDA（2025-08）证实 95% 企业 GenAI 试点失败、仅 5% 实现收入加速，主因含资源错配（超半数预算投销售营销而非后台自动化；外购成功率 67% vs 自建 ~22%）——这正是"缺成本模型/缺经济门禁"导致规模化失败的实证（来源：Drivetrain / Fortune）。反模式会复合放大成本：invisible state 导致重复工具调用、mega-prompt 每次调用消耗 token、exotic topology 倍增消耗（来源：Allen Chan）。

### 7.6 追逐花哨拓扑而非修补架构

当基础坏掉时却去抓 Swarm、CodeAct、LLM-as-Judge、智能体辩论等 exotic 拓扑是误诊——"在 invisible state 之上加 Swarm 拓扑并不修复 invisible state，只是把它分散到更多智能体"。智能体生产失败源于"任务范围界定、上下文管理、工具设计——而非智能体拓扑选择"。失败常在 demo 看不见：20 步 prompt 测试可行，到 200 步或 1000 并发用户时架构债"往往突然、在最坏时机"显现。解决：先用成熟模式（单一范围明确的 prompt、ReAct、Chain-of-Thought、Supervisor），只在被具体诊断出的失败模式驱动时才考虑 exotic 方案（来源：Allen Chan）。

### 7.7 把 AI 当 feature 而非 platform（补研新增）

企业把 AI 当 feature 而非 platform 是共同错误，结果产出 fragile ecosystem（prompts/models/vector stores/agents 各建不同、治理不一致、无法规模化）。三个不同 vector DB、两套不兼容 eval 框架是碎片化团队的典型症状。解决：如云时代 DevOps/Platform Engineering 一样设专职 AI 平台团队，水平工作归平台、垂直工作嵌入产品（见 3.12 标准 1，来源：CTAIO）。五大组织反模式须避免：AI Center of Bottleneck（按"最吵的轮子"排优先级）、Lone Wolf（单一嵌入 AI engineer，离开后两月内功能坏）、Platform for Nobody（华丽基础设施无人能用）、Research Lab（为发论文而非生产影响优化）、Stealth AI Team（暗中堆积模型无监控/成本/安全审查直至事故）（来源：CTAIO）。

### 7.8 仅防 prompt injection 而忽视纵深（补研新增）

把"安全"等同于"防 prompt injection"是反模式。OWASP 2025 已把过度代理权（LLM06 Excessive Agency）、供应链（LLM03 Supply Chain）单列为顶级风险，NIST AI 100-2 建立了覆盖 evasion/poisoning/extraction/backdoor 的对抗性 ML 分类。仅防 prompt injection 无法覆盖权重投毒与依赖篡改，也无法覆盖 agent 自主权滥用导致的真实世界损害（见 3.8，来源：OWASP、NIST）。

## 八、成熟度模型与自检清单

### 8.1 AI-Native 成熟度模型（5 级）

AI-Native Engineering 提出 5 级阶梯：Level1 AI-Curious（个人零散实验，无组织策略）→ Level2 AI-Assisted（采用 AI 编码助手+规范，人主导 AI 辅助）→ Level3 AI-Integrated（AI 嵌入工作流，spec 驱动开发，有指标追踪 AI 贡献）→ Level4 AI-Native（Agent 作为团队成员，建立持续学习闭环，人机协作成常态）→ Level5 AI-Leading（定义行业最佳实践，AI 能力驱动产品战略）。6 个评估维度各配一个判别问题：Strategy / Culture / Process / Tools / Skills / Governance（来源：AI-Native Engineering）。

Jimmy Song 白皮书另提出 M1-M4 四级成熟度：M1 概念验证级（AI 以孤立模块存在）→ M2 早期试用级（场景化初步闭环，形成"感知—决策—反馈"）→ M3 成熟应用级（核心业务深度集成，多模态感知与复杂推理）→ M4 完全成熟级（企业级自适应迭代，AI 成为业务创新核心引擎）。三个避坑原则：拒绝对话框依赖（"对话框是 AI 的降级体验，真正的 AI 原生应是'隐形'的"）、拥抱灰度需求（接受 80% 理解正确率而非追求 100%）、放弃确定性执念（建立"兜底逻辑"和"评估体系"）（来源：Jimmy Song）。

### 8.2 治理导向成熟度框架

MITRE AI Maturity Model：6 支柱（Ethical/Equitable/Responsible Use、Strategy & Resources、Organization、Technology Enablers、Data、Performance & Application），5 个就绪级别 Initial→Adopted→Defined→Managed→Optimized，级别累进（来源：MITRE）。OWASP AIMA（V1.0, 2025-08）：5 域 Strategy/Design/Implementation/Operations/Governance，评估项含构建vs采购决策、伦理对齐、安全、透明度、问责、合规（来源：OWASP，经核验框架结构确认）。补研新增：NIST AI RMF 以 GOVERN/MAP/MEASURE/MANAGE 四函数组织 AI 风险管理，GOVERN 作为横切函数贯穿全程，要求文档化问责、合规理解、第三方风险管理和可信特征内嵌（见 3.11 标准 4，来源：NIST AI RMF）。Google SAIF 六要素把安全纵深扩展到 AI，含定期红队、对抗性威胁命名与 SLSA 供应链（见 3.8 标准 3，来源：Google SAIF）。

### 8.3 自检清单

基于前述十二维标准，提炼为可执行的自检项：

**存在性判据**
- [ ] 移除测试：关闭所有 AI 调用路径后，核心业务流程是否端到端崩溃？
- [ ] 逻辑核心是概率性的（AI 是心脏）还是确定性的（AI 是点缀）？

**架构标准**
- [ ] 模型是否位于核心请求路径上（而非仅作外挂特性）？
- [ ] 是否遵循"模型推理、框架治理"分离原则？
- [ ] 关键业务流程（审批/回滚/审计）是否由确定性工作流引擎保证，而非全靠模型"近似"？

**数据与知识标准**
- [ ] 是否有六步数据飞轮闭环？闭环延迟（交互到模型更新）多长？
- [ ] 是否实施了上下文工程（策展最小高信号 token 集）而非仅提示工程？
- [ ] 是否拥有四层数据壁垒（专有暗数据/刷新速度/行为智能/闭环集成）？

**Agent 系统标准**
- [ ] 是否沿复杂度谱系按需升级，而非一开始就上自主 agent？
- [ ] 每个 agent 是否设置了最大迭代次数等停止条件？
- [ ] ACI 投入是否与整体 prompt 工程同等？
- [ ] 是否有 per-tool 调用上限防止 verifier stall？

**产品设计标准**
- [ ] 交互是否意图驱动（用户指定做什么而非如何做）？
- [ ] 是否有自主度滑块实现渐进式委托？
- [ ] 是否追踪"纠正时间"与"信任校准"指标？
- [ ] 是否避免了默认套壳聊天框？

**业务流程标准**
- [ ] AI 是否在价值交付关键路径上自主执行？
- [ ] 人机协同模式是否按问题域良好定义性选择？
- [ ] 人均收入（ARR/人）是否随 AI 采用而提升？
- [ ] 流程是否从零重设计（而非叠加 AI）？

**评估与可观测性标准**
- [ ] 是否区分 capability eval 与 regression eval？
- [ ] 是否同时追踪 pass@k 与 pass^k？
- [ ] 是否有五层粒度分布式追踪？
- [ ] 生产失败案例是否回流为离线测试集，CI/CD 是否将 AI 质量作为部署门禁？
- [ ] 是否对 prompt injection 做了输入/输出/动作三重筛查？

**成本与经济模型标准（补研新增）**
- [ ] cost-per-query 是否声明四约束 + 六行成本分解？是否同时给中位数与 P95？
- [ ] 推理 TCO 是否用三组件模型（折旧+功耗+维护）？利用率是否在 70% 以上？
- [ ] 是否按年 API 花费分级（5 万/50 万阈值）决策迁移与 fine-tune？
- [ ] ROI 是否做了 ±10pp 自动化敏感性测试？Payback 是否 ≤18 个月？
- [ ] 毛利预期是否从 60-80% 下调到 50-60%？是否按 cost-per-workflow 锚定预算？

**安全与对齐纵深标准（补研新增）**
- [ ] 是否采用 RLAIF/Constitutional AI 或等效对齐方法？
- [ ] 是否针对 evasion/poisoning/extraction/backdoor 四类对抗性 ML 攻击建立检测与防护？
- [ ] 是否有制度化的定期红队演练？
- [ ] agent 工具/API 自主权是否遵循最小权限？是否对"过度代理权"做独立审计？
- [ ] 是否有 AI SBOM 覆盖预训练模型/微调数据/第三方组件/部署基础设施？是否校验模型权重与依赖完整性？

**多模态架构标准（补研新增）**
- [ ] 多轮多模态 agent 是否用 Files API/artifact handle 引用大二进制而非每轮重传 base64？
- [ ] 是否按场景在五种架构模式中选型，而非默认把所有模态塞进最大统一模型？
- [ ] 多模态成本/延迟是否按模态单独预算（视觉 2-5x、文档管线主导成本）？
- [ ] 各模态是否有独立评估面？是否按模态设人工复核门？

**边缘与端侧部署标准（补研新增）**
- [ ] 延迟敏感场景（<100ms）是否将模型下沉到边缘/端侧？
- [ ] 路由层是否轻量（<50ms）且按复杂度/置信度路由？
- [ ] 端侧模型是否用 AWQ/GPTQ 4-bit 量化与 MoE 稀疏激活？是否避免 3B 以下量化到 Q4 以下？
- [ ] 隐私敏感场景是否用联邦学习把训练分布到边缘？是否用 DP/HE 保护参数？
- [ ] 边缘运行时是否 C++ 原生、完全离线、无云依赖？

**合规与监管标准（补研新增）**
- [ ] 系统是否按 EU AI Act 定级？高风险是否满足六项强制义务？
- [ ] 自动决策是否受 GDPR Article 22 约束？是否提供人类干预和可争议权？是否做 DPIA？
- [ ] 处理 PHI 是否签 BAA？是否仅在 HIPAA-eligible 服务中处理？
- [ ] 是否用 NIST AI RMF 四函数组织治理？GOVERN 是否横切且文档化问责与第三方风险？
- [ ] 金融场景是否满足 ECOA adverse action 可解释性？黑箱模型是否被禁用？
- [ ] 跨境数据流是否用充分性决定/SCCs/BCRs/EU-US DPF 合法化？

**组织与团队结构标准（补研新增）**
- [ ] 水平工作（模型/共享基建）是否归平台团队？垂直工作（RAG/agent/prompt）是否嵌入产品团队？
- [ ] stream-aligned 团队是否已从 7-9 人缩到 3-5 人？platform team 是否升为重心？
- [ ] 是否区分 ML Engineer/AI Engineer/ML Platform Engineer/AI PM/AI Safety-Red Team 六类角色？AI Safety 是否独立汇报？
- [ ] eval 所所有权是否从共享起步、成熟后引入专职 MLE？是否"评估评估器"并解耦推理与测试？
- [ ] 是否避免五大组织反模式（Bottleneck/Lone Wolf/Platform for Nobody/Research Lab/Stealth Team）？平台:stream 比例是否在 1:8-10？

## 九、参考资料（真实 URL 列表）

### 定义与本质
- Aicadium — AI-Enabled AI-First AI-Native: Why It Matters：https://aicadium.ai/ai-enabled-vs-ai-first-vs-ai-native-how-do-you-know-which-strategy-to-choose/
- 虎嗅 — 从0到1拆解，什么才是真正的ai原生应用？：https://www.huxiu.com/article/4837957.html
- Jimmy Song — 第 1 章：AI 原生应用及其架构：https://jimmysong.io/zh/book/ai-native-whitepaper/01-ai-native-application/
- Custom AI Studio — What It Actually Means to Be AI Native — A First Principles Approach：https://www.customaistudio.io/articles/ai-native-first-principles/
- Arco — AI-Native vs AI-Enabled: The Structural Divide：https://arcoventure.studio/blog/ai-native-vs-ai-enabled
- ThoughtSpot — What Is AI-Native? Definition, Examples, and Why It Matters：https://www.thoughtspot.com/data-trends/artificial-intelligence/ai-native

### 架构原则与参考架构
- Indium — Building the Future: A Guide to AI-Native Reference Architecture：https://www.indium.tech/blog/ai_native_architecture_guide/
- ittech-pulse — AI-Native Architecture: Designing Systems for Intelligence First：https://ittech-pulse.com/our-tech-insights/ai-native-architecture-designing-systems-for-intelligence-first/
- SAP Architecture Center — AI-Native North Star Architecture / Platform Layer：https://architecture.learning.sap.com/docs/ai-native-north-star-architecture/platform-layer
- Catio — Emerging Architecture Patterns for the AI-Native Enterprise：https://www.catio.tech/blog/emerging-architecture-patterns-for-the-ai-native-enterprise
- Anthropic — Building effective agents：https://www.anthropic.com/engineering/building-effective-agents
- a16z — Emerging Architectures for LLM Applications：https://a16z.com/emerging-architectures-for-llm-applications
- AWS — Machine Learning Lens (Well-Architected Framework)：https://docs.aws.amazon.com/wellarchitected/latest/machine-learning-lens/welcome.html

### 数据层与知识层
- NVIDIA — Data flywheel: What it is and how it works：https://www.nvidia.com/en-us/glossary/data-flywheel/
- NVIDIA Developer — Maximize AI Agent Performance with Data Flywheels Using NVIDIA NeMo Microservices：https://developer.nvidia.com/blog/maximize-ai-agent-performance-with-data-flywheels-using-nvidia-nemo-microservices/
- Anthropic — Effective context engineering for AI agents：https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- arXiv (EMNLP 2024) — Retrieval Augmented Generation or Long-Context LLMs? A Comprehensive Study：https://arxiv.org/abs/2407.16833
- Towards Data Science — Agentic RAG vs Classic RAG: From a Pipeline to a Control Loop：https://towardsdatascience.com/agentic-rag-vs-classic-rag-from-a-pipeline-to-a-control-loop/
- AWS — The role of vector databases in generative AI applications：https://aws.amazon.com/blogs/database/the-role-of-vector-datastores-in-generative-ai-applications/
- aitech365 — The AI Playbook for Building Proprietary Data Moats：https://aitech365.com/insights/featured-articles/the-ai-playbook-for-building-proprietary-data-moats/
- Axel Tombereau — Data Moats & Proprietary Intelligence: Where Differentiation Lives：https://axeltombereau.substack.com/p/data-moats-and-proprietary-intelligence
- Google Developers Blog — Architecting efficient context-aware multi-agent framework for production：https://developers.googleblog.com/architecting-efficient-context-aware-multi-agent-framework-for-production/

### Agent 系统设计
- Anthropic — Building Effective AI Agents：https://www.anthropic.com/research/building-effective-agents
- Azure Architecture Center — AI Agent Orchestration Patterns：https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns
- dev.to — ReAct, Plan-and-Execute, or Reflection? The Three Agent Patterns Every Engineer Needs in 2026：https://dev.to/gabrielanhaia/react-plan-and-execute-or-reflection-the-three-agent-patterns-every-engineer-needs-in-2026-355p
- Redis — AI agent memory: types, architecture & implementation：https://redis.io/blog/ai-agent-memory-stateful-systems/
- Claude — Building agents with the Claude Agent SDK：https://claude.com/blog/building-agents-with-the-claude-agent-sdk
- Microsoft Learn — Multi-agent patterns：https://learn.microsoft.com/en-us/agents/architecture/multi-agent-patterns

### 产品设计范式
- UX Tigers (Jakob Nielsen) — Intent by Discovery: Designing the AI User Experience：https://www.uxtigers.com/post/intent-ux
- Microsoft Learn — Creating a dynamic UX: guidance for generative AI applications：https://learn.microsoft.com/en-us/microsoft-cloud/dev/copilot/isv/ux-guidance
- Mantlr — Designing for AI Agents: 10 UX Patterns (2026)：https://mantlr.com/blog/designing-for-ai-agents-ux-patterns-2026
- Nielsen Norman Group — Designing AI Products and Features: Study Guide：https://www.nngroup.com/articles/designing-ai-study-guide/

### 业务流程重构
- Anthropic — Building effective agents（流程编排模式）：https://www.anthropic.com/engineering/building-effective-agents
- Trackmind — Humans on the Loop vs. In the Loop: Balancing Automation：https://www.trackmind.com/humans-in-the-loop-vs-on-the-loop/
- IBM Community — AI in the Loop vs Human in the Loop: A Technical Analysis：https://community.ibm.com/community/user/blogs/anuj-bahuguna/2025/05/25/ai-in-the-loop-vs-human-in-the-loop
- arXiv — Human-in-the-loop or AI-in-the-loop? Automate or Collaborate?：https://arxiv.org/html/2412.14232v1
- Towards Data Science — Building Human-In-The-Loop Agentic Workflows：https://towardsdatascience.com/building-human-in-the-loop-agentic-workflows/
- Pepper Effect — Decouple Revenue from Headcount: The 5-Step Blueprint：https://peppereffect.com/blog/decouple-revenue-from-headcount
- Beri — 80% Cut Jobs for AI But Got No ROI: Gartner Study：https://www.beri.net/article/80-percent-cut-jobs-for-ai-but-got-no-roi-gartner-study
- Grammarly — Rebuilding Legacy Workflows for AI-Native Work：https://www.grammarly.com/blog/enterprise-ai/rebuild-legacy-workflows/

### 评估与可观测性
- AI-Native Engineering — AI-Native Maturity Model：https://ainative.engineering/resources/maturity-model
- MITRE — AI Maturity Model：https://aimaturitymodel.mitre.org/
- Anthropic — Demystifying evals for AI agents：https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- Towards Data Science — LLM-as-a-Judge: What It Is, Why It Works, and How to Use It：https://towardsdatascience.com/llm-as-a-judge-what-it-is-why-it-works-and-how-to-use-it-to-evaluate-ai-models/
- Langfuse — Documentation：https://langfuse.com/docs
- Maxim AI — Hallucination Evaluation Frameworks: Technical Comparison：https://www.getmaxim.ai/articles/hallucination-evaluation-frameworks-technical-comparison-for-production-ai-systems-2025/
- OWASP — LLM Prompt Injection Prevention Cheat Sheet：https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
- Martin Fowler — Engineering Practices for LLM Application Development：https://martinfowler.com/articles/engineering-practices-llm.html
- applied-llms.org — What We've Learned From A Year of Building with LLMs：https://applied-llms.org/

### 成本与经济模型（补研新增）
- SfaiLabs — Decoding cost-per-query: a defensible unit-economics framework：https://sfailabs.com/guides/decoding-cost-per-query-a-defensible-unit-economics-framework
- arXiv — Beyond Benchmarks: The Economics of AI Inference：https://arxiv.org/html/2510.26136v1
- Ptolemay — LLM Total Cost of Ownership 2025: Build vs Buy Math：https://www.ptolemay.com/post/llm-total-cost-of-ownership
- Acropolium — AI agent unit economics: TCO, ROI, payback：https://acropolium.com/blog/ai-agent-unit-economics/
- Drivetrain — Unit economics for AI SaaS companies: CFO guide：https://www.drivetrain.ai/post/unit-economics-of-ai-saas-companies-cfo-guide-for-managing-token-based-costs-and-margins
- Fortune — MIT report: 95% of generative AI pilots failing：https://fortune.com/2025/08/18/mit-report-95-percent-generative-ai-pilots-at-companies-failing-cfo/
- NVIDIA Developer — LLM Inference Benchmarking: How Much Does Your LLM Inference Cost?：https://developer.nvidia.com/blog/llm-inference-benchmarking-how-much-does-your-llm-inference-cost/

### 安全与对齐纵深（补研新增）
- OWASP — Top 10 for LLM Applications 2025：https://genai.owasp.org/llm-top-10/
- OWASP — GenAI Security Project：https://genai.owasp.org/
- NIST — AI 100-2e2023 Adversarial Machine Learning: Taxonomy and Terminology：https://csrc.nist.gov/pubs/ai/100/2/e2023/final
- Anthropic — Constitutional AI: Harmlessness from AI Feedback：https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback
- Google — Introducing the Secure AI Framework (SAIF)：https://blog.google/technology/safety-security/introducing-googles-secure-ai-framework/

### 多模态架构（补研新增）
- Anthropic — Claude Vision 官方文档：https://platform.claude.com/docs/en/docs/build-with-claude/vision
- Compel Framework — Multimodal Architecture: Vision, Audio, Document：https://www.compelframework.org/articles/multimodal-architecture-vision-audio-document
- 字节跳动 — Seed-Multimodal 研究方向：https://research.doubao.com/zh/direction/multimodal
- Roboflow — Best Multimodal Models of 2026 Rankings: Test & Compare：https://blog.roboflow.com/best-multimodal-models/

### 边缘与端侧部署（补研新增）
- arXiv — Mobile Edge Intelligence for Large Language Models: A Comprehensive Survey (MEI4LLM)：https://arxiv.org/abs/2407.18921
- tianpan — Hybrid Cloud-Edge LLM Inference: When On-Device Models Beat the Cloud：https://tianpan.co/blog/2026-04-10-hybrid-cloud-edge-llm-inference-when-to-run-on-device
- arXiv — On-Device Language Models: A Comprehensive Review：https://arxiv.org/html/2409.00088v1
- PMC — Federated learning in cloud-edge collaborative architecture：https://pmc.ncbi.nlm.nih.gov/articles/PMC9753079/
- NVIDIA — TensorRT-Edge-LLM (GitHub)：https://github.com/NVIDIA/TensorRT-Edge-LLM

### 合规与监管（补研新增）
- 欧盟委员会 — AI Act 监管框架官方页面：https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai
- GDPR 全文（通用数据保护条例）：https://gdpr-info.eu/
- AWS — HIPAA 合规说明：https://aws.amazon.com/compliance/hipaa-compliance/
- NIST AIRC — AI RMF Core 四函数详解：https://airc.nist.gov/airmf-resources/airmf/5-sec-core/
- MoFo 律所 — CFPB AI 信贷决策指南分析：https://www.mofo.com/resources/insights/231002-cfpb-issues-guidance-on-ai-use-in-credit-decisions
- AICPA — SOC 2 主题页：https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2
- 欧盟委员会 — EU-US 数据隐私框架充分性决定：https://commission.europa.eu/document/fa09cbad-dd7d-4684-ae60-be03fcb0fddf_en

### 组织与团队结构（补研新增）
- CTAIO — AI Team Topology: Where LLM Engineers Actually Sit：https://ctaio.dev/en/ai-team-design/
- prommer.net — Team Topologies in the AI Era: How AI Changes Engineering Org Design：https://prommer.net/en/tech/guides/team-topologies-ai-era/

### 从 0 到 1 落地实现路径
- apidots — AI-Native SaaS Development Guide (2026)：https://apidots.com/blog/how-to-build-ai-native-saas-products/
- lushbinary — AI-Native SaaS Architecture 2026: Patterns & Stack Guide：https://lushbinary.com/blog/ai-native-saas-architecture-patterns-developer-guide/

### 案例研究
- Engineer's Codex — How Cursor Indexes Codebases Fast：https://read.engineerscodex.com/p/how-cursor-indexes-codebases-fast
- Cursor 官方博客 — Securely indexing large codebases：https://cursor.com/blog/secure-codebase-indexing
- collabnix — Cursor AI: Deep Dive into Features & Architecture：https://collabnix.com/cursor-ai-deep-dive-technical-architecture-advanced-features-best-practices-2025/
- ziptie — How Perplexity AI Answers Work：https://ziptie.dev/blog/how-perplexity-ai-answers-work/
- gist — A complete architectural teardown of how Perplexity's deep research works：https://gist.github.com/Co-Messi/bfcfb39eede5c6bc2fadd2c04139a136
- mmntm — Devin: The Autonomous Engineer (Or Is It?)：https://www.mmntm.net/articles/devin-deep-dive
- Cognition 官方 — Closing the Agent Loop: Devin Autofixes Review Comments：https://cognition.com/blog/closing-the-agent-loop-devin-autofixes-review-comments
- markaicode — GitHub Copilot System Design: Architecture Behind Sub-200ms Code：https://markaicode.com/architecture/github-copilot-system-design-architecture-948/

### 反模式与陷阱
- CFA Institute — AI Washing: Signs, Symptoms, and Suggested Solutions：https://rpc.cfainstitute.org/research/reports/2025/ai-washing
- InfoQ — 开发者怒扒200家AI公司，73%套壳拿融资：https://www.infoq.cn/article/h5a2hycvqhiji4mfj97i
- Justin Bartak — AI-Native vs. Bolt-On AI: The Foundation Changes Everything：https://justinbartak.ai/blog/ai-native-vs-bolt-on-ai
- Allen Chan — AI Agent Anti-Patterns (Part 1): Architectural Pitfalls：https://achan2013.medium.com/ai-agent-anti-patterns-part-1-architectural-pitfalls-that-break-enterprise-agents-before-they-32d211dded43
- InfoWorld — How to recognize (and avoid) 'AI washing'：https://www.infoworld.com/article/2256854/how-to-recognize-and-avoid-ai-washing.html

---

### 核验说明

本研究包共含 98 条关键声明（初稿 61 条 + 补研 37 条）。

**初稿核验结果（61 条，其中 18 条经对抗式独立核验）**：

- **Confirmed（已确认）**：16 条。这些声明的核心论点在原始来源中逐字或近逐字命中，可作为肯定结论使用。
- **Refuted（已证伪）**：1 条。即"「从 0 到 1 以大模型为核心底座构建」的精确含义……且必须是 clean-sheet 新建而非改造现有架构"——经核验，该声明将 Arco 的 clean-sheet 观点错误归因于 Jimmy Song 源页（Jimmy Song 第 1 章并无此表述，反而称 AI 原生应用"建立在云原生的基础之上"）。本文已将 clean-sheet 论断改为引用 Arco 独立来源，并将 Jimmy Song 已确认的部分（模型为认知基础、Prompt 驱动、11 大要素）单独作为肯定结论使用。
- **Uncertain（存疑）**：1 条。即"多家厂商参考架构高度一致"——Indium 的 6 层架构本身逐字确认，但跨厂商一致性结论无法由单一来源支持，First Line Software 的 6 层模型无法定位核实。本文已将 Indium 架构作为确认参考呈现，跨厂商一致性仅作方向性趋同描述。
- **未核验**：43 条。这些声明在研究包中均有真实 source_url 支撑，但未及独立抓取原始来源做逐字核对，其可信度依赖研究包标注的 credibility 字段（high/medium）。

**补研核验结果（37 条，含 25 条 is_key_claim）**：

补研声明均附真实 source_url 与 credibility 字段（high/medium），但未及全部独立抓取原始来源做逐字核对。其中 credibility=high 的来源包括：SfaiLabs、arXiv（Beyond Benchmarks）、NIST AI 100-2、Anthropic Constitutional AI、Google SAIF、OWASP Top 10 LLM 2025、Claude Vision、Google ADK、字节跳动 Seed-Multimodal、MEI4LLM、tianpan、On-Device Language Models Review、PMC Federated learning、NVIDIA TensorRT-Edge-LLM、欧盟委员会 AI Act、GDPR、AWS HIPAA、NIST AI RMF、MoFo/CFPB。credibility=medium 的来源包括：Ptolemay、Acropolium、Compel Framework、Roboflow、CTAIO、prommer.net。补研中标注 is_key_claim=false 的声明（如 NVIDIA 六步法、OWASP 供应链、OWASP 红队、多模态分词路线、端侧技术栈、TensorRT-Edge-LLM、SOC2、EU-US DPF、context engineering 分布职能、比例与迁移路径）作为补充证据使用，不作为独立肯定结论的核心支撑。

本文遵循的原则：confirmed 声明作为肯定结论；refuted/uncertain 声明仅以"争议/待考证"方式提及，不作肯定结论；未核验声明使用时标注其来源，读者可按需追溯原始 URL 独立核验。补研新增的六个维度（成本与经济模型、安全与对齐纵深、多模态架构、边缘与端侧部署、合规与监管、组织与团队结构）均明确标注为补研新增，其声明可信度依赖来源 credibility 字段。