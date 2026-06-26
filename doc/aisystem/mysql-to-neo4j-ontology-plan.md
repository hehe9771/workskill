# MySQL → Neo4j 本体数据落地方案

> 版本: v1.0 | 日期: 2026-06-25 | 状态: **待审批**

---

## 一、问题定义

**核心目标**：将公司某系统的 MySQL 关系型数据，转化为 Neo4j 中的本体（Ontology）数据，形成知识图谱。

**本质问题**：关系模型（表-行-列-外键）→ 图模型（节点-属性-关系-本体）的语义转换。

---

## 二、技术路线选择

### 2.1 三种可选方案对比

| 方案 | 描述 | 优点 | 缺点 | 适用场景 |
|------|------|------|------|----------|
| **A. R2RML 标准映射** | W3C 标准，用 Turtle 语法定义映射规则，生成 RDF 后导入 Neo4j | 标准化、可复用、可共享 | 学习曲线高、复杂映射编写困难 | 需要标准化输出的场景 |
| **B. Python ETL 脚本** | 用 Python 读取 MySQL，用 rdflib 生成 RDF，通过 n10s 导入 Neo4j | 灵活可控、可调试、可测试 | 需编写代码、需维护 | **推荐：大多数业务场景** |
| **C. 直接 Cypher 导入** | 用 Python 读 MySQL，直接写 Cypher 语句创建节点和关系 | 简单直接、不需要 RDF 中间层 | 缺少本体语义、无 SHACL 校验 | 只需图结构不需本体的场景 |

### 2.2 推荐方案：B（Python ETL）+ 本体层

**理由**：
1. 你已安装 neosemantics，目标明确是"本体数据"而非普通图数据
2. Python ETL 可以精确控制映射逻辑，处理业务特殊规则
3. 生成标准 RDF 格式（Turtle），既可通过 n10s 导入，也可复用给其他系统
4. 可测试、可回滚、可增量更新

---

## 三、整体架构

```
┌──────────────────────────────────────────────────────────────┐
│                    MySQL 数据库（源）                          │
│  ┌──────┐  ┌──────┐  ┌──────────┐  ┌──────────┐            │
│  │ 用户表│  │ 订单表│  │ 产品表    │  │ 其他业务表│            │
│  └──┬───┘  └──┬───┘  └────┬─────┘  └────┬─────┘            │
│     │         │           │              │                   │
└─────┼─────────┼───────────┼──────────────┼───────────────────┘
      │         │           │              │
      ▼         ▼           ▼              ▼
┌──────────────────────────────────────────────────────────────┐
│                Phase 1: Schema 分析 & 本体设计               │
│                                                              │
│  MySQL Schema → 领域模型 → OWL/RDFS 本体定义                  │
│  ┌────────────────────────────────┐                         │
│  │  ontology.ttl (Turtle 格式)     │                         │
│  │  - 类定义 (Class)              │                         │
│  │  - 属性定义 (Property)         │                         │
│  │  - 关系定义 (Relationship)     │                         │
│  │  - 约束定义 (SHACL)           │                         │
│  └────────────────────────────────┘                         │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│              Phase 2: Python ETL 管道                        │
│                                                              │
│  ┌─────────┐    ┌──────────┐    ┌───────────┐              │
│  │ MySQL    │ →  │ 映射引擎  │ →  │ RDF 生成  │              │
│  │ Connector│    │ (规则库) │    │ (Turtle)  │              │
│  └─────────┘    └──────────┘    └─────┬─────┘              │
│                                       │                     │
│              ┌────────────────────────┘                      │
│              │                                               │
│              ▼                                               │
│  ┌──────────────────┐                                       │
│  │ n10s.rdf.import  │ → Neo4j 本体数据                       │
│  │ .fetch / .inline │                                       │
│  └──────────────────┘                                       │
└──────────────────────────────────────────────────────────────┘
```

---

## 四、Workflow 执行计划

### Phase 1: 信息采集（前置条件）

**目标**：获取 MySQL 数据库结构信息

