# Loop Engineering 实战手册：从理论到可复制粘贴的命令

*版本: 3.0 (Theory + Practice) | 2026/06/22*

---

# Part 1: Engineering核心理论（精简版）

## 为什么需要Engineering？

**Loop ≠ 命令，Loop = 工程系统**

```
传统Prompt：人 → prompt → Agent → 结果 → 结束
Loop系统：  人 → 设计loop → loop持续运行 → loop自主决策 → loop自主终止
```

**Engineering解决的核心问题：**
- 状态管理：跨迭代的记忆和一致性
- 故障恢复：优雅降级、人工接管
- 可观测性：追踪决策链、分析失败原因
- 成本控制：防止token消耗失控
- 质量保证：自动化评估，但评估者也会犯错

**核心公式：**
```
Loop Engineering = System Design + Tradeoff Analysis + Failure Mode Prevention + Observability
```

---

## 六个原语的架构设计

| 原语 | 作用 | 工程决策 |
|------|------|----------|
| **Automations** | 何时触发loop | 定时？事件触发？手动？ |
| **Worktrees** | 隔离级别 | 独立checkout？共享？ |
| **Skills** | 知识来源 | SKILL.md？隐式匹配？ |
| **Connectors** | 触达范围 | MCP servers？Plugins？ |
| **Sub-agents** | 内部分工 | 单agent？多agent？ |
| **State** | 记忆方式 | progress.md？structured JSON？ |

**架构模式选择：**

```
任务复杂度？
├─ 简单（lint修复）→ 单Agent串行
├─ 中等（功能实现）→ Evaluator-Optimizer
└─ 复杂（多模块）→ Orchestrator-Workers
```

---

## 关键工程权衡

### 1. 成本 vs 质量

```
迭代1-3：+30分 / $0.30 = 100分/$  ← 高收益
迭代4+：+2分 / $0.10 = 20分/$     ← 收益递减

决策：迭代3次是成本-质量平衡点
```

### 2. 并行度 vs 审查带宽

```
编排税：5个worker并行，但每小时只能审查1个PR
→ 实际并行度 = min(worker数量, 你的审查速度)
```

### 3. 自主性 vs 可控性

```
低风险（lint修复）→ 完全自主
中风险（功能实现）→ 自主执行，PR需人审查
高风险（数据库迁移）→ 自主分析，人确认后执行
```

---

## 失败模式预防

| 失败模式 | 症状 | 预防 |
|---------|------|------|
| **无限循环** | 迭代100+，成本$50+ | 在goal条件中加 "or stop after N turns" |
| **递归爆炸** | agent_count > 10 | 限制嵌套深度：max_depth: 2 |
| **评估者疲劳** | 3次相同反馈 | 停滞检测：quality变化<2分连续3次 |
| **成本超支** | 重试10次 | 断路器：连续3次失败则暂停 |

---

# Part 2: 实战手册（10+场景）

---

## 入门级场景

### 场景1：自动修复Lint错误

**什么时候用：**
- 代码库积累大量lint警告
- 团队没有精力手动修复
- 希望保持代码风格一致性

**Engineering考量：**
- 低风险任务，可以完全自主
- 需要幂等性：同一文件不重复修复
- 成本可控：单次修复~$0.10-0.50

**具体命令：**

```bash
# 方式1：一次性修复
claude -p "扫描整个代码库，修复所有lint错误，提交PR"

# 方式2：定时loop（推荐）
/loop --frequency daily --time 03:00 --command "
1. 运行 npm run lint（或项目的lint命令）
2. 自动修复可修复的错误
3. 对于无法自动修复的错误，记录到lint-report.md
4. 如果有修改，提交PR
5. 如果没有修改，不创建PR
"

# 方式3：goal模式
/goal "所有文件lint检查通过，无warning和error"
```

**Claude Code的实际命令：**

