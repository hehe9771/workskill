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

---

## 九、SPARQL 是什么，Neo4j 需不需要它

### 9.1 SPARQL 是什么

SPARQL 是 **RDF 数据（三元组数据）的专用查询语言**，地位相当于关系型数据库里的 SQL。

RDF 数据是"主语-谓语-宾语"三元组格式：

```
<张三> -- <是员工> --> <公司A>
<张三> -- <工号> --> "E001"
<公司A> -- <位于> --> <北京>
```

查询语言的对应关系：

| 数据模型 | 查询语言 |
|---------|---------|
| 关系表 (SQL) | SQL |
| 属性图 (Neo4j) | Cypher |
| RDF 三元组 | **SPARQL** |

SPARQL 查询示例（查"张三属于哪个公司"）：

```sparql
PREFIX : <http://example.com/>
SELECT ?company
WHERE {
  :张三 :是员工 ?company .
}
```

### 9.2 SPARQL 的实际用途

1. **查本体/Ontology** — OWL、RDFS、SKOS 都是 RDF 格式，SPARQL 是查它们的标准语言
2. **知识图谱互通** — 不同系统间交换语义数据时，SPARQL 是 W3C 标准，跨平台通用
3. **Linked Data 查询** — DBpedia、Wikidata 等开放知识库都暴露 SPARQL 端点

### 9.3 Neo4j 需不需要 SPARQL

**结论：取决于数据源。**

| 问法 | 答案 |
|------|------|
| Neo4j 能跑 SPARQL 吗？ | 不能，它跑 Cypher |
| Neo4j 需要 SPARQL 吗？ | 不需要，Cypher 能完成等价查询 |
| 那 n10s 的意义是什么？ | **数据迁移桥梁**：把 RDF 世界的数据搬到属性图世界，搬完之后就用 Cypher 了 |

**两种情况：**

**情况 1：纯属性图场景 → 不需要 SPARQL**

数据本来就是节点+关系（用户、订单、商品等），Neo4j 用 Cypher 就够了，和 SPARQL 完全没关系。99% 的 Neo4j 用户属于这种情况。

**情况 2：数据源是 RDF/本体 → 需要 SPARQL 的等价能力**

如果数据来自语义网、OWL 本体、SKOS 词表等 RDF 格式，这些天然是三元组结构。这时：

- **不用 Neo4j**：直接用 RDF 存储（如 Apache Jena、GraphDB）+ SPARQL 查询，一条路走到底
- **用 Neo4j**：通过 n10s 把 RDF **导入转成属性图**，之后用 Cypher 查 — SPARQL 只在导入前用来验证/探索原始数据时用一下

**一句话**：Neo4j 的世界观是属性图 + Cypher，SPARQL 是 RDF 世界的东西。两者解决同类问题但路径不同，Neo4j 不需要 SPARQL，n10s 的作用就是让你**不再需要** SPARQL。

---

## 十、n10s + native 双库协同查询架构

### 10.1 为什么要分两个库

- **ontology_db（n10s 语义库）**：存本体定义、类层级、属性约束、标签词典
- **native_db（业务图库）**：存实际业务数据（客户、联系人、关系）、向量索引、GDS 投影

分库的好处：
- 语义层和业务层隔离，互不干扰
- 本体更新不影响业务数据
- 业务库可以独立做 GDS 投影和向量索引优化

### 10.2 核心痛点：Cypher 不支持跨库查询

Neo4j 支持单实例多数据库，但 **Cypher 原生不支持跨库查询**。不能写 `MATCH (n:ONTOLOGY.Customer) ... (d:NATIVE.User)` 这种跨库语句。这是架构上必须解决的核心问题。

### 10.3 双库数据分层

```
┌─────────────────────────────────────────────────────────────┐
│  Neo4j 实例（单实例多库）                                       │
│                                                               │
│  数据库 A: ontology_db（n10s 语义库）                           │
│  ├── 本体类定义（Customer、EnterpriseCustomer）                │
│  ├── 属性约束（SHACL）                                        │
│  ├── 类层级关系（rdfs:subClassOf）                             │
│  └── 标签词典（中英文映射，供 Text-to-Cypher 查）              │
│                                                               │
│  数据库 B: native_db（业务图库）                                │
│  ├── 实际业务数据（客户节点、联系人、关系）                     │
│  ├── 向量索引（Embedding）                                    │
│  ├── GDS 图投影（算法用）                                     │
│  └── 全量 ETL 同步自 MySQL                                    │
└─────────────────────────────────────────────────────────────┘
```

### 10.4 跨库协同三种方案

