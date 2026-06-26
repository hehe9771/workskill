# AI 原生智能表格/表单 — GitHub 开源项目调研

> 日期: 2026-06-25 | 调研范围: GitHub 开源项目

---

## 一、项目总览

### 1.1 AI 智能表格类

| 项目 | ⭐ Stars | 定位 | AI 能力 | 技术栈 |
|------|---------|------|---------|--------|
| **NocoDB** | 63.6k | 开源 Airtable | ❌ 无原生 AI | Vue 3 + TypeScript |
| **APITable** | 15.4k | 多维表格平台 | ✅ ChatGPT 集成 | Next.js + NestJS + Spring Boot |
| **Teable** | 21.4k | 高性能表格 | ✅ 原生 AI | Next.js + NestJS + PostgreSQL |
| **AFFiNE** | 69.8k | All-in-one 工作台 | ✅ 多模态 AI | React + Vite + Electron + CRDT |
| **Anytype** | 8.3k | 本地优先工作台 | ✅ AI Agents | Electron + TypeScript + Go |

### 1.2 动态表单生成类

| 项目 | ⭐ Stars | 定位 | AI 能力 | 技术栈 |
|------|---------|------|---------|--------|
| **Formily** | 45.9k | 动态表单框架 | ❌ 无 AI，但 Schema 驱动 | TypeScript + React/Vue |
| **react-jsonschema-form** | 15.8k | JSON Schema → 表单 | ❌ 无 AI，纯 Schema 渲染 | TypeScript + React |

---

## 二、重点项目详细分析

### 2.1 Teable ⭐ 最推荐

**GitHub**: https://github.com/teableio/teable
**Stars**: 21.4k | **技术栈**: TypeScript / Next.js / NestJS / PostgreSQL

**核心能力**：
- 类 Excel 表格界面，支持**百万级行**数据
- 支持 Grid / Form / Kanban / Gallery / Calendar 多视图
- 批量编辑、聚合、过滤、公式、SQL 查询
- 导入/导出、数据校验
- **原生 AI 集成**（企业版）

**与我们方案的契合度**：
| 需求 | Teable 支持度 |
|------|-------------|
| 表格内编辑 | ✅ 完整支持 |
| 百万级数据 | ✅ 原生支持 |
| 多视图切换 | ✅ 5 种视图 |
| AI 辅助 | ✅ 企业版支持 |
| 数据校验 | ✅ 内置 |
| SQL 查询 | ✅ 支持 |
| 动态表单 | ✅ Form 视图 |

**评价**：最接近我们需要的"AI 智能表格"。表格性能强（百万行），已有 AI 集成，可以作为底层表格引擎，上层叠加本体驱动的动态表单逻辑。

---

### 2.2 Formily ⭐ 表单生成最佳选择

**GitHub**: https://github.com/formilyjs/formily
**Stars**: 45.9k | **技术栈**: TypeScript + React/Vue

**核心能力**：
- **JSON Schema 驱动**的动态表单生成
- 可视化 Form Builder（拖拽设计表单）
- 字段独立管理，高性能（不整树重渲染）
- 支持 React / React Native / Vue 2 / Vue 3
- 集成 Alibaba Fusion / Ant Design 组件
- 复杂数据联动（Side Effects 独立管理）

**与我们方案的契合度**：
| 需求 | Formily 支持度 |
|------|---------------|
| JSON Schema → 表单 | ✅ 核心能力 |
| 动态字段渲染 | ✅ 完整支持 |
| 字段联动 | ✅ Side Effects 机制 |
| 可视化设计器 | ✅ Designable |
| AI 集成 | ❌ 需自行叠加 |
| 后端驱动渲染 | ✅ Protocol Driven |

**评价**：**动态表单生成的最佳选择**。我们的方案中"本体定义 → JSON Schema → 动态表单"这条链路，Formily 可以直接承接后半段。只需在 Formily 上层加一个"本体 → JSON Schema"的转换层。

---

### 2.3 APITable

**GitHub**: https://github.com/apitable/apitable
**Stars**: 15.4k | **技术栈**: Next.js + NestJS + Spring Boot + React

**核心能力**：
- 实时多人协作（OT 算法）
- 自动表单生成
- 无限跨表关联
- 7 种视图类型
- **AI 版本集成 ChatGPT**
- 行列级权限控制

**评价**：AI 集成已有基础（ChatGPT），协作能力强。但技术栈偏重（Java 后端），与我们纯 Python 后端方案不太匹配。

---

### 2.4 NocoDB

**GitHub**: https://github.com/nocodb/nocodb
**Stars**: 63.6k | **技术栈**: Vue 3 + TypeScript

