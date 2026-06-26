# AI 原生客户系统：模块架构与交互设计

> 版本: v1.0 | 日期: 2026-06-25 | 从 0 到 1 设计

---

## 一、系统总览

### 1.1 什么是"AI 原生"

**不是**：在现有系统上加一个 AI 助手（AI 赋能）
**而是**：AI 就是一切，系统围绕 AI 构建（AI 原生）

```
传统系统架构:
  用户 → [表单/菜单 UI] → [REST API] → [MySQL] → [表格返回] → 用户看表格

AI 原生架构:
  用户 → [对话/意图] → [AI Agent] → [知识图谱 + 业务库] → [自然语言/可视化返回] → 用户得到答案
```

### 1.2 系统分层架构

```
┌─────────────────────────────────────────────────────────────┐
│  L5 交互层                                                  │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌────────────┐  │
│  │ Chat UI   │ │ Graph Viz │ │ Dashboard │ │ API Gateway│  │
│  └───────────┘ └───────────┘ └───────────┘ └────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  L4 智能分析层                                              │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐  │
│  │ 关系分析   │ │ 风险分析   │ │ 合规校验   │ │ 客户推荐   │  │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘  │
├─────────────────────────────────────────────────────────────┤
│  L3 AI 引擎层                                               │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐  │
│  │ 对话引擎   │ │ Text-to-  │ │ GraphRAG  │ │ 推理引擎   │  │
│  │           │ │ Cypher    │ │           │ │           │  │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘  │
├─────────────────────────────────────────────────────────────┤
│  L2 业务功能层                                              │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐  │
│  │客户管理 │ │联系人   │ │银行账户 │ │评级管理 │ │发票/报表│  │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘  │
├─────────────────────────────────────────────────────────────┤
│  L1 数据层                                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐   │
│  │ MySQL 业务库  │ │ Neo4j 知识图谱│ │ 本体 + 向量索引   │   │
│  └──────────────┘ └──────────────┘ └──────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  L0 基础设施层                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ 认证授权  │ │ 数据同步  │ │ 日志监控  │ │ 系统管理      │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、技术栈与标准

### 2.1 技术选型

| 层 | 组件 | 技术 | 版本 | 说明 |
|----|------|------|------|------|
| L0 | 认证 | Keycloak / Casdoor | latest | OAuth2 + OIDC |
| L0 | 数据同步 | Python ETL + APScheduler | - | 增量同步 |
| L0 | 监控 | Prometheus + Grafana | latest | 系统 + AI 指标 |
| L1 | 关系库 | MySQL (Aliyun RDS) | 8.0 | 业务写入 |
| L1 | 图数据库 | Neo4j Community | 5.26 | 知识图谱 |
| L1 | 本体 | neosemantics | 5.26.0 | RDF/OWL |
| L2 | 后端框架 | FastAPI | 0.110+ | 异步高性能 |
| L2 | ORM | SQLAlchemy 2.0 | 2.0+ | MySQL 访问 |
| L2 | 图驱动 | neo4j Python Driver | 5.x | Bolt 协议 |
| L3 | AI 框架 | LangChain | 0.2+ | LLM 编排 |
| L3 | LLM | Claude API / GPT-4 | - | 主力模型 |
| L3 | Embedding | text-embedding-3-small | - | 向量化 |
| L3 | GraphRAG | neo4j-graphrag | 1.x | 图检索增强 |
| L4 | 图算法 | Neo4j GDS | 5.x | 社区检测/PageRank |
| L5 | 对话 UI | React + Chat UI Kit | - | 前端对话 |
| L5 | 图谱可视化 | Neo4j Bloom / ECharts | - | 关系网络 |
| L5 | API 网关 | FastAPI + Nginx | - | 路由/限流 |

### 2.2 编码标准

| 标准 | 说明 |
|------|------|
| API 设计 | RESTful + SSE（流式返回 AI 回答） |
| 错误处理 | 统一错误码 + 结构化错误体 |
| 日志 | structlog 结构化日志，JSON 格式 |
| 测试 | pytest + httpx（异步测试） |
| 容器化 | Docker Compose 编排全部服务 |
| 配置 | pydantic-settings，环境变量驱动 |

### 2.3 项目结构

```
ai-customer-system/
├── docker-compose.yml              # 全部服务编排
├── .env                            # 环境变量
│
├── backend/                        # FastAPI 后端
│   ├── main.py                     # 应用入口
│   ├── config.py                   # 配置管理
│   │
│   ├── core/                       # L0 基础设施
│   │   ├── auth/                   # 认证授权
│   │   ├── sync/                   # 数据同步
│   │   └── admin/                  # 系统管理
│   │
│   ├── data/                       # L1 数据层
│   │   ├── mysql/                  # MySQL 连接 & 模型
│   │   ├── neo4j/                  # Neo4j 连接 & 查询
│   │   └── ontology/               # 本体管理
│   │
│   ├── business/                   # L2 业务功能
│   │   ├── customer/               # 客户管理
│   │   ├── contact/                # 联系人
│   │   ├── bank_account/           # 银行账户
│   │   ├── rating/                 # 评级
│   │   ├── invoice/                # 发票
│   │   └── report/                 # 报表
│   │
│   ├── ai/                         # L3 AI 引擎
│   │   ├── chat/                   # 对话引擎
│   │   ├── text2cypher/            # 自然语言→Cypher
│   │   ├── graphrag/               # GraphRAG
│   │   └── reasoning/              # 推理引擎
│   │
│   └── analysis/                   # L4 智能分析
│       ├── relation/               # 关系分析
│       ├── risk/                   # 风险分析
│       ├── compliance/             # 合规校验
│       └── recommendation/         # 客户推荐
│
├── frontend/                       # L5 交互层
│   ├── chat/                       # 对话界面
│   ├── graph/                      # 图谱可视化
│   └── dashboard/                  # 管理面板
│
└── tests/                          # 测试
    ├── unit/
    ├── integration/
    └── e2e/
