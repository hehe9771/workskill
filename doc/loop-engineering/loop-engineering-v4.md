# Loop Engineering：自主运行提示词设计手册

*版本: 4.0 (Prompt Design Focus) | 2026/06/22*

---

## 核心论点

**Loop Engineering的本质是设计能够自主运行的提示词系统。**

不是教你怎么用`/loop`命令，而是教你**怎么写提示词**，让Agent能够：
1. 理解任务目标
2. 自主执行任务
3. 自主评估进度
4. 自主决定下一步
5. 自主判断是否完成
6. 自主处理失败

**核心公式：**
```
自主运行的提示词 = 任务定义 + 执行步骤 + 评估标准 + 决策逻辑 + 终止条件 + 失败处理 + 状态管理
```

---

## 一、提示词设计的七个核心要素

### 1.1 任务定义（What）

**垃圾提示词：**
```
修复lint错误
```

**好的提示词：**
```
你的任务是修复代码库中的所有lint错误。

范围：
- 所有 src/ 目录下的 .ts 和 .tsx 文件
- 不包括 node_modules/ 和 dist/

目标状态：
- npm run lint 命令返回 exit code 0
- 无 error 和 warning
```

**关键要素：**
- 明确范围（哪些文件？哪些类型？）
- 明确目标（什么是"完成"？）
- 明确排除（什么不做？）

---

### 1.2 执行步骤（How）

**垃圾提示词：**
```
修复lint错误
```

**好的提示词：**
```
执行步骤：

Step 1: 诊断
- 运行 npm run lint
- 解析输出，提取所有错误和警告
- 按文件分组，统计每个文件的错误数量
- 输出诊断报告到 lint-diagnosis.md

Step 2: 优先级排序
- 按错误严重程度排序：error > warning
- 同级别内，按文件修改频率排序（高频文件优先）
- 生成修复计划到 lint-plan.md

Step 3: 逐个修复
- 对每个文件：
  a. 读取文件内容
  b. 分析错误原因
  c. 应用修复
  d. 运行 npm run lint <file> 验证修复
  e. 如果修复成功，继续下一个文件
  f. 如果修复失败，记录失败原因，跳过该文件

Step 4: 验证
- 运行 npm run lint
- 如果 exit code 0，任务完成
- 如果仍有错误，回到 Step 3 继续修复
```

**关键要素：**
- 分步骤（Step 1, Step 2, ...）
- 每步骤有明确的输入和输出
- 每步骤有验证机制

---

### 1.3 评估标准（How Good）

**垃圾提示词：**
```
修复lint错误
```

**好的提示词：**
```
评估标准：

每次修复后，必须验证：

1. 语法正确性
   - 运行 npm run lint <file>
   - 必须返回 exit code 0
   - 无新的 error 或 warning

2. 功能完整性
   - 修复不能改变代码逻辑
   - 运行相关测试：npm test -- <related-tests>
   - 测试必须全部通过

3. 代码质量
   - 修复后的代码必须符合项目代码规范
   - 不能引入新的反模式
   - 不能降低代码可读性

如果任何一项不满足，必须回滚修复，尝试其他方案。
```

**关键要素：**
- 量化的评估标准（exit code 0、测试通过）
- 多维度的评估（语法、功能、质量）
- 失败的后果（回滚、重试）

---

### 1.4 决策逻辑（If-Then）

**垃圾提示词：**
```
修复lint错误
```

**好的提示词：**
```
决策逻辑：

在每一步，根据当前状态做出决策：

IF 诊断报告显示 0 个错误
THEN 任务完成，输出完成报告

IF 诊断报告显示 < 10 个错误
THEN 逐个修复，每个错误修复后立即验证

IF 诊断报告显示 >= 10 个错误
THEN 按文件分组，优先修复错误最多的文件

IF 某个错误无法自动修复
THEN 记录失败原因，跳过该错误，继续修复其他错误
最后输出无法自动修复的错误清单

IF 修复后引入新的错误
THEN 回滚修复，尝试其他方案
如果尝试 3 次仍失败，标记为"需要人工介入"

IF 修复后测试失败
THEN 回滚修复，记录失败原因
输出测试失败的详细信息
```

**关键要素：**
- IF-THEN结构（清晰的条件-行动对）
- 覆盖所有可能的情况
- 每个决策都有明确的行动

---

### 1.5 终止条件（When to Stop）

**垃圾提示词：**
```
修复lint错误
```

**好的提示词：**
```
终止条件：

任务在以下情况下终止：

成功终止：
- npm run lint 返回 exit code 0
- 无 error 和 warning
- 所有相关测试通过
- 输出完成报告到 lint-completion.md

失败终止：
- 连续 3 次修复尝试失败
- 修复引入新的严重错误
- 测试持续失败
- 输出失败报告到 lint-failure.md

部分成功终止：
- 修复了 80% 以上的错误
- 剩余错误已记录到 lint-remaining.md
- 输出部分成功报告

强制终止：
- 迭代次数超过 10 次
- 消耗 token 超过 $5
- 输出终止报告到 lint-terminated.md
```

**关键要素：**
- 多种终止情况（成功、失败、部分成功、强制）
- 每种情况都有明确的输出
- 强制终止作为安全网

---

### 1.6 失败处理（What If Fails）

**垃圾提示词：**
```
修复lint错误
```

**好的提示词：**
```
失败处理：

当遇到问题时，按以下策略处理：

1. 语法错误
   - 原因：修复引入了语法错误
   - 处理：回滚修复，尝试其他方案
   - 如果尝试 3 次仍失败，标记为"需要人工介入"

2. 测试失败
   - 原因：修复改变了代码逻辑
   - 处理：回滚修复，分析测试失败原因
   - 如果是测试本身有问题，记录但不修复
   - 如果是修复有问题，尝试其他方案

3. 无法理解的错误
   - 原因：错误信息不明确
   - 处理：搜索错误信息，查阅文档
   - 如果无法解决，记录错误信息，跳过该错误

4. 循环依赖
   - 原因：修复 A 引入 B，修复 B 引入 A
   - 处理：检测到循环后，停止修复，输出循环依赖报告

5. 性能问题
   - 原因：修复导致性能下降
   - 处理：回滚修复，尝试优化方案
   - 如果无法优化，标记为"需要人工介入"

所有失败都必须记录到 lint-failures.md，包括：
- 失败时间
- 失败原因
- 尝试的解决方案
- 最终状态
```

**关键要素：**
- 分类处理（不同类型的失败）
- 每种失败都有明确的处理策略
- 所有失败都记录

---

### 1.7 状态管理（Memory）

**垃圾提示词：**
```
修复lint错误
```

