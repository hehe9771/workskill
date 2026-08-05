# 本机 eval 相关 Skill 盘点

> 生成日期：2026-07-07
> 范围：本机（`C:\Users\wuyan\.claude\`）所有与 eval / evaluation 相关的 skill 与 slash command
> 目的：定位每个 skill 的安装来源、所属插件、用途、使用场景与触发提示词

---

## 一、来源结论

本机 eval 相关 skill/command **几乎全部来自 ECC 插件**（Everything Claude Code）：

| 属性 | 值 |
|------|-----|
| Marketplace 名 | `ecc` |
| 插件名 | `ecc` |
| 版本 | 2.0.0 |
| 作者 | Affaan Mustafa |
| 仓库 | https://github.com/affaan-m/ECC |
| 主页 | https://ecc.tools |
| 缓存路径 | `C:\Users\wuyan\.claude\plugins\cache\ecc\ecc\2.0.0\` |
| Marketplace 源 | `C:\Users\wuyan\.claude\plugins\marketplaces\ecc\` |
| 自描述 | 67 agents, 277 skills, 93 legacy command shims, reusable hooks, rules, selective install profiles |

另有 1 个 `source-eval` 来自无关仓库 `github.com/kimny1143/claude-code-template`，被 clone 到 `~/.claude/skills/temp-check/` 下做检查用副本，**非激活**。

---

## 二、总览表

| # | 名称 | 类型 | 来源插件 | 激活可用 | 用途一句话 |
|---|------|------|----------|----------|-----------|
| 1 | `eval-harness` | Skill | ECC | ✅ | Claude Code 会话的 EDD 评估框架（pass@k 指标） |
| 2 | `/eval` | Command | ECC | ✅ | EDD 工作流命令行入口（define/check/report/list） |
| 3 | `/learn-eval` | Command | ECC | ✅ | 提取可复用模式 + 质量门禁 + 保存位置决策 |
| 4 | `agent-eval` | Skill | ECC | ❌ | 多 agent 横向对比（Claude Code vs Aider vs Codex） |
| 5 | `agent-self-evaluation` | Skill | ECC | ❌ | agent 完成任务后 5 轴自评 |
| 6 | `healthcare-eval-harness` | Skill | ECC | ❌ | 医疗应用部署的患者安全评估门禁 |
| 7 | `scientific-thinking-scholar-evaluation`（内部名 `scholar-evaluation`） | Skill | ECC | ❌ | 学术论文/提案结构化同行评审 |
| 8 | `source-eval` | Skill | `kimny1143/claude-code-template` | ❌ | 外部技术来源 A+B+C 三轴质量筛选 |

> **激活状态说明**
> - ✅ 表示在当前会话的 Skill / slash command 可用列表中，可直接调用。
> - ❌ 表示 SKILL.md 存在于插件 `skills/` 目录，但未进入可用列表——属于 ECC "selective install profiles" 未启用的部分（第 4–7 项），或位于 `temp-check` 仓库副本内不被加载（第 8 项）。

---

## 三、逐个详细说明

### 1. `eval-harness` ✅ 可用

- **来源路径**：`C:\Users\wuyan\.claude\skills\eval-harness\SKILL.md`（同时存在于 `skills\ecc\eval-harness\`、`.agents\skills\eval-harness\`、ECC 插件 `skills\eval-harness\`）
- **frontmatter origin**：ECC
- **用途**：把"评估"当 AI 开发的单元测试——在写代码前定义能力评估（capability eval）和回归评估（regression eval），用 pass@k / pass^k 量化 agent 可靠性，配套 code / rule / model / human 四种 grader。
- **Eval 类型**：
  - Capability Eval：测 Claude 现在能不能做到之前做不到的事
  - Regression Eval：确保改动不破坏既有功能
- **Grader 类型**：Code-Based（确定性）/ Rule-Based（正则 schema）/ Model-Based（LLM-as-judge）/ Human（人工裁定）
- **核心指标**：
  - `pass@k`：k 次内至少 1 次成功（pass@1 首次成功率，pass@3 实用可靠性，目标 ≥ 0.90）
  - `pass^k`：k 次全过（pass^3 = 1.00 用于发布关键路径）
- **使用场景**：
  - 给新功能定 success criteria
  - prompt 或 agent 改动后跑回归
  - 跨模型版本 benchmark
  - 在 `.claude/evals/<feature>.md` 沉淀评估资产
- **提示词 / 调用**：
  - 直接调命令：`/eval define add-authentication` → `/eval check add-authentication` → `/eval report add-authentication`
  - 自然语言：「用 eval-harness 给这个鉴权功能定义评估标准，pass@3 目标 90%」
- **产物路径**：
  - `.claude/evals/<feature>.md` — 评估定义
  - `.claude/evals/<feature>.log` — 运行历史
  - `.claude/evals/baseline.json` — 回归基线
  - `docs/releases/<version>/eval-summary.md` — 发布快照
- **反模式**（SKILL.md 明确警告）：
  - 把 prompt 过拟合到已知 eval 样例
  - 只测 happy-path
  - 追 pass 率时忽略 cost / latency 漂移
  - 在发布门禁里放 flaky grader

---

### 2. `/eval` ✅ 可用

- **来源路径**：`C:\Users\wuyan\.claude\commands\eval.md`（ECC 插件 `commands\eval.md` 同源）
- **用途**：`eval-harness` skill 的命令行操作入口，4 个子命令管理评估生命周期。
- **子命令**：
  | 命令 | 作用 |
  |------|------|
  | `/eval define <name>` | 新建评估定义模板到 `.claude/evals/<name>.md` |
  | `/eval check <name>` | 跑当前评估，报 IN PROGRESS / READY |
  | `/eval report <name>` | 生成完整报告含 pass@1/pass@3/pass^3 与 SHIP / NEEDS WORK / BLOCKED 建议 |
  | `/eval list` | 列出所有评估定义及通过率 |
  | `/eval clean` | 清理旧 log（保留最近 10 次） |
- **使用场景**：实现前定义、实现中检查、实现后出报告、列出全部评估。
- **提示词示例**：
  ```
  /eval define add-authentication
  /eval check add-authentication
  /eval report add-authentication
  /eval list
  ```
- **报告输出格式**：
  ```
  EVAL REPORT: feature-name
  Capability pass@1: 67%
  Capability pass@3: 100%
  Regression pass^3: 100%
  RECOMMENDATION: SHIP / NEEDS WORK / BLOCKED
  ```

---

### 3. `/learn-eval` ✅ 可用

- **来源路径**：`C:\Users\wuyan\.claude\commands\learn-eval.md`（ECC 插件 `commands\learn-eval.md` 同源）
- **用途**：`/learn` 的增强版——从会话里提取可复用模式，保存前过**质量门禁**，并用整体判定决定是新建 skill 还是并入已有 skill，还要决定存 Global 还是 Project。
- **提取对象**：错误根因修复模式、调试技巧、库的 workaround、项目特定约定。
- **质量门禁（Step 5）**：
  - 5a 必查清单：grep `~/.claude/skills/` 查重 → 查 MEMORY.md（项目+全局）查重 → 评估能否并入既有 skill → 确认是可复用模式而非一次性修复
  - 5b 整体判定（四选一）：
    | Verdict | 含义 | 下一步 |
    |---------|------|--------|
    | Save | 独立、具体、范围清晰 | 落盘 |
    | Improve then Save | 有价值但需打磨 | 列改进 → 修订 → 再评一次 |
    | Absorb into [X] | 应并入既有 skill | 显示目标 skill + diff |
    | Drop | 琐碎/冗余/太抽象 | 解释理由后停止 |
- **保存位置决策**：
  - Global（`~/.claude/skills/learned/`）：跨 2+ 项目通用的模式
  - Project（`.claude/skills/learned/`）：项目特定知识
  - 拿不准选 Global（Global→Project 比 反向容易）
- **使用场景**：刚解决一个非平凡 bug 或发现一个库的怪癖，想沉淀成 skill 但不确定值不值得存、该存哪。
- **提示词**：`/learn-eval`（无参，自动扫描当前会话）——它会先输出 Checklist + Verdict + rationale，经确认才落盘。
- **设计说明**：v2 用 checklist + 整体判定取代了旧的 5 维 1–5 分数值评分；理由是现代前沿模型（Opus 4.6+）上下文判断力强，把丰富定性信号压成数字会失真。

---

### 4. `agent-eval` ❌ 插件内未激活

- **来源路径**：`C:\Users\wuyan\.claude\plugins\cache\ecc\ecc\2.0.0\skills\agent-eval\SKILL.md`
- **frontmatter origin**：ECC
- **用途**：用 YAML 声明任务（prompt + 指定文件 + judge 规则 + pin commit），让多个编码 agent 各自在独立 git worktree 里跑，横向对比 **pass rate / cost / time / consistency**。把"哪个 coding agent 最强"从感觉变成数据。
- **核心机制**：
  - YAML 任务定义：声明 prompt、待改文件、judge 规则、pin 到具体 commit
  - Git worktree 隔离：每个 agent run 一个独立 worktree，无需 Docker，agent 间互不干扰
  - Judge 类型：Code-Based（pytest/build）/ Pattern-Based（grep）/ Model-Based（LLM-as-judge）
- **使用场景**：
  - 团队选型前在自家代码库上对比 Claude Code / Aider / Codex
  - agent 升模型后跑回归
  - 产出数据驱动的 agent 选择决策
- **最佳实践**：
  - 起步 3–5 个真实任务，不要 toy example
  - 每 agent 至少 3 次试验以捕获方差
  - pin commit 保证可复现
  - 每 task 至少 1 个确定性 judge（LLM judge 有噪声）
  - 跟踪 cost 而非只看 pass 率
- **提示词示例**（激活后）：
  ```yaml
  # tasks/add-retry-logic.yaml
  name: add-retry-logic
  repo: ./my-project
  files: [src/http_client.py]
  prompt: |
    Add exponential backoff retry. Max 3, init 1s, max 30s.
  judge:
    - type: pytest
      command: pytest tests/test_http_client.py -v
    - type: grep
      pattern: "exponential_backoff|retry"
  commit: "abc1234"
  ```
  调用：
  ```bash
  agent-eval run --task tasks/add-retry-logic.yaml --agent claude-code --agent aider --runs 3
  agent-eval report --format table
  ```
- **关联外部仓库**：https://github.com/joaquinhuigomez/agent-eval （SKILL.md 指向的 CLI 工具）

---

### 5. `agent-self-evaluation` ❌ 插件内未激活

- **来源路径**：`C:\Users\wuyan\.claude\plugins\cache\ecc\ecc\2.0.0\skills\agent-self-evaluation\SKILL.md`
- **frontmatter origin**：ECC
- **用途**：完成复杂任务后，agent 按 5 轴自评 1–5 分，每条 <5 分必须引用具体证据，产出 scorecard + 1–3 条改进。
- **5 轴 rubric**：
  | 轴 | 问题 | 抓什么 |
  |----|------|--------|
  | Accuracy | 事实/claim/输出是否正确 | 幻觉、错 API 名、错语法 |
  | Completeness | 是否覆盖了用户全部需求 | 漏边界、漏错误路径、漏子任务 |
  | Clarity | 解释是否易懂、结构是否清晰 | 晦涩、术语无定义、跑题 |
  | Actionability | 用户能否立即行动 | 模糊建议、缺步骤、"你应该 X"却不示怎么做 |
  | Conciseness | 是否用了最少 token | 冗余、过度解释、复读用户问题 |
- **评分尺度**：5 无可改进 / 4 仅小瑕疵 / 3 有明显短板 / 2 影响可用或正确性 / 1 根本没满足
- **证据规则**：每个 <5 分必须引具体证据——"Show the gap, don't just name it."
- **使用场景**：
  - 写完跨 3+ 文件或 50+ 行代码后
  - 完成多步工作流（实现→测试→评审）后
  - 调试 3+ 次尝试后
  - 产出设计文档/架构决策/分析报告后
  - 用户问"how good was that?" / "rate yourself"
  - Stop hook 触发时
- **提示词**：
  - 「用 agent-self-evaluation 给刚才的鉴权实现打分」
  - 「rate yourself on that last task」
- **反模式**：
  - "Everything is a 5"（无证据的自夸）
  - 用未要求的 scope creep 拉低分
  - 借自评重提已定设计争议
  - 把个人偏好当客观 gap
- **替代方案**：本机虽未激活该 skill，但有同名 agent `agent-evaluator`（在 agents 列表），实现同一套 5 轴 rubric——可直接用 `Agent` 工具调 `agent-evaluator` 替代。

---

### 6. `healthcare-eval-harness` ❌ 插件内未激活

- **来源路径**：`C:\Users\wuyan\.claude\plugins\cache\ecc\ecc\2.0.0\skills\healthcare-eval-harness\SKILL.md`
- **frontmatter origin**：Health1 Super Speciality Hospitals — Dr. Keyur Patel 贡献（ECC 收录的社区贡献）
- **版本**：1.0.0
- **用途**：医疗应用部署前的**患者安全门禁**。一个 CRITICAL 失败即阻断部署——"Patient safety is non-negotiable."
- **5 类测试**：
  | 类别 | 阈值 | 失败后果 |
  |------|------|----------|
  | CDSS Accuracy（临床决策支持） | 100% | **阻断部署** |
  | PHI Exposure（受保护健康信息泄露） | 100% | **阻断部署** |
  | Data Integrity（数据完整性） | 100% | **阻断部署** |
  | Clinical Workflow（临床工作流） | 95%+ | 警告，评审后放行 |
  | Integration Compliance（集成合规，HL7/FHIR） | 95%+ | 警告，评审后放行 |
- **CI 集成**：CRITICAL gate 用 `--bail` 首失败即停；强制 `--coverage --coverageThreshold`（branches/functions/lines ≥ 80%）。
- **使用场景**：
  - EMR/EHR 应用部署前
  - 改了 CDSS 药物交互/剂量/评分逻辑后
  - 改了触及患者数据的数据库 schema 后
  - 改了认证或访问控制后
  - 医疗 app 的 CI/CD pipeline 配置
  - 临床模块合并冲突解决后
- **提示词**：
  - 「用 healthcare-eval-harness 给这次发布做安全门禁」
  - 直接套命令（本地跑全部 CRITICAL gate）：
    ```bash
    npx jest --testPathPattern='tests/cdss' --bail --ci --coverage && \
    npx jest --testPathPattern='tests/security/phi' --bail --ci && \
    npx jest --testPathPattern='tests/data-integrity' --bail --ci
    ```
- **反模式**：跳过 CDSS 测试"因为上次过了" / CRITICAL 阈值低于 100% / 用 `--no-bail` / 集成测试里 mock CDSS 引擎 / 红灯仍部署 / CDSS 不带 coverage。

---

### 7. `scientific-thinking-scholar-evaluation` ❌ 插件内未激活

- **来源路径**：`C:\Users\wuyan\.claude\plugins\cache\ecc\ecc\2.0.0\skills\scientific-thinking-scholar-evaluation\SKILL.md`（也装到 `~/.claude/skills/ecc/scientific-thinking-scholar-evaluation/`）
- **内部 frontmatter name**：`scholar-evaluation`
- **frontmatter origin**：community
- **用途**：对学术论文/提案/文献综述等做结构化同行评审，9 维度 rubric，每维 1–5 分带 evidence，输出 scorecard + Critical Issues + Recommended Revisions + Evidence Checks Needed。
- **9 维度 rubric**：
  1. Problem and Research Question（问题与提问）
  2. Literature and Context（文献与背景）
  3. Methodology（方法）
  4. Data and Evidence（数据与证据）
  5. Analysis（分析）
  6. Results and Interpretation（结果与解释）
  7. Limitations and Threats to Validity（局限与效度威胁）
  8. Writing and Structure（写作与结构）
  9. Citations（引用）
- **评审范围 scope**：comprehensive（全维度）/ targeted（1–2 维）/ comparative（多篇同 rubric 排序）
- **适用作品类型**：实证/理论研究论文、技术报告、系统或叙述性文献综述、研究提案、学位论文章节、会议摘要。
- **使用场景**：
  - 审论文/开题报告/学位论文章节/文献综述
  - 核查 claim 是否被引用支撑
  - 两篇论文对比排序
  - 给作者结构化修改反馈
- **提示词**：
  - 「用 scholar-evaluation 评审这篇论文，focus on methodology and citations」
  - 「比较这两篇论文哪个更严谨」
- **输出模板**：含 Overall Assessment（总分 + 置信度 + 摘要）、Dimension Scores 表（维度/分/证据/修改优先级）、Critical Issues、Recommended Revisions、Evidence Checks Needed。
- **陷阱**：不要用分数代替具体反馈 / 不要因超出 scope 的缺失扣分 / 不要把引用数、期刊、作者声誉当质量证据 / 不要因 claim 出现在摘要就采信。

---

### 8. `source-eval` ❌ 非 ECC、未激活

- **来源路径**：`C:\Users\wuyan\.claude\skills\temp-check\.claude\skills\source-eval\SKILL.md`
- **来源仓库**：`https://github.com/kimny1143/claude-code-template`（日本 freee 财务 SaaS 相关的 claude-code 模板仓库）
- **本机状态**：被 clone 到 `~/.claude/skills/temp-check/` 作为检查副本，Claude Code **不会**把它加载为顶层 skill。
- **语言**：日文
- **用途**：对外部技术来源（官方文档/技术博客/GitHub README/会议资料）做 **A 汎用性 + B 重複なし + C 実証済み** 三轴筛选，A+B+C 全 YES 自动生成"skill 化依頼文"给 template 课，结果存 `sources/<slug>-eval-YYYYMMDD.md`。
- **三轴定义**：
  - A 汎用性：是否不依赖特定工具、可跨 3+ 课适用
  - B 重複なし：与既有 skill 不重复（查 `ls .claude/skills/`）
  - C 実証済み：有具体事例/数值/实现例（最重要）