```

---

## 三、L0 基础设施层

---

### 模块 0.1：认证授权

**定义**：统一身份认证、权限控制、多租户支持

**AI 原生交互方式**：
- 用户通过对话界面自然登录："以张三身份登录"
- 权限控制影响 AI 回答范围（不同角色看到不同数据）
- AI Agent 调用业务 API 时携带用户身份

**后端实现**：

```
API 端点:
  POST   /api/auth/login           # 登录获取 token
  POST   /api/auth/logout          # 登出
  GET    /api/auth/me              # 当前用户信息
  GET    /api/auth/permissions     # 用户权限列表

Agent:
  auth_agent                      # 认证 Agent（内部）
  - 校验 token
  - 注入用户上下文到 AI 对话
  - 控制数据可见范围
```

**数据流**：
```
用户对话 "查看张三公司" → Auth Agent 注入用户角色/机构
  → 查询时自动添加 WHERE 机构过滤条件 → 只返回该用户权限内的数据
```

---

### 模块 0.2：数据同步（ETL）

**定义**：MySQL → Neo4j 增量数据同步，保证知识图谱与业务库一致

**AI 原生交互方式**：
- 用户问 "数据是最新的吗？" → AI 查询同步状态
- 用户说 "立即同步最新数据" → 触发手动同步
- 同步异常时 AI 主动告警

**后端实现**：

```
API 端点:
  GET    /api/sync/status          # 同步状态
  POST   /api/sync/trigger          # 手动触发同步
  GET    /api/sync/history          # 同步历史记录

Agent:
  sync_agent                       # 同步调度 Agent
  - 定时任务（每日 Hive 更新后触发）
  - 增量检测（updated_at > last_sync）
  - 变更行 → RDF 生成 → n10s 导入

内部组件:
  MySQLReader → RDFGenerator → Neo4jLoader
  - 分页读取 MySQL 变更数据
  - rdflib 生成 Turtle 格式
  - docker cp + n10s.rdf.import.fetch 导入
```

---

### 模块 0.3：系统管理

**定义**：系统配置、用户管理、日志审计

**AI 原生交互方式**：
- "系统运行状态怎么样？" → AI 查询健康指标
- "修改 LLM 模型为 Claude 3.5" → AI 调用配置 API
- "查看最近的错误日志" → AI 查询日志

**后端实现**：

```
API 端点:
  GET    /api/admin/health          # 健康检查
  GET    /api/admin/config          # 系统配置
  PUT    /api/admin/config          # 修改配置
  GET    /api/admin/users           # 用户列表
  GET    /api/admin/audit-log       # 审计日志

