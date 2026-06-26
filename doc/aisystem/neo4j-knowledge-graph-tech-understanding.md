# Neo4j 知识图谱核心技术理解

> 整理自 2026-06-25 会话讨论
> 关键词：Text-to-Cypher、GraphRAG、推理引擎、本体、节点/边/关系

---

## 一、Text-to-Cypher

### 1.1 是什么

将自然语言（人类语言）自动转换为 Cypher 查询语句的技术。

- **Cypher** 是 Neo4j 图数据库的查询语言（类似 SQL 之于关系数据库）
- **Text-to-Cypher** 让 LLM 理解用户的自然语言问题，自动生成对应的 Cypher 查询

### 1.2 作用

用户用自然语言提问，系统自动生成图数据库查询并返回结果：

| 用户输入（自然语言） | 生成的 Cypher |
|---|---|
| "三一集团有哪些子公司？" | `MATCH (c:Company)-[:SUBSIDIARY_OF]->(p:Company {name: '三一集团'}) RETURN c.name` |
| "谁担任法定代表人最多的公司？" | `MATCH (p:Person)-[:LEGAL_REP]->(c:Company) RETURN p.name, count(c) ORDER BY count(c) DESC` |

### 1.3 与双库架构的关系

在 MySQL + Neo4j 双库架构下，AI 需要同时具备 **Text-to-SQL**（处理 MySQL 中的表单数据）和 **Text-to-Cypher**（处理 Neo4j 中的关系图谱）两种能力，根据用户问题智能路由。

### 1.4 实现方式

**推荐：LangChain `GraphCypherQAChain`**

```python
from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_anthropic import ChatAnthropic

# 1. 连接 Neo4j（自动读取 schema）
graph = Neo4jGraph(url="bolt://localhost:7687", username="neo4j", password="xxx")

# 2. 初始化 LLM
llm = ChatAnthropic(model="claude-sonnet-4-20250514")

# 3. 一行搞定 Text-to-Cypher
chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,
    validate_cypher=True,   # 自动校验生成的 Cypher 语法
    return_intermediate_steps=True,
)

# 4. 直接用
result = chain.invoke({"query": "三一集团有哪些联系人？"})
```

**LangChain 帮你做的：**
- 自动从 Neo4j 读取 schema（节点标签、关系类型、属性）
- 把 schema 注入 Prompt（不用手动拼）
- 安全校验（validate_cypher=True 自动检查语法）
- 错误重试（生成错误 Cypher 会自动重试）
- 结果翻译（把查询结果用自然语言回答）

**需要额外做的：**
- 把本体定义也注入进去（LangChain 默认只读 schema，不读本体）
- 加业务约束（比如限制最多返回 50 条）
- 加权限过滤（不同用户看不同数据）

**代码量对比：**
- 自己从零写：~300-500 行
- 用 LangChain：~50-80 行

---

## 二、GraphRAG

### 2.1 是什么

**GraphRAG** = Knowledge Graph + RAG（检索增强生成）

传统 RAG 是基于文档/片段的向量检索，GraphRAG 在此基础上加入**知识图谱的结构化关系**，让 AI 不仅"搜到信息"，还能"理解关系"。

### 2.2 传统 RAG vs GraphRAG

| 维度 | 传统 RAG | GraphRAG |
|------|---------|----------|
| 检索单元 | 文本片段（chunk） | 实体 + 关系 + 文本片段 |
| 存储 | 向量数据库 | 知识图谱 + 向量索引 |
| 检索逻辑 | 语义相似度 | 图遍历 + 语义匹配 |
| 能力边界 | 只能回答"文档里写了什么" | 能推理"实体之间什么关系" |
| 典型问题 | "三一集团的主营业务是什么？" | "三一集团的实控人通过哪些公司间接持股？" |

### 2.3 工作流程

```
用户提问（自然语言）
    ↓
1. 实体识别：从问题中提取关键实体（公司名、人名等）
    ↓
2. 图检索：在 Neo4j 中遍历关系，找到相关子图
    ↓
3. 上下文构建：将子图结构 + 关联文本拼接为 Prompt 上下文
    ↓
4. LLM 生成：基于结构化上下文生成准确回答
```