**好的提示词：**
```
状态管理：

在整个过程中，维护以下状态文件：

1. lint-diagnosis.md
   - 初始诊断结果
   - 错误清单（按文件分组）
   - 严重程度统计

2. lint-plan.md
   - 修复计划
   - 优先级排序
   - 预计工作量

3. lint-progress.md
   - 当前进度（已修复/总数）
   - 每次修复的记录
   - 失败记录

4. lint-remaining.md
   - 无法自动修复的错误
   - 需要人工介入的问题

5. lint-completion.md 或 lint-failure.md
   - 最终结果
   - 统计数据
   - 建议

每次迭代开始时，先读取 lint-progress.md，了解当前状态。
每次迭代结束后，更新 lint-progress.md。
```

**关键要素：**
- 明确的状态文件
- 每个文件的内容定义
- 状态更新时机

---

## 二、完整的自主运行提示词示例

### 2.1 Lint自动修复（完整版）

```markdown
# Lint自动修复任务

## 任务定义
你的任务是修复代码库中的所有lint错误。

范围：
- 所有 src/ 目录下的 .ts 和 .tsx 文件
- 不包括 node_modules/ 和 dist/

目标状态：
- npm run lint 命令返回 exit code 0
- 无 error 和 warning

## 执行步骤

### Step 1: 诊断
- 运行 npm run lint
- 解析输出，提取所有错误和警告
- 按文件分组，统计每个文件的错误数量
- 输出诊断报告到 lint-diagnosis.md

### Step 2: 优先级排序
- 按错误严重程度排序：error > warning
- 同级别内，按文件修改频率排序（高频文件优先）
- 生成修复计划到 lint-plan.md

### Step 3: 逐个修复
对每个文件：
a. 读取文件内容
b. 分析错误原因
c. 应用修复
d. 运行 npm run lint <file> 验证修复
e. 如果修复成功，继续下一个文件
f. 如果修复失败，记录失败原因，跳过该文件

### Step 4: 验证
- 运行 npm run lint
- 如果 exit code 0，任务完成
- 如果仍有错误，回到 Step 3 继续修复

## 评估标准

每次修复后，必须验证：

1. 语法正确性
   - 运行 npm run lint <file>
   - 必须返回 exit code 0
   - 无新的 error 或 warning

2. 功能完整性
   - 修复不能改变代码逻辑
   - 运行相关测试：npm test -- <related-tests>
   - 测试必须全部通过

3. 代码质量
   - 修复后的代码必须符合项目代码规范
   - 不能引入新的反模式
   - 不能降低代码可读性

如果任何一项不满足，必须回滚修复，尝试其他方案。

## 决策逻辑

在每一步，根据当前状态做出决策：

IF 诊断报告显示 0 个错误
THEN 任务完成，输出完成报告

IF 诊断报告显示 < 10 个错误
THEN 逐个修复，每个错误修复后立即验证

IF 诊断报告显示 >= 10 个错误
THEN 按文件分组，优先修复错误最多的文件

IF 某个错误无法自动修复
THEN 记录失败原因，跳过该错误，继续修复其他错误
最后输出无法自动修复的错误清单

IF 修复后引入新的错误
THEN 回滚修复，尝试其他方案
如果尝试 3 次仍失败，标记为"需要人工介入"

IF 修复后测试失败
THEN 回滚修复，记录失败原因
输出测试失败的详细信息

## 终止条件

任务在以下情况下终止：

成功终止：
- npm run lint 返回 exit code 0
- 无 error 和 warning
- 所有相关测试通过
- 输出完成报告到 lint-completion.md

失败终止：
- 连续 3 次修复尝试失败
- 修复引入新的严重错误
- 测试持续失败
- 输出失败报告到 lint-failure.md

部分成功终止：
- 修复了 80% 以上的错误
- 剩余错误已记录到 lint-remaining.md
- 输出部分成功报告

强制终止：
- 迭代次数超过 10 次
- 消耗 token 超过 $5
- 输出终止报告到 lint-terminated.md

## 失败处理

当遇到问题时，按以下策略处理：

1. 语法错误
   - 原因：修复引入了语法错误
   - 处理：回滚修复，尝试其他方案
   - 如果尝试 3 次仍失败，标记为"需要人工介入"

2. 测试失败
   - 原因：修复改变了代码逻辑
   - 处理：回滚修复，分析测试失败原因
   - 如果是测试本身有问题，记录但不修复
   - 如果是修复有问题，尝试其他方案

3. 无法理解的错误
   - 原因：错误信息不明确
   - 处理：搜索错误信息，查阅文档
   - 如果无法解决，记录错误信息，跳过该错误

4. 循环依赖
   - 原因：修复 A 引入 B，修复 B 引入 A
   - 处理：检测到循环后，停止修复，输出循环依赖报告

5. 性能问题
   - 原因：修复导致性能下降
   - 处理：回滚修复，尝试优化方案
   - 如果无法优化，标记为"需要人工介入"

所有失败都必须记录到 lint-failures.md，包括：
- 失败时间
- 失败原因
- 尝试的解决方案
- 最终状态

## 状态管理

在整个过程中，维护以下状态文件：

1. lint-diagnosis.md
   - 初始诊断结果
   - 错误清单（按文件分组）
   - 严重程度统计

2. lint-plan.md
   - 修复计划
   - 优先级排序
   - 预计工作量

3. lint-progress.md
   - 当前进度（已修复/总数）
   - 每次修复的记录
   - 失败记录

4. lint-remaining.md
   - 无法自动修复的错误
   - 需要人工介入的问题

5. lint-completion.md 或 lint-failure.md
   - 最终结果
   - 统计数据
   - 建议

每次迭代开始时，先读取 lint-progress.md，了解当前状态。
每次迭代结束后，更新 lint-progress.md。

## 使用方式

/goal npm run lint 返回 exit code 0 且无 error 和 warning or stop after 10 turns
```

---

### 2.2 CI失败自动修复

**什么时候用：**
- PR的CI挂了，需要快速修复
- 夜间构建失败，需要自动修复
- 希望减少开发者等待CI修复的时间

**完整提示词：**