| # | 任务 | 输出 |
|---|------|------|
| 1.1 | 用户提供 MySQL 连接信息（host/port/db/user/password） | 连接参数 |
| 1.2 | 自动提取 Schema（表结构、字段类型、主外键、索引） | schema_dump.json |
| 1.3 | 识别业务实体和关系（分析表间关联） | entity_relationship_map |
| 1.4 | 确认数据量级（每表行数、总数据量） | data_volume_report |

**依赖**：需要用户提供 MySQL 连接信息

---

### Phase 2: 本体设计

**目标**：将关系模型转化为领域本体

| # | 任务 | 方法 | 输出 |
|---|------|------|------|
| 2.1 | 定义命名空间和基础前缀 | Turtle 语法 | namespace 定义 |
| 2.2 | 表 → 类（Class）映射 | 每个业务表对应一个 OWL Class | class_definitions |
| 2.3 | 列 → 数据属性（DatatypeProperty）映射 | 字段类型 → RDF 数据类型 | property_definitions |
| 2.4 | 外键 → 对象属性（ObjectProperty）映射 | FK 关系 → 语义关系 | relationship_definitions |
| 2.5 | 枚举/字典表 → 受控词表 | 值域约束 | vocabulary |
| 2.6 | 生成完整本体文件 | 整合以上 | `ontology.ttl` |

**映射规则示例**：

```
MySQL 表: user(id INT PK, name VARCHAR, dept_id INT FK, role ENUM)
    ↓
OWL Class: ex:User
    ↓
DatatypeProperty: ex:name (xsd:string)
ObjectProperty: ex:belongsToDepartment → ex:Department
Individual: ex:AdminRole, ex:UserRole (枚举实例化)
```

---

### Phase 3: ETL 管道开发

**目标**：构建可复用的 Python ETL 脚本

| # | 任务 | 技术 | 输出 |
|---|------|------|------|
| 3.1 | MySQL 连接层 | SQLAlchemy + PyMySQL | db_connector.py |
| 3.2 | RDF 生成层 | rdflib (Graph, Namespace, URIRef) | rdf_generator.py |
| 3.3 | 映射规则引擎 | 配置文件驱动 | mapping_config.yaml |
| 3.4 | n10s 导入层 | Cypher 调用 / Bolt 直连 | neo4j_loader.py |
| 3.5 | 主控流程 | 分表处理 + 进度日志 | main_etl.py |

**技术栈**：
```
Python 3.x (conda env: picproject)
├── sqlalchemy      ← MySQL 连接
├── pymysql         ← MySQL 驱动
├── rdflib          ← RDF 生成
├── neo4j (python)  ← Bolt 直连（可选）
└── pyyaml          ← 映射配置
```

---

### Phase 4: 数据导入

**目标**：将生成的 RDF 数据导入 Neo4j

| # | 步骤 | 命令/方法 | 说明 |
|---|------|-----------|------|
| 4.1 | 初始化图配置 | `CALL n10s.graphconfig.init()` | 设定命名空间处理策略 |
| 4.2 | 导入本体定义 | `n10s.rdf.import.fetch("file:///...ontology.ttl", "Turtle")` | 类、属性、关系定义 |
| 4.3 | 批量导入实例数据 | 分表循环 `n10s.rdf.import.inline(rdf_content, "Turtle")` | 每批次 ≤ 10000 三元组 |
| 4.4 | 创建全文索引（可选） | `CREATE FULLTEXT INDEX ...` | 支持中文搜索 |

**导入策略**：
- 本体定义（Schema）→ 先导入
- 实例数据（Data）→ 按表分批导入
- 关系数据（外键）→ 最后导入（确保目标节点已存在）

---

### Phase 5: 验证 & 测试

| # | 验证项 | 方法 |
|---|--------|------|
| 5.1 | 节点数量一致性 | MySQL COUNT(*) vs Neo4j MATCH (n:Label) RETURN count(n) |
| 5.2 | 关系完整性 | 外键关系数 vs Neo4j 关系数 |
| 5.3 | 属性值正确性 | 抽样对比 10-20 条记录 |
| 5.4 | 本体约束验证 | `CALL n10s.shacl.validate(...)` |
| 5.5 | 查询可用性 | 编写典型业务查询 Cypher 验证 |

