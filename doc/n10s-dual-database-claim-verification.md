# n10s「双库分离是事实默认」论断核验报告

*生成日期： 2026-08-04 | 方法： 官方一手文档直采 + 社区样本检索 | 置信度： 官方部分 高 / 社区部分 中*

## 结论（Executive Summary）

**论断不成立，且证据指向相反方向。**

「neo4j + n10s 与 neo4j native 双库分离是 n10s 圈子的事实默认架构」这一说法**没有官方或社区证据支持**。n10s（neosemantics）的官方设计哲学恰恰相反：**把 RDF 数据无损存进 Neo4j 属性图所在数据库，与原生图数据共存、用 Cypher 统一查询**。官方手册通篇以「the graph」（单数）为前提，mapping 机制的存在目的就是让导入的 RDF 与**已有图**的模式对齐——同库共存是设计意图本身，不是可选项。

「双库分离」在特定约束下是合理的工程模式（见下文「分库的合理场景」），但称其为「n10s 圈子的事实默认」属于过度概括。

## 一、官方一手证据（2025.06 分支手册直采）

### 1. 设计定位：RDF 存进 Neo4j 图内，而非另立库存

> "Neosemantics is a plugin that enables the **use of RDF in Neo4j**... **Store RDF data in Neo4j** in a lossless manner... On-demand **export property graph data from Neo4j as RDF**."
> — introduction.adoc

> "It imports and **persists into Neo4j** the triples returned by an URI."
> — import.adoc（n10s.rdf.import.fetch 描述）

仓库官方描述同样明确：*"Graph+Semantics: Import/Export RDF **from** Neo4j. SHACL Validation, Model mapping and more."*（949 stars，活跃维护，默认分支 2025.06，2026-08-04 仍有提交）

### 2. mapping 机制 = 为「同库对齐已有图」而设计

mapping.adoc 给出的两个 canonical 用例都以**同一个图**为前提：

- *"We have **a graph in Neo4j** that we want to publish as JSON-LD... map the elements in our graph to a public vocabulary"*
- *"import a public taxonomy (SKOS)... **persist it in Neo4j using our own schema terms**... `skos:narrower` 要叫 `:CHILD_CATEGORY` in **our Neo4j graph**"*

即：mapping 的价值恰恰是把外部 RDF 词汇表映射到**你库里已有的图模型**上。若默认双库分离，这套机制就失去存在意义。

### 3. 导出机制：任何原生图就地序列化为 RDF

> "it is possible to serialise in RDF **any Neo4j graph, even in the case when the data in Neo4j is not the result of importing RDF**."
> — export.adoc

原生属性图**不需要先进一个「RDF 库」**就能当 RDF 发布——这是「单库哲学」最直接的官方表述。

### 4. GraphConfig：按图（库）全局唯一且锁定

> "All settings defined in a Graph Config are **global** and remain valid for the **whole lifetime of the graph**... once data is imported... these will not be changeable **until the graph is emptied**."
> — config.adoc

约束前提：`CREATE CONSTRAINT n10s_unique_uri ON (r:Resource) ASSERT r.uri IS UNIQUE` —— RDF 资源以 `Resource` 标签节点形式落在**当前数据库**的属性图里。

### 5. 全文检索佐证

对 import.adoc / config.adoc / mapping.adoc（合计约 6.5 万字符）全文 grep `separate` / `multiple database` / `same graph` / `alongside` 等关键词：**无任何「建议分库存储」的表述**，仅一处无关的字面命中（IRI 后缀说明）。

### 6. 官方列举的实际用法（examples.adoc）

AWS 基础设施映射（awless 产 RDF → 导入 Neo4j 查询）、Refinitiv 数据集导入教程——全部为「导入同一个图后直接用」的模式。

## 二、社区样本（直接检索）

三渠道合计 40+ 条样本，**零「双库/分库架构」讨论**：

- **Neo4j 官方论坛 `neosemantics` tag**（tag JSON 直采，19 个主题）：全部是导入失败、SHACL 校验、Desktop 安装、SPARQL 支持提问（如 "Does SPARQL query execution is supported in Neosemantics plugin 5.x"）——无一例讨论数据应分库存储。
- **GitHub Issues**（`repo:neo4j-labs/neosemantics database in:title,body`，15 条）：全部是导入报错/安装问题——无架构层面分库讨论。
- **Stack Overflow `neosemantics` tag**：问题量很小，高票问题全部是「如何导入/建模/校验 OWL、SHACL」类，**无一例讨论「要不要分库」**。
- 论坛模糊搜索 `neosemantics separate database`、`n10s multiple databases`：无专门讨论帖浮出水面。