```markdown
# CI失败自动修复任务

## 任务定义
你的任务是分析并修复当前CI pipeline的失败。

范围：
- 仅修复导致CI失败的代码问题
- 不修改测试文件（除非测试本身有bug）
- 不做功能变更

目标状态：
- CI pipeline所有步骤通过（build、lint、test、type-check）
- 不引入新的失败

## 执行步骤

### Step 1: 收集失败信息
- 运行 CI 中失败的命令（如 npm run build、npm test 等）
- 捕获完整的错误输出
- 识别失败的步骤和具体错误信息
- 将错误信息写入 ci-failure-log.md

### Step 2: 分析根因
- 分类错误类型：
  a. 编译错误（类型错误、语法错误、import缺失）
  b. 测试失败（断言失败、超时、mock问题）
  c. Lint错误（代码风格、未使用变量）
  d. 类型检查错误（TypeScript类型不匹配）
- 对每类错误，定位到具体的文件和行号
- 将分析结果写入 ci-analysis.md

### Step 3: 修复
按优先级修复：编译错误 > 类型错误 > 测试失败 > lint错误

对每个修复：
a. 修改代码
b. 运行对应的验证命令（如 tsc --noEmit、npm test -- <file>）
c. 如果验证通过，继续下一个
d. 如果验证失败，回滚并尝试其他方案

### Step 4: 全量验证
- 运行完整的 CI 命令序列：
  a. npm run build
  b. npm run lint
  c. npm run type-check
  d. npm test
- 所有命令必须返回 exit code 0

## 评估标准

1. 编译通过
   - npm run build 返回 exit code 0
   
2. 测试通过
   - npm test 返回 exit code 0
   - 测试覆盖率不低于修复前

3. 无回归
   - git diff --stat 显示修改范围最小化
   - 不修改不相关的文件

## 决策逻辑

IF CI失败原因是编译错误
THEN 优先修复编译错误，修复后运行 npm run build 验证

IF CI失败原因是测试失败
THEN 分析测试失败原因：
  IF 是代码bug → 修复代码
  IF 是测试本身的问题（如过时的mock） → 修复测试
  IF 是环境问题（如网络超时） → 记录，跳过，通知人

IF CI失败原因是lint错误
THEN 自动修复lint错误，修复后运行 npm run lint 验证

IF 修复后引入了新的失败
THEN 回滚修复，尝试其他方案
如果尝试3次仍失败，停止并输出详细报告

IF 所有错误都已修复
THEN 运行完整CI验证，通过后提交

## 终止条件

成功终止：
- 所有CI步骤通过
- 提交修复代码
- 输出修复报告到 ci-fix-report.md

失败终止：
- 连续3次修复尝试失败
- 修复引入了更严重的问题
- 无法确定失败原因
- 输出失败报告到 ci-fix-failure.md

## 失败处理

1. 编译错误无法修复
   - 分析：可能是架构问题，不是简单修复能解决的
   - 处理：记录详细分析，通知人

2. 测试反复失败
   - 分析：可能是flaky test或环境问题
   - 处理：运行3次，如果2次以上通过，标记为flaky test
   - 如果 consistently 失败，记录详细分析

3. 修复引入了新bug
   - 处理：git checkout 回滚，尝试不同方案
   - 记录每次尝试的方案和结果

## 状态管理

维护以下文件：
1. ci-failure-log.md - 原始错误信息
2. ci-analysis.md - 根因分析
3. ci-fix-progress.md - 修复进度
4. ci-fix-report.md - 最终报告（成功或失败）
```

**直接复制使用的命令：**

```bash
# 方式1：goal模式（推荐）
/goal CI所有步骤通过（build、lint、type-check、test全部exit code 0）or stop after 5 turns

# 方式2：先分析再修复（分两步）
claude -p "分析当前CI失败的原因，输出分析报告到 ci-analysis.md"
# 看完报告后：
claude -p "根据 ci-analysis.md 的分析，修复CI失败，修复后运行完整CI验证"

# 方式3：放在 .claude/loop.md 中持续监控
# .claude/loop.md 内容：
# 检查CI状态。如果CI失败，分析原因并修复。
# 修复后运行完整CI验证。如果修复失败，记录原因。
# 如果CI已通过，报告状态。
/loop 15m
```

---

### 2.3 代码审查Loop

**什么时候用：**
- 写完代码后需要自动审查质量
- 希望从安全性、性能、可读性多维度审查
- 审查不通过自动迭代改进

**完整提示词：**

```markdown
# 代码审查Loop任务

## 任务定义
你的任务是审查最近变更的代码，发现问题并修复。

范围：
- git diff main...HEAD 中的所有变更
- 只审查变更的代码，不审查未变更的代码

目标状态：
- 代码通过所有审查维度（安全、质量、性能、测试）
- 每个维度的评分 >= 8/10
- 无 CRITICAL 级别的问题

## 执行步骤

### Step 1: 获取变更
- 运行 git diff main...HEAD --name-only 获取变更文件列表
- 运行 git diff main...HEAD 获取具体变更内容
- 读取每个变更文件的完整上下文（不仅是diff，还要读取完整文件）

### Step 2: 多维度审查
对每个变更文件，从以下维度审查：

a. 安全性（0-10分）
   - 是否有硬编码的密钥/密码/token
   - 是否有SQL注入风险（字符串拼接SQL）
   - 是否有XSS风险（未转义的用户输入）
   - 是否有路径遍历风险
   - 是否有不安全的反序列化

b. 代码质量（0-10分）
   - 函数是否小于50行
   - 是否有深层嵌套（>4层）
   - 命名是否清晰
   - 是否有重复代码
   - 是否符合项目约定（检查 CLAUDE.md）

c. 性能（0-10分）
   - 是否有N+1查询
   - 是否有不必要的全表扫描
   - 是否有内存泄漏风险
   - 是否有可以缓存的重复计算

d. 测试（0-10分）
   - 变更的代码是否有对应测试
   - 测试是否覆盖了正常路径和异常路径
   - 测试是否可靠（无flaky test）

### Step 3: 生成审查报告
将审查结果写入 code-review-report.md：
- 每个维度的评分
- 发现的具体问题（文件、行号、描述、严重程度）
- 改进建议

### Step 4: 修复问题
按严重程度修复：CRITICAL > HIGH > MEDIUM
- 对每个问题，应用修复
- 修复后重新评估对应维度
- 更新审查报告

### Step 5: 最终验证
- 重新运行完整审查
- 如果所有维度 >= 8 且无 CRITICAL，任务完成
- 如果仍有问题，回到 Step 4

## 评估标准

1. 安全性 >= 8/10 且无 CRITICAL
2. 代码质量 >= 8/10
3. 性能 >= 7/10
4. 测试覆盖 >= 8/10

如果任何维度不达标，必须修复后重新评估。

## 决策逻辑

IF 发现 CRITICAL 安全问题
THEN 立即修复，不继续审查其他问题

IF 发现 HARDcoded 密钥
THEN 替换为环境变量，记录到 .env.example

IF 发现 N+1 查询
THEN 改为 JOIN 或批量查询

IF 发现缺少测试
THEN 生成对应的测试用例

IF 所有维度评分 >= 8 且无 CRITICAL
THEN 任务完成，输出最终审查报告

IF 迭代3次后仍有 CRITICAL 问题
THEN 停止，输出详细报告，标记需要人工介入

## 终止条件

成功终止：
- 所有维度评分 >= 8
- 无 CRITICAL 问题
- 输出最终审查报告到 code-review-report.md

失败终止：
- 迭代3次后仍有 CRITICAL 问题
- 修复引入了新的问题
- 输出失败报告

## 失败处理

1. 修复引入新问题
   - 回滚修复
   - 尝试更保守的方案
   - 记录尝试历史

2. 无法确定是否安全
   - 标记为"需要人工审查"
   - 不强行修复

3. 审查标准冲突
   - 安全性优先于性能
   - 性能优先于代码风格

## 状态管理

1. code-review-report.md - 审查报告（每次迭代更新）
2. review-fix-history.md - 修复历史记录
```

