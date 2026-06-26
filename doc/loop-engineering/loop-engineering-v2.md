# Loop Engineering：从Prompt到自主循环的系统工程

*生成日期: 2026/06/22 | 版本: 2.0 (Engineering Focus)*

---

## 核心论点

**Loop Engineering不是一门"如何使用loop命令"的学问，而是一门系统工程学科。**

它解决的问题不是"怎么让Agent跑起来"，而是：
- 如何设计一个**可靠运行**的自主系统？
- 如何在**成本、质量、可控性**之间做工程权衡？
- 如何**测试、调试、运维**一个会自主决策的系统？
- 如何分析并预防系统的**失败模式**？

**核心公式：**
```
Loop Engineering = System Design + Tradeoff Analysis + Failure Mode Prevention + Observability
```

---

## 一、问题定义：为什么需要"Engineering"？

### 1.1 从"跑一次"到"持续运行"的本质变化

**传统Prompt模式：**
```
人 → 写prompt → Agent执行 → 人检查结果 → 结束
```
- 单次执行，人在loop内
- 失败成本低（重来一次就行）
- 不需要状态管理、故障恢复、可观测性

**Loop模式：**
```
人 → 设计loop → loop持续运行 → loop自主决策 → loop自主终止（或升级给人）
```
- 持续运行，人在loop外
- 失败成本高（可能烧掉几十美元、提交错误代码、进入无限循环）
- **需要完整的系统工程支撑**

### 1.2 Engineering的核心挑战

| 挑战 | 传统Prompt | Loop |
|------|-----------|------|
| **状态管理** | 不需要（单次执行） | 必须（跨迭代状态一致性） |
| **故障恢复** | 重来一次 | 优雅降级、人工接管 |
| **可观测性** | 看输出就行 | 追踪决策链、分析失败原因 |
| **成本控制** | 单次token消耗 | 持续消耗，可能失控 |
| **质量保证** | 人检查 | 自动化评估，但评估者也会犯错 |
| **测试** | 测试Agent输出 | 测试loop本身的决策逻辑 |

**关键洞察：** Loop Engineering的本质是**把一个非确定性的LLM封装成一个确定性的工程系统**。

---

## 二、系统工程维度

### 2.1 状态管理：Loop的记忆

**问题：** LLM在两次运行之间忘记一切，但loop需要跨迭代的记忆。

**工程解法：**
```
State = 磁盘上的持久化文件 + 结构化的状态机
```

**状态设计模式：**

```yaml
# 模式1：Progress File（简单场景）
state:
  file: progress.md
  format: |
    # 当前状态
    - 已完成: [任务1, 任务2]
    - 进行中: [任务3]
    - 待处理: [任务4, 任务5]
    
    # 迭代历史
    - Iteration 1: 完成任务1
    - Iteration 2: 完成任务2
    
# 优点：人可读，易调试
# 缺点：无schema验证，容易格式漂移
```

```yaml
# 模式2：Structured State（复杂场景）
state:
  file: state.json
  schema:
    completed_tasks: string[]
    in_progress: string | null
    pending_tasks: string[]
    iteration_count: number
    last_decision:
      timestamp: string
      reasoning: string
      action: string
      outcome: string
    
# 优点：schema验证，类型安全
# 缺点：需要解析，不如markdown直观
```

**工程权衡：**
- **简单性 vs 可靠性**：markdown易读但易错，JSON严格但笨重
- **粒度选择**：太粗丢失信息，太细增加复杂度
- **版本兼容**：state schema变化时如何迁移？

**最佳实践：**
```
1. 从progress.md开始，验证loop逻辑
2. 当状态复杂度超过50行时，迁移到structured state
3. 为state schema添加版本号，支持迁移
4. 每次状态变更记录reasoning（为什么做这个决策）
```

### 2.2 幂等性：重复执行不产生副作用

**问题：** Loop可能因为故障、超时、人为中断而重新执行某个迭代。如何保证重复执行不会导致重复提交PR、重复修改文件？

**工程解法：**