### 2.4 两种检索模式

**本地检索（Local Search）：** 从查询实体出发，沿关系向外扩展 N 跳，收集直接相关的实体和文本。适用于具体实体相关的精确问题。

**全局检索（Global Search）：** 利用预先构建的社区摘要（community summaries），回答跨实体的宏观问题。适用于总结性、分析性问题。

### 2.5 实现方式

**推荐：neo4j-graphrag（Neo4j 官方库）**

```python
from neo4j import GraphDatabase
from neo4j_rag import Neo4jRetriever, SimpleKGRetriever
from langchain_anthropic import ChatAnthropic

class CustomerGraphRAG:
    """基于 neo4j-graphrag 的客户 GraphRAG"""
    
    def __init__(self, driver, llm):
        self.driver = driver
        self.llm = llm
    
    async def query(self, question: str, target_entity: str):
        # Step 1: 找到目标节点
        target = await self._find_entity(target_entity)
        
        # Step 2: 图遍历取上下文（1-3度）
        context = await self._traverse_graph(target, depth=2)
        
        # Step 3: 向量检索补充语义相关节点
        similar = await self._vector_search(question, top_k=5)
        
        # Step 4: 构建完整上下文
        full_context = self._build_context(context, similar)
        
        # Step 5: LLM 生成回答
        answer = await self.llm.ainvoke(f"""
        基于以下图谱数据分析问题：
        上下文：{full_context}
        问题：{question}
        """)
        return answer
```

**不推荐微软 GraphRAG：** 它是独立的完整系统，会维护自己的图，和 Neo4j 数据重复，架构上多了一坨东西要维护。数据量只有 25 万行，杀鸡用牛刀。

### 2.6 前置工作

1. 给核心节点生成 Embedding（~2万 Customer + ~1万联系人），用 text-embedding-3-small，存为节点属性
2. 创建 Neo4j 向量索引
3. 写 GraphRAG 服务层，封装 neo4j-graphrag 的检索逻辑，约 100-150 行代码
4. 集成到 ChatOrchestrator

---

## 三、Neo4j ≠ 知识图谱

### 3.1 核心区分

Neo4j 是**图数据库软件（产品）**，知识图谱是**一种数据组织方式（概念/方法论）**。

| | Neo4j | 知识图谱 |
|---|---|---|
| 本质 | 图数据库软件 | 数据组织方法论 |
| 类比 | MySQL ≠ 业务数据模型 | Neo4j ≠ 知识图谱 |
| 做什么 | 存储节点和边，提供查询语言 | 用实体+关系+语义来描述世界 |

### 3.2 知识图谱的三要素

```
知识图谱 = 数据 + 语义 + 推理

 数据层：  节点、边、属性                ← Neo4j 能存
 语义层：  本体(Ontology)、分类体系      ← Neo4j 不天然具备
 推理层：  基于语义的逻辑推导            ← 需要额外构建
```

### 3.3 系统里的知识图谱怎么来的

```
MySQL 业务库  →  ETL 同步  →  Neo4j（图数据）
                                +
                          本体定义（OWL/RDFS）
                                +
                         向量索引（Embedding）
                                ↓
                        = 你的知识图谱
```

- **Neo4j** 只负责**存和查**图数据（节点、关系）
- **本体（neosemantics）** 提供语义层
- **向量索引** 提供语义相似度检索能力（给 GraphRAG 用）
- 三者加在一起，才构成完整的知识图谱能力

---

## 四、节点、边、关系

### 4.1 核心对照：MySQL → 图模型

```
MySQL                →    Neo4j 图模型
─────────────────────────────────────────
一行数据（记录）      →    节点（Node）
表                   →    节点标签（Label）
列值                  →    节点属性（Property）
外键 / 关联表         →    边（Edge）= 关系（Relationship）
```

**边和关系是同一个东西**，Neo4j 里叫 Relationship，它既是一条"边"（结构），也有语义含义（类型）。

### 4.2 节点（Node）= 一个具体的"东西"

MySQL 里**一行数据**就是图里**一个节点**：