Agent:
  admin_agent                      # 管理 Agent
  - 系统健康监控
  - 配置变更管理
  - 日志查询与告警
```

---

## 四、L1 数据层

---

### 模块 1.1：MySQL 业务库

**定义**：关系型数据存储，业务写入层，事务中心

**AI 原生交互方式**：
- AI 不直接暴露 MySQL 给用户
- 当 AI 判断需要写入操作时，自动调用 MySQL API
- 用户说 "把张三公司的电话改成 138xxxx" → AI 调用 MySQL UPDATE

**后端实现**：

```
组件:
  MySQLConnection                  # 连接池管理
  CustomerRepository               # 客户 CRUD
  ContactRepository                # 联系人 CRUD
  BankAccountRepository            # 账户 CRUD
  RatingRepository                 # 评级 CRUD
  InvoiceRepository                # 发票 CRUD

API 端点 (内部，不直接暴露给前端):
  POST   /api/data/customer         # 新增客户
  PUT    /api/data/customer/{id}    # 修改客户
  DELETE /api/data/customer/{id}    # 删除客户
  GET    /api/data/customer/{id}    # 查单个客户
  GET    /api/data/customers        # 客户列表（分页）

标准:
  - 所有写操作走 MySQL
  - 使用 SQLAlchemy 事务管理
  - 操作后触发 Neo4j 增量同步
```

---

### 模块 1.2：Neo4j 知识图谱

**定义**：图数据存储，关系查询，图谱分析

**AI 原生交互方式**：
- 所有涉及关系、分析、智能查询的操作走 Neo4j
- AI Agent 生成 Cypher 查询 Neo4j
- 图谱结构本身就是 AI 的"记忆"

**后端实现**：

```
组件:
  Neo4jConnection                  # Bolt 连接管理
  GraphQueryExecutor               # Cypher 执行器
  GraphTraversalService            # 图遍历服务

API 端点:
  POST   /api/graph/query           # 执行 Cypher
  POST   /api/graph/traverse        # 图遍历
  GET    /api/graph/stats           # 图谱统计
  POST   /api/graph/import          # 导入 RDF

标准:
  - 所有读分析操作走 Neo4j
  - Cypher 查询超时 30 秒
  - 查询结果缓存（TTL 5 分钟）
```

---

### 模块 1.3：本体管理

**定义**：OWL/RDFS 本体定义、SHACL 约束、命名空间管理

**AI 原生交互方式**：
- 本体是 LLM 理解数据的"词典"
- Text-to-Cypher 时 LLM 读取本体生成准确查询
- 用户说 "本体里有哪些类？" → AI 查询本体结构

**后端实现**：

```
API 端点:
  GET    /api/ontology/classes       # 类列表
  GET    /api/ontology/properties    # 属性列表
  GET    /api/ontology/relations     # 关系列表
  POST   /api/ontology/upload        # 上传本体文件
  POST   /api/ontology/validate      # SHACL 校验

Agent:
  ontology_agent                    # 本体 Agent
  - 提供本体结构给 LLM 作为上下文
  - 校验数据是否符合本体约束
  - 辅助 Text-to-Cypher 生成

标准:
  - 本体文件格式: Turtle (.ttl)
  - 命名空间: cus:http://mftcc.com/ontology/cus#
  - 每个类有 rdfs:label (中文) + rdfs:comment
```

---

## 五、L2 业务功能层

> 每个模块同时支持两种交互模式：
> - **传统模式**：REST API + 表单界面（CRUD 操作）
> - **AI 模式**：对话界面 + Agent（智能查询/分析）

---

### 模块 2.1：客户管理

**定义**：客户全生命周期管理（登记、查看、修改、删除）

**AI 原生交互方式**：

```
场景 1 - 自然语言查客户:
  用户: "找一下注册资本超过 5000 万的制造业企业"
  AI Agent → Text-to-Cypher → Neo4j 查询 → 自然语言回答