**直接复制使用的命令：**

```bash
# 方式1：goal模式（推荐）
/goal 代码审查所有维度（安全性、代码质量、性能、测试）评分>=8且无CRITICAL问题，审查报告在 code-review-report.md 中 or stop after 3 turns

# 方式2：手动触发
claude -p "审查 git diff main...HEAD 的所有变更，从安全性、代码质量、性能、测试四个维度打分，发现问题直接修复，输出审查报告到 code-review-report.md"

# 方式3：作为PR审查skill
# 保存为 .claude/skills/review-pr/SKILL.md，然后使用 /review-pr
```

---

### 2.4 测试用例自动生成

**什么时候用：**
- 新增功能缺少测试
- 希望提高测试覆盖率到80%以上
- 需要生成边界条件和异常路径的测试

**完整提示词：**

```markdown
# 测试用例自动生成任务

## 任务定义
你的任务是为变更的代码生成完整的单元测试。

范围：
- src/ 目录下所有变更的 .ts 文件
- 不包括 .test.ts、.spec.ts（已有测试文件）
- 不包括 utils/、helpers/（可选，根据需要调整）

目标状态：
- 每个导出函数至少有3个测试用例（正常、边界、异常）
- 测试覆盖率 >= 80%
- 所有测试通过

## 执行步骤

### Step 1: 识别需要测试的代码
- 运行 git diff main...HEAD --name-only 获取变更文件
- 过滤出 src/ 下的 .ts 文件（排除测试文件）
- 对每个文件，提取所有导出的函数/类/方法
- 检查是否已有对应测试文件
- 输出需要测试的函数清单到 test-plan.md

### Step 2: 分析每个函数
对每个需要测试的函数：
- 读取函数代码和类型定义
- 识别：
  a. 输入参数（类型、是否可选、默认值）
  b. 返回值（类型）
  c. 副作用（数据库操作、API调用、文件操作）
  d. 可能的异常路径（参数无效、外部服务失败）

### Step 3: 生成测试用例
对每个函数，生成以下测试：

a. 正常路径（Happy Path）
   - 标准输入，预期输出
   - 至少1个测试

b. 边界条件（Edge Cases）
   - 空值（null、undefined、空字符串、空数组）
   - 极值（最大数、最小数、空字符串、超长字符串）
   - 特殊值（特殊字符、Unicode、超大数字）
   - 至少2个测试

c. 异常路径（Error Cases）
   - 无效参数类型
   - 缺少必填参数
   - 外部依赖失败（mock失败场景）
   - 至少1个测试

### Step 4: 编写测试代码
- 使用项目现有的测试框架（检查 package.json 中的 jest/vitest/mocha）
- 使用项目现有的 mock 方式（检查已有测试文件）
- 测试文件放在对应源文件旁边：src/foo.ts → src/foo.test.ts
- 命名规范：describe('函数名') + it('应该...')

### Step 5: 运行并验证
- 运行新生成的测试：npm test -- <test-file>
- 如果测试失败：
  IF 是测试代码写错了 → 修复测试代码
  IF 是源代码有bug → 记录bug，不修复，跳过该测试
- 运行覆盖率：npm run coverage -- --collectCoverageFrom='<source-file>'
- 如果覆盖率 < 80%，补充测试用例

## 评估标准

1. 测试通过
   - 所有测试 green
   - 无 flaky test（运行3次都通过）

2. 覆盖率 >= 80%
   - 行覆盖率 >= 80%
   - 分支覆盖率 >= 70%

3. 测试质量
   - 每个测试只测一件事
   - 测试名称清晰描述预期行为
   - 无重复测试

## 决策逻辑

IF 函数有外部依赖（数据库、API、文件系统）
THEN 使用 mock，不真实调用

IF 函数是纯函数（无副作用）
THEN 不需要 mock，直接测试输入输出

IF 已有测试文件
THEN 在已有文件中追加新测试，不覆盖已有测试

IF 测试运行失败
THEN 分析失败原因：
  IF 是测试代码问题 → 修复测试
  IF 是源代码bug → 记录到 test-bugs.md，跳过该测试
  IF 是环境问题 → 跳过，记录原因

IF 覆盖率已达80%
THEN 停止为该文件生成测试

## 终止条件

成功终止：
- 所有变更函数都有测试
- 覆盖率 >= 80%
- 所有测试通过
- 输出测试报告到 test-report.md

失败终止：
- 某些函数无法生成测试（如复杂的集成逻辑）
- 记录原因到 test-report.md

## 失败处理

1. 测试无法mock外部依赖
   - 尝试不同的mock策略
   - 如果无法mock，标记为"需要集成测试"

2. 覆盖率无法达到80%
   - 分析哪些分支无法覆盖
   - 如果是不可达代码，记录原因
   - 如果是测试难以覆盖，标记为"需要手动测试"

## 状态管理

1. test-plan.md - 需要测试的函数清单
2. test-progress.md - 生成进度
3. test-bugs.md - 发现的源代码bug
4. test-report.md - 最终报告
```

**直接复制使用的命令：**

```bash
# 方式1：goal模式（推荐）
/goal 所有变更的导出函数都有单元测试且覆盖率>=80%且所有测试通过 or stop after 5 turns

# 方式2：针对特定文件
claude -p "为 src/auth/login.ts 生成完整的单元测试，包括正常路径、边界条件和异常路径，使用项目现有的测试框架和mock方式，运行测试确保全部通过，运行覆盖率确保>=80%"

# 方式3：定时loop（每周检查测试覆盖率）
# .claude/loop.md 内容：
# 检查最近一周变更的源文件，为缺少测试或覆盖率不足80%的文件生成测试。
# 运行测试确保通过。输出报告到 test-report.md。
/loop 7d
```

---

### 2.5 Bug修复

**什么时候用：**
- 收到bug报告，需要定位和修复
- 有错误日志，需要分析根因并修复
- 有复现步骤，需要修复并验证

**完整提示词：**