```bash
# /goal命令 - 设置目标，持续工作直到条件满足
/goal <condition>                    # 设置目标
/goal                                # 查看状态
/goal clear                          # 清除目标

# 例子
/goal all tests in test/auth pass and the lint step is clean
/goal npm test exits 0 and git status is clean
/goal 所有P0 issue已关闭 or stop after 20 turns  # 可以加迭代上限

# /loop命令 - 定时循环
/loop [interval] [prompt]            # 定时执行prompt
/loop 5m check if the deployment finished
/loop check the deploy               # Claude自动选择间隔
/loop                                # 使用内置维护prompt

# 停止loop
# 按Esc键停止等待中的loop

# 自定义默认prompt
# 创建 loop.md 文件：
# - .claude/loop.md (项目级)
# - ~/.claude/loop.md (用户级)
```

**loop.md示例（.claude/loop.md）：**
```markdown
Check the `release/next` PR. If CI is red, pull the failing job log,
diagnose, and push a minimal fix. If new review comments have arrived,
address each one and resolve the thread. If everything is green and
quiet, say so in one line.
```

**失败模式：**
- **过度修复**：Agent修改了不该修改的代码
  - 预防：限制修改范围为lint自动修复的工具
  - 调试：检查git diff，确认只修改了lint相关代码
  
- **无限循环**：lint工具报告错误，但Agent无法修复
  - 预防：在goal条件中加 "or stop after 5 turns"
  - 调试：查看哪类错误无法修复，手动处理

**调试方法：**
```bash
# 查看loop状态
/loop status

# 查看决策历史
/loop history

# 手动终止
/loop terminate
```

---

### 场景2：CI失败自动修复

**什么时候用：**
- CI经常因为小问题失败（typo、缺少import）
- 开发者忙于其他任务，无法立即修复
- 希望加速PR合并流程

**Engineering考量：**
- 中风险任务，自主执行但PR需审查
- 需要状态管理：记录失败的CI run和修复尝试
- 需要重试策略：第一次修复可能不成功

**实际命令：**

```bash
# 方式1：goal模式（推荐）
/goal CI pipeline全部通过，无失败test or stop after 3 turns

# 方式2：定时loop
/loop 15m "检查最近的CI run状态，如果有失败的CI，分析失败日志并尝试修复"

# 方式3：针对特定PR
claude -p "这个PR的CI失败了，分析失败原因并修复"

# 方式4：自定义loop.md（.claude/loop.md）
# 内容：
# 检查最近的CI run状态
# 如果有失败的CI：
#   - 分析失败日志
#   - 识别失败原因
#   - 尝试修复
#   - 提交修复并触发新的CI run
# 如果连续3次修复失败，停止并通知人
```

**在goal条件中限制迭代次数：**
```bash
/goal CI pipeline全部通过 or stop after 3 turns  # 最多3次迭代
```

**失败模式：**
- **错误修复**：Agent修复了错误的东西
  - 预防：要求Agent先解释失败原因，再修复
  - 调试：查看Agent的reasoning日志
  
- **CI风暴**：反复提交触发大量CI run
  - 预防：限制提交频率（每小时最多2次）
  - 调试：检查CI队列，暂停loop

**调试方法：**
```bash
# 查看CI失败日志
cat .ci/failure-log.md

# 查看Agent的修复尝试
git log --oneline -5

# 检查loop状态
/loop status
```

---

### 场景3：文档自动更新

**什么时候用：**
- 代码变更后，文档经常过时
- 团队没有精力维护文档
- 希望保持文档与代码同步

**Engineering考量：**
- 低风险任务，可以完全自主
- 需要识别受影响的文档
- 需要避免过度更新（不是每次代码变更都需要更新文档）

**实际命令：**

```bash
# 方式1：goal模式（推荐）
/goal 所有公共API函数都有对应的JSDoc注释，且README中的示例代码与当前实现一致

# 方式2：定时loop
/loop 1d "扫描代码库，识别文档过时的地方，更新过时的文档并提交PR"

# 方式3：自定义loop.md（.claude/loop.md）
# 内容：
# 检测最近合并的代码变更
# 识别受影响的文档：
#   - API变更 → 更新API文档
#   - 配置变更 → 更新README配置部分
#   - 新功能 → 更新CHANGELOG
# 更新文档
# 提交文档更新PR
# 如果没有需要更新的文档，不创建PR

# 然后运行：
/loop 1d
```

