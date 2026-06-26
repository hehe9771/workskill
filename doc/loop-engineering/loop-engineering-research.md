# Loop Engineering（循环工程）深度研究报告

*生成日期: 2026/06/22 | 来源数量: 8+ | 置信度: 高*

## 执行摘要

**Loop Engineering（循环工程）** 是2026年6月在AI工程圈爆火的新范式，核心思想是**从手动编写Prompt转向设计自主循环（Loop）来驱动AI Agent**。这一概念由OpenClaw创始人Peter Steinberger和Claude Code之父Boris Cherny在2026年6月初同步提出并推广。

**核心转变：** 人不再是Agent的执行者，而是Agent运行系统的设计者。模型变成子程序，人变成Loop的作者。

---

## 一、核心定义与概念

### 1.1 什么是Loop Engineering？

**官方定义：** Loop Engineering是构建驱动AI Agent的系统，而不是构建单个Prompt。

| 模式 | 流程 |
|------|------|
| **传统Prompt模式** | 人 → 写prompt → Agent输出 → 人读结果 → 人写新prompt → … |
| **Loop模式** | 人 → 设计loop → loop自动prompt Agent → loop读输出 → loop判断是否完成 → loop自动重prompt或终止 |

**核心公式：**
```
Loop = Cron + 决策器
```

**Peter Steinberger（OpenClaw创始人）原话：**
> "你不应该再手动prompt coding agent了。你应该设计loop来prompt你的agent。"

**Boris Cherny（Claude Code之父）：**
> "他现在的工作就是写Loop"

### 1.2 概念层级关系

```
Prompt Engineering     →  怎么跟模型说话
Harness Engineering    →  怎么给模型造运行环境
Loop Engineering       →  怎么让运行环境自己跑起来
Factory Model          →  怎么让多个loop协同产出软件
```

**Addy Osmani的定位：**
> "Loop Engineering sits one floor above the harness."

- **Harness** 是静态的基础设施
- **Loop** 是动态的编排层
- Harness解决"Agent能不能跑"，Loop解决"Agent跑不跑、怎么跑、跑到什么时候停"

---

## 二、Loop的六个原语（架构原理）

### 2.1 六原语总览

| 原语 | Loop中的角色 | Claude Code实现 |
|------|-------------|----------------|
| **Automations** | 定时发现与分诊 | `/loop` + `/goal` + hooks + GitHub Actions |
| **Worktrees** | 并行隔离 | `git worktree` + `--worktree` + `isolation: worktree` |
| **Skills** | 固化项目知识 | `SKILL.md`, 隐式匹配 |
| **Connectors** | 连接外部工具 | MCP servers + Plugins |
| **Sub-agents** | 制作与审查分离 | `.claude/agents/` + agent teams |
| **State** | 跨会话记忆 | `AGENTS.md` / progress files / Linear |

### 2.2 详细解析

**Automations（自动化）：Loop的心跳**
- 不是跑一次就结束，而是持续运行、持续发现
- Claude Code: `/loop`按频率重跑，`/goal`跑到条件满足为止，hooks在生命周期特定节点触发
- 关键决策：`/goal`给定可验证的终止条件（如"test/auth全通过且lint clean"），Agent持续工作直到满足

**Worktrees（工作树）：并行不冲突**
- Git worktree让每个Agent有独立的checkout，物理上不可能互相覆盖
- 深层限制：worktrees解决了机械冲突，但review带宽才是真正的上限

**Skills（技能）：意图的固化**
- Skill的本质不是"教Agent做事"，而是**把意图固化到磁盘上**
- Agent每次启动都是失忆的，没有skill，loop每个循环都从零推导项目约定
- 区分：Skill是authoring format，Plugin是分发format

**Connectors（连接器）：Loop触达真实世界**
- MCP连接器让Agent读issue tracker、查数据库、调staging API、发Slack消息
- 没有connector的Agent说"这是修复方案"，有connector的loop自己开PR、关联Linear ticket

**Sub-agents（子代理）：制造者与审查者分离**
- 最有效的结构：一个Agent写代码，一个不同指令（甚至不同模型）的Agent审查
- "制造者不批改自己的作业"

**State（状态）：Agent忘记，仓库不忘记**
- 模型在两次运行之间忘记一切，所以记忆必须在磁盘上，不在上下文里

---

## 三、10+使用场景与具体提示词

### 场景1：自动修复Lint错误（入门Loop）