```
MySQL 表 cus_customer 的一行：
┌──────────┬──────────────────────────────┬──────────┐
│ cusNo    │ cusName                      │ cusType  │
├──────────┼──────────────────────────────┼──────────┤
│ C001     │ 三一集团有限公司              │ 1(企业)   │
└──────────┴──────────────────────────────┴──────────┘

         ↓ 变成 Neo4j 节点

(:EnterpriseCustomer {
    cusNo: "C001",
    cusName: "三一集团有限公司",
    registerDate: date("2022-04-14")
})
```

### 4.3 边（Edge）= 两个节点之间的连线

MySQL 里**外键**或**关联表**就是边：

```
MySQL 外键关系：
  cus_contact_info.cus_no → cus_customer.cus_no

         ↓ 变成 Neo4j 边

(三一集团) ──────→ (王善义)
     └── 这条线就是"边"
```

### 4.4 关系（Relationship）= 边 + 语义类型

```
                    关系类型
                       ↓
(三一集团) ──[:hasContact]──→ (王善义)

解读：三一集团 拥有联系人 王善义
```

**关系就是带名字的边。** 名字告诉你"这两个节点之间是什么关系"。

### 4.5 以 mftcc-cus-server 表为例的完整图谱

```
MySQL                          Neo4j 节点
───────────────────────────────────────────────────
cus_customer 第 100 行     →   (:EnterpriseCustomer {cusName: "三一集团"})
cus_contact_info 第 50 行  →   (:ContactPerson {contactName: "王善义"})
cus_bank_acc_manage 第 20 行→  (:BankAccount {accountNo: "6222...7890"})
cus_bank_info 第 5 行      →   (:Bank {bankName: "工商银行"})
cus_corp_base_info 第 10 行→   (属性合并到 Customer 节点里，不单独建节点)
```

关联关系表 `cus_relevance_relation` 的每条记录变成一条关系：

```
MySQL 关联表:
┌────────────┬────────────┬──────────┐
│ cus_no_a   │ cus_no_b   │ rel_type │
├────────────┼────────────┼──────────┤
│ C001       │ C002       │ 02       │
│ C001       │ C005       │ 02       │
└────────────┴────────────┴──────────┘

         ↓ 变成 Neo4j 关系

(C001 三一集团) ──[:relatedTo {type: '02'}]──→ (C002 三一重型装备)
(C001 三一集团) ──[:relatedTo {type: '02'}]──→ (C005 富鸿资本)
```

---

## 五、本体在数据库设计时就定好了

### 5.1 核心洞察

MySQL 设计表结构的时候，其实已经隐含了一套"本体"：

```
数据库设计时做的决策              其实就是本体决策
────────────────────────────────────────────────────
建一张 cus_customer 表        →  "客户是一种实体"
建一张 cus_contact_info 表    →  "联系人也是一种实体"
cus_contact_info 里有 cus_no  →  "联系人属于客户"（关系）
注册资本放在 corp_base_info   →  "注册资本是属性，不是实体"
```

数据库设计者已经替你做了一次"什么是实体、什么是属性、什么是关系"的判断。ETL 只是把这个判断翻译成图模型的表达方式。

### 5.2 判断标准：什么该变成实体

**条件 1：它能独立存在，有唯一标识**

```
cus_customer 的每一行：
  cusNo = "C001"  ← 唯一标识，独立存在 → ✅ 是实体

cus_corp_base_info 的每一行：
  cus_no = "C001"  ← 没有自己的唯一ID，依附于客户
  → ❌ 不是独立实体，合并为 Customer 节点的属性
```

**条件 2：它会被多个东西引用，或需要被独立查询**

```
cus_contact_info:
  一个联系人可能同时出现在多个客户里 → ✅ 需要独立查询，变成节点

cus_corp_base_info:
  注册资本只属于某个客户，不会被共享 → ❌ 不需要独立存在，变成属性
```

### 5.3 本体不只是"翻译"