**失败模式：**
- **过度更新**：Agent修改了不需要修改的文档
  - 预防：限制修改范围为受影响的文档
  - 调试：检查git diff
  
- **遗漏更新**：Agent没有识别到需要更新的文档
  - 预防：提供明确的文档清单
  - 调试：手动检查是否有过时的文档

**调试方法：**
```bash
# 查看最近合并的代码
git log main --since="7 days ago" --oneline

# 查看文档更新PR
gh pr list --state open --label "documentation"
```

---

## 进阶级场景

### 场景4：Issue自动分诊与处理

**什么时候用：**
- 项目有大量issue需要处理
- 希望自动分优先级并处理P0 issue
- 团队人力有限，需要自动化辅助

**Engineering考量：**
- 中高风险任务，需要人工审查
- 需要状态管理：记录issue处理进度
- 需要sub-agent：分诊agent + 修复agent

**实际命令：**

```bash
# 方式1：goal模式（推荐）
/goal 所有P0 issue已关闭且CI green or stop after 10 turns

# 方式2：定时loop
/loop 1d "扫描所有新issue，按优先级分类，对P0 issue创建修复PR"

# 方式3：手动触发
claude -p "扫描所有新issue，分优先级，对P0 issue创建修复PR"

# 方式4：自定义loop.md（.claude/loop.md）
# 内容：
# 扫描所有新issue
# 按优先级分类：P0/P1/P2
# 对P0 issue：
#   - 分析问题
#   - 在独立worktree中实现修复
#   - 开PR并关联issue
# 对P1 issue：
#   - 添加标签：'needs-triage'
#   - 分配给团队成员
# 结果写入progress.md

# 然后运行：
/loop 1d
```

**在goal条件中限制迭代次数：**
```bash
/goal 所有P0 issue已关闭 or stop after 10 turns  # 最多10次迭代
```

**失败模式：**
- **错误分诊**：Agent将P1 issue标记为P0
  - 预防：提供明确的优先级定义
  - 调试：检查分诊理由
  
- **修复质量差**：Agent快速修复但引入新bug
  - 预防：使用Evaluator-Optimizer模式
  - 调试：检查PR的代码审查评论

**调试方法：**
```bash
# 查看issue处理进度
cat progress.md

# 查看创建的PR
gh pr list --state open --author "claude[bot]"

# 查看loop状态
/loop status
```

---

### 场景5：代码审查Loop（Evaluator-Optimizer）

**什么时候用：**
- 实现新功能后，需要自动审查代码质量
- 希望减少人工review负担
- 代码会被多人使用，质量要求高

**Engineering考量：**
- 制造者-审查者分离：Generator用fast model（成本），Evaluator用strong model（质量）
- 迭代上限：防止无限优化（通常3-5次）
- 成本-质量权衡：每次迭代~$0.50-2.00

**实际命令：**

```bash
# 方式1：goal模式（推荐）
/goal "代码通过所有审查标准：无CRITICAL/HIGH级别安全问题，测试覆盖率≥80%，代码复杂度在可接受范围" or stop after 3 turns

# 方式2：手动触发
claude -p "实现用户登录功能，并使用Evaluator-Optimizer模式确保代码质量"

# 方式3：自定义SKILL.md（.claude/skills/code-review-loop/SKILL.md）
```