**说明：** 最基础的loop，自动检测并修复代码风格问题

**具体提示词/命令：**
```bash
# 创建自动lint修复loop
/loop --frequency 1h --command "扫描代码库，检测所有lint错误，自动修复并提交PR"

# 或者使用goal模式
/goal "所有文件lint检查通过且无warning"
```

**预算控制：**
```yaml
max_iterations: 10
max_tokens: $2
timeout: 300s
```

---

### 场景2：CI失败自动修复

**说明：** 扫描CI失败，自动尝试修复，直到CI变绿

**具体提示词/命令：**
```bash
# 持续监控CI状态并自动修复
/goal "CI pipeline全部通过，无失败test"

# 或者使用automation
/loop --frequency 15m --trigger "CI失败" --command "分析失败原因，修复代码，提交并等待CI重新运行"
```

**完整workflow：**
```
1. Automation检测到CI失败
2. 调用$ci-triage skill分析失败原因
3. 派出sub-agent修复代码
4. 提交并触发新的CI run
5. 检查CI状态：
   - 通过 → loop终止
   - 失败 → 重新分析，最多重试5次
```

---

### 场景3：Issue自动分诊与处理

**说明：** 自动扫描新issue，分优先级，派出agent处理

**具体提示词/命令：**
```bash
# 每天早上自动分诊issue
/loop --frequency daily --time 09:00 --command "
1. 扫描所有新issue（使用$triage skill）
2. 按优先级分类：P0/P1/P2
3. 对P0 issue：
   - 派出sub-agent分析
   - 在独立worktree中实现修复
   - 开PR并关联issue
4. 结果写入progress.md
"
```

**真实loop形状（来自Anthropic内部实践）：**
```
1. Automation每天早上在repo上运行  
   → 调用$triage skill，扫描新issue和CI失败  
   → 结果写入progress.md（State）  

2. Loop读取progress.md，找到最高优先级任务  
   → 派出sub-agent A（实现者，用fast model）  
   → 在独立worktree中工作  
   → 完成后派sub-agent B（审查者，用strong model）  
   → 审查通过 → 开PR + 关联Linear ticket（Connector）  
   → 审查不通过 → 反馈写回progress.md，A重新尝试  

3. /goal判断："所有P0 issue已关闭且CI green"  
   → 满足 → loop终止，通知人  
   → 超过迭代上限 → 终止，升级给人  

4. 预算控制：max 15 iterations / $5 / 300s
```

---

### 场景4：代码审查Loop（制造者-审查者分离）

**说明：** 一个agent写代码，另一个agent审查，迭代直到质量达标

**具体提示词/命令：**
```bash
# Evaluator-Optimizer模式
/goal "代码通过所有审查标准：
- 无CRITICAL/HIGH级别安全问题
- 测试覆盖率≥80%
- 代码复杂度在可接受范围
- 通过code-reviewer agent审查"
```

**Workflow详细设计：**
```yaml
loop:
  name: code-review-loop
  steps:
    - name: implementer
      agent: sub-agent-A
      model: claude-sonnet-4-6  # fast model
      task: "实现功能X"
      
    - name: reviewer
      agent: sub-agent-B
      model: claude-opus-4-8  # strong model
      task: |
        审查以下代码变更：
        - 检查安全性（OWASP Top 10）
        - 检查代码质量（复杂度、可读性）
        - 检查测试覆盖率
        - 输出审查意见：APPROVE/REQUEST_CHANGES
        
    - name: decision
      logic: |
        if review == APPROVE:
          开PR，终止loop
        elif review == REQUEST_CHANGES and iterations < 3:
          将反馈传回implementer，继续loop
        else:
          升级给人工审查
```

---

### 场景5：测试用例自动生成

**说明：** 根据代码变更自动生成测试，确保覆盖率达标

**具体提示词/命令：**
```bash
# TDD Loop
/goal "所有新增/修改的函数都有对应的单元测试，且覆盖率≥80%"

# 或者手动触发
/loop --command "
1. 识别最近变更的代码文件
2. 对每个变更的函数：
   - 分析函数签名和逻辑
   - 生成测试用例（正常路径+边界条件+错误路径）
   - 运行测试确保通过
3. 如果覆盖率不足，继续生成测试
"
```