场景 2 - 修改客户信息:
  用户: "把三一集团的联系电话改成 010-xxxx"
  AI Agent → 意图识别[修改] → MySQL UPDATE → 确认回复

场景 3 - 新增客户:
  用户: "新增一个客户：张三公司，统一社会信用代码 xxx"
  AI Agent → 提取信息 → MySQL INSERT → 返回客户号

场景 4 - 客户全景画像:
  用户: "分析三一集团的全面情况"
  AI Agent → 图遍历(1-3度) → 数据汇总 → LLM 生成报告
```

**后端实现**：

```
API 端点 (传统 CRUD):
  POST   /api/customers              # 新增
  GET    /api/customers              # 列表
  GET    /api/customers/{id}         # 详情
  PUT    /api/customers/{id}         # 修改
  DELETE /api/customers/{id}         # 删除

Agent:
  customer_query_agent              # 客户查询 Agent
  - Text-to-Cypher 生成
  - 本体辅助理解
  - 多轮对话上下文管理

  customer_profile_agent            # 客户画像 Agent
  - 图遍历获取全部关联数据
  - LLM 生成结构化报告
  - 支持 "深入看某一项" 多轮对话

内部调用:
  customer_query_agent:
    1. 读取本体 → 获取 Customer 类定义
    2. LLM + 本体 → 生成 Cypher
    3. Neo4j 执行 → 返回结果
    4. LLM 格式化 → 自然语言回答
```

---

### 模块 2.2：联系人管理

**定义**：客户联系人信息维护与关联分析

**AI 原生交互方式**：

```
场景 1 - 查联系人:
  用户: "三一集团有哪些联系人？"
  AI → MATCH (c)-[:hasContact]->(p) ... → 列表回答

场景 2 - 联系人交叉分析:
  用户: "王五这个人在哪些企业担任联系人？"
  AI → 反向遍历 → 找到所有关联客户 → 汇总回答

场景 3 - 新增联系人:
  用户: "给三一集团加一个联系人：李四，电话 139xxxx"
  AI → MySQL INSERT → 触发同步 → Neo4j 更新
```

**后端实现**：

```
API 端点:
  POST   /api/contacts               # 新增
  GET    /api/contacts               # 列表
  GET    /api/customers/{id}/contacts # 某客户的联系人
  PUT    /api/contacts/{id}          # 修改
  DELETE /api/contacts/{id}          # 删除

Agent:
  contact_analysis_agent            # 联系人分析 Agent
  - 交叉查询（一个人出现在多个企业）
  - 关键人物识别（出现在最多企业的联系人 Top N）
  - 联系人网络可视化数据生成
```

---

### 模块 2.3：银行账户管理

**定义**：客户银行账户信息管理

**AI 原生交互方式**：

```
场景 1:
  用户: "三一集团在哪些银行开了户？"
  AI → 图遍历 Customer→BankAccount→Bank → 回答

场景 2:
  用户: "工商银行有多少客户在他们那开户？"
  AI → 反向遍历 Bank→BankAccount→Customer → 统计回答
```

**后端实现**：

```
API 端点:
  POST   /api/bank-accounts          # 新增
  GET    /api/customers/{id}/accounts # 客户账户列表
  PUT    /api/bank-accounts/{id}     # 修改

Agent:
  bank_analysis_agent               # 银行分析 Agent
  - 银行客户分布统计
  - 账户用途分析
  - 异常账户检测
```

---

### 模块 2.4：评级管理

**定义**：客户信用评级管理、评级模型配置

**AI 原生交互方式**：

```
场景 1:
  用户: "评级为 AA 的制造业企业有哪些？"
  AI → 图查询过滤 → 排序回答

场景 2:
  用户: "三一集团的评级是怎么算出来的？用了哪些指标？"
  AI → 查询评级模型 + 指标 → 解释评级逻辑

场景 3:
  用户: "同行业中评级最高的前 10 家企业"
  AI → 行业过滤 + 评级排序 → 排名回答
```

**后端实现**：

```
API 端点:
  GET    /api/ratings                # 评级列表
  GET    /api/ratings/{customerId}   # 某客户评级
  POST   /api/ratings                # 录入评级
  GET    /api/eval-models            # 评级模型列表
  GET    /api/eval-models/{id}       # 模型详情+指标