```markdown
# Bug修复任务

## 任务定义
你的任务是定位、修复并验证一个bug。

Bug描述：
<粘贴bug描述、错误日志、复现步骤>

目标状态：
- bug的根因已定位
- bug已修复
- 复现步骤不再触发bug
- 不引入新的bug（回归测试通过）

## 执行步骤

### Step 1: 复现bug
- 根据bug描述，尝试复现问题
- 如果是API bug，用curl/httpie发送请求
- 如果是UI bug，分析相关代码路径
- 如果是构建bug，运行构建命令
- 记录复现结果到 bug-reproduction.md

### Step 2: 定位根因
- 从错误信息出发，追踪调用链
- 读取相关源代码
- 分析可能的原因（至少列出3个假设）
- 对每个假设，寻找证据支持或反驳
- 确定根因后，写入 bug-analysis.md

### Step 3: 设计修复方案
- 提出至少2个修复方案
- 对每个方案评估：
  a. 是否真正修复了根因（不是打补丁）
  b. 修改范围是否最小化
  c. 是否有副作用
  d. 是否影响其他功能
- 选择最优方案，记录理由

### Step 4: 实施修复
- 应用修复方案
- 修改范围最小化（只改必须改的代码）
- 不修改不相关的代码

### Step 5: 验证修复
- 运行原始复现步骤，确认bug不再出现
- 运行相关测试，确认无回归
- 运行全量测试，确认无其他回归
- 如果有边界条件，也验证边界条件

### Step 6: 生成回归测试
- 为这个bug编写一个回归测试
- 测试应该在修复前失败，修复后通过
- 将测试加入测试套件

## 评估标准

1. Bug已修复
   - 原始复现步骤不再触发bug
   
2. 无回归
   - 所有已有测试通过
   - 修改范围最小化

3. 有回归测试
   - 新增至少1个测试覆盖这个bug

## 决策逻辑

IF 无法复现bug
THEN 要求更多信息（环境、版本、日志）
停止修复，输出信息需求清单

IF 根因不明确
THEN 列出所有假设，对每个假设收集证据
不猜测，不盲目修复

IF 修复方案有多个
THEN 选择"修复根因"而非"绕过症状"的方案
选择修改范围最小的方案

IF 修复引入了新的测试失败
THEN 分析是新bug还是已有测试的问题
IF 是新bug → 回滚，换方案
IF 是已有测试的问题 → 分析是否测试需要更新

IF bug涉及安全漏洞
THEN 优先修复，评估影响范围
检查是否有其他类似漏洞

## 终止条件

成功终止：
- bug已修复
- 复现步骤不再触发
- 回归测试通过
- 新增回归测试
- 输出修复报告到 bug-fix-report.md

失败终止：
- 无法复现bug
- 无法定位根因
- 修复引入更严重的问题
- 输出失败报告到 bug-fix-failure.md

## 失败处理

1. 无法复现
   - 记录已有的信息
   - 列出需要补充的信息
   - 通知人

2. 修复引入回归
   - 回滚修复
   - 分析为什么引入回归
   - 尝试更保守的方案

3. 根因太深（框架级别）
   - 不强行修复
   - 记录分析结果
   - 建议workaround
   - 通知人

## 状态管理

1. bug-reproduction.md - 复现记录
2. bug-analysis.md - 根因分析
3. bug-fix-report.md - 修复报告
```

**直接复制使用的命令：**

```bash
# 方式1：传入bug描述（推荐）
claude -p "
bug描述：用户登录时，如果密码包含特殊字符<>&，会报500错误。
复现步骤：
1. POST /api/login，body: {email: 'test@test.com', password: 'pass<word>'}
2. 返回500 Internal Server Error
预期：返回401或200

分析根因，修复bug，编写回归测试，运行所有测试确保无回归。
输出修复报告到 bug-fix-report.md
"

# 方式2：从错误日志修复
claude -p "
分析以下错误日志，定位根因并修复：

Error: Cannot read property 'id' of undefined
  at UserService.getProfile (src/services/user.ts:42:18)
  at ProfileController.handle (src/controllers/profile.ts:15:30)

修复后编写回归测试，确保所有测试通过。
"

# 方式3：goal模式（复杂bug需要多轮迭代）
/goal bug已修复（POST /api/login 对特殊字符密码不再报500），回归测试通过，修复报告在 bug-fix-report.md 中 or stop after 5 turns
```

---

### 2.6 文档自动同步

**什么时候用：**
- 代码变更后文档过时
- API改了但README没更新
- 希望文档和代码始终保持一致

**完整提示词：**

```markdown
# 文档自动同步任务

## 任务定义
你的任务是检查代码变更后，文档是否需要同步更新，并执行更新。

范围：
- 对比 git diff main...HEAD 的代码变更
- 检查以下文档是否需要同步：
  a. README.md（项目说明、安装、使用方式）
  b. CHANGELOG.md（变更记录）
  c. API文档（src/中的JSDoc/TSDoc注释）
  d. 配置文件说明（.env.example、config/）

目标状态：
- README中的代码示例可以运行
- README中的配置说明和实际配置一致
- API文档和代码实现一致
- CHANGELOG包含本次变更

## 执行步骤

### Step 1: 分析代码变更
- 运行 git diff main...HEAD --stat 查看变更概览
- 运行 git log main...HEAD --oneline 查看commit历史
- 分类变更类型：
  a. 新功能 → 更新README功能列表、CHANGELOG
  b. API变更 → 更新API文档
  c. 配置变更 → 更新.env.example和说明
  d. Bug修复 → 更新CHANGELOG
  e. 重构 → 通常不需要更新文档

### Step 2: 检查README
- 读取 README.md
- 检查：
  a. 安装步骤是否还能运行
  b. 使用示例中的API是否还存在
  c. 配置说明是否和.env.example一致
  d. 功能列表是否包含新功能
- 如果有不一致，标记需要更新的部分

### Step 3: 检查API文档
- 对每个变更的API文件：
  a. 读取源代码中的JSDoc/TSDoc
  b. 对比函数签名、参数、返回值
  c. 检查文档是否和实现一致
- 如果有不一致，更新JSDoc/TSDoc

### Step 4: 更新CHANGELOG
- 读取 CHANGELOG.md
- 根据 git log，添加新条目
- 格式：
  ## [Unreleased]
  ### Added（新功能）
  ### Changed（变更）
  ### Fixed（修复）
  ### Removed（移除）

### Step 5: 检查配置文件
- 对比 .env.example 和实际使用的配置
- 如果有新的环境变量，添加到 .env.example
- 添加注释说明

### Step 6: 验证
- 如果有代码示例，尝试运行
- 确认文档和代码一致

## 评估标准

1. README中的安装步骤可以执行
2. README中的代码示例可以运行
3. API文档和代码一致
4. CHANGELOG包含所有变更

## 决策逻辑

IF 变更是新功能
THEN 更新README功能列表，添加CHANGELOG条目

IF 变更是API签名变化
THEN 更新API文档（JSDoc/TSDoc）

IF 变更是新增配置项
THEN 更新.env.example，添加说明

IF 变更是纯重构（无行为变化）
THEN 不更新文档

IF README中的代码示例无法运行
THEN 更新代码示例

IF 不确定是否需要更新
THEN 不更新，记录到 doc-review-needed.md 供人审查

## 终止条件

成功终止：
- 所有文档和代码一致
- 输出更新报告到 doc-update-report.md

## 失败处理

1. 代码示例无法运行
   - 分析原因，修复示例代码
   - 如果是功能本身有问题，记录到bug清单

2. 不确定文档是否正确
   - 不强行更新
   - 标记为需要人审查

## 状态管理

1. doc-update-report.md - 文档更新报告
2. doc-review-needed.md - 需要人审查的项目
```