| 维度 | A 应用层编排 | B Fabric | C 元数据同步 |
|------|------------|---------|------------|
| 复杂度 | 低 | 中 | 低 |
| 实时性 | 实时 | 实时 | 有延迟（分钟级） |
| 企业版要求 | 否 | **是** | 否 |
| 跨库 JOIN | 应用层合并 | 不支持 | 无需求（元数据已在业务库）|
| 运维负担 | 低 | 中 | 需维护同步任务 |
| 推荐场景 | 查询复杂、实时性要求高 | 已有企业版、简单场景 | 本体变化不频繁 |

**实际建议**：A + C 组合。元数据同步解决 Text-to-Cypher 词典查询（高频），应用层编排处理深度组合查询（低频但复杂）。

---

## 十一、方案 A：应用层编排（推荐，90% 场景够用）

最简单也最可控：Python 层分别查两个库，在内存中合并结果。

代码路径：`code/neo4j-dual-db/cross_db_query.py`

```python
# code/neo4j-dual-db/cross_db_query.py

from neo4j import AsyncGraphDatabase
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class DualNeo4jConfig:
    uri: str
    user: str
    password: str
    ontology_db: str = "ontology_db"
    native_db: str = "native_db"


class CrossDBQueryService:
    """双库协同查询服务：应用层编排"""

    def __init__(self, config: DualNeo4jConfig):
        self._driver = AsyncGraphDatabase.driver(
            config.uri, auth=(config.user, config.password)
        )
        self._ontology_db = config.ontology_db
        self._native_db = config.native_db

    async def close(self):
        await self._driver.close()

    # ── 基础能力：指定库执行 Cypher ──────────────────────────

    async def _run_on(self, db: str, cypher: str, params: dict = None):
        """在指定数据库上执行 Cypher"""
        async with self._driver.session(database=db) as session:
            result = await session.run(cypher, parameters=params or {})
            return [record.data() async for record in result]

    async def query_ontology(self, cypher: str, params: dict = None):
        return await self._run_on(self._ontology_db, cypher, params)

    async def query_native(self, cypher: str, params: dict = None):
        return await self._run_on(self._native_db, cypher, params)

    # ── 场景 1：Text-to-Cypher 时查本体辅助 LLM ─────────────

    async def get_ontology_hints(self, keyword: str) -> list[dict]:
        """
        查本体词典，返回标签/属性的中英文映射，
        注入到 Text-to-Cypher 的 prompt 里，让 LLM 知道 cusName 是客户名称。
        """
        cypher = """
        CALL n10s.ontoSearch.search($keyword)
        YIELD term, uri, description
        RETURN term, uri, description
        LIMIT 20
        """
        try:
            return await self.query_ontology(cypher, {"keyword": keyword})
        except Exception as e:
            logger.error(f"本体词典查询失败: keyword={keyword}, error={e}")
            return []

    async def get_class_hierarchy(self, class_name: str) -> list[dict]:
        """
        查某类的子类层级，
        用于：用户问"查所有客户"时，自动展开到 EnterpriseCustomer + PersonalCustomer
        """
        cypher = """
        MATCH path = (parent {name: $class_name})<-[:subClassOf*]-(child)
        RETURN [n IN nodes(path) | n.name] AS hierarchy
        """
        return await self.query_ontology(cypher, {"class_name": class_name})

    # ── 场景 2：查询业务数据前先用本体校验查询条件 ─────────────

    async def get_required_properties(self, class_name: str) -> list[str]:
        """从本体获取某类的必填属性列表"""
        cypher = """
        MATCH (c {name: $class_name})-[:hasProperty]->(p)
        WHERE p.isRequired = true
        RETURN p.name AS prop_name
        """
        rows = await self.query_ontology(cypher, {"class_name": class_name})
        return [r["prop_name"] for r in rows]

    # ── 场景 3：跨库组合查询（最核心的场景）─────────────────────

    async def customer_full_profile(self, cus_name: str) -> dict:
        """
        完整客户画像：业务数据 + 语义元数据，跨库组装

        步骤：
        1. native_db 查业务数据（节点属性、关系）
        2. ontology_db 查该类型的语义定义（应有属性、约束）
        3. 合并，标记哪些字段缺失
        """
        # Step 1: 业务库查实际数据
        native_cypher = """
        MATCH (c:EnterpriseCustomer {cusName: $name})
        OPTIONAL MATCH (c)-[r]->(related)
        RETURN c {.cusName, .registerDate, .ratingGrade,
                  .assetLiabilityRatio} AS customer,
               collect({
                   rel_type: type(r),
                   target: labels(related)[0],
                   target_name: coalesce(related.cusName, related.contactName)
               }) AS relations
        """
        native_rows = await self.query_native(native_cypher, {"name": cus_name})
        if not native_rows:
            return {"error": f"未找到客户: {cus_name}"}

        customer = native_rows[0]["customer"]
        relations = native_rows[0]["relations"]

        # Step 2: 本体库查该类型的应有属性
        ontology_cypher = """
        MATCH (c {name: 'EnterpriseCustomer'})-[:hasProperty]->(p)
        RETURN p.name AS prop, p.description AS desc, 
               coalesce(p.isRequired, false) AS required
        """
        ontology_rows = await self.query_ontology(ontology_cypher)

        # Step 3: 合并，找出缺失字段
        actual_props = set(k for k, v in customer.items() if v is not None)
        completeness = []
        for row in ontology_rows:
            completeness.append({
                "property": row["prop"],
                "description": row["desc"],
                "present": row["prop"] in actual_props,
                "required": row["required"],
            })

        missing_required = [
            c["property"] for c in completeness
            if c["required"] and not c["present"]
        ]

        return {
            "customer": customer,
            "relations": relations,
            "completeness": completeness,
            "missing_required": missing_required,
            "completeness_rate": (
                f"{sum(1 for c in completeness if c['present']) "
                f"/ len(completeness) * 100:.1f}%"
                if completeness else "N/A"
            ),
        }

    # ── 场景 4：SHACL 校验 + 业务数据修复 ──────────────────────

    async def validate_and_report(self) -> dict:
        """
        用本体约束校验业务数据，返回违规列表
        """
        # Step 1: 在本体库跑 SHACL 校验
        try:
            shacl_result = await self.query_ontology(
                "CALL n10s.shacl.validate() YIELD report RETURN report"
            )
            violations = shacl_result[0]["report"] if shacl_result else []
        except Exception as e:
            logger.error(f"SHACL 校验失败: {e}")
            violations = []

        # Step 2: 对违规项，到业务库取详细数据
        issues = []
        for v in violations[:50]:  # 限制处理量
            detail_cypher = """
            MATCH (n) WHERE elementId(n) = $node_id
            RETURN labels(n) AS labels, properties(n) AS props
            """
            detail = await self.query_native(
                detail_cypher, {"node_id": v.get("node_id", "")}
            )
            issues.append({"violation": v, "detail": detail[0] if detail else None})

        return {"total_violations": len(violations), "issues": issues}


# ── 使用示例 ──────────────────────────────────────────────────

async def demo():
    config = DualNeo4jConfig(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="your_password",
    )
    svc = CrossDBQueryService(config)
    try:
        profile = await svc.customer_full_profile("三一集团有限公司")
        print(profile)
    finally:
        await svc.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())
```