Agent:
  rating_analysis_agent             # 评级分析 Agent
  - 评级分布统计
  - 同行业排名
  - 评级变化趋势
  - 评级指标解读
```

---

### 模块 2.5：发票管理

**定义**：客户发票信息管理

**AI 原生交互方式**：

```
场景 1:
  用户: "三一集团的开票信息是什么？"
  AI → 查询 Invoice 节点 → 返回发票详情

场景 2:
  用户: "哪些客户是一般纳税人？"
  AI → 查询发票信息中的纳税人类型 → 列表
```

**后端实现**：

```
API 端点:
  POST   /api/invoices               # 新增
  GET    /api/customers/{id}/invoices # 客户发票
  PUT    /api/invoices/{id}          # 修改

Agent: (无独立 Agent，由 customer_query_agent 统一处理)
```

---

### 模块 2.6：财务报表管理

**定义**：客户财务报表数据管理

**AI 原生交互方式**：

```
场景 1:
  用户: "三一集团最近一期的总资产是多少？"
  AI → 查询 FinancialReport → 返回数据

场景 2:
  用户: "资产负债率超过 70% 的企业有哪些？"
  AI → 计算资产负债率 → 过滤 → 列表
```

**后端实现**：

```
API 端点:
  POST   /api/financial-reports      # 录入报表
  GET    /api/customers/{id}/reports # 客户报表
  GET    /api/financial/analysis     # 财务分析

Agent:
  financial_analysis_agent          # 财务分析 Agent
  - 财务指标计算（资产负债率、流动比率等）
  - 同行业对比
  - 异常检测
```

---

## 六、L3 AI 引擎层

---

### 模块 3.1：对话引擎（Chat Engine）

**定义**：AI 对话的核心调度器，管理多轮对话、意图识别、Agent 路由

**AI 原生交互方式**：
- 用户所有输入都经过对话引擎
- 引擎决定调用哪个 Agent / 哪个 API
- 维护对话上下文和历史

**后端实现**：

```
API 端点:
  POST   /api/chat/message           # 发送消息（SSE 流式返回）
  GET    /api/chat/history           # 对话历史
  DELETE /api/chat/history           # 清空对话
  POST   /api/chat/feedback          # 用户反馈

Agent:
  chat_orchestrator                 # 对话编排 Agent（核心）
  职责:
    1. 意图识别 → 分类到具体场景
    2. Agent 路由 → 选择合适的子 Agent
    3. 上下文管理 → 记住 "它"="三一集团"
    4. 结果整合 → 合并多个 Agent 的输出

意图分类（由 LLM 判断）:
  "查询类" → customer_query_agent / text2cypher_agent
  "分析类" → customer_profile_agent / risk_agent
  "修改类" → crud_dispatch_agent
  "关系类" → relation_analysis_agent
  "闲聊类" → general_chat_agent

核心代码逻辑:
  class ChatOrchestrator:
    async def process(self, message, context):
      intent = await self.classify_intent(message, context)
      agent = self.route_to_agent(intent)
      response = await agent.execute(message, context)
      context.update(response)
      return response
```

---

### 模块 3.2：Text-to-Cypher

**定义**：将自然语言转化为准确的 Cypher 查询语句

**AI 原生交互方式**：
- 用户说人话 → 系统生成 Cypher → 执行 → 翻译回人话
- 本体定义作为 LLM 的"数据词典"提高准确率

**后端实现**：

```
API 端点:
  POST   /api/text2cypher/convert    # 自然语言 → Cypher
  POST   /api/text2cypher/execute    # 转换 + 执行
  GET    /api/text2cypher/history    # 转换历史

Agent:
  text2cypher_agent                 # 转换 Agent
  输入: 自然语言 + 本体定义 + 对话上下文
  输出: Cypher 语句 + 执行结果 + 自然语言回答

  处理流程:
    1. 加载本体 → 获取类/属性/关系定义
    2. LLM Prompt = 本体 + 用户问题 + 示例
    3. LLM 生成 Cypher
    4. 安全校验（防止危险操作）
    5. Neo4j 执行
    6. LLM 将结果翻译为自然语言

