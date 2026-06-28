# Neo4j + neosemantics + APOC Docker 安装指南

> 版本: v1.0 | 日期: 2026-06-26
> 从历史会话中提取整理

---

## 一、版本信息

| 组件 | 版本 |
|------|------|
| Neo4j | 5.26.27 |
| neosemantics (n10s) | 5.26.0 |
| APOC | 5.26.0-extended |
| Docker 镜像 | neo4j-n10s:5.26 |
| Docker 容器名 | neo4j-n10s |

---

## 二、目录结构

```
neo4j-n10s/
├── Dockerfile                    # 自定义镜像构建
├── docker-compose.yml            # 容器编排
├── plugins/
│   ├── neosemantics-5.26.0.jar   # RDF/OWL 语义层插件
│   └── apoc-5.26.0-extended.jar  # 扩展过程库
├── conf/
│   └── neo4j-custom.conf         # Neo4j 自定义配置
├── ontology/
│   └── cus_ontology.ttl          # 本体定义文件
├── etl/
│   ├── mapping_config.yaml       # MySQL → RDF 映射规则
│   ├── db_connector.py           # MySQL 连接
│   ├── rdf_generator.py          # RDF 生成（~500 行，13 种实体生成器）
│   ├── neo4j_loader.py           # Neo4j 导入（docker exec cypher-shell）
│   └── main_etl.py               # 6 阶段编排脚本
└── output/
    └── *.ttl                     # 生成的 RDF 数据文件
```

---

## 三、Dockerfile

```dockerfile
FROM neo4j:5.26.27
COPY plugins/neosemantics-5.26.0.jar /plugins/
COPY plugins/apoc-5.26.0-extended.jar /plugins/
COPY conf/neo4j-custom.conf /conf/
EXPOSE 7474 7687
```

**构建命令：**
```bash
docker build -t neo4j-n10s:5.26 .
```

---

## 四、docker-compose.yml

```yaml
services:
  neo4j:
    image: neo4j-n10s:5.26
    container_name: neo4j-n10s
    ports:
      - "7474:7474"   # Neo4j Browser
      - "7687:7687"   # Bolt 协议
    environment:
      - NEO4J_AUTH=neo4j/password123
      - NEO4J_dbms_security_procedures_unrestricted=n10s.*,apoc.*
    volumes:
      - D:\neo4j-data\data:/data
      - D:\neo4j-data\logs:/logs
      - D:\neo4j-data\conf:/conf
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "password123", "RETURN 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
```

**启动命令：**
```bash
docker compose up -d
```

**验证容器状态：**
```bash
docker ps | grep neo4j-n10s
# 状态应显示 (healthy)
```

---

## 五、Neo4j 自定义配置

**neo4j-custom.conf：**
```conf
dbms.security.procedures.unrestricted=n10s.*,apoc.*
dbms.unmanaged_extension_classes=n10s.endpoint=/rdf
```

---

## 六、初始化图配置

连接 Neo4j 后执行：

```cypher
// 初始化 n10s 图配置
CALL n10s.graphconfig.init({
  handleMultival: "OVERWRITE",
  handleVocabUris: "SHORTEN",
  keepLangTag: false,
  keepCustomDataTypes: false
});

// 验证插件加载
CALL n10s.graphconfig.get();
```

---

## 七、ETL 技术栈

| 组件 | 技术 |
|------|------|
| Python 环境 | conda `picproject` |
| MySQL 连接 | pymysql + sqlalchemy |
| RDF 生成 | rdflib |
| Neo4j 导入 | docker exec cypher-shell（n10s.rdf.import.fetch） |
| 本体命名空间 | `http://mftcc.com/ontology/cus#` |
| 数据 URI 模式 | `http://mftcc.com/data/cus#customer/{identifier}` |

**Python 依赖：**
```bash
pip install pymysql sqlalchemy rdflib neo4j pyyaml
```

---

## 八、导入方式

通过 n10s 插件的 `n10s.rdf.import.fetch` 过程，将 RDF Turtle 文件从容器内 `/data/import` 目录加载：

```cypher
// 导入本体定义
CALL n10s.rdf.import.fetch("file:///data/import/ontology.ttl", "Turtle");

// 导入实例数据（分批，每批 < 1M 三元组）
CALL n10s.rdf.import.fetch("file:///data/import/01_dictionary.ttl", "Turtle");
CALL n10s.rdf.import.fetch("file:///data/import/02_customer.ttl", "Turtle");
// ...
```

---

## 九、ETL 执行结果

| 指标 | 数值 |
|------|------|
| 源数据库 | mftcc-cus-server（阿里云 RDS MySQL，205 张表） |
| 核心表 | 13 张 |
| 执行时间 | 162.1 秒（2.7 分钟） |
| 生成 RDF 三元组 | 1,167,572 条 |
| Neo4j 节点总数 | 221,588 |
| Neo4j 关系总数 | 49,606 |

**节点分布：**

| 标签 | 数量 | 占比 |
|------|------|------|
| Bank | 153,000 | 69% |
| PersonalCustomer | 15,170 | 7% |
| ContactPerson | 13,927 | 6% |
| BankAccount | 10,055 | 5% |
| FinancialReport | 10,389 | 5% |
| Invoice | 10,357 | 5% |
| EnterpriseCustomer | 8,000 | 4% |
| Industry | 1,772 | <1% |

**关系类型（12 种）：**

| 类型 | 数量 |
|------|------|
| hasContact | 12,900 |
| hasBankAccount | 10,400 |
| hasFinancialReport | 10,300 |
| hasInvoice | 9,700 |
| belongsToBank | 4,300 |
| parentIndustry | 1,700 |
| relatedTo | 23 |
| ... | ... |

---

## 十、踩坑记录

| 问题 | 解决方案 |
|------|---------|
| n10s graph config 初始化失败（图非空） | 非阻塞错误，已有数据时跳过配置步骤，支持幂等操作 |
| URI 唯一性约束已存在 | 捕获异常并跳过，属于幂等操作 |
| MySQL 中文注释乱码 | 指定 `charset=utf8mb4` 解决 |
| 客户 ID 特殊字符导致 URI 生成失败 | URI 生成函数加入字符清洗（sanitize） |
| n10s 单次导入 620MB+ 文件会失败 | 采用分批导入，每次 < 1M 三元组 |
| 大表（银行 15 万行）导入慢 | 采用 5000 行批次 offset 分页处理 |
| hasEvalIndex 关系查询返回空 | 源数据缺失模型-索引关联，非 ETL 问题 |
| 企业详情字段全部为空 | 确认是 MySQL 源数据本身未录入，非导入问题 |