- **判定矩阵**：
  | A | B | C | 判定 |
  |---|---|---|------|
  | YES | YES | YES | skill 化依頼（生成依頼文） |
  | YES | YES | NO | 本地引入提案（research 课内参照） |
  | YES | NO | YES | 重複确认后再评估（建议强化既有 skill） |
  | NO | — | — | 见送り（汎用性不足） |
  | — | — | NO | 见送り（无实证） |
- **使用场景**：研究课做外部 best-practice 的一次筛查；判断某博客/README 是否值得 skill 化。
- **提示词示例**（日文）：
  - 「このソースを評価して: https://...」
  - 「sources/に追加できるか判断して」
  - 「このブログ記事をスクリーニングして」
- **鮮度チェック**：2 年内正常评 / 2–4 年标"鮮度注意" / 4 年以上技术快变领域原则上见送り（best-practice/设计原则例外）。

---

## 四、激活状态分布与启用方法

### 激活状态分布

- **✅ 已激活可用（3 个）**：`eval-harness`（skill）、`/eval`（command）、`/learn-eval`（command）——随 ECC 主 profile 激活。
- **❌ ECC 内未激活（4 个）**：`agent-eval`、`agent-self-evaluation`、`healthcare-eval-harness`、`scientific-thinking-scholar-evaluation`——属于 ECC selective install profiles 未启用部分。
- **❌ 非 ECC 未激活（1 个）**：`source-eval`——位于 `temp-check` 仓库副本内，不被加载。