Prompt 模板:
  你是 Cypher 查询专家。基于以下本体定义生成查询:
  {ontology_summary}
  
  用户问题: {user_question}
  对话上下文: {conversation_context}
  
  规则:
  - 只生成 MATCH/RETURN 查询，禁止 CREATE/DELETE
  - 使用 ns1__ 前缀的属性名
  - 返回结果不超过 50 条
  - 生成的 Cypher:
```

---

### 模块 3.3：GraphRAG

**定义**：基于知识图谱的检索增强生成，为 LLM 提供精准的图数据上下文

**AI 原生交互方式**：
- 用户问深度问题 → GraphRAG 遍历图谱 → 提取上下文 → LLM 生成分析

**后端实现**：

```
API 端点:
  POST   /api/graphrag/query         # GraphRAG 查询
  POST   /api/graphrag/summarize     # 图谱摘要生成

Agent:
  graphrag_agent                    # GraphRAG Agent
  输入: 用户问题 + 目标实体
  输出: 基于图数据的分析报告

  处理流程:
    1. 实体识别 → 从问题中提取目标实体
    2. 图遍历 → 从目标节点出发遍历 1-3 度
    3. 上下文构建 → 图数据 → 结构化文本
    4. LLM 分析 → 上下文 + 问题 → 分析报告
    5. 引用标注 → 标注数据来源

  上下文构建示例:
    "目标: 三一集团有限公司
     基本信息: 渠道商, 登记于 2022-04-14
     联系人: 王善义 (18890987658)
     银行账户: 工行长沙星沙支行
     关联企业 (12家):
       - 三一重型装备有限公司
       - 富鸿资本(湖南)融资租赁有限公司
       - ...
     关联关系类型: 全部为渠道商关联(02)"
```

---

### 模块 3.4：推理引擎

**定义**：基于本体约束和图结构的逻辑推理

**AI 原生交互方式**：
- 用户问 "如果 A 出问题会影响谁？" → 推理引擎沿图路径传导分析
- 用户问 "这个客户资料完整吗？" → 本体约束校验

**后端实现**：

```
API 端点:
  POST   /api/reasoning/propagate    # 风险传导推理
  POST   /api/reasoning/validate     # 本体约束校验
  POST   /api/reasoning/infer        # 通用推理

Agent:
  reasoning_agent                   # 推理 Agent
  能力:
    - 风险传导: 沿图路径分析影响范围
    - 完整性检查: 本体定义 vs 实际数据
    - 一致性检查: 数据间矛盾检测
    - 推断补全: 根据图结构推断缺失信息
```

---

## 七、L4 智能分析层

---

### 模块 4.1：关系分析

**定义**：客户间关联关系的发现、可视化与分析

**AI 原生交互方式**：

```
场景 1 - 关联查询:
  用户: "张三公司和哪些客户有关联？"
  AI → 1 度遍历 → 列表 + 可视化

场景 2 - 深层关系:
  用户: "张三物流和张三公司是什么关系？"
  AI → 路径查找 → 解释关系链路

场景 3 - 网络发现:
  用户: "画出张三公司的 3 度关系网络"
  AI → 3 度遍历 → 生成可视化数据 → 前端渲染图谱
```

**后端实现**：

```
API 端点:
  POST   /api/analysis/relations      # 关系查询
  POST   /api/analysis/network        # 网络图数据
  POST   /api/analysis/path           # 路径查找

Agent:
  relation_analysis_agent           # 关系分析 Agent
  - 关系发现与分类
  - 路径查找（最短路径）
  - 网络可视化数据生成（节点+边 JSON）
  - 关键节点识别（度中心性）
```

---

### 模块 4.2：风险分析

**定义**：担保圈分析、风险传导、异常检测

**AI 原生交互方式**：

```
场景 1 - 担保圈:
  用户: "画出三一集团的担保圈"
  AI → 环检测算法 → 可视化 → 风险评估

场景 2 - 风险传导:
  用户: "如果李四贸易违约，影响范围有多大？"
  AI → 传导路径分析 → 影响金额估算 → 风险报告

场景 3 - 异常检测:
  用户: "有没有异常的关联关系？"
  AI → 图算法（社区检测/异常点）→ 异常报告