```
MySQL 表结构（隐含的）          本体额外提供的
───────────────────────────────────────────────────
表 A 有外键指向表 B           ✅ 关系（两边都有）
"这个外键叫 cus_no"          →  "这个关系语义上叫 hasContact"
                              →  "Customer 有子类 EnterpriseCustomer"
                              →  "cusName 是必填的"（SHACL 约束）
                              →  "注册资本必须是正数"（值域约束）
```

MySQL 只保证**结构正确**，本体额外保证**语义正确**。

---

## 六、neosemantics 的语义层

### 6.1 neosemantics 做什么

把本体"存进" Neo4j，让 Neo4j 不仅"存数据"，还"懂数据"。

没有 neosemantics，Neo4j 里只有裸数据（节点标签、关系类型、属性）。

有了 neosemantics，Neo4j 里同时存着数据的"说明书"：
- Customer 有子类 EnterpriseCustomer, PersonalCustomer
- hasContact 的方向只能是 Customer → ContactPerson
- cusName 是必填的
- registeredCapital 必须是数字

### 6.2 语义层的三个实际用途

**1. Text-to-Cypher 时，LLM 能查"词典"**

```cypher
-- LLM 查询本体：
CALL n10s.ontoSearch.search("客户名称")
-- 返回: Customer.cusName (rdfs:label: "客户名称")
-- LLM 精确知道 cusName 就是客户名 → 生成正确 Cypher
```

**2. 数据校验，SHACL 约束**

```cypher
CALL n10s.shacl.validate()
-- ✅ Customer C001: cusName = "三一集团" — 通过
-- ❌ Customer C099: cusName 为空 — 违反约束
```

**3. 子类推理**

```
本体定义：EnterpriseCustomer rdfs:subClassOf Customer

查询：MATCH (c:Customer) RETURN count(c)
→ 自动包含 EnterpriseCustomer + PersonalCustomer

MySQL 里没有"子类"概念，cus_base_type = '1' 只是一个字段值，
数据库不会自动推导"企业客户也是客户"。
```

### 6.3 对比总结

| | 没有 neosemantics | 有 neosemantics |
|---|---|---|
| 数据长什么样 | ✅ 有节点和关系 | ✅ 有节点和关系 |
| 数据意味着什么 | ❌ 不知道 | ✅ 有类层级、属性含义、约束规则 |
| LLM 能不能理解数据 | ❌ 靠猜 | ✅ 查本体词典 |
| 数据合不合规 | ❌ 无法自动校验 | ✅ SHACL 校验 |
| 能不能推理子类 | ❌ 不能 | ✅ 能 |

---

## 七、推理引擎

### 7.1 定位

推理引擎**不是一个产品/库**，而是自己组装的**服务层**，把四块能力拼起来。

### 7.2 四种能力的实现来源

| 能力 | 用什么 | 做什么 |
|------|--------|--------|
| 风险传导 | Neo4j GDS 图算法 | PageRank、最短路径、环路检测 |
| 完整性检查 | neosemantics SHACL | 本体约束校验 |
| 一致性检查 | 自定义 Cypher 规则 | 业务规则（如高负债高评级矛盾） |
| 推断补全 | LLM | 给上下文让 Claude 推断 |

### 7.3 风险传导实现（Neo4j GDS）

```python
async def risk_propagation(self, company_name: str, depth: int = 3):
    """风险传导分析"""
    
    # Step 1: 找到目标节点的所有 N 度关联
    cypher = """
    MATCH path = (start:EnterpriseCustomer {cusName: $name})
                 -[:relatedTo*1..3]-(affected:EnterpriseCustomer)
    WHERE start <> affected
    RETURN affected.cusName AS name,
           affected.ratingGrade AS rating,
           length(path) AS distance
    ORDER BY distance
    """
    results = await self.execute(cypher, {"name": company_name})
    
    # Step 2: 用 GDS PageRank 计算影响权重
    # Step 3: 组合结果 → 返回给 LLM 生成报告
    return {
        "affected_companies": results,
        "propagation_paths": paths,
        "risk_level": self._calculate_risk(results)
    }
```

### 7.4 完整性检查实现（neosemantics SHACL）