**SKILL.md示例（.claude/skills/code-review-loop/SKILL.md）：**
```markdown
---
name: code-review-loop
description: 使用Evaluator-Optimizer模式自动审查代码
---

# Code Review Loop

## 流程
1. Generator实现代码
2. Evaluator审查代码
3. 如果APPROVE → 提交PR
4. 如果REQUEST_CHANGES → 反馈给Generator，重新实现
5. 在goal中使用 "or stop after 3 turns" 限制迭代次数

## 审查标准
- 安全性（OWASP Top 10）
- 代码质量（复杂度<10，函数<50行）
- 测试覆盖率≥80%
- 无硬编码密钥

## 使用方式
/goal 代码通过code-review-loop审查 or stop after 3 turns
```

**失败模式：**
- **评估者疲劳**：Evaluator反复给出相同反馈
  - 预防：检测停滞，连续3次相同反馈则终止
  - 调试：查看Evaluator的反馈历史
  
- **评估者同质化**：Generator和Evaluator相同模型
  - 预防：使用不同模型
  - 调试：检查是否有盲区重叠

**调试方法：**
```bash
# 查看每次迭代的质量评分
cat iteration-history.json

# 查看Evaluator的反馈
cat evaluator-feedback.md

# 检查停滞检测
/loop status | grep stagnation
```

---

### 场景6：测试用例自动生成

**什么时候用：**
- 新增功能缺少测试
- 希望提高测试覆盖率
- 团队没有精力手写测试

**Engineering考量：**
- 中风险任务，测试需要人审查
- 需要识别变更的代码
- 需要生成多种测试场景（正常路径、边界条件、错误路径）

**实际命令：**

```bash
# 方式1：goal模式
/goal 所有新增/修改的函数都有对应的单元测试，且覆盖率≥80% or stop after 5 turns

# 方式2：针对特定文件
claude -p "为src/auth/login.ts生成完整的单元测试，覆盖正常路径、边界条件和错误路径"

# 方式3：定时loop
/loop 7d "识别最近一周变更的代码文件，对每个变更的函数生成测试用例，提交PR"

# 方式4：自定义loop.md（.claude/loop.md）
# 内容：
# 识别最近一周变更的代码文件
# 对每个变更的函数：
#   - 分析函数签名和逻辑
#   - 生成测试用例（正常路径+边界条件+错误路径）
#   - 运行测试确保通过
# 如果覆盖率不足，继续生成测试
# 提交PR

# 然后运行：
/loop 7d
```

**失败模式：**
- **测试质量差**：生成的测试只覆盖happy path
  - 预防：明确要求覆盖边界条件和错误路径
  - 调试：检查测试用例的覆盖范围
  
- **测试不稳定**：生成的测试有时通过有时失败
  - 预防：要求测试幂等性
  - 调试：运行测试多次，检查flaky tests

**调试方法：**
```bash
# 查看覆盖率报告
npm run coverage

# 查看生成的测试
git diff --name-only | grep test

# 检查测试稳定性
for i in {1..5}; do npm test; done
```

---

### 场景7：依赖更新与安全扫描

**什么时候用：**
- 依赖经常有安全漏洞
- 希望自动升级依赖版本
- 团队没有精力手动检查

**Engineering考量：**
- 高风险任务，需要人工审查
- 需要检测破坏性变更
- 需要运行测试确保无回归

**实际命令：**

```bash
# 方式1：goal模式
/goal npm audit报告无高危漏洞 or stop after 5 turns

# 方式2：定时loop
/loop 7d "运行npm audit，识别高危漏洞，尝试升级依赖版本，运行测试，提交PR"

# 方式3：手动触发
claude -p "检查依赖安全漏洞，升级有漏洞的依赖，确保测试通过"

# 方式4：自定义loop.md（.claude/loop.md）
# 内容：
# 运行 npm audit
# 识别高危漏洞
# 尝试升级依赖版本
# 运行测试确保无破坏性变更
# 提交PR并标记为security
# 如果测试失败，回滚并通知人

# 然后运行：
/loop 7d
```

**失败模式：**
- **破坏性升级**：升级依赖后功能失效
  - 预防：运行完整测试套件
  - 调试：检查依赖的CHANGELOG
  
- **测试失败**：升级后测试不通过
  - 预防：先在小范围测试
  - 调试：查看失败的测试，回滚升级