```

**后端实现**：

```
API 端点:
  POST   /api/analysis/risk/circle    # 担保圈分析
  POST   /api/analysis/risk/propagate # 风险传导
  POST   /api/analysis/risk/anomaly   # 异常检测

Agent:
  risk_analysis_agent               # 风险分析 Agent
  - 担保圈检测（环路检测算法）
  - 风险传导路径（BFS/DFS + 权重）
  - 异常模式识别
  - 风险报告生成

Cypher 示例（环路检测）:
  MATCH path = (start)-[:ns1__relatedTo*2..5]->(start)
  WHERE start.ns1__cusName = '三一集团有限公司'
  RETURN path
```

---

### 模块 4.3：合规校验

**定义**：基于本体约束的数据合规性检查

**AI 原生交互方式**：

```
场景 1:
  用户: "三一集团的资料完整吗？"
  AI → 本体约束检查 → 缺失项列表 → 补充建议

场景 2:
  用户: "哪些企业客户缺少注册资本信息？"
  AI → 批量校验 → 列表
```

**后端实现**：

```
API 端点:
  POST   /api/compliance/check        # 单客户校验
  POST   /api/compliance/batch        # 批量校验
  GET    /api/compliance/rules        # 校验规则列表

Agent:
  compliance_agent                  # 合规 Agent
  - 基于本体定义校验数据完整性
  - 基于 SHACL 规则校验约束
  - 生成合规报告
```

---

### 模块 4.4：客户推荐

**定义**：基于图谱特征的智能客户推荐

**AI 原生交互方式**：

```
场景 1:
  用户: "推荐制造业的优质客户"
  AI → 多条件过滤 + 排序 → 推荐列表

场景 2:
  用户: "有没有和张三公司类似的客户？"
  AI → 相似度计算 → 排名
```

**后端实现**：

```
API 端点:
  POST   /api/recommend/similar       # 相似度推荐
  POST   /api/recommend/quality       # 优质客户推荐
  POST   /api/recommend/industry      # 行业推荐

Agent:
  recommendation_agent              # 推荐 Agent
  - 多维度相似度计算
  - 行业/地区/规模匹配
  - 评级/财务指标加权排序
```

---

## 八、L5 交互层

---

### 模块 5.1：对话界面（Chat UI）

**定义**：AI 原生系统的核心交互入口

**交互设计**：

```
┌──────────────────────────────────────────────────────┐
│  AI 客户助手                              [设置] [?] │
├──────────────────────────────────────────────────────┤
│                                                      │
│  🤖 你好，我是客户智能助手。你可以问我关于客户的      │
│     任何问题，比如：                                  │
│     - "三一集团的全面情况"                            │
│     - "找一下制造业评级 AA 的企业"                    │
│     - "张三公司的担保圈"                              │
│                                                      │
│  👤 帮我分析一下三一集团                              │
│                                                      │
│  🤖 ## 三一集团有限公司 全景画像                      │
│     **基本信息**                                      │
│     - 渠道商，登记于 2022-04-14                      │
│     - 统一社会信用代码：91430009722592271H            │
│     ...                                               │
│     **关联网络**                                      │
│     - 关联企业 12 家，覆盖 11 个省市                  │
│     [📊 查看关系图谱]                                 │
│                                                      │
│  👤 赫锐德评级为什么是 C？                            │
│                                                      │
├──────────────────────────────────────────────────────┤
│  [输入消息...]                            [发送 ➤]   │
└──────────────────────────────────────────────────────┘
```

**技术实现**：
- React + TypeScript
- SSE（Server-Sent Events）流式接收 AI 回答
- Markdown 渲染（支持表格、代码、图谱嵌入）
- 对话历史本地存储 + 服务端同步

---

### 模块 5.2：图谱可视化

**定义**：关系网络的交互式可视化展示

**交互设计**：

```
┌──────────────────────────────────────────────────────┐
│  [← 返回对话]     三一集团 关系网络     [导出] [全屏] │
├──────────────────────────────────────────────────────┤
│                                                      │
│          [湖南中旺] ─── [江西中旺]                    │
│               │                                     │
│    [三一重型] ─┤                                     │
│               │                                     │
│         ┌─── [三一集团] ─── [富鸿资本]               │
│         │      │           │                         │
│    [广州巨和]  │     [新疆京泓]                       │
│         │      │           │                         │
│    [福建闽瑞通] ┤     [重庆正汇/正源]                 │
│               │           │                         │
│         [保定汤晨]   [云南正源睿德]                    │
│                   ⚠️[赫锐德-C级]                     │
│                                                      │
│  图例: ● 核心企业  ● 关联企业  ⚠️ 低评级              │
├──────────────────────────────────────────────────────┤
│  节点: 13  边: 12  层级: 1度    [展开2度] [展开3度]   │
└──────────────────────────────────────────────────────┘
```

**技术实现**：
- ECharts / D3.js / Neo4j Bloom
- 支持缩放、拖拽、点击节点查看详情
- 支持从对话界面一键跳转到图谱视图

---

### 模块 5.3：管理面板（Dashboard）

**定义**：传统管理界面，用于 CRUD 操作和系统管理

**交互设计**：标准后台管理界面（表格+表单+筛选）

**技术实现**：
- React + Ant Design / Material UI
- 标准 CRUD 表格
- 表单录入/编辑

---

## 九、模块间协作流程

### 9.1 典型请求流转

```
用户: "帮我分析三一集团，看看有没有风险"
  │
  ▼