### 启用未激活 ECC skill

ECC 用 selective install profiles 管理 277 个 skill 的启用范围。本机已装 `configure-ecc` skill（在可用列表），可用它选择性安装：

- 提示词：「用 configure-ecc 启用 agent-eval 和 healthcare-eval-harness」
- 或直接 `/configure-ecc` 走交互式安装

启用后对应 SKILL.md 才会进入 Skill 可用列表。`/eval`、`/learn-eval` 这类 command 已随主 profile 激活，无需额外操作。

### 关于 `agent-self-evaluation` 的替代

若只需 5 轴自评功能而暂不想启用该 skill，可直接用本机已激活的同名 agent `agent-evaluator`（在 agents 列表，描述明确提到 "when the agent-self-evaluation skill is active"），它实现同一套 rubric，通过 `Agent` 工具调用即可。

---

## 五、决策建议

| 你想做的事 | 用哪个 |
|------------|--------|
| 给 Claude Code 的某功能定"成功标准"并跑回归 | `eval-harness` + `/eval` |
| 沉淀会话里的可复用模式，要查重 + 判定存哪 | `/learn-eval` |
| 对比 Claude Code / Aider / Codex 谁更强 | `agent-eval`（需启用） |
| 让 agent 完成任务后自评打分 | `agent-evaluator` agent（已可用）或启用 `agent-self-evaluation` skill |
| 医疗应用发布前的患者安全门禁 | `healthcare-eval-harness`（需启用） |
| 审论文/提案，结构化同行评审 | `scientific-thinking-scholar-evaluation`（需启用） |
| 筛选外部技术来源是否值得 skill 化 | `source-eval`（需从 `temp-check` 取出独立安装，或参考其 A+B+C 思路自建） |
