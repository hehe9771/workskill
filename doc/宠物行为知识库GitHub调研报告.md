# 宠物行为知识库 GitHub 调研报告

> 调研日期：2026-07-06 ｜ 方法：Dynamic Workflow 多 agent 编排 + 对抗核验
> 调研目标：从 GitHub 检索"宠物行为知识库/文档"类项目，不少于 5 个，输出情况与对比

---

## 一、任务与方法

### 1.1 执行约束
- 本机无 `gh` CLI、无 `GITHUB_TOKEN`（未认证限速 60 req/h/IP）
- 采用 **GitHub Search REST API（主线程控速）+ WebFetch 抓 github.com 网页（不耗 API 配额，可并行）+ DuckDuckGo HTML 补充** 的三段式调研模式
- **防伪装执行**：所有 agent 的结构化输出强制带 `sources_fetched` 字段（每条 URL + fetch_status: success/failed），可一眼识别是否真抓取、有无编造

### 1.2 Dynamic Workflow 编排（两轮）

**第一轮 `wf_06188a66-800`**：5 个并行搜索 agent（多策略）→ 去重 → top12 深度调研 → 对抗核验
- Agent 1-3：GitHub Search API（英文 pet/dog/cat behavior + 中文"宠物行为/犬行为"）
- Agent 4：WebFetch 抓 GitHub topic 页（animal-behavior / pet / dog-training）
- Agent 5：WebFetch 打 DuckDuckGo HTML + 顺藤摸瓜抓用户仓库列表
- 结果：38 候选 → 去重 36 → 深度调研 12 → **确认 2 个**（Animal-Kingdom、birnuruzunn/cats）
- **设计缺陷暴露**：主线程按 star 降序取 top12，0-star 纯文档知识库被高 star 工具/代码仓库挤出，未进入深度调研

**第二轮 `wf_2e64fea9-471`（补救）**：针对被 star 排序挤出的 10 个低 star/文档型候选，直接 deepdive → verify
- 结果：深度调研 10 → **确认 6 个**，驳回 4 个
- 修复了第一轮"按 star 取 top 致文档型知识库被埋没"的偏差

### 1.3 对抗核验机制
每个确认项目都经独立 agent 三/四角度尝试推翻：①URL 是否 404 ②是否其实不是知识库（app/游戏/商店/工具）③是否与宠物行为无关 ④是否只是无关项目误命中。默认怀疑，证据不足即判 uncertain/refuted。**8 个最终确认项目均通过对抗核验（verdict=confirmed）**。

### 1.4 执行统计
| 轮次 | agent 数 | token | 工具调用 | 耗时 |
|------|---------|-------|---------|------|
| 第一轮 | 19 | 1,085,410 | 101 | 494s |
| 第二轮 | 16 | 916,192 | 79 | 495s |
| **合计** | **35** | **2,001,602** | **180** | **~16.5min** |

---

## 二、确认项目总览（对比表）

共 **8 个项目**通过深度调研 + 对抗核验，确认为宠物/动物行为知识库或文档。

