# mftcc-cus-server 本体化实施方案

> 版本: v1.0 | 日期: 2026-06-25 | 状态: **待审批**
> 数据库: mftcc-cus-server | 205 张表 | 核心数据 ~60K 行

---

## 一、数据库分析结论

### 1.1 系统定位

这是一个**融资租赁/保理公司的客户主数据管理系统（CRM）**，核心功能：
- 客户登记（企业 + 个人）
- 客户评级
- 账户管理
- 财务报表管理
- 关联关系管理

### 1.2 数据量分级

| 分级 | 表名 | 行数 | 本体化策略 |
|------|------|------|------------|
| **核心实体** | cus_customer | 22,703 | ✅ 本体化 |
| **企业详情** | cus_corp_base_info | 6,513 | ✅ 本体化 |
| **个人详情** | cus_pers_base_info | 15,170 | ✅ 本体化 |
| **联系人** | cus_contact_info | 13,927 | ✅ 本体化 |
| **银行账户** | cus_bank_acc_manage | 10,055 | ✅ 本体化 |
| **发票信息** | cus_invoice_info | 10,357 | ✅ 本体化 |
| **财务报表** | cus_assets_report_data | 10,389 | ✅ 本体化 |
| **银行字典** | cus_bank_info | 151,630 | ⚠️ 字典表，按需导入 |
| **行业分类** | industry | 1,772 | ✅ 字典本体 |
| **客户类型** | cus_type | 18 | ✅ 类型本体 |
| **评级模型** | cus_eval_model + cus_eval_index | 190 | ✅ 本体化 |
| **关联关系** | cus_relevance_relation | 23 | ✅ 本体化 |
| **配置/空表** | 其余 ~90 张 | 0 或极少 | ❌ 跳过 |

**总计需本体化数据量：约 25 万行** → 约 **200 万三元组** → n10s 可承受范围内。

---

## 二、本体设计

### 2.1 类（Class）定义

```
命名空间: ex:http://mftcc.com/ontology/cus#

核心类:
├── Customer (客户) ← cus_customer
│   ├── EnterpriseCustomer (企业客户) ← cus_base_type='1'
│   └── PersonalCustomer (个人客户) ← cus_base_type='2'
├── ContactPerson (联系人) ← cus_contact_info
├── BankAccount (银行账户) ← cus_bank_acc_manage
├── Bank (银行) ← cus_bank_info
├── Invoice (发票信息) ← cus_invoice_info
├── FinancialReport (财务报表) ← cus_assets_report_data
├── CustomerType (客户类型) ← cus_type
├── Industry (行业) ← industry
├── EvalModel (评级模型) ← cus_eval_model
├── EvalIndex (评级指标) ← cus_eval_index
└── Region (地区) ← 省/市/区提取
```

### 2.2 数据属性（DatatypeProperty）定义

```
Customer 属性:
├── cusNo (客户号) → xsd:string
├── cusName (客户名称) → xsd:string
├── idType (证件类型) → xsd:string
├── idNo (证件号码) → xsd:string
├── ratingScore (评级分数) → xsd:decimal
├── ratingGrade (评级等级) → xsd:string
├── preCreditSum (预授信总额) → xsd:decimal
├── registerDate (登记日期) → xsd:date
├── channelSource (渠道来源) → xsd:string
└── ... (其他直接属性)

EnterpriseCustomer 附加属性:
├── registeredCapital (注册资本) → xsd:decimal
├── paidCapital (实缴资本) → xsd:decimal
├── totalAssets (资产总额) → xsd:decimal
├── employeeCount (员工人数) → xsd:integer
├── mainBusiness (主营业务) → xsd:string
├── businessScope (经营范围) → xsd:string
├── companyType (公司类型) → xsd:string
├── taxNo (税号) → xsd:string
├── setupDate (成立日期) → xsd:date
└── ... (约 80+ 属性)

PersonalCustomer 附加属性:
├── birthday (出生日期) → xsd:date
├── gender (性别) → xsd:string
├── education (学历) → xsd:string
├── maritalStatus (婚姻状况) → xsd:string
├── nationality (民族) → xsd:string
└── ... (约 30+ 属性)
```