---

## 五、关键映射规则

### 5.1 表 → 类

```
规则: 每个业务表 → 一个 OWL Class
例外: 关联表（如 user_role）→ 对象属性，不生成独立类
命名: 表名去下划线 → PascalCase → ex:ClassName
```

### 5.2 列 → 属性

| MySQL 类型 | RDF/XSD 类型 |
|------------|-------------|
| INT/BIGINT | xsd:integer |
| VARCHAR/TEXT | xsd:string |
| DECIMAL/FLOAT | xsd:decimal |
| DATE | xsd:date |
| DATETIME/TIMESTAMP | xsd:dateTime |
| BOOLEAN/TINYINT(1) | xsd:boolean |
| ENUM | 实例化为个体（Individual） |

### 5.3 外键 → 关系

```
规则: FK 列 → ObjectProperty
命名: FK名 → 语义关系名（如 dept_id → belongsToDepartment）
方向: 子表 → 父表
```

### 5.4 关联表 → 多对多关系

```
MySQL: user_role(user_id FK, role_id FK)
    ↓
Neo4j: (User)-[:HAS_ROLE]->(Role)
```

---

## 六、待确认事项

**在开始执行前，需要确认以下信息：**

| # | 问题 | 说明 |
|---|------|------|
| 1 | **目标 MySQL 数据库的连接信息** | host, port, database, user, password |
| 2 | **数据库的业务领域** | 是绩效系统？ERP？CRM？其他？ |
| 3 | **数据量级** | 预估表数量、总行数 |
| 4 | **期望的本体粒度** | 仅映射核心业务表？还是全库所有表？ |
| 5 | **是否需要增量同步** | 一次性导入？还是需要定期同步更新？ |

---

## 七、Dynamic Workflow 执行编排

### 确认后立即执行以下步骤：

```
Phase 1: 信息采集（并行）
├── Agent A: 连接 MySQL，提取 Schema
├── Agent B: 分析表间关系，识别业务实体
└── Agent C: 统计数据量级

Phase 2: 本体设计（依赖 Phase 1）
├── Agent D: 生成 ontology.ttl
└── Agent E: 生成 mapping_config.yaml

Phase 3: ETL 开发（依赖 Phase 2，并行）
├── Agent F: 开发 MySQL 连接 + RDF 生成
├── Agent G: 开发 n10s 导入逻辑
└── Agent H: 编写测试用例

Phase 4: 执行导入（串行）
├── Step 1: 初始化 Neo4j 图配置
├── Step 2: 导入本体定义
├── Step 3: 分批导入实例数据
└── Step 4: 建立关系

Phase 5: 验证（并行）
├── Agent I: 数据量一致性校验
├── Agent J: 抽样数据正确性校验
└── Agent K: Cypher 查询可用性测试
```

### 预计耗时

| 阶段 | 耗时 |
|------|------|
| Phase 1 信息采集 | 10 min |
| Phase 2 本体设计 | 20 min |
| Phase 3 ETL 开发 | 30 min |
| Phase 4 数据导入 | 15 min（视数据量） |
| Phase 5 验证 | 15 min |
| **总计** | **~90 min** |

---

## 八、交付物

| 交付物 | 路径 | 说明 |
|--------|------|------|
| 本体文件 | `neo4j-n10s/ontology/ontology.ttl` | 领域本体定义 |
| 映射配置 | `neo4j-n10s/etl/mapping_config.yaml` | 表-类-属性映射规则 |
| ETL 脚本 | `neo4j-n10s/etl/main_etl.py` | 主执行脚本 |
| RDF 中间文件 | `neo4j-n10s/etl/output/*.ttl` | 生成的 RDF 数据 |
| 验证报告 | `doc/mysql-to-ontology-validation.md` | 数据一致性报告 |