**TDD Loop的ReAct模式：**
```
Thought: 我需要为auth/login.ts的login函数生成测试
Action: 读取login函数代码
Observation: login函数接收email和password，返回JWT token

Thought: 我需要测试正常登录场景
Action: 编写test case: "should return JWT token for valid credentials"
Observation: 测试通过

Thought: 我需要测试错误密码场景
Action: 编写test case: "should throw error for invalid password"
Observation: 测试通过

Thought: 所有场景已覆盖，检查覆盖率
Action: 运行coverage report
Observation: 覆盖率85%，达标
→ Loop终止
```

---

### 场景6：文档自动更新

**说明：** 代码变更后自动更新相关文档

**具体提示词/命令：**
```bash
/loop --trigger "代码合并到main" --command "
1. 检测最近合并的代码变更
2. 识别受影响的文档：
   - API文档
   - README
   - CHANGELOG
   - 架构文档
3. 更新文档内容
4. 提交文档更新PR
"
```

**具体示例：**
```bash
/goal "所有公共API函数都有对应的JSDoc注释，且README中的示例代码与当前实现一致"
```

---

### 场景7：依赖更新与安全扫描

**说明：** 定期检查依赖漏洞并尝试修复

**具体提示词/命令：**
```bash
# 每周自动扫描
/loop --frequency weekly --day monday --command "
1. 运行npm audit / pip-audit / cargo-audit
2. 识别高危漏洞
3. 尝试升级依赖版本
4. 运行测试确保无破坏性变更
5. 提交PR并标记为security
"
```

**预算控制：**
```yaml
max_iterations: 5
max_cost: $3
auto_merge: false  # 安全相关变更需要人工审查
```

---

### 场景8：性能优化循环

**说明：** 持续监控并优化性能瓶颈

**具体提示词/命令：**
```bash
/goal "核心API响应时间P95 < 200ms，数据库查询无N+1问题"

# 或者手动触发性能优化loop
/loop --command "
1. 运行性能分析工具（profiling）
2. 识别慢查询和热点函数
3. 优化方案：
   - 添加索引
   - 优化查询
   - 添加缓存
   - 重构热点代码
4. 运行性能测试验证改进
5. 如果未达标，继续优化
"
```

---

### 场景9：多模块并行开发

**说明：** 多个agent在不同worktree并行工作，由orchestrator协调

**具体提示词/命令：**
```bash
# Orchestrator-Workers模式
/orchestrator "实现用户管理系统" --workers 3

# 详细配置
orchestrator:
  task: "实现用户管理系统"
  decomposition:
    - worker-1: "实现用户注册API" (worktree-A)
    - worker-2: "实现用户登录API" (worktree-B)
    - worker-3: "实现用户权限模型" (worktree-C)
  
  coordination:
    - 每个worker独立工作
    - 完成后由orchestrator合并
    - 解决冲突（如果有）
    - 集成测试
```

**实际提示词示例：**
```
你是orchestrator，负责协调3个worker agent完成用户管理系统。

任务分解：
1. worker-1（在worktree-A中）：实现POST /api/register
2. worker-2（在worktree-B中）：实现POST /api/login
3. worker-3（在worktree-C中）：实现User和Role模型

协调规则：
- 每个worker独立工作，不能看到其他worker的代码
- 完成后提交PR到各自的branch
- 你负责：
  a) 监控进度
  b) 在所有worker完成后，合并代码
  c) 解决合并冲突
  d) 运行集成测试
  e) 如果测试失败，派worker修复

终止条件：所有API可用，集成测试通过
预算：max $10 / 30 iterations
```

---

### 场景10：递归自我改进（高级）

**说明：** Agent帮助训练下一个Agent，实现自我进化

**具体提示词/命令：**
```bash
# 注意：这是高级场景，需要谨慎设计
/loop --command "
1. 分析当前agent的表现日志
2. 识别失败案例和低效模式
3. 生成改进建议：
   - 优化prompt模板
   - 改进skill定义
   - 调整决策逻辑
4. 更新SKILL.md和hooks配置
5. 运行测试验证改进
"
```

**Anthropic内部真实案例：**
> Claude自主优化训练代码，从3x加速提升到52x（2025年5月到2026年4月）

---

### 场景11：自动化PR审查（GitHub Actions集成）

**说明：** 每个PR自动触发审查loop

**具体提示词/命令：**
```yaml
# .github/workflows/claude-review.yml
name: Claude Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - name: Claude Review
        run: |
          claude -p "
          审查这个PR的代码变更：
          1. 检查安全性
          2. 检查代码质量
          3. 检查测试覆盖率
          4. 输出审查意见到PR comment
          "
```