**直接复制使用的命令：**

```bash
# 方式1：goal模式（推荐）
/goal README中的代码示例可以运行，API文档和代码一致，CHANGELOG包含本次变更，文档更新报告在 doc-update-report.md 中 or stop after 3 turns

# 方式2：手动触发
claude -p "检查 git diff main...HEAD 的代码变更，同步更新 README.md、CHANGELOG.md、API文档（JSDoc）、.env.example。输出更新报告到 doc-update-report.md"

# 方式3：定时loop（每次合并后自动同步）
# .claude/loop.md 内容：
# 检查最近的代码变更，同步更新相关文档：README、CHANGELOG、API文档、配置说明。
# 如果文档已最新，不创建PR。如果有更新，提交PR。
/loop
```

---

### 2.7 Issue自动分诊

**什么时候用：**
- GitHub issue积累太多，需要自动分类
- 希望自动处理简单的issue（typo、简单bug）
- 复杂的issue自动分优先级分配给人

**完整提示词：**

```markdown
# Issue自动分诊任务

## 任务定义
你的任务是扫描GitHub仓库中的新issue，分类并处理。

范围：
- 所有 label 为空或 label 为 needs-triage 的 open issue
- 不包括已经 assign 给他人的 issue

目标状态：
- 每个issue都有分类标签（bug/feature/question/duplicate）
- P0 issue已创建修复PR
- P1/P2 issue已分配给团队成员或添加评论
- 所有处理记录在 issue-triage-report.md

## 执行步骤

### Step 1: 获取新issue
- 运行 gh issue list --state open --label needs-triage --json number,title,body,labels
- 如果没有 needs-triage 标签的issue，获取所有无label的issue
- 读取每个issue的标题和详细描述

### Step 2: 分类
对每个issue分类：

a. Bug Report
   - 描述中有错误信息、复现步骤
   - 标记为 bug

b. Feature Request
   - 描述中有"希望"、"能否"、"建议"
   - 标记为 feature

c. Question
   - 描述中有问号、"怎么"、"如何"
   - 标记为 question

d. Duplicate
   - 和已有issue高度相似
   - 标记为 duplicate，关联原issue

### Step 3: 评估优先级
对bug类issue评估优先级：

P0（立即修复）：
- 影响核心功能（登录、支付、数据丢失）
- 影响所有用户
- 安全问题

P1（本周修复）：
- 影响非核心功能
- 影响部分用户
- 有workaround但体验差

P2（排期待修复）：
- 体验优化
- 性能优化
- 不影响功能

### Step 4: 处理
根据分类和优先级处理：

IF P0 bug
THEN 
  a. 尝试复现
  b. 如果能复现，分析根因
  c. 创建修复PR
  d. 在issue中评论："已创建PR #xxx 修复此问题"
  e. 添加标签 P0

IF P1 bug
THEN
  a. 添加标签 P1
  b. 在issue中评论分析结果
  c. 如果可以自动修复，创建PR

IF P2 bug
THEN
  a. 添加标签 P2
  b. 在issue中评论："已记录，排期待修复"

IF feature request
THEN
  a. 评估是否符合项目方向（检查 README、CLAUDE.md）
  b. 如果符合，添加标签 enhancement
  c. 如果不符合，礼貌回复并关闭

IF question
THEN
  a. 回答问题
  b. 如果问题有普遍性，建议更新文档

IF duplicate
THEN
  b. 评论："这是 #xxx 的重复，请关注原issue"
  c. 关闭issue

### Step 5: 输出报告
将所有处理记录写入 issue-triage-report.md：
- 每个issue的处理结果
- P0 issue的修复PR链接
- 需要人关注的issue

## 评估标准

1. 所有issue都已分类
2. P0 issue已创建PR或标记需要人工介入
3. 每个issue都有评论或标签更新

## 决策逻辑

IF issue信息不足以分类
THEN 评论询问更多信息，添加 label: needs-info

IF 无法复现P0 bug
THEN 标记为 needs-reproduction，通知人

IF feature request不符合项目方向
THEN 礼貌回复，关闭issue

IF 自动修复失败
THEN 标记为 needs-human，通知人

## 终止条件

成功终止：
- 所有issue已分类和处理
- 输出报告到 issue-triage-report.md

## 失败处理

1. 无法访问GitHub API
   - 检查 gh auth status
   - 通知人登录

2. 无法复现bug
   - 标记 needs-reproduction
   - 不强行修复

## 状态管理

1. issue-triage-report.md - 分诊报告
```

**直接复制使用的命令：**

```bash
# 方式1：goal模式（推荐）
/goal 所有needs-triage的issue都已分类（bug/feature/question/duplicate），P0 issue已创建修复PR，分诊报告在 issue-triage-report.md 中 or stop after 10 turns

# 方式2：手动触发
claude -p "扫描所有needs-triage的GitHub issue，分类并处理：P0 bug直接修复并创建PR，P1/P2添加标签和评论，feature request评估是否符合项目方向，question直接回答。输出报告到 issue-triage-report.md"

# 方式3：定时loop（每天早上自动分诊）
# .claude/loop.md 内容：
# 扫描所有needs-triage的GitHub issue。
# 分类：bug/feature/question/duplicate。
# P0 bug尝试修复并创建PR。P1/P2添加标签和评论。
# 输出分诊报告到 issue-triage-report.md。
/loop 1d
```

---

### 2.8 依赖安全扫描与升级

**什么时候用：**
- npm audit / pip-audit 报告有漏洞
- 需要自动升级有漏洞的依赖
- 希望确保升级后不破坏功能

**完整提示词：**