```yaml
# 模式1：状态检查（推荐）
iteration:
  before_action:
    - check: "PR for this task already exists?"
      if_true: "skip, move to next task"
      if_false: "proceed"
      
# 模式2：幂等操作
actions:
  - type: "create_pr"
    idempotency_key: "task-{task_id}-iter-{iteration}"
    # 如果PR已存在，返回现有PR而不是创建新的
    
# 模式3：事务性操作
actions:
  - type: "modify_files"
    transaction: true
    rollback_on_failure: true
```

**失败案例：**
```
Iteration 3: Agent修复了bug，提交了PR #123
Iteration 3（重试）: Agent不知道PR已存在，又创建了PR #124
结果：重复PR，reviewer困惑，loop状态不一致
```

**工程纪律：**
```
每个action必须回答：
1. 如果这个action重复执行，会发生什么？
2. 如何检测到"已经执行过"？
3. 如何恢复到"未执行"状态？
```

### 2.3 故障恢复：Loop不能假设一切正常

**故障类型分类：**

| 故障类型 | 示例 | 恢复策略 |
|---------|------|----------|
| **瞬时故障** | API超时、网络抖动 | 重试（指数退避） |
| **持久故障** | API密钥失效、配额用尽 | 暂停loop，通知人 |
| **逻辑故障** | Agent陷入死循环、质量持续下降 | 终止loop，升级给人 |
| **资源故障** | 磁盘满、内存不足 | 清理资源，或终止loop |

**故障恢复设计模式：**

```yaml
# 模式1：重试 + 退避
retry_policy:
  max_retries: 3
  backoff:
    type: exponential
    initial_delay: 1s
    max_delay: 30s
    
# 模式2：断路器（Circuit Breaker）
circuit_breaker:
  failure_threshold: 5  # 连续5次失败
  state: CLOSED → OPEN
  recovery_timeout: 5m  # 5分钟后尝试恢复
  on_open: "暂停loop，发送告警"
  
# 模式3：检查点 + 回滚
checkpoint:
  frequency: per_iteration
  state_snapshot: true
  on_failure:
    - rollback_to_last_checkpoint
    - notify_human
    - pause_loop
```

**工程权衡：**
- **自动恢复 vs 人工介入**：瞬时故障自动恢复，逻辑故障必须人工介入
- **恢复成本 vs 重新开始**：回滚可能比重新执行更贵
- **恢复时间 vs 数据一致性**：快速恢复可能牺牲一致性

### 2.4 可观测性：理解Loop在做什么

**问题：** "为什么loop做了这个决策？" — 这是最难回答的问题。

**可观测性三支柱：**

```yaml
# 1. 日志（Logs）
logs:
  level: INFO
  format: structured
  fields:
    - timestamp
    - iteration
    - event_type  # decision, action, state_change, error
    - reasoning   # 为什么做这个决策
    - context     # 决策时的状态快照
    - outcome     # 决策的结果
    
# 示例日志
{
  "timestamp": "2026-06-22T10:30:00Z",
  "iteration": 3,
  "event_type": "decision",
  "reasoning": "测试覆盖率78%，低于目标80%，继续生成测试",
  "context": {
    "completed_tasks": ["task1", "task2"],
    "coverage": 0.78,
    "target_coverage": 0.80
  },
  "outcome": "continue_loop"
}

# 2. 指标（Metrics）
metrics:
  - iteration_count          # 当前迭代次数
  - token_consumed           # 已消耗token
  - cost_usd                 # 已消耗成本
  - quality_score            # 质量评分（来自evaluator）
  - action_success_rate      # action成功率
  - time_per_iteration       # 每次迭代耗时
  
# 3. 追踪（Traces）
traces:
  trace_id: "loop-abc123"
  spans:
    - name: "iteration-3"
      start: "2026-06-22T10:30:00Z"
      end: "2026-06-22T10:35:00Z"
      events:
        - "analyze_state"
        - "generate_code"
        - "run_tests"
        - "evaluate_quality"
        - "decide_next_action"
```

**工程挑战：**
- **日志量**：每次迭代可能产生数千行日志，如何过滤？
- **reasoning质量**：Agent生成的reasoning可能不准确，如何验证？
- **追踪关联**：多个sub-agent并行时，如何关联trace？