---

### 场景12：日志监控与异常处理

**说明：** 持续监控日志，发现异常自动处理

**具体提示词/命令：**
```bash
# 实时监控
/loop --frequency 5m --command "
1. 读取最近5分钟的app.log
2. 检测异常模式：
   - 错误率突增
   - 响应时间异常
   - 特定错误重复出现
3. 如果发现异常：
   - 分析根因
   - 尝试自动修复（如重启服务、清理缓存）
   - 如果无法修复，发送Slack告警
"
```

**实际使用：**
```bash
tail -200 app.log | claude -p "分析日志，如果发现异常就Slack通知我"
```

---

## 四、最佳实践

### 4.1 终止设计（最关键）

**第一条规则：设计清晰终止行为**（从AutoGPT失败中学到）

```yaml
# 好的终止设计
/goal "test/auth全通过且lint clean"

# 坏的终止设计
/goal "优化代码"  # 太模糊，永远无法终止
```

**终止条件类型：**
1. **可验证目标**：测试通过、覆盖率达标、lint clean
2. **迭代上限**：max 15 iterations
3. **预算上限**：max $5
4. **时间上限**：timeout 300s

### 4.2 预算控制

**Token成本是真实约束：**
- 一个设计不当的loop可以在几小时内烧掉数十美元
- 预算上限不是可选项，是前提

**示例配置：**
```yaml
max_iterations: 15
max_tokens_cost: $5
timeout_seconds: 300
stop_on_budget_exceeded: true
```

### 4.3 自验证机制

**核心原则：制造者不批改自己的作业**

```yaml
# 正确做法
generator:
  model: claude-sonnet-4-6  # fast model
  task: "生成代码"
  
evaluator:
  model: claude-opus-4-8  # strong model, 独立于generator
  task: "评估代码质量"
```

### 4.4 可复用Skills

**把隐性知识编码为SKILL.md：**

```markdown
# SKILL.md: code-review

## 触发条件
当需要审查代码时自动激活

## 审查清单
- [ ] 安全性检查（OWASP Top 10）
- [ ] 代码质量（复杂度<10，函数<50行）
- [ ] 测试覆盖率≥80%
- [ ] 无硬编码密钥
- [ ] 错误处理完整

## 输出格式
APPROVE / REQUEST_CHANGES + 具体意见
```

### 4.5 并行度管理

**Review带宽是真正上限：**

> "编排税"：5个并行Agent，如果每小时只能审查1个PR，其他4个就是浪费

**建议：**
- 从1-2个并行agent开始
- 确保有足够的review带宽
- 监控queue长度和等待时间

### 4.6 可调试性

**每个iteration都需要可追溯：**

```yaml
logging:
  - 每个iteration的完整输入输出
  - 决策树追踪（为什么做这个决策）
  - 状态变更记录
  - 人可读的progress.md
```

---

## 五、挑战与风险

| 风险 | 说明 | 缓解措施 |
|------|------|----------|
| **Token成本失控** | 设计不当的loop可快速烧钱 | 设置硬性预算上限 |
| **质量保证** | "能跑"和"可维护"是两件事 | 使用strong model做review |
| **可调试性** | "为什么做了这个决策"最难回答 | 完整记录每个iteration |
| **编排税** | Review带宽是并行度的真正上限 | 控制并行度，匹配review能力 |
| **失控风险** | 没有终止条件的自主loop是灾难 | 必须设计终止条件 |

---

## 六、真实生产力数据（Anthropic内部证据）

| 指标 | 数值 |
|------|------|
| Claude写的代码占合并总量 | >80% (2026年5月) |
| 工程师日均代码合并量 | 比2024年增长8x |
| 开放式任务成功率 | 76% (2026年5月，半年前26%) |
| Claude自主优化训练代码加速 | 从3x (2025年5月) 到52x (2026年4月) |

**两个拐点：**
1. **2025年初**：Claude从"建议代码"变成"自己跑代码"
2. **2026年初**：模型开始长时间自主工作

---

## 七、如何成为Loop Engineer

### 7.1 思维转变

| 从 | 到 |
|----|-----|
| 我写代码 | 我设计写代码的系统 |
| 我prompt Agent | 我设计prompt Agent的loop |
| 我验证结果 | 我设计验证结果的机制 |
| 我在循环里 | 我在循环外 |