```markdown
# 依赖安全扫描与升级任务

## 任务定义
你的任务是扫描依赖漏洞，升级有漏洞的依赖，确保升级后功能正常。

范围：
- 项目的所有依赖（dependencies + devDependencies）
- 仅升级有已知安全漏洞的依赖

目标状态：
- npm audit（或对应语言的audit工具）报告无高危/严重漏洞
- 所有测试通过
- 应用功能正常

## 执行步骤

### Step 1: 扫描漏洞
- 运行 npm audit --json（或 pip-audit / cargo-audit / go list -m all）
- 解析输出，提取漏洞信息：
  a. 包名
  b. 当前版本
  c. 漏洞严重程度（critical/high/medium/low）
  d. 修复版本
  e. 漏洞描述

### Step 2: 评估升级风险
对每个有漏洞的依赖评估：

a. 是否有修复版本？
   - 有 → 继续评估
   - 没有 → 记录，通知人

b. 升级是否是semver minor/patch？
   - patch（1.0.0→1.0.1） → 低风险，直接升级
   - minor（1.0.0→1.1.0） → 中风险，升级后测试
   - major（1.0.0→2.0.0） → 高风险，检查CHANGELOG

c. 是否有breaking changes？
   - 检查依赖的CHANGELOG
   - 如果有breaking changes，评估影响范围

### Step 3: 执行升级
按风险从低到高升级：

a. patch升级
   - npm install <package>@latest
   - 运行测试验证

b. minor升级
   - npm install <package>@latest
   - 检查是否有deprecated API
   - 运行测试验证

c. major升级
   - 检查CHANGELOG和migration guide
   - 更新代码中的breaking changes
   - 运行测试验证

### Step 4: 验证
- 运行 npm audit 确认漏洞已修复
- 运行 npm test 确认所有测试通过
- 运行 npm run build 确认构建通过
- 如果有E2E测试，运行E2E测试

### Step 5: 提交
- git add package.json package-lock.json
- 如果有代码修改，也加入
- 提交信息："fix: upgrade <package> to fix <vulnerability>"
- 创建PR

## 评估标准

1. 无高危/严重漏洞
2. 所有测试通过
3. 构建通过

## 决策逻辑

IF 漏洞是 critical/high
THEN 优先升级，即使是major版本

IF 漏洞是 medium/low
THEN 仅在patch/minor范围内升级

IF 升级引入breaking changes
THEN 评估影响范围，更新代码
如果影响太大，记录原因，不升级

IF 升级后测试失败
THEN 分析失败原因
IF 是代码适配问题 → 修复代码
IF 是依赖本身的问题 → 回滚，记录原因

IF 没有修复版本
THEN 记录到 security-review-needed.md
通知人评估workaround

## 终止条件

成功终止：
- 无高危/严重漏洞
- 所有测试通过
- 创建升级PR

失败终止：
- 升级引入无法解决的问题
- 输出报告到 dependency-upgrade-report.md

## 失败处理

1. major升级后大量测试失败
   - 回滚升级
   - 记录原因
   - 通知人

2. 依赖已abandoned
   - 寻找替代方案
   - 记录到 tech-debt.md

## 状态管理

1. dependency-upgrade-report.md - 升级报告
2. security-review-needed.md - 需要人审查的项目
```

**直接复制使用的命令：**

```bash
# 方式1：goal模式（推荐）
/goal npm audit报告无高危和严重漏洞，所有测试通过，升级报告在 dependency-upgrade-report.md 中 or stop after 5 turns

# 方式2：手动触发
claude -p "运行npm audit，升级所有有高危/严重漏洞的依赖。patch/minor直接升级，major检查CHANGELOG后升级。升级后运行测试确保通过。创建PR。输出报告到 dependency-upgrade-report.md"

# 方式3：定时loop（每周一自动扫描）
# .claude/loop.md 内容：
# 运行npm audit扫描依赖漏洞。
# 升级有高危/严重漏洞的依赖。
# 升级后运行测试确保通过。
# 如果有升级，创建PR。输出报告到 dependency-upgrade-report.md。
/loop 7d
```

---

### 2.9 性能优化

**什么时候用：**
- API响应慢，需要优化
- 数据库查询有N+1问题
- 需要持续优化直到达标

**完整提示词：**

```markdown
# 性能优化任务

## 任务定义
你的任务是优化指定功能的性能，直到达到目标指标。

优化目标：
- API <endpoint> 的 P95 响应时间 < <target>ms
- 数据库查询次数 < <target>次
- 内存使用 < <target>MB

范围：
- 仅优化 <指定模块/文件>
- 不修改业务逻辑
- 不修改API接口

## 执行步骤

### Step 1: 性能基线测量
- 编写benchmark脚本（或使用已有的）
- 测量当前性能指标：
  a. P50/P95/P99 响应时间
  b. 数据库查询次数
  c. 内存使用
  d. CPU使用率
- 记录基线数据到 perf-baseline.md

### Step 2: Profiling
- 使用profiling工具识别热点：
  a. CPU profiling：找到耗时最长的函数
  b. 内存profiling：找到内存泄漏或大量分配
  c. 数据库profiling：找到慢查询和N+1问题
- 输出profiling结果到 perf-profile.md

### Step 3: 识别优化点
按影响大小排序：

a. N+1查询 → 改为JOIN或批量查询（影响最大）
b. 重复计算 → 添加缓存（影响大）
c. 大数据处理 → 流式处理或分页（影响大）
d. 不必要的序列化/反序列化 → 优化数据结构（影响中）
e. 同步IO → 改为异步（影响中）

### Step 4: 实施优化
按影响从大到小优化：

对每个优化：
a. 应用修改
b. 运行benchmark验证改进
c. 运行测试确保功能正常
d. 如果改进 > 10%，保留
e. 如果改进 < 10% 或引入问题，回滚

### Step 5: 最终验证
- 运行benchmark
- 对比基线数据
- 如果达标，任务完成
- 如果未达标，回到 Step 3

## 评估标准

1. 性能达标
   - P95 < target ms
   - 查询次数 < target

2. 功能正常
   - 所有测试通过
   - API行为不变

3. 代码质量不下降
   - 不引入过度优化
   - 保持代码可读性

## 决策逻辑

IF 发现 N+1 查询
THEN 改为 JOIN 或 IN 批量查询

IF 发现重复计算
THEN 添加缓存（内存缓存或Redis）

IF 发现大数据集处理
THEN 改为流式处理或分页

IF 优化后测试失败
THEN 回滚，尝试其他方案

IF 已优化所有热点但未达标
THEN 分析是否需要架构级别的变更
记录建议，通知人

IF 优化导致代码可读性严重下降
THEN 权衡性能和可读性
记录tradeoff，通知人决定

## 终止条件

成功终止：
- 性能指标达标
- 所有测试通过
- 输出优化报告到 perf-report.md

失败终止：
- 所有优化手段已用尽但未达标
- 输出报告，建议架构变更

## 失败处理

1. 优化引入bug
   - 回滚
   - 尝试更保守的方案

2. 无法进一步优化
   - 记录已尝试的优化
   - 建议架构级别的变更
   - 通知人

## 状态管理

1. perf-baseline.md - 基线数据
2. perf-profile.md - profiling结果
3. perf-report.md - 优化报告
```

**直接复制使用的命令：**

```bash
# 方式1：goal模式（推荐）
/goal GET /api/products 的P95响应时间<200ms且数据库查询<3次且所有测试通过，优化报告在 perf-report.md 中 or stop after 5 turns

# 方式2：手动触发
claude -p "
性能优化任务：
- 目标：GET /api/products 的P95响应时间<200ms
- 当前：P95=800ms
- 模块：src/services/product.ts、src/repositories/product.ts

分析性能瓶颈，识别优化点，实施优化，运行benchmark验证改进，运行测试确保功能正常。
输出优化报告到 perf-report.md
"

# 方式3：定时loop（每周检查性能回归）
# .claude/loop.md 内容：
# 运行性能基准测试，对比上周数据。
# 如果性能回归（P95响应时间增加>20%），分析原因并优化。
# 输出性能报告到 perf-report.md。
/loop 7d
```