---

## 三、架构设计：六个原语的组合模式

### 3.1 不是"六个功能"，而是"六个架构决策"

**原语的本质：**
- **Automations** → 决定loop何时触发
- **Worktrees** → 决定loop的隔离级别
- **Skills** → 决定loop的知识来源
- **Connectors** → 决定loop的触达范围
- **Sub-agents** → 决定loop的内部分工
- **State** → 决定loop的记忆方式

### 3.2 架构模式分类

**模式1：单Agent串行Loop（最简单）**

```
┌─────────────┐
│ Automation  │ → 触发loop
└─────────────┘
      ↓
┌─────────────┐
│   Agent     │ → 执行任务
└─────────────┘
      ↓
┌─────────────┐
│   State     │ → 更新状态
└─────────────┘
      ↓
┌─────────────┐
│  Decision   │ → 继续or终止？
└─────────────┘
      ↓
  [继续] → 回到Agent
  [终止] → 结束
```

**适用场景：** 简单任务（lint修复、文档更新）
**工程复杂度：** 低
**失败风险：** 低（单点故障，易调试）

---

**模式2：Evaluator-Optimizer Loop（制造者-审查者分离）**

```
┌─────────────┐
│  Generator  │ → 生成代码（fast model）
└─────────────┘
      ↓
┌─────────────┐
│  Evaluator  │ → 评估质量（strong model）
└─────────────┘
      ↓
  [APPROVE] → 提交PR
  [REQUEST_CHANGES] → 反馈给Generator
```

**关键架构决策：**
- **模型选择**：Generator用fast model（成本），Evaluator用strong model（质量）
- **评估标准**：如何量化"质量"？（测试覆盖率、代码复杂度、安全评分）
- **迭代上限**：防止无限优化（通常3-5次）

**工程权衡：**
```
成本 vs 质量：
- Generator: claude-sonnet-4-6 ($3/M tokens) → 快但可能粗糙
- Evaluator: claude-opus-4-8 ($15/M tokens) → 慢但严格
- 每次迭代成本：~$0.50-2.00
- 迭代3次的总成本：~$1.50-6.00
- 质量提升：从60分 → 85分（经验值）

问题：值不值得？
- 如果代码会被100人使用 → 值得
- 如果是一次性脚本 → 不值得
```

**失败模式：**
- **评估者疲劳**：Evaluator反复给出相同反馈，Generator无法改进
- **评估者同质化**：Evaluator和Generator使用相同模型，盲区重叠
- **质量震荡**：评分在APPROVE/REQUEST_CHANGES之间反复跳动

**工程解法：**
```yaml
# 检测评估者疲劳
detect_stagnation:
  condition: "last 3 evaluations have same feedback"
  action: "终止loop，升级给人"

# 避免评估者同质化
evaluator:
  model: "different from generator"
  # 如果Generator用Sonnet，Evaluator用Opus
  # 或者使用不同的system prompt
```

---

**模式3：Orchestrator-Workers Loop（并行分工）**

```
┌──────────────────┐
│  Orchestrator    │ → 分解任务，协调workers
└──────────────────┘
         ↓
┌────────┬────────┬────────┐
↓        ↓        ↓        ↓
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│ W1  │ │ W2  │ │ W3  │ │ W4  │
│(WT-A)│ │(WT-B)│ │(WT-C)│ │(WT-D)│
└─────┘ └─────┘ └─────┘ └─────┘
         ↓        ↓        ↓
         └────────┴────────┘
                  ↓
         ┌──────────────────┐
         │  Merge & Test    │
         └──────────────────┘
```

**关键架构决策：**
- **任务分解**：如何拆分成独立子任务？（按模块？按功能？按文件？）
- **并行度**：多少个worker？（受review带宽限制）
- **冲突解决**：worker之间修改了相同文件怎么办？