---

## 十二、方案 B：Neo4j Fabric 跨库视图（企业版）

Fabric 是 Neo4j 企业版功能，可以在一条查询里引用不同数据库，用 `CALL` 过程桥接。

代码路径：`code/neo4j-dual-db/fabric_bridge.py`

```python
# code/neo4j-dual-db/fabric_bridge.py

from neo4j import AsyncGraphDatabase
import logging

logger = logging.getLogger(__name__)


class FabricBridge:
    """
    利用 Neo4j Fabric 做跨库查询。
    
    前置配置（需要在 Neo4j 中创建 Fabric 数据库）：
    
    CREATE DATABASE fabric;
    
    -- 在 fabric 数据库的 system 配置里注册两个分片：
    -- fabric_endpoint_ontology → ontology_db
    -- fabric_endpoint_native  → native_db
    """

    def __init__(self, driver, fabric_db: str = "fabric"):
        self._driver = driver
        self._fabric_db = fabric_db

    async def cross_db_query(self, cus_name: str) -> list[dict]:
        """
        Fabric 跨库查询：
        先查 native 库拿业务数据，再用结果查 ontology 库拿语义定义。
        
        注意：Fabric 的跨库是"串行调用"，不是 JOIN，
        本质和方案 A 类似，但封装在数据库层。
        """
        cypher = """
        // 先查 native 分片
        USE fabric_endpoint_native
        MATCH (c:EnterpriseCustomer {cusName: $name})
        RETURN c.cusName AS name, c.ratingGrade AS rating,
               c.assetLiabilityRatio AS debt_ratio,
               id(c) AS node_id
        
        UNION
        
        // 再查 ontology 分片（独立结果，需要应用层合并）
        USE fabric_endpoint_ontology
        MATCH (c {name: 'EnterpriseCustomer'})-[:hasProperty]->(p)
        RETURN p.name AS name, p.description AS rating, 
               coalesce(p.isRequired, false) AS debt_ratio,
               -1 AS node_id
        """
        async with self._driver.session(database=self._fabric_db) as session:
            result = await session.run(cypher, parameters={"name": cus_name})
            return [record.data() async for record in result]
```

### Fabric 的限制

- 企业版才有（Community 版不支持）
- 不能做跨库 JOIN，只能 UNION 或者多次 USE
- 实际收益有限，复杂度却增加了

---

## 十三、方案 C：元数据同步（消除跨库需求）

核心思路：**把本体库的元数据定期复制到业务库**，让业务库自给自足，彻底消除跨库查询。