判断：社区讨论的全部重心是「怎么把 RDF 导进图里用」，「分库」在可见样本中从未作为架构话题出现。「事实默认」级别的共识若存在，理应在这些渠道留下痕迹——**正面证据完全缺失**。

## 三、「双库分离」说法的可能来源与合理场景

分库不是错，是**有条件适用**的工程模式，可能因此被误传为「默认」：

1. **GraphConfig 锁定约束**：一个库一个 GraphConfig 且导数据后不可改（config.adoc）。需以**不同配置**导入异构 RDF 数据集时，只能分库。
2. **对接既有 triple store**：组织已有 Jena/RDF4J/GraphDB 等 SPARQL 端点，Neo4j 侧做属性图分析——这是「两个系统」而非「n10s 双库」，n10s 在此只是 ETL 工具。
3. **staging → 应用库流水线**：Neo4j 4.x+ 多数据库特性下，RDF 暂存库清洗后转入应用库。属于数据工程惯例，非 n10s 特有架构。

## 四、Key Takeaways

- n10s 的事实默认是**单库混存**：RDF 以 Resource 节点/关系形式落在属性图内，与原生数据同库，Cypher 统一查询。
- 官方手册（含最新 2025.06 分支）**从未推荐** RDF 与原生图分库存储。
- mapping / GraphConfig / export-any-graph 三大机制的设计前提都是同库共存。
- 需要分库的真实触发条件：异构 RDF 需不同 GraphConfig、必须保留外部 SPARQL 端点、staging 流水线——是例外场景而非默认。

## 五、置信度与缺口

| 部分 | 置信度 | 说明 |
|---|---|---|
| 官方设计 = 单库 | **高** | 6 个一手文档直采，引文可复核 |
| 社区无「双库默认」共识 | **中高** | 论坛 tag 19 主题 + GitHub issues 15 条 + SO tag + 模糊搜索，40+ 样本零分库讨论；属「无正面证据 + 大量反向沉默」 |
| 中文社区说法溯源 | 低 | 未检索到「双库分离是 n10s 事实默认」的中文出处，不排除个别博客以讹传讹 |

## 来源清单

1. [neosemantics GitHub 仓库元数据](https://api.github.com/repos/neo4j-labs/neosemantics) — 描述、活跃度、分支状态
2. [introduction.adoc (2025.06)](https://github.com/neo4j-labs/neosemantics/blob/2025.06/docs/modules/ROOT/pages/introduction.adoc) — 官方定位：RDF 存进 Neo4j
3. [import.adoc (2025.06)](https://github.com/neo4j-labs/neosemantics/blob/2025.06/docs/modules/ROOT/pages/import.adoc) — 导入即持久化到当前库
4. [config.adoc (2025.06)](https://github.com/neo4j-labs/neosemantics/blob/2025.06/docs/modules/ROOT/pages/config.adoc) — GraphConfig 全局唯一且锁定
5. [mapping.adoc (2025.06)](https://github.com/neo4j-labs/neosemantics/blob/2025.06/docs/modules/ROOT/pages/mapping.adoc) — mapping 为同库对齐设计
6. [export.adoc (2025.06)](https://github.com/neo4j-labs/neosemantics/blob/2025.06/docs/modules/ROOT/pages/export.adoc) — 任意原生图可就地导出 RDF
7. [examples.adoc (2025.06)](https://github.com/neo4j-labs/neosemantics/blob/2025.06/docs/modules/ROOT/pages/examples.adoc) — 实际项目用法均为单库导入
8. [Neo4j Labs neosemantics 页](https://neo4j.com/labs/neosemantics/) — 手册版本止于 4.3，5.x/2025.x 文档在仓库 docs/ 内
9. [Neo4j 论坛 neosemantics tag](https://community.neo4j.com/tag/neosemantics)（tag JSON 直采 19 主题）— 全为导入/校验/安装问题，无分库讨论
10. [neosemantics GitHub Issues 检索](https://github.com/neo4j-labs/neosemantics/issues?q=database)（API 直采 15 条）— 全为报错类，无架构分库讨论
11. Stack Overflow `neosemantics` tag（api.stackexchange.com 直采）— 无分库讨论
12. community.neo4j.com search.json（两组关键词直采）— 无分库专帖

## 方法论备注

直采链路：GitHub REST API（仓库元数据、docs 目录、issues 检索）→ jsDelivr CDN 抓 adoc 原文（规避 raw.githubusercontent 429）→ Discourse tag/search JSON + Stack Exchange API 社区检索。曾派 3 个 WebFetch 调研 agent（官方补充/社区/架构反证），两批均因 `API Error: 400` 中途死亡、零产出；全部证据改由主线程直采完成，不依赖 agent 转述。