**核心能力**：
- 类 Excel 表格界面
- 多种视图（Grid / Gallery / Kanban / Form）
- App Store 自动化工作流
- REST API + SDK
- Docker 部署
- 支持 SQLite / PostgreSQL

**评价**：Star 最多的开源表格项目，但**没有原生 AI 能力**。适合作为纯数据表格使用，需要自行叠加 AI 层。

---

### 2.5 AFFiNE

**GitHub**: https://github.com/toeverything/AFFiNE
**Stars**: 69.8k | **技术栈**: TypeScript + React + Vite + Electron + CRDT

**核心能力**：
- Docs + Whiteboard 融合
- **多模态 AI**（一句话生成报告/演示/思维导图）
- 本地优先（Local-first）
- 实时协作
- 私有化部署

**评价**：Star 最高，AI 能力最强（多模态），但定位是"all-in-one 工作台"而非专业的数据表格系统。更适合作为参考，而非直接采用。

---

## 三、方案推荐

### 3.1 推荐组合

```
我们的 AI 原生客户系统 = Formily（动态表单）+ Teable（智能表格）+ 自建 AI 层

┌──────────────────────────────────────────────────────┐
│  AI 对话引擎（自建）                                  │
│  ┌───────────┐ ┌───────────┐ ┌───────────────────┐  │
│  │ Text-to-  │ │ GraphRAG  │ │ 意图识别 + Agent   │  │
│  │ Cypher    │ │           │ │ 路由              │  │
│  └───────────┘ └───────────┘ └───────────────────┘  │
├──────────────────────────────────────────────────────┤
│  交互层                                              │
│  ┌────────────────────┐  ┌───────────────────────┐  │
│  │ Formily            │  │ Teable                │  │
│  │ (动态表单生成)      │  │ (智能表格/批量录入)    │  │
│  │                    │  │                       │  │
│  │ 本体 → JSON Schema │  │ Excel 式编辑          │  │
│  │ → 动态表单渲染     │  │ + AI 校验/补全        │  │
│  │ → AI 辅助填充      │  │ + 百万行性能          │  │
│  └────────────────────┘  └───────────────────────┘  │
├──────────────────────────────────────────────────────┤
│  数据层                                              │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │ MySQL (RDS)  │  │ Neo4j + n10s │                 │
│  └──────────────┘  └──────────────┘                 │
└──────────────────────────────────────────────────────┘
```

### 3.2 各组件职责

| 组件 | 职责 | 为什么选它 |
|------|------|-----------|
| **Formily** | 动态表单渲染 | JSON Schema 驱动，45.9k star，最成熟 |
| **Teable** | 智能表格/批量录入 | 百万行性能，多视图，已有 AI 基础 |
| **本体 → Schema 转换层** | 本体定义 → JSON Schema | 自建，连接本体和 Formily |
| **AI 对话引擎** | 意图识别 + Agent 路由 | 自建，LangChain + Neo4j |
| **MySQL** | 业务写入 | 已有，不动 |
| **Neo4j** | 知识图谱 + AI 查询 | 已有，已迁移 |

### 3.3 数据流

```
场景: 用户说"新增企业客户"

1. AI 对话引擎判断意图 → 返回表单描述
   { mode: "create", entityType: "EnterpriseCustomer" }

2. 本体 → Schema 转换层
   读取 ontology.ttl 中 EnterpriseCustomer 类定义
   → 生成 JSON Schema（必填字段 + 类型 + 校验规则）

3. Formily 渲染表单
   接收 JSON Schema → 动态生成表单 UI
   → 用户填写（或 AI 自动填充部分字段）

4. 用户提交
   → API → MySQL INSERT
   → 触发 ETL 同步到 Neo4j

场景: 用户说"批量导入 100 个联系人"

1. AI 对话引擎判断 → 打开表格模式

2. Teable 渲染表格
   → Excel 式界面，支持粘贴/拖拽
   → AI 实时校验（重复检测、格式校验）

3. 用户批量填入
   → 一键保存 → API → MySQL 批量 INSERT
   → 触发同步到 Neo4j
```

---

## 四、总结

| 问题 | 答案 |
|------|------|
| 有没有现成的"AI 原生智能表格"？ | **没有完全匹配的**，但有强力组件可组合 |
| 动态表单用什么？ | **Formily**（45.9k star，JSON Schema 驱动） |
| 智能表格用什么？ | **Teable**（21.4k star，百万行 + AI） |
| 需要自己开发什么？ | 本体→Schema 转换层 + AI 对话引擎 |
| 能否 100% 开源？ | ✅ 全部组件均为开源 |