**调试方法：**
```bash
# 查看安全漏洞报告
npm audit

# 查看升级的依赖
git diff package.json

# 查看失败的测试
npm test 2>&1 | grep FAIL
```

---

## 高级场景

### 场景8：多模块并行开发（Orchestrator-Workers）

**什么时候用：**
- 需要实现多个独立模块
- 希望并行加速开发
- 模块之间耦合度低

**Engineering考量：**
- 高复杂度任务，需要orchestrator协调
- 需要worktree隔离，防止冲突
- 需要合并策略，解决冲突

**实际命令：**

```bash
# 方式1：goal模式
/goal 用户管理系统所有API可用，集成测试通过 or stop after 30 turns

# 方式2：手动配置（使用sub-agents）
claude -p "
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
"

# 注意：Claude Code没有/orchestrator命令，需要使用sub-agents或手动协调
```

**失败模式：**
- **合并冲突**：worker修改了相同文件
  - 预防：任务分解时避免重叠
  - 调试：检查冲突文件，手动解决
  
- **集成失败**：单个worker测试通过，合并后失败
  - 预防：合并后运行集成测试
  - 调试：查看失败的集成测试
  
- **协调开销**：orchestrator的token消耗超过worker
  - 预防：限制orchestrator的迭代次数
  - 调试：查看orchestrator的token消耗

**调试方法：**
```bash
# 查看各worker的进度
for wt in worktree-A worktree-B worktree-C; do
  echo "=== $wt ==="
  cd $wt && git log --oneline -3
done

# 查看合并冲突
git status | grep conflict

# 查看orchestrator日志
cat orchestrator-log.md
```

---

### 场景9：性能优化循环

**什么时候用：**
- API响应时间慢
- 数据库查询有N+1问题
- 希望自动识别和优化性能瓶颈

**Engineering考量：**
- 中风险任务，需要性能测试验证
- 需要profiling工具识别瓶颈
- 需要迭代优化，直到达标

**实际命令：**

```bash
# 方式1：goal模式
/goal 核心API响应时间P95 < 200ms，数据库查询无N+1问题 or stop after 5 turns

# 方式2：手动触发
claude -p "运行性能分析工具，识别慢查询和热点函数，优化并验证改进"

# 方式3：定时loop
/loop 7d "运行性能基准测试，识别性能退化的地方，尝试优化，提交PR"

# 方式4：自定义loop.md（.claude/loop.md）
# 内容：
# 运行性能基准测试
# 识别性能退化的地方
# 优化方案：
#   - 添加索引
#   - 优化查询
#   - 添加缓存
#   - 重构热点代码
# 运行性能测试验证改进
# 如果未达标，继续优化
# 提交PR

# 然后运行：
/loop 7d
```

**失败模式：**
- **过度优化**：Agent为了性能牺牲可读性
  - 预防：明确要求保持代码可读性
  - 调试：检查代码复杂度
  
- **性能回归**：优化后其他功能变慢
  - 预防：运行完整性能测试套件
  - 调试：对比优化前后的性能数据

**调试方法：**
```bash
# 查看性能基准测试
npm run benchmark

# 查看profiling结果
cat profiling-report.md

# 查看优化前后的对比
git diff HEAD~1 --stat
```

---

### 场景10：递归自我改进（高级）

**什么时候用：**
- 希望loop自动优化自己的行为
- 有足够的数据分析loop的表现
- 团队有高级工程能力

**Engineering考量：**
- 极高风险任务，需要严格监控
- 需要防止递归失控
- 需要人工审查所有改进

**实际命令：**

```bash
# 方式1：手动触发（推荐）
claude -p "
分析当前agent的表现日志，识别失败案例和低效模式，生成改进建议，
更新SKILL.md和hooks配置，运行测试验证改进，提交PR等待人工审查
"

# 方式2：goal模式（谨慎使用）
/goal agent的成功率从70%提升到85% or stop after 3 turns

# ⚠️ 不推荐：完全自主的自我改进
# /loop "自动分析并优化agent表现"
# 原因：容易失控，难以调试
```