**工程权衡：**
```
并行度 vs Review带宽（编排税）：

假设：
- 每个worker完成需要30分钟
- 每个PR审查需要1小时
- 你有4个worker并行

实际情况：
- T=0: 4个worker同时开始
- T=30min: 4个worker同时完成，提交4个PR
- T=30min-2.5h: 你逐个审查4个PR（瓶颈！）
- T=2.5h: 所有PR合并

问题：worker在等待审查时闲置，但你无法加快审查速度

结论：
- 并行度 = min(worker数量, 你的审查速度)
- 如果每小时只能审查1个PR，最多2个worker并行
- 否则就是浪费（worker闲置 = 浪费token）
```

**失败模式：**
- **合并冲突**：worker修改了相同文件的相同区域
- **集成失败**：单个worker的测试通过，但合并后失败
- **协调开销**：orchestrator的token消耗超过worker

**工程解法：**
```yaml
# 预防合并冲突
task_decomposition:
  rule: "每个worker修改不同目录"
  # 例如：
  # worker-1: src/auth/*
  # worker-2: src/api/*
  # worker-3: src/ui/*

# 预防集成失败
integration_test:
  after_each_merge: true
  on_failure:
    - identify_conflicting_workers
    - rollback_last_merge
    - retry_with_smaller_batch
```

---

### 3.3 架构选择决策树

```
任务复杂度？
├─ 简单（lint修复、文档更新）→ 模式1：单Agent串行
├─ 中等（功能实现、bug修复）→ 模式2：Evaluator-Optimizer
└─ 复杂（多模块开发、系统重构）→ 模式3：Orchestrator-Workers

质量要求？
├─ 低（一次性脚本）→ 单模型，无evaluator
├─ 中（内部工具）→ Evaluator-Optimizer，迭代2-3次
└─ 高（生产代码）→ Evaluator-Optimizer，迭代3-5次，strong evaluator

成本预算？
├─ 低（<$1）→ 限制迭代次数，用fast model
├─ 中（$1-$10）→ Evaluator-Optimizer，balanced models
└─ 高（>$10）→ Orchestrator-Workers，parallel workers
```

---

## 四、工程权衡深度分析

### 4.1 成本 vs 质量

**核心问题：** 迭代多少次算"足够好"？

**量化分析：**

```
假设任务：实现一个API endpoint

迭代1：
- Generator生成代码（Sonnet，$0.10）
- Evaluator评分：60/100
- 问题：缺少错误处理

迭代2：
- Generator改进（Sonnet，$0.10）
- Evaluator评分：80/100
- 问题：缺少日志

迭代3：
- Generator改进（Sonnet，$0.10）
- Evaluator评分：90/100
- 问题：无

总成本：$0.30
质量提升：60 → 90（+30分）

迭代4（如果继续）：
- Generator改进（Sonnet，$0.10）
- Evaluator评分：92/100
- 问题：minor style issue

总成本：$0.40
质量提升：90 → 92（+2分）

边际收益分析：
- 迭代1-3：+30分 / $0.30 = 100分/$
- 迭代4：+2分 / $0.10 = 20分/$
- 迭代5+：收益递减

结论：迭代3次是成本-质量的平衡点
```

**工程决策：**
```yaml
quality_target: 85  # 不是100，因为边际收益递减
max_iterations: 5   # 硬性上限，防止无限优化
cost_cap: $2.00     # 成本上限，超限终止
```

### 4.2 自主性 vs 可控性

**核心问题：** loop应该多自主？什么时候需要人工介入？

**自主性光谱：**

```
完全手动 ←————————————————————→ 完全自主
   ↓                              ↓
每次都要人确认              人完全不介入
   ↓                              ↓
[低效]                        [危险]

最佳实践：根据任务风险调整自主性
```

**风险分级：**

| 风险级别 | 示例 | 自主性策略 |
|---------|------|-----------|
| **低** | lint修复、文档更新 | 完全自主，自动提交 |
| **中** | 功能实现、bug修复 | 自主执行，但PR需要人审查 |
| **高** | 数据库迁移、安全相关 | 自主分析，但必须人确认后执行 |
| **极高** | 生产环境部署 | 完全手动，loop只提供建议 |

**工程实现：**
```yaml
autonomy_level: medium

actions:
  - type: "modify_code"
    requires_approval: false
    
  - type: "create_pr"
    requires_approval: false
    
  - type: "merge_pr"
    requires_approval: true  # 需要人确认
    
  - type: "deploy_to_production"
    requires_approval: true
    approval_method: slack_notification
```