```python
async def completeness_check(self, cus_name: str):
    """数据完整性检查"""
    
    # Step 1: 从本体获取该类型实体的必填属性
    ontology_props = await self._get_required_properties("EnterpriseCustomer")
    
    # Step 2: 查实际数据有哪些属性
    # Step 3: 对比 → 找出缺失项
    missing = [p for p in ontology_props if not actual.get(p)]
    
    return {
        "entity": cus_name,
        "required_fields": len(ontology_props),
        "filled_fields": len(ontology_props) - len(missing),
        "missing_fields": missing,
        "completeness_rate": f"{(1 - len(missing)/len(ontology_props))*100:.1f}%"
    }
```

### 7.5 一致性检查实现（自定义 Cypher 规则）

```python
rules = [
    {
        "name": "高负债高评级",
        "description": "资产负债率>70% 但评级为 AA 以上",
        "cypher": """
        MATCH (c:EnterpriseCustomer)
        WHERE c.ratingGrade IN ['AAA','AA+','AA']
          AND c.assetLiabilityRatio > 0.7
        RETURN c.cusName, c.ratingGrade, c.assetLiabilityRatio
        """
    },
    {
        "name": "担保圈风险",
        "description": "A担保B、B担保C、C又担保A → 闭环",
        "cypher": """
        MATCH path = (a)-[:guarantee*2..5]->(a)
        RETURN [n IN nodes(path) | n.cusName] AS circle
        """
    },
    {
        "name": "同一联系人多企业",
        "description": "同一手机号出现在 3 家以上企业",
        "cypher": """
        MATCH (p:ContactPerson)
        WITH p.contactMobilePhone AS phone, count(*) AS cnt
        WHERE cnt >= 3
        MATCH (c:Customer)-[:hasContact]->(p:ContactPerson)
        WHERE p.contactMobilePhone = phone
        RETURN phone, collect(c.cusName) AS companies, cnt
        """
    }
]
```

### 7.6 推断补全实现（LLM）

```python
async def inference_fill(self, cus_name: str, target_field: str):
    """推断缺失信息"""
    
    # Step 1: 取已知信息作为上下文
    context = await self._get_customer_context(cus_name)
    
    # Step 2: 让 LLM 推断
    prompt = f"""
    根据以下已知信息，推断该客户可能的{target_field}。
    已知信息：
    - 关联企业: {context['related_companies']}
    - 所在地区: {context['region']}
    请推断并说明推理依据。
    """
    
    answer = await self.llm.ainvoke(prompt)
    return answer
```

### 7.7 推理引擎的文件结构

```
推理引擎 (reasoning_service.py)
├── risk_propagation.py       → 用 Neo4j GDS 图算法
├── completeness_check.py     → 用 neosemantics SHACL
├── consistency_check.py      → 自定义 Cypher 规则（自己写）
└── inference.py              → 用 LLM 推断

对外暴露统一接口：
  POST /api/reasoning/propagate   → 风险传导
  POST /api/reasoning/validate    → 完整性/一致性校验
  POST /api/reasoning/infer       → 推断补全
```

---

## 八、整体架构总结

```
用户提问
    │
    ▼
ChatOrchestrator（意图识别）
    │
    ├── 精确查询类 → Text-to-Cypher
    │                (LangChain GraphCypherQAChain)
    │                例: "三一集团有哪些联系人？"
    │
    ├── 语义搜索类 → GraphRAG
    │                (neo4j-graphrag)
    │                例: "和张三公司类似的客户？"
    │
    ├── 深度分析类 → 两者结合
    │                例: "分析三一集团的风险"
    │
    └── 推理/校验类 → 推理引擎
                     (Neo4j GDS + SHACL + 自定义规则 + LLM)
                     例: "客户资料完整吗？""风险会传导给谁？"
```

### 技术选型总结

| 模块 | 方案 | 代码量 |
|------|------|--------|
| Text-to-Cypher | LangChain `GraphCypherQAChain` | ~50-80 行 |
| GraphRAG | neo4j-graphrag 库 | ~100-150 行 |
| 推理引擎 | 自建服务层（GDS + SHACL + Cypher 规则 + LLM） | ~300-400 行 |