**失败模式：**
- **递归失控**：Agent反复调用自己，消耗大量token
  - 预防：严格限制递归深度
  - 调试：查看agent调用链
  
- **过度优化**：Agent为了指标优化，牺牲实际质量
  - 预防：人工审查所有改进
  - 调试：对比改进前后的实际表现

**调试方法：**
```bash
# 查看agent表现日志
cat agent-performance-log.md

# 查看改进建议
cat improvement-suggestions.md

# 查看调用链
cat agent-call-chain.md
```

---

# Part 3: 快速参考卡片

## 常用命令速查表

```bash
# /goal命令 - 设置目标，持续工作直到条件满足
/goal <condition>                    # 设置目标
/goal                                # 查看状态
/goal clear                          # 清除目标
/goal <condition> or stop after N turns  # 限制迭代次数

# /loop命令 - 定时循环
/loop [interval] [prompt]            # 定时执行prompt
/loop 5m check if the deployment finished
/loop check the deploy               # Claude自动选择间隔
/loop                                # 使用内置维护prompt

# 停止loop
# 按Esc键停止等待中的loop

# 自定义默认prompt
# 创建 loop.md 文件：
# - .claude/loop.md (项目级)
# - ~/.claude/loop.md (用户级)

# 手动触发
claude -p "<任务描述>"
```

## loop.md模板库

### 入门级模板（.claude/loop.md）
```markdown
# Lint修复
运行 npm run lint
自动修复可修复的错误
对于无法自动修复的错误，记录到lint-report.md
如果有修改，提交PR
如果没有修改，不创建PR
```

### 进阶级模板（.claude/loop.md）
```markdown
# 代码审查Loop
1. 实现代码
2. 审查代码质量：
   - 安全性检查
   - 代码质量检查
   - 测试覆盖率检查
3. 如果通过审查，提交PR
4. 如果不通过，根据反馈改进
5. 最多迭代3次（使用 "or stop after 3 turns"）
```

### 高级模板（.claude/loop.md）
```markdown
# 多模块并行开发
1. 分解任务为独立子任务
2. 为每个子任务创建独立worktree
3. 在每个worktree中实现子任务
4. 合并所有worktree
5. 解决合并冲突
6. 运行集成测试
7. 如果测试失败，修复问题
```

## 故障排查清单

### Loop不终止
- [ ] 检查goal条件是否明确
- [ ] 检查是否在goal中添加了 "or stop after N turns"
- [ ] 查看/goal状态：`/goal`
- [ ] 手动清除goal：`/goal clear`
- [ ] 按Esc停止/loop

### 成本超支
- [ ] 查看/goal的token消耗：`/goal`
- [ ] 检查是否有重试风暴
- [ ] 考虑降低迭代次数（在goal条件中加 "or stop after N turns"）
- [ ] 手动终止：`/goal clear` 或 按Esc

### 质量下降
- [ ] 检查评估者是否疲劳（连续3次相同反馈）
- [ ] 检查评估者同质化（使用不同模型）
- [ ] 查看质量趋势
- [ ] 考虑使用stronger model

### 合并冲突
- [ ] 检查任务分解是否合理
- [ ] 检查worktree隔离
- [ ] 手动解决冲突
- [ ] 考虑减少并行度

---

## 总结

**Loop Engineering = Theory + Practice**

- **Theory**：系统工程、架构设计、工程权衡、失败模式
- **Practice**：10+场景、具体命令、配置模板、故障排查

**核心原则：**
1. 从简单loop开始，逐步增加复杂度
2. 每个loop都必须有明确的终止条件
3. 每个loop都必须有成本上限
4. 每个loop都必须有失败恢复策略
5. 每个loop都必须有可观测性

**最后的思考：**
> Loop Engineering不是让Agent更聪明，而是让系统更可靠。