### 4.3 简单性 vs 灵活性

**核心问题：** loop应该多复杂？

**复杂度成本：**

```
简单loop（单Agent串行）：
- 开发时间：1小时
- 调试难度：低
- 维护成本：低
- 适用场景：80%的任务

复杂loop（Orchestrator-Workers）：
- 开发时间：10小时
- 调试难度：高
- 维护成本：高
- 适用场景：20%的任务

问题：那20%的任务值不值得10小时的开发成本？
```

**工程纪律：**
```
1. 从简单loop开始
2. 只有当简单loop无法满足需求时，才增加复杂度
3. 每次增加复杂度，必须回答：
   - 解决了什么问题？
   - 引入了什么新风险？
   - 调试成本增加了多少？
```

---

## 五、失败模式分析

### 5.1 Loop失控

**失败模式1：无限循环**

```
场景：
/goal "优化代码质量"

问题：
- "优化"没有明确的终止条件
- Evaluator总能找到改进空间
- Loop永远无法达到"足够好"

结果：
- 迭代100次
- 消耗$50
- 代码从80分优化到85分
- 边际收益极低
```

**工程解法：**
```yaml
# 必须有可验证的终止条件
/goal "测试覆盖率≥80% 且 lint检查通过"  # ✓ 明确
/goal "优化代码"  # ✗ 模糊

# 必须有硬性上限
max_iterations: 15
max_cost: $5.00
max_duration: 1h

# 必须有停滞检测
detect_stagnation:
  condition: "quality_score变化 < 2分 连续3次迭代"
  action: "终止loop，通知人"
```

---

**失败模式2：递归爆炸**

```
场景：
Loop A调用Sub-agent B
Sub-agent B又调用Loop C
Loop C又调用Sub-agent D
...

问题：
- 递归深度无限制
- Token消耗指数级增长
- 最终OOM或成本失控

结果：
- 1次任务触发100次sub-agent调用
- 消耗$1000
- 实际只完成了一个简单任务
```

**工程解法：**
```yaml
recursion_limit:
  max_depth: 2  # 最多2层嵌套
  max_total_agents: 10  # 总共最多10个agent
  
monitoring:
  alert_on: "agent_count > 5"
  auto_terminate_on: "agent_count > 10"
```

---

### 5.2 质量下降

**失败模式3：评估者疲劳**

```
场景：
Evaluator反复给出相同反馈：
- 迭代3: "添加错误处理"
- 迭代4: "添加错误处理"（Generator没改）
- 迭代5: "添加错误处理"（Generator还是没改）

问题：
- Generator无法理解或执行反馈
- Evaluator无法检测到"没有改进"
- Loop陷入死循环

结果：
- 达到max_iterations，终止
- 浪费$5
- 任务未完成
```

**工程解法：**
```yaml
detect_stagnation:
  method: "feedback_similarity"
  threshold: 0.9  # 90%相似
  window: 3  # 连续3次
  
action:
  - log_warning: "Evaluator给出重复反馈，Generator可能无法执行"
  - escalate_to_human: true
  - pause_loop: true
```

---

**失败模式4：评估者同质化**

```
场景：
Generator: claude-sonnet-4-6
Evaluator: claude-sonnet-4-6（相同模型）

问题：
- 两个模型有相同的盲区
- Evaluator无法发现Generator没发现的问题
- 质量评估虚高

结果：
- Evaluator评分：95/100
- 人工审查发现：严重安全漏洞
- Evaluator完全没检测到
```

**工程解法：**
```yaml
evaluator:
  model: "different from generator"
  # 如果Generator用Sonnet，Evaluator用Opus
  
  system_prompt: |
    你是一个安全专家。
    你的任务是找到代码中的安全漏洞。
    不要关注代码风格，只关注安全性。
  # 专门化的prompt，避免同质化
```

---

### 5.3 成本超支

**失败模式5：重试风暴**