### 2.3 对象属性（ObjectProperty / 关系）定义

```
├── hasContact        Customer → ContactPerson     (客户拥有联系人)
├── hasBankAccount    Customer → BankAccount        (客户拥有银行账户)
├── belongsToBank     BankAccount → Bank            (账户属于银行)
├── hasInvoice        Customer → Invoice            (客户拥有发票信息)
├── hasFinancialReport Customer → FinancialReport   (客户拥有财务报表)
├── hasCustomerType   Customer → CustomerType       (客户属于类型)
├── inIndustry        EnterpriseCustomer → Industry (企业所属行业)
├── locatedInRegion   Customer → Region             (客户所在地区)
├── relatedTo         Customer → Customer           (客户关联关系)
├── parentType        CustomerType → CustomerType   (类型层级)
├── parentIndustry    Industry → Industry           (行业层级)
└── evaluatedByModel  Customer → EvalModel          (客户使用评级模型)
```

### 2.4 实体关系图

```
                    ┌─────────────┐
                    │ CustomerType│
                    └──────┬──────┘
                           │ hasCustomerType
                           ▼
┌──────────┐    hasContact    ┌──────────────┐    hasBankAccount   ┌────────────┐
│  Bank    │◄──belongsToBank──│ BankAccount  │◄────────────────────│  Customer  │
└──────────┘                  └──────────────┘                     └──────┬───────┘
     ▲                                                                    │
     │                                                                    ├── hasContact → ContactPerson
     │                                                                    ├── hasInvoice → Invoice
     │                                                                    ├── hasFinancialReport → FinancialReport
     │                                                                    ├── inIndustry → Industry
     │                                                                    ├── locatedInRegion → Region
     │                                                                    └── relatedTo → Customer (self)
     │
     │                  ┌─────────────┐
     │    inIndustry    │  Industry   │
     └──────────────────└─────────────┘
```

---

## 三、实施计划

### Phase 1: 本体文件生成（20 min）

**任务**: 生成 `ontology.ttl`

| 步骤 | 内容 | 输出 |
|------|------|------|
| 1.1 | 定义命名空间和前缀 | Turtle header |
| 1.2 | 生成 12 个 Class 定义 | owl:Class 声明 |
| 1.3 | 生成 ~150 个 DatatypeProperty | 数据类型属性 |
| 1.4 | 生成 12 个 ObjectProperty | 关系属性 |
| 1.5 | 生成枚举/受控词表 | 客户类型、行业分类等 |
| 1.6 | 导入 Neo4j | n10s.rdf.import.fetch |

**输出**: `neo4j-n10s/ontology/cus_ontology.ttl`

### Phase 2: ETL 管道开发（40 min）

**任务**: 开发 Python ETL 脚本

| 步骤 | 脚本 | 功能 |
|------|------|------|
| 2.1 | `db_connector.py` | MySQL 连接、分页查询 |
| 2.2 | `rdf_generator.py` | 表行 → RDF 三元组转换 |
| 2.3 | `mapping_config.yaml` | 21 张表的映射规则 |
| 2.4 | `neo4j_loader.py` | 分批调用 n10s 导入 |
| 2.5 | `main_etl.py` | 主控流程（按依赖顺序执行） |

**导入顺序**（按依赖关系）：
```
1. 字典数据: cus_type, industry, cus_bank_info
2. 核心实体: cus_customer → EnterpriseCustomer / PersonalCustomer
3. 详情数据: cus_corp_base_info, cus_pers_base_info
4. 关联实体: cus_contact_info, cus_bank_acc_manage, cus_invoice_info
5. 财务数据: cus_assets_report_data
6. 关系数据: cus_relevance_relation
7. 评级数据: cus_eval_model, cus_eval_index
```

### Phase 3: 数据导入（20 min）