| # | 项目 | Star | 物种 | 行为主题 | 数据格式 | License | 活跃度 |
|---|------|------|------|---------|---------|---------|--------|
| 1 | [sutdcv/Animal-Kingdom](https://github.com/sutdcv/Animal-Kingdom) | 164 | 850 物种/6 大纲（野生动物为主） | 动作识别/姿态估计/视频时序定位（140 行为标签） | Excel 元数据 + 视频（离线） + Python 代码 | 未指定 | stale |
| 2 | [birnuruzunn/cats](https://github.com/birnuruzunn/cats) | 22 | 家猫 | 身体语言推断（尾巴/耳朵/眼睛） | CLIPS 专家系统规则（.clp） + markdown | 未指定 | stale |
| 3 | [sstroell/dog-behavior-framework](https://github.com/sstroell/dog-behavior-framework) | 0 | 犬 | 信任训练/情感训练/幼犬印记/创伤康复/情感召回 | markdown（纯文档） + CITATION.cff + Zenodo DOI | MIT | stale |
| 4 | [sstroell/puppy-development-timeline](https://github.com/sstroell/puppy-development-timeline) | 0 | 犬（幼犬） | 0-16 周发育 5 阶段/恐惧期/情绪记忆/印记 | 单 markdown 文件 | 未指定 | stale |
| 5 | [sstroell/dogsoul-dictionary](https://github.com/sstroell/dogsoul-dictionary) | 0 | 犬 | 训练术语词典（15 个术语，召回/信任/情绪调节） | markdown（README + glossary/ 目录） | CC BY 4.0 | stale |
| 6 | [sstroell/neurobond-docs](https://github.com/sstroell/neurobond-docs) | 0 | 犬 | 关系优先训练系统/神经联结/隐形牵引/反馈机制 | markdown（GitBook 风格 10 个 .md + SUMMARY.md） | 未指定 | stale |
| 7 | [kokitakahashi-baulife/dog-curriculum](https://github.com/kokitakahashi-baulife/dog-curriculum) | 0 | 家犬 | 服从命令/护理/等级/路线图/行为问题/课程阶段 | TypeScript → JSON（结构化数据层） | 未指定 | unknown |
| 8 | [codeWithRewaskar/shadow-reactivity-coach](https://github.com/codeWithRewaskar/shadow-reactivity-coach) | 0 | 犬 | 反应性训练（26 技术/20 品种画像/3 类反应框架） | markdown（SKILL.md 主） + MCP TS 代码 | CC-BY-4.0 | stale |

**分类视角**：
- **学术数据集**：#1 Animal-Kingdom（CVPR 2022，唯一高 star、唯一跨物种）
- **专家系统/可执行知识**：#2 birnuruzunn/cats（CLIPS 规则推断，唯一猫科）
- **纯文档知识库**（sstroell 系列 4 个 + shadow-reactivity-coach）：#3 #4 #5 #6 #8
- **结构化数据集**：#7 dog-curriculum（TS→JSON，机器可读）

---

## 三、项目详情

### 3.1 sutdcv/Animal-Kingdom ⭐164
- **URL**：https://github.com/sutdcv/Animal-Kingdom
- **性质**：CVPR 2022 论文配套的大规模动物行为理解数据集
- **覆盖**：850 个物种、6 大动物纲（哺乳/两栖/爬行/鸟/鱼等）、140 个动作/行为标签
- **任务**：动作识别（30K 视频序列）、姿态估计（33K 帧）、视频时序定位（50h 标注视频）；含作者提出的 CARe 模型（针对未见过动物的行为泛化）
- **优势**：学术权威性高（CVPR 同行评审）；规模与多样性罕见；多任务一体；含完整代码与环境脚本可复现
- **不足**：**非宠物专属**——覆盖野生/多物种动物行为，与家养宠物定位有偏差；数据集经 Google Form 离线分发，不在 repo 内直接可取；无 LICENSE（商用合规不明）；140 行为标签明细未在 README 列出；近期维护停滞
- **核验结论**：confirmed（独立三次 WebFetch，URL 真实、README 与论文吻合；唯一保留意见是"宠物"定性偏宽，实为 broader animal/wildlife behavior）

### 3.2 birnuruzunn/cats ⭐22
- **URL**：https://github.com/birnuruzunn/cats
- **性质**：用 CLIPS 专家系统编码猫的身体语言与行为知识，可执行推断
- **覆盖**：家猫（felis catus）；尾巴/耳朵/眼睛/身体动作 → 行为状态推断
- **格式**：cats.clp（产生式规则）+ README；README 明确写 "represents the behavioral knowledge of cats"
- **优势**：**唯一以可执行知识库形式编码猫行为**的项目；主题聚焦身体语言解读；CLIPS 规则可推理而非静态文档
- **不足**：知识封装在 CLIPS 源码中而非结构化数据集，不便外部系统消费；规模极小（2 文件/7 commits/单贡献者）；无 license；活跃度低
- **核验结论**：confirmed（三角度推翻均失败；main 分支 404 仅因默认分支为 master，改抓 master 即获 README 与 cats.clp）

### 3.3 sstroell/dog-behavior-framework ⭐0
- **URL**：https://github.com/sstroell/dog-behavior-framework
- **性质**：基于信任的犬类行为概念框架（纯文档，non-coding repo）
- **覆盖**：trust-based off-leash training、情感行为训练、人犬沟通、幼犬印记协议 0-16 周、创伤康复清单、情感召回流程图
- **核心理念**："Connection instead of correction"、"Recall without force"
- **作者**：Sebastian Stroeller（Zoeta Dogsoul，泰国清迈，犬类行为学家 + NLP 专家）
- **优势**：主题聚焦专业；含路线图与阶段化训练协议；提供 CITATION.cff + Zenodo DOI 支持学术引用；MIT 许可
- **不足**：体量极小（3 文件/单 README）；0 star 无社区关注；路线图多项 TODO 未落地；物种单一；无结构化知识
- **核验结论**：confirmed（四角度推翻均失败：URL 可达、纯文档无代码、明确犬行为主题、框架/清单/流程图属知识库形态）

### 3.4 sstroell/puppy-development-timeline ⭐0
- **URL**：https://github.com/sstroell/puppy-development-timeline
- **性质**：幼犬发育行为知识库（单文件 README，无代码）
- **覆盖**：出生至 16 周龄 5 阶段——新生儿期(0-2w)、过渡期(2-3w)、社会化期(3-7w)、关键期(8-12w)、适应期(12-16w)
- **主题**：神经系统/感觉发育、社交信号、环境印记、情绪记忆、恐惧期、依恋、注意力塑造；含训练实践建议
- **优势**：覆盖幼犬行为学核心议题（恐惧期/情绪记忆/印记）；5 阶段结构化时间线表格；面向训练师/寄养/主人可操作
- **不足**：单文件，深度有限；仅 0-16 周不含成年犬；**无许可证**；无 star/fork；缺参考文献，知识可信度难核验
- **核验结论**：confirmed（四轴推翻均失败；GitHub topics 含 dog-behavior/canine-psychology/socialization/puppy-development）

### 3.5 sstroell/dogsoul-dictionary ⭐0
- **URL**：https://github.com/sstroell/dogsoul-dictionary
- **性质**：犬类训练行为术语词典（glossary）
- **覆盖**：15 个专有术语——Neurobond、Soul Recall、Real-Life Recall、Off-Leash Trust、Invisible Leash、Emotional Calibration、Nervous System Sync、Relational Leadership 等
- **结构**：每条 = 标题 + Definition + Explanation + Related Terms（交叉引用）；含 glossary/ 目录（迁移中，仅完成 1/15）
- **优势**：**CC BY 4.0 开放许可**；术语条目结构化清晰；术语关联网络体现知识库特征；README 单文件即可获全部内容
- **不足**：仅 15 个**自创术语**（Zoeta Dogsoul 平台专有，非通用学术术语）；客观性与可迁移性存疑；方法论偏概念化/灵性化（如"Dogsoul Energy"），缺科学文献支撑；glossary 迁移不完整
- **核验结论**：confirmed（四角度推翻均失败；明确自识为 glossary，每条有定义/解释/关联术语，属知识库形态）

### 3.6 sstroell/neurobond-docs ⭐0
- **URL**：https://github.com/sstroell/neurobond-docs
- **性质**：NeuroBond 训练方法论文档库（GitBook/mdBook 风格）
- **覆盖**：relationship-first training；章节——core-philosophy、neurobond、invisible-leash、feedback-mechanism、training-in-practice、case-studies、glossary、introduction
- **核心理念**：nervous system attunement、emotional clarity、structured feedback（README 明确 "Built for dogs"）
- **优势**：纯文档型知识库，结构化清晰（GitBook SUMMARY.md 组织 8 章节）；覆盖完整方法论链路
- **不足**：极早期（3 commits/0 star/0 fork）；**无许可证**；README 仅 7 行极简；物种单一仅狗；"Backed by behavioral science" 文本被截断无法验证科学依据
- **核验结论**：confirmed（四角度推翻均失败；10 个 .md 文件含 SUMMARY.md，纯文档无代码）

### 3.7 kokitakahashi-baulife/dog-curriculum ⭐0
- **URL**：https://github.com/kokitakahashi-baulife/dog-curriculum
- **性质**：家犬训练课程结构化数据层（TypeScript → JSON），被 baudog.world 网站与 iOS 训练 app 共用
- **覆盖**：commands（带口令）、careTasks（护理）、levels（训练等级/测试，含 testType=trial/duration/tally、measure 自动评分、requires 解锁依赖）、roadmap（お迎え→マスター）、lifeStages、problems、fundamentals、missions、program（programPhases/milestones）
- **优势**：**schema 契约清晰的结构化犬训练课程数据集**（单一真相源）；覆盖面全；有 OTA 版本化分发机制；机器可读 JSON 端点
- **不足**：无 License；README 仅文档化 schema，实际内容藏在 .ts 源文件需读源码；**非可读文档**（TS→JSON 而非 markdown/wiki）；物种范围窄（家犬）；活跃度极低
- **核验结论**：confirmed（三角度推翻均失败；README 明确"共有データ層"，非 app/shop/game；数据模型全部围绕犬行为/训练）

### 3.8 codeWithRewaskar/shadow-reactivity-coach ⭐0
- **URL**：https://github.com/codeWithRewaskar/shadow-reactivity-coach
- **性质**：反应性犬训练教练 LLM 知识库（SKILL.md，可粘贴进任意 LLM）
- **覆盖**：reactivity training，force-free 循证；三类反应框架（恐惧型/挫折屏障型/兴奋过度唤起型）；26 个训练技术（DS/CC、LAT、Engage-Disengage、BAT 2.0、pattern games、stationing、muzzle conditioning、紧急协议等）；20 个品种特异性反应画像
- **安全护栏**：风险等级升级、厌恶方法护栏、医学/认证训练师转介（引用 IAABC、CCPDT、KPA）
- **优势**：方法学严谨（force-free、循证，引用认证机构）；**品种感知**而非通用建议；**CC-BY-4.0 开放许可**；含 10 个对话示例；单一 SKILL.md 即可独立使用
- **不足**：0 star/fork/watcher；混码仓（文档+MCP TS 代码）致语言统计误导（TS 97% 不反映文档为主）；20 品种画像未在 README 枚举；早期无 release
- **核验结论**：confirmed（三角度推翻均失败；raw README 扫描零商业/零游戏，结构化知识表 26 技术 + 20 品种 + 3 类框架 + 4 认证 + 7 书籍，属策展知识库）

---

## 四、驳回项目及原因

两轮共深度调研 22 个候选，驳回 14 个。驳回原因均为"非宠物行为知识库/文档"——多是工具、app 源码、游戏或无关项目误命中。

| 项目 | Star | 驳回原因 |
|------|------|---------|
| Ido-Levi/claude-code-tamagotchi | 430 | 虚拟 Tamagotchi + AI 行为监控工具，"behavioral"指 AI 行为非动物行为 |
| olivierfriard/BORIS | 241 | 通用行为观察记录软件（工具），本身不含任何物种/行为知识，用户需自定义 ethogram |
| ehsanik/dogTorch | 83 | 狗行为建模 ML 论文代码，非知识库/文档 |
| Vetdatahub/VetDataHub | 44 | 兽医医学数据集框架（临床/基因/流行病），不涉行为学；仓库实质是贡献指南+空框架 |
| vocalpy/vocalpy | 43 | 鸟类声学通信 Python 包（工具库），非行为知识 |
| TheChymera/behaviopy | 26 | 行为数据分析可视化 Python toolkit，非知识库 |
| unl-cchil/canine_precise_dispenser | 24 | 犬认知实验零食分配器硬件/软件工程，不含行为知识 |
| MartianZoo/solarnet | 16 | 桌游 Terraforming Mars 引擎，"Pets"是游戏 DSL，与真实动物无关 |
| wandb/catz | 16 | 猫 GIF 视频帧预测 ML 竞赛，无行为标签，"behavior"指视觉帧预测 |
| fruitmob/murderface-pets | 11 | FiveM/GTA 游戏宠物伴侣系统脚本，非真实动物行为 |
| catiseyeqaq/Real-time-Monitoring-and-Analysis-of-Pet-Behavior | 7 | 实为 ultralytics YOLO fork，README 是框架文档，宠物逻辑仅一个 Gradio 入口文件 |
| orujovshah/Classification-of-Dogs-Emotional-Behaviour | 2 | 犬情绪分类 ML 训练代码，不内置行为知识/数据 |
| alms93/SingleBehaviorLab | 7 | 通用动物视频行为定位训练工具，不内置 ethogram |
| ryanpeach/DogBarking | 0 | 狗叫检测+高频声制止 app，行为仅是功能场景，无知识内容 |

> **关键观察**：高 star 项目（BORIS 241、dogTorch 83、vocalpy 43）多是**行为学研究工具/ML 代码**，而非"行为知识库/文档"。真正的纯文档知识库（sstroell 系列、shadow-reactivity-coach）star 均为 0，在 GitHub 上属于长尾。这正是第一轮按 star 取 top12 漏掉它们的原因。

---

## 五、结论与选型建议

### 5.1 关键发现
1. **GitHub 上"宠物行为知识库/文档"是稀缺品类**——高 star 项目多是工具/数据集/ML 代码，纯知识库文档 star 极低（多为 0）
2. **犬类占绝对主导**：8 个确认项目中 7 个聚焦犬，仅 birnuruzunn/cats 覆盖猫，无其他宠物（兔、鸟、啮齿等）专属行为知识库
3. **sstroell（Zoeta Dogsoul）一人贡献了 4 个知识库**，是该领域最活跃的文档型贡献者，但方法论偏概念化、缺科学文献支撑
4. **学术级 vs 应用级分野明显**：Animal-Kingdom 是唯一学术权威（CVPR），其余均为个人/小团队应用级知识库

### 5.2 按用途选型建议

| 用途 | 推荐项目 | 理由 |
|------|---------|------|
| 跨物种行为识别研究/模型训练 | #1 Animal-Kingdom | 唯一学术级、大规模、多任务、可复现 |
| 猫科行为知识/可执行推断 | #2 birnuruzunn/cats | 唯一猫科 + CLIPS 规则可推理 |
| 犬类训练方法论参考 | #3 dog-behavior-framework、#6 neurobond-docs | 框架完整、理念清晰、可学术引用（前者 MIT + Zenodo DOI） |
| 幼犬发育/关键期知识 | #4 puppy-development-timeline | 0-16 周 5 阶段结构化时间线 |
| 犬训练术语体系 | #5 dogsoul-dictionary | CC BY 4.0、结构化术语词典 |
| 机器可读犬训练课程数据 | #7 dog-curriculum | TS→JSON schema 契约清晰，可直接接入系统 |
| 反应性犬训练/LLM 知识注入 | #8 shadow-reactivity-coach | SKILL.md 可粘贴进 LLM，26 技术 + 20 品种画像，CC-BY-4.0 |

### 5.3 局限性
- 中文宠物行为知识库在 GitHub 上覆盖稀疏（"宠物行为/犬行为"关键词未单独命中高质量中文仓库）；若需中文来源，建议补搜知乎/CSDN/哔哩哔哩及 HuggingFace Datasets
- 未覆盖 HuggingFace Datasets、Zenodo、Kaggle 等数据集平台（仅限 GitHub）
- 0 star 项目的知识可信度未经第三方验证，使用前应交叉核对来源

---

## 六、执行元数据

- **Workflow 脚本**：`code/pet-behavior-kb-research/workflow.js`（第一轮）、`code/pet-behavior-kb-research/workflow2.js`（第二轮）
- **总 agent 数**：35（5 搜索 + 12+10 深度调研 + 8 对抗核验）
- **总 token**：2,001,602
- **总工具调用**：180（全部 WebFetch / Bash curl / StructuredOutput，无伪装执行）
- **防伪装校验**：所有 agent 返回 `sources_fetched`，每条带 `fetch_status`；8 个确认项目均经独立 agent 对抗核验（verdict=confirmed）
- **核验抽样**：
  - Animal-Kingdom：3 次独立 WebFetch（主页/raw master README/根目录），raw/main 404 仅因默认分支为 master，非仓库缺失
  - birnuruzunn/cats：3 路径推翻均失败，CLIPS 源码 cats.clp 真实存在
  - sstroell 系列 4 个：四轴推翻（404/非知识库/非宠物行为/游戏工具商店）均失败
  - dog-curriculum、shadow-reactivity-coach：三轴推翻均失败