```
场景：
API调用失败，触发重试
重试策略：指数退避，最多10次

问题：
- 每次重试消耗token
- 10次重试 × $0.50 = $5.00
- 最终API还是失败

结果：
- 浪费$5
- 任务未完成
```

**工程解法：**
```yaml
retry_policy:
  max_retries: 3  # 不是10
  backoff:
    type: exponential
    initial_delay: 1s
    max_delay: 30s
    
  cost_aware: true
  # 如果已经消耗>$2，停止重试
  
  circuit_breaker:
    failure_threshold: 3
    state: OPEN
    recovery_timeout: 5m
```

---

### 5.4 调试困难

**失败模式6：决策链不透明**

```
场景：
Loop做了一个错误的决策（例如删除了错误的文件）

问题：
- 为什么loop做了这个决策？
- 当时的状态是什么？
- Evaluator的评分是多少？
- 有没有备选方案？

结果：
- 无法重现问题
- 无法修复loop逻辑
- 只能猜测原因
```

**工程解法：**
```yaml
observability:
  decision_log:
    format: structured
    fields:
      - timestamp
      - iteration
      - state_snapshot  # 决策时的完整状态
      - reasoning  # Agent给出的理由
      - alternatives  # 考虑过的备选方案
      - chosen_action
      - outcome
      
  replay_capability:
    save_full_context: true
    # 保存完整的prompt和response
    # 可以重放任何一次决策
```

---

## 六、测试Loop本身

### 6.1 为什么需要测试Loop？

**传统测试：** 测试Agent的输出（代码是否正确）
**Loop测试：** 测试Loop的决策逻辑（Loop是否做出了正确的决策）

**类比：**
- 传统测试 = 测试司机的驾驶技术
- Loop测试 = 测试自动驾驶系统的决策算法

### 6.2 测试策略

**测试层级：**

```
1. 单元测试：测试loop的决策函数
2. 集成测试：测试loop的状态转换
3. 端到端测试：测试完整的loop执行
4. 压力测试：测试loop在极端条件下的表现
```

---

**单元测试：测试决策函数**

```python
def test_loop_decision_continue():
    """测试loop在质量不达标时继续迭代"""
    state = State(
        iteration=2,
        quality_score=70,
        target_quality=85,
        max_iterations=5
    )
    
    decision = make_decision(state)
    
    assert decision.action == "continue"
    assert decision.reasoning == "质量70分 < 目标85分，继续迭代"

def test_loop_decision_terminate():
    """测试loop在质量达标时终止"""
    state = State(
        iteration=3,
        quality_score=90,
        target_quality=85,
        max_iterations=5
    )
    
    decision = make_decision(state)
    
    assert decision.action == "terminate"
    assert decision.reasoning == "质量90分 >= 目标85分，任务完成"

def test_loop_decision_max_iterations():
    """测试loop在达到最大迭代次数时终止"""
    state = State(
        iteration=5,
        quality_score=70,
        target_quality=85,
        max_iterations=5
    )
    
    decision = make_decision(state)
    
    assert decision.action == "terminate"
    assert decision.reasoning == "达到最大迭代次数5，强制终止"
```

---

**集成测试：测试状态转换**

```python
def test_state_transition_happy_path():
    """测试loop的正常状态转换"""
    loop = Loop(
        goal="测试覆盖率≥80%",
        max_iterations=5
    )
    
    # 初始状态
    assert loop.state == "running"
    assert loop.iteration == 0
    
    # 迭代1：覆盖率60%
    loop.run_iteration(coverage=0.60)
    assert loop.state == "running"
    assert loop.iteration == 1
    
    # 迭代2：覆盖率75%
    loop.run_iteration(coverage=0.75)
    assert loop.state == "running"
    assert loop.iteration == 2
    
    # 迭代3：覆盖率85%
    loop.run_iteration(coverage=0.85)
    assert loop.state == "completed"
    assert loop.iteration == 3

def test_state_transition_failure():
    """测试loop在API失败时的状态转换"""
    loop = Loop(
        goal="测试覆盖率≥80%",
        max_iterations=5
    )
    
    # 模拟API失败
    with mock_api_failure():
        loop.run_iteration()
        
    assert loop.state == "failed"
    assert loop.error == "API failure after 3 retries"
```