### 7.2 技能栈

1. **编程基础**：Python/TypeScript（loop本身就是程序）
2. **系统设计**：分布式系统、状态管理、故障恢复
3. **LLM理解**：能力边界、失效模式、token经济学
4. **评估设计**：量化Agent输出质量的评估体系
5. **编排能力**：多Agent协同、任务分解、依赖管理
6. **Skills设计**：把隐性知识编码为可复用的SKILL.md

### 7.3 入门路径

1. **从简单loop开始**：自动修复lint错误的loop
2. **加入验证、终止条件、预算控制**
3. **尝试sub-agent编排**：一个写，一个审
4. **构建可复用skill库**
5. **设计完整的自主工作流**

---

## 八、核心提示词模板汇总

### 8.1 基础Loop模板

```bash
# 模板1：简单自动修复
/loop --frequency <频率> --command "<任务描述>"

# 模板2：目标驱动
/goal "<可验证的终止条件>"

# 模板3：触发式
/loop --trigger "<触发条件>" --command "<任务描述>"
```

### 8.2 Evaluator-Optimizer模板

```yaml
loop:
  name: evaluator-optimizer
  generator:
    model: claude-sonnet-4-6
    prompt: |
      实现以下功能：
      <需求描述>
      
      要求：
      - 代码质量高
      - 测试覆盖完整
      - 无安全问题
      
  evaluator:
    model: claude-opus-4-8
    prompt: |
      评估以下代码：
      <代码>
      
      评估标准：
      - 安全性（0-10分）
      - 代码质量（0-10分）
      - 测试覆盖率（0-10分）
      
      输出：APPROVE（总分≥25）或 REQUEST_CHANGES + 改进建议
      
  termination:
    condition: evaluator输出APPROVE
    max_iterations: 3
    max_cost: $5
```

### 8.3 Orchestrator-Workers模板

```yaml
orchestrator:
  prompt: |
    你是orchestrator，负责分解任务并协调worker agents。
    
    任务：<总体任务描述>
    
    分解策略：
    1. 将任务分解为独立子任务
    2. 为每个子任务派出worker
    3. 监控worker进度
    4. 合并结果，解决冲突
    5. 运行集成测试
    
    终止条件：<可验证的目标>
    
workers:
  - id: worker-1
    worktree: worktree-A
    task: <子任务1>
  - id: worker-2
    worktree: worktree-B
    task: <子任务2>
```

### 8.4 ReAct Loop模板

```
Thought: 我需要<目标>
Action: <执行某个操作>
Observation: <观察结果>

Thought: 基于观察，我需要<下一步>
Action: <执行下一个操作>
Observation: <观察结果>

...（循环直到目标达成）

Thought: 目标已达成，终止loop
```

---

## 九、趋势判断

1. **Loop会成为默认开发模式** — 不是选择，而是默认模式的迁移
2. **人从"写代码"变成"写写代码的系统"** — 升级而非消亡
3. **递归自我改进的阴影** — Claude正在帮助训练下一个Claude
4. **Review带宽是新瓶颈** — 编排税是核心挑战

---

## 十、总结

| 要点 | 内容 |
|------|------|
| **定义** | Loop = Cron + 决策器，模型是子程序 |
| **六个原语** | Automations、Worktrees、Skills、Connectors、Sub-agents、State |
| **三个高度** | 手写补全 → 并行Agent → 自主Loop |
| **核心能力** | 终止设计、自验证、预算控制、可复用Skills |
| **真实数据** | Anthropic内部80%+代码由Claude编写，8x产出增长 |
| **最大风险** | token成本失控、审查带宽不足、递归自我改进 |
| **核心判断** | Review带宽是新瓶颈，编排税是核心挑战 |

**核心答案：** 当Agent足够聪明时，人做什么？→ 人设计让Agent自主运行的系统，然后只在系统卡住时介入。你不是司机了，你是调度中心。

---

## 来源

1. daoyuly.cn — 《Loop Engineering 深度综述》(2026-06-14)
2. 51CTO — 《全网爆火的Loop到底是什么？》(2026-06-15)
3. Anthropic — Building Effective Agents
4. Lilian Weng — LLM Powered Autonomous Agents
5. Claude Code Documentation — code.claude.com
6. Anthropic Cookbook — patterns/agents/
7. Peter Steinberger (OpenClaw) — 原始概念提出
8. Boris Cherny (Claude Code) — Loop实践分享