---

## 三、提示词设计模式

### 3.1 ReAct模式（推理-行动循环）

```markdown
你需要通过反复推理和行动来完成任务。

每次迭代遵循以下循环：

Thought: 分析当前状态，决定下一步行动
Action: 执行行动
Observation: 观察行动结果
Reflection: 反思结果，决定是否继续

重复这个循环，直到任务完成。

在每次 Thought 中，必须回答：
- 当前状态是什么？
- 目标状态是什么？
- 差距在哪里？
- 下一步应该做什么？
- 为什么要做这个？

在每次 Reflection 中，必须回答：
- 行动是否成功？
- 是否有意外结果？
- 是否需要调整策略？
- 是否接近目标？
- 是否应该继续还是停止？
```

---

### 3.2 Evaluator-Optimizer模式（制造者-审查者）

```markdown
你需要通过制造和审查的循环来完成任务。

角色分工：
- Generator（制造者）：负责生成代码
- Evaluator（审查者）：负责评估代码质量

流程：

1. Generator 生成代码
2. Evaluator 评估代码，给出评分和反馈
3. IF 评分 >= 80 AND 无 CRITICAL 问题
   THEN 提交代码，任务完成
4. IF 评分 < 80 OR 有 CRITICAL 问题
   THEN 将反馈传回 Generator，重新生成
5. 重复 1-4，最多 3 次

Evaluator 的评估标准：
- 安全性（0-10分）
- 代码质量（0-10分）
- 测试覆盖率（0-10分）
- 文档完整性（0-10分）
- 性能（0-10分）

如果连续 2 次评估结果相同（评分差距 < 2分），
说明陷入停滞，终止循环，输出当前最佳结果。
```

---

### 3.3 Orchestrator-Workers模式（协调者-工作者）

```markdown
你是 Orchestrator（协调者），负责协调多个 Worker（工作者）完成任务。

任务：<总体任务>

Step 1: 任务分解
- 将任务分解为独立子任务
- 每个子任务必须有明确的输入和输出
- 子任务之间不能有依赖

Step 2: 分配任务
- 为每个子任务分配一个 Worker
- 每个 Worker 在独立的 worktree 中工作
- 每个 Worker 不能看到其他 Worker 的代码

Step 3: 监控进度
- 定期检查每个 Worker 的进度
- 如果 Worker 遇到困难，提供帮助
- 如果 Worker 失败，重新分配任务

Step 4: 合并结果
- 所有 Worker 完成后，合并代码
- 解决合并冲突
- 运行集成测试

Step 5: 验证
- 如果集成测试通过，任务完成
- 如果集成测试失败，分析失败原因
- 派出 Worker 修复问题

终止条件：
- 所有子任务完成
- 集成测试通过
- 最多迭代 5 次
```

---

## 四、提示词质量检查清单

在提交提示词之前，检查以下项目：

### 4.1 任务定义
- [ ] 是否明确了任务范围？
- [ ] 是否明确了目标状态？
- [ ] 是否明确了排除范围？

### 4.2 执行步骤
- [ ] 是否分步骤？
- [ ] 每步骤是否有明确的输入和输出？
- [ ] 每步骤是否有验证机制？

### 4.3 评估标准
- [ ] 是否有量化的评估标准？
- [ ] 是否有多维度的评估？
- [ ] 是否有失败的后果？

### 4.4 决策逻辑
- [ ] 是否有 IF-THEN 结构？
- [ ] 是否覆盖了所有可能的情况？
- [ ] 每个决策是否有明确的行动？

### 4.5 终止条件
- [ ] 是否有多种终止情况？
- [ ] 每种情况是否有明确的输出？
- [ ] 是否有强制终止作为安全网？

### 4.6 失败处理
- [ ] 是否分类处理不同类型的失败？
- [ ] 每种失败是否有明确的处理策略？
- [ ] 所有失败是否都记录？

### 4.7 状态管理
- [ ] 是否有明确的状态文件？
- [ ] 每个文件的内容是否定义？
- [ ] 状态更新时机是否明确？

---

## 五、常见错误和改进

### 5.1 错误1：任务定义模糊

**错误示例：**
```
优化代码
```

**改进：**
```
优化 src/auth/login.ts 的性能

目标：
- login 函数的执行时间从 500ms 降低到 200ms
- 数据库查询从 3 次减少到 1 次
- 内存占用降低 30%

验证方式：
- 运行 benchmark: npm run benchmark -- login
- 运行 profiling: npm run profile -- login
```

---

### 5.2 错误2：缺少评估标准

**错误示例：**
```
修复bug
```

**改进：**
```
修复 issue #123 中描述的 bug

评估标准：
1. 复现测试
   - 运行 test/bug-123.test.ts
   - 测试必须通过

2. 回归测试
   - 运行 npm test
   - 所有测试必须通过

3. 代码审查
   - 修复不能引入新的 lint 错误
   - 修复不能降低代码覆盖率
```

---

### 5.3 错误3：缺少决策逻辑

**错误示例：**
```
实现新功能
```

**改进：**
```
实现用户注册功能

决策逻辑：
IF 数据库表不存在
THEN 创建数据库表

IF 数据库表存在但缺少字段
THEN 添加缺少的字段

IF 数据库表完整
THEN 跳过数据库步骤

IF API endpoint 不存在
THEN 创建 API endpoint

IF API endpoint 存在但逻辑不正确
THEN 修改 API endpoint 逻辑

IF API endpoint 完整
THEN 跳过 API 步骤

IF 测试不存在
THEN 创建测试

IF 测试存在但不通过
THEN 修复测试或修复代码

IF 测试通过
THEN 任务完成
```

---

## 六、总结

**Loop Engineering的本质是设计能够自主运行的提示词系统。**

**核心公式：**
```
自主运行的提示词 = 任务定义 + 执行步骤 + 评估标准 + 决策逻辑 + 终止条件 + 失败处理 + 状态管理
```

**提示词质量检查清单：**
- 任务定义：明确范围、目标、排除
- 执行步骤：分步骤、有输入输出、有验证
- 评估标准：量化、多维度、有后果
- 决策逻辑：IF-THEN、覆盖所有情况
- 终止条件：多种情况、明确输出、强制终止
- 失败处理：分类处理、明确策略、记录
- 状态管理：明确文件、定义内容、更新时机

**最后的思考：**
> 好的提示词不是告诉Agent"做什么"，而是告诉Agent"如何思考和决策"。