---

**端到端测试：测试完整执行**

```python
def test_e2e_simple_loop():
    """端到端测试：简单的lint修复loop"""
    loop = Loop(
        goal="所有文件lint检查通过",
        max_iterations=3,
        max_cost=1.00
    )
    
    # 准备测试环境
    setup_test_repo(lint_errors=5)
    
    # 运行loop
    result = loop.run()
    
    # 验证结果
    assert result.status == "completed"
    assert result.iterations == 2
    assert result.cost < 1.00
    assert get_lint_errors() == 0

def test_e2e_stagnation_detection():
    """端到端测试：停滞检测"""
    loop = Loop(
        goal="优化代码质量",
        max_iterations=10,
        stagnation_threshold=3
    )
    
    # 模拟质量停滞
    with mock_quality_scores([60, 62, 61, 63]):  # 质量不再提升
        result = loop.run()
    
    # 验证loop检测到停滞并终止
    assert result.status == "terminated"
    assert result.reason == "stagnation_detected"
    assert result.iterations == 4  # 提前终止
```

---

**压力测试：测试极端条件**

```python
def test_stress_high_cost():
    """压力测试：高成本场景"""
    loop = Loop(
        goal="优化代码",
        max_cost=0.50  # 严格成本限制
    )
    
    # 模拟高成本操作
    with mock_high_cost_operations():
        result = loop.run()
    
    # 验证loop在成本超支前终止
    assert result.cost <= 0.50
    assert result.status in ["completed", "cost_limit_reached"]

def test_stress_infinite_loop():
    """压力测试：防止无限循环"""
    loop = Loop(
        goal="永远无法达成的目标",
        max_iterations=100  # 允许很多迭代
    )
    
    # 模拟无法达成的目标
    with mock_impossible_goal():
        result = loop.run()
    
    # 验证loop最终终止（不是无限循环）
    assert result.iterations <= 100
    assert result.status == "terminated"
```

---

## 七、运维Loop

### 7.1 监控

**关键指标：**

```yaml
operational_metrics:
  # 运行状态
  - loop_status: running | completed | failed | terminated
  - current_iteration: number
  - uptime: duration
  
  # 成本
  - token_consumed: number
  - cost_usd: number
  - cost_per_iteration: number
  
  # 质量
  - quality_score: number (0-100)
  - quality_trend: improving | stable | degrading
  
  # 性能
  - time_per_iteration: duration
  - total_duration: duration
  
  # 健康
  - error_count: number
  - retry_count: number
  - stagnation_detected: boolean
```

**告警规则：**

```yaml
alerts:
  - name: "成本超支"
    condition: "cost_usd > budget * 0.8"
    severity: warning
    action: "通知人"
    
  - name: "成本严重超支"
    condition: "cost_usd > budget"
    severity: critical
    action: "终止loop，通知人"
    
  - name: "迭代过多"
    condition: "iteration > max_iterations * 0.8"
    severity: warning
    action: "检查是否停滞"
    
  - name: "质量下降"
    condition: "quality_trend == 'degrading' for 3 iterations"
    severity: warning
    action: "暂停loop，通知人"
    
  - name: "错误率过高"
    condition: "error_count / iteration > 0.5"
    severity: critical
    action: "终止loop，通知人"
```

### 7.2 故障恢复

**故障恢复策略：**

```yaml
recovery_strategies:
  # 瞬时故障
  transient_failure:
    strategy: "retry_with_backoff"
    max_retries: 3
    
  # 持久故障
  persistent_failure:
    strategy: "pause_and_notify"
    action:
      - pause_loop
      - save_state
      - notify_human
      
  # 逻辑故障（停滞、质量下降）
  logical_failure:
    strategy: "terminate_and_escalate"
    action:
      - terminate_loop
      - save_state
      - notify_human
      - provide_debugging_info
      
  # 资源故障（磁盘满、内存不足）
  resource_failure:
    strategy: "cleanup_or_terminate"
    action:
      - try_cleanup
      - if_cleanup_fails: terminate_loop
```

### 7.3 人工接管

**何时需要人工接管？**