代码路径：`code/neo4j-dual-db/metadata_sync.py`

```python
# code/neo4j-dual-db/metadata_sync.py

from neo4j import AsyncGraphDatabase
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class OntologyMetadataSync:
    """
    定期把 ontology_db 的元数据同步到 native_db，
    让业务库自带语义信息，查询不再需要跨库。
    
    同步内容：
    - 类定义 → 变成 native_db 的 __MetaClass 节点
    - 属性定义 → 变成 __MetaProperty 节点，挂到 __MetaClass 下
    - 标签词典 → 注入 __MetaClass.label_zh / label_en
    """

    def __init__(self, driver, ontology_db: str, native_db: str):
        self._driver = driver
        self._ontology_db = ontology_db
        self._native_db = native_db

    async def sync_once(self) -> dict:
        """执行一次全量元数据同步"""
        # Step 1: 从本体库导出所有类定义
        async with self._driver.session(database=self._ontology_db) as session:
            result = await session.run("""
                MATCH (c:Class)
                OPTIONAL MATCH (c)-[:hasProperty]->(p:Property)
                RETURN c.name AS class_name,
                       c.label_zh AS label_zh,
                       collect({
                           prop: p.name,
                           desc: p.description,
                           required: coalesce(p.isRequired, false),
                           datatype: p.datatype
                       }) AS properties
            """)
            class_defs = [record.data() async for record in result]

        logger.info(f"从本体库读取 {len(class_defs)} 个类定义")

        # Step 2: 写入业务库
        async with self._driver.session(database=self._native_db) as session:
            # 清除旧元数据
            await session.run("MATCH (n:__MetaClass) DETACH DELETE n")

            # 写入新元数据
            for cls in class_defs:
                await session.run(
                    """
                    CREATE (mc:__MetaClass {
                        name: $class_name,
                        label_zh: $label_zh,
                        synced_at: $synced_at
                    })
                    WITH mc
                    UNWIND $properties AS prop
                    CREATE (mp:__MetaProperty {
                        name: prop.prop,
                        description: prop.desc,
                        required: prop.required,
                        datatype: prop.datatype
                    })
                    CREATE (mc)-[:hasProperty]->(mp)
                    """,
                    parameters={
                        "class_name": cls["class_name"],
                        "label_zh": cls["label_zh"],
                        "synced_at": datetime.now().isoformat(),
                        "properties": cls["properties"],
                    },
                )

        logger.info(f"元数据同步完成: {len(class_defs)} 个类")
        return {
            "synced_classes": len(class_defs),
            "synced_at": datetime.now().isoformat(),
        }

    async def get_class_metadata_in_native(self, class_name: str) -> list[dict]:
        """
        同步后，业务库直接查元数据，无需跨库。
        Text-to-Cypher 时用这个替代方案 A 的 get_ontology_hints。
        """
        async with self._driver.session(database=self._native_db) as session:
            result = await session.run(
                """
                MATCH (mc:__MetaClass {name: $class_name})-[:hasProperty]->(mp)
                RETURN mp.name AS prop, mp.description AS desc,
                       mp.required AS required, mp.datatype AS datatype
                """,
                parameters={"class_name": class_name},
            )
            return [record.data() async for record in result]


# ── 定时任务（用 APScheduler 或 cron）────────────────────────

async def scheduled_sync():
    """每小时同步一次"""
    driver = AsyncGraphDatabase.driver(
        "bolt://localhost:7687", auth=("neo4j", "password")
    )
    syncer = OntologyMetadataSync(driver, "ontology_db", "native_db")
    try:
        result = await syncer.sync_once()
        logger.info(f"定时同步完成: {result}")
    finally:
        await driver.close()
```

---

## 十四、双库架构文件结构总结

```
code/neo4j-dual-db/
├── cross_db_query.py    → 方案 A：应用层编排（核心）
├── fabric_bridge.py     → 方案 B：Fabric 跨库（企业版）
└── metadata_sync.py     → 方案 C：元数据同步（消除跨库）
```

### 与第八章架构的关系

```
用户提问
    │
    ▼
ChatOrchestrator（意图识别）
    │
    ├── 精确查询类 → Text-to-Cypher
    │                └─ 查 native_db（方案C 已同步元数据，无需跨库）
    │
    ├── 语义搜索类 → GraphRAG
    │                └─ 查 native_db 向量索引
    │
    ├── 深度分析类 → 两者结合
    │                └─ 查 native_db（图遍历 + 向量检索）
    │
    ├── 推理/校验类 → 推理引擎
    │                ├─ SHACL 校验 → ontology_db（方案A 跨库编排）
    │                └─ 业务规则 → native_db
    │
    └── 元数据查询类 → ontology_db（本体词典、类层级）
                     └─ 或通过方案C 在 native_db 查 __MetaClass