| 步骤 | 操作 | 预估三元组数 |
|------|------|-------------|
| 3.1 | 初始化图配置 | - |
| 3.2 | 导入本体定义 ontology.ttl | ~500 |
| 3.3 | 导入字典数据 | ~5,000 |
| 3.4 | 导入客户实体 | ~50,000 |
| 3.5 | 导入详情数据 | ~100,000 |
| 3.6 | 导入关联实体 | ~80,000 |
| 3.7 | 导入财务数据 | ~30,000 |
| 3.8 | 导入关系 | ~50,000 |
| **总计** | | **~315,000** |

**注意**：31 万三元组远低于 n10s 的 500 万上限，可以安全使用 n10s 直接导入。

### Phase 4: 验证（15 min）

| 验证项 | 方法 |
|--------|------|
| 节点数量 | MySQL COUNT vs Neo4j MATCH |
| 关系完整性 | FK 关系数 vs Neo4j 关系数 |
| 抽样正确性 | 随机抽取 20 条对比 |
| 查询可用性 | 典型 Cypher 查询测试 |

---

## 四、技术栈

```
Python (picproject env)
├── pymysql          ← MySQL 连接
├── rdflib           ← RDF 生成
└── pyyaml           ← 映射配置

Neo4j 5.26 + neosemantics 5.26.0
├── n10s.rdf.import.fetch  ← 文件导入
├── n10s.rdf.import.inline ← 内联导入
└── Cypher Shell            ← 验证查询
```

---

## 五、项目文件结构

```
D:\mydoc\workskill\neo4j-n10s\
├── ontology/
│   └── cus_ontology.ttl          ← 本体定义
├── etl/
│   ├── mapping_config.yaml       ← 映射规则
│   ├── db_connector.py           ← MySQL 连接
│   ├── rdf_generator.py          ← RDF 生成
│   ├── neo4j_loader.py           ← Neo4j 导入
│   └── main_etl.py               ← 主控脚本
└── output/
    ├── 01_dictionary.ttl         ← 字典数据 RDF
    ├── 02_customer.ttl           ← 客户实体 RDF
    ├── 03_detail.ttl             ← 详情数据 RDF
    ├── 04_relations.ttl          ← 关系数据 RDF
    └── 05_financial.ttl          ← 财务数据 RDF
```

---

## 六、风险评估

| 风险 | 等级 | 缓解 |
|------|------|------|
| 中文编码问题 | LOW | 全程 UTF-8，pymysql charset=utf8mb4 |
| FK 引用缺失 | LOW | 导入顺序按依赖关系排列 |
| 枚举值含义不清 | MEDIUM | 从注释中提取，部分需确认 |
| 空字段处理 | LOW | 空值不生成三元组 |

---

## 七、典型查询示例（本体化后可用）

```cypher
// 1. 查找某客户的所有联系人
MATCH (c:EnterpriseCustomer {cusName: '某公司'})-[:hasContact]->(p:ContactPerson)
RETURN p.contactName, p.contactMobilePhone

// 2. 查找某行业的所有企业客户
MATCH (c:EnterpriseCustomer)-[:inIndustry]->(i:Industry {name: '制造业'})
RETURN c.cusName, c.ratingGrade

// 3. 查找关联客户网络
MATCH path = (c:Customer)-[:relatedTo*1..3]->(related:Customer)
WHERE c.cusNo = 'C001'
RETURN path

// 4. 查找某银行的所有账户
MATCH (ba:BankAccount)-[:belongsToBank]->(b:Bank {bankName: '工商银行'})
RETURN ba.accountNo, ba.accountName

// 5. 评级分布统计
MATCH (c:EnterpriseCustomer)
RETURN c.ratingGrade, count(*) AS cnt ORDER BY cnt DESC
```

---

## 八、预计耗时

| 阶段 | 耗时 |
|------|------|
| Phase 1 本体文件生成 | 20 min |
| Phase 2 ETL 管道开发 | 40 min |
| Phase 3 数据导入 | 20 min |
| Phase 4 验证 | 15 min |
| **总计** | **~95 min** |

---

**WAITING FOR CONFIRMATION**: 确认后立即开始执行。