```yaml
escalation_triggers:
  - "成本超过预算"
  - "迭代次数超过上限"
  - "质量持续下降"
  - "检测到停滞"
  - "遇到无法自动恢复的故障"
  - "任务超出loop的设计范围"
```

**人工接管接口：**

```bash
# 暂停loop
claude loop pause <loop_id>

# 查看loop状态
claude loop status <loop_id>

# 查看决策历史
claude loop history <loop_id>

# 修改loop目标
claude loop update-goal <loop_id> "新的目标"

# 恢复loop
claude loop resume <loop_id>

# 终止loop
claude loop terminate <loop_id>
```

---

## 八、工程纪律

### 8.1 Loop定义的版本管理

**问题：** Loop定义本身需要迭代，如何管理版本？

**工程解法：**

```yaml
# loop.yaml
version: 1.2.0  # 语义化版本

changelog:
  - version: 1.2.0
    date: 2026-06-22
    changes:
      - "增加停滞检测"
      - "调整Evaluator模型为Opus"
      
  - version: 1.1.0
    date: 2026-06-15
    changes:
      - "增加成本上限"
      
  - version: 1.0.0
    date: 2026-06-01
    changes:
      - "初始版本"

config:
  goal: "测试覆盖率≥80%"
  max_iterations: 5
  max_cost: $2.00
  
  generator:
    model: claude-sonnet-4-6
    
  evaluator:
    model: claude-opus-4-8  # v1.2.0升级
```

### 8.2 Loop的代码审查

**审查清单：**

```markdown
## Loop定义审查

### 终止条件
- [ ] 目标是否可验证？
- [ ] 是否有最大迭代次数？
- [ ] 是否有成本上限？
- [ ] 是否有停滞检测？

### 状态管理
- [ ] 状态是否持久化？
- [ ] 状态转换是否清晰？
- [ ] 是否有状态回滚机制？

### 故障恢复
- [ ] 瞬时故障是否有重试？
- [ ] 持久故障是否有降级？
- [ ] 逻辑故障是否有升级？

### 可观测性
- [ ] 是否有决策日志？
- [ ] 是否有成本指标？
- [ ] 是否有质量指标？

### 成本控制
- [ ] 是否有限制token消耗？
- [ ] 是否有限制迭代次数？
- [ ] 是否有成本告警？

### 安全性
- [ ] 是否有权限控制？
- [ ] 是否有操作审计？
- [ ] 是否有敏感数据保护？
```

---

## 九、总结

### Loop Engineering的核心原则

1. **Loop是工程系统，不是命令** — 需要状态管理、故障恢复、可观测性
2. **工程权衡是核心** — 成本vs质量、并行度vs审查带宽、自主性vs可控性
3. **失败模式必须预防** — 无限循环、递归爆炸、评估者疲劳、成本超支
4. **Loop本身需要测试** — 单元测试、集成测试、端到端测试、压力测试
5. **运维是持续工作** — 监控、告警、故障恢复、人工接管
6. **工程纪律不可少** — 版本管理、代码审查、文档

### Loop Engineer的技能栈

| 技能 | 重要性 | 说明 |
|------|-------|------|
| **系统设计** | 高 | 状态管理、故障恢复、可观测性 |
| **工程权衡** | 高 | 成本vs质量、并行度vs审查带宽 |
| **失败分析** | 高 | 识别和预防失败模式 |
| **测试工程** | 中 | 测试loop的决策逻辑 |
| **运维工程** | 中 | 监控、告警、故障恢复 |
| **LLM理解** | 中 | 能力边界、失效模式 |

### 最后的思考

**Loop Engineering的本质：**
> 把一个非确定性的LLM封装成一个确定性的工程系统

**不是让Agent更聪明，而是让系统更可靠。**

---

## 参考来源

1. daoyuly.cn — 《Loop Engineering 深度综述》(2026-06-14)
2. Peter Steinberger (OpenClaw) — 原始概念提出
3. Boris Cherny (Claude Code) — Loop实践分享
4. Anthropic — Building Effective Agents
5. 系统工程原理 — 状态管理、故障恢复、可观测性