Chat UI → POST /api/chat/message
  │
  ▼
ChatOrchestrator（对话引擎）
  │
  ├─ 1. 意图识别 → "分析 + 风险"
  │
  ├─ 2. 路由 → customer_profile_agent + risk_analysis_agent
  │
  ├─ 3. 并行执行:
  │   ├─ profile_agent:
  │   │   ├─ 图遍历（Neo4j）→ 获取全部关联数据
  │   │   └─ LLM 生成画像报告
  │   │
  │   └─ risk_agent:
  │       ├─ 环路检测（Neo4j Cypher）→ 担保圈
  │       ├─ 传导分析（Neo4j）→ 影响范围
  │       └─ LLM 生成风险评估
  │
  ├─ 4. 结果整合 → 合并画像 + 风险
  │
  └─ 5. SSE 流式返回 → Chat UI 渲染
```

### 9.2 数据库选择规则（代码级）

```python
class DatabaseRouter:
    """根据操作类型自动路由到正确的数据库"""
    
    def route(self, operation: str, entity: str) -> str:
        if operation in ['CREATE', 'UPDATE', 'DELETE']:
            return 'mysql'        # 写操作 → MySQL
        if operation == 'READ_DETAIL':
            return 'mysql'        # 单条精确查询 → MySQL
        if operation == 'READ_LIST':
            return 'mysql'        # 列表/统计 → MySQL
        if operation in ['TRAVERSE', 'ANALYZE', 'RELATION']:
            return 'neo4j'        # 关系/分析 → Neo4j
        if operation == 'AI_QUERY':
            return 'neo4j'        # AI 查询 → Neo4j
        if operation == 'VALIDATE':
            return 'neo4j'        # 本体校验 → Neo4j
```

---

## 十、实施路线图

| 阶段 | 模块 | 耗时 | 产出 |
|------|------|------|------|
| **Sprint 1** | L0 基础设施 + L1 数据层 + 项目脚手架 | 3 天 | 项目可运行 |
| **Sprint 2** | L2 客户管理 + 联系人 + 银行账户 | 3 天 | CRUD 可用 |
| **Sprint 3** | L3 对话引擎 + Text-to-Cypher | 3 天 | 能对话查数据 |
| **Sprint 4** | L3 GraphRAG + 客户画像 | 2 天 | 能生成分析报告 |
| **Sprint 5** | L4 关系分析 + 风险分析 | 3 天 | 图谱分析可用 |
| **Sprint 6** | L5 Chat UI + 图谱可视化 | 3 天 | 完整交互界面 |
| **Sprint 7** | L4 合规 + 推荐 + 财务分析 | 2 天 | 全功能覆盖 |
| **Sprint 8** | 集成测试 + 性能优化 + 部署 | 3 天 | 上线就绪 |
| **总计** | | **22 天** | **完整 AI 原生客户系统** |
