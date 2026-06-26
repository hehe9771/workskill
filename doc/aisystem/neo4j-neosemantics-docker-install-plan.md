# Neo4j + neosemantics Docker 安装报告

> 创建日期：2026-06-25
> **状态：✅ 安装完成并验证通过**

---

## 一、项目调研总结

### 1.1 Neo4j

| 项目 | 说明 |
|------|------|
| 定位 | 高性能图数据库，支持事务型网络结构存储 |
| 最新版本 | **2026.05.0**（latest）、5.26.27、4.4.48 |
| 许可证 | GPL-3.0（Community）/ 商业许可（Enterprise） |
| Docker 镜像 | `neo4j:latest`（2026.05.0）、`neo4j:5.26.27`、`neo4j:4.4.48` |
| 端口 | 7474（HTTP/Browser）、7687（Bolt/协议） |

### 1.2 neosemantics（n10s）

| 项目 | 说明 |
|------|------|
| 定位 | Neo4j 插件，实现 RDF 数据导入/导出（W3C 标准） |
| 最新版本 | **2025.06.1**；Neo4j 版本对应版：5.26.0、5.20.0、5.18.0 等 |
| 核心能力 | RDF 无损存储、OWL/RDFS/SKOS 本体导入、SHACL 校验、属性图→RDF 导出 |
| 安装方式 | jar 包放入 Neo4j `plugins/` 目录 + 修改 `neo4j.conf` |
| 依赖 | APOC 插件（JSON-LD 格式必需） |
| Docker 官方支持 | **无**，需自定义 Dockerfile 或 volume 挂载 |

### 1.3 版本兼容矩阵

| Neo4j 版本 | neosemantics 版本 | 说明 |
|------------|-------------------|------|
| 2026.05.0 | 2025.06.1 | 最新组合，风险较高 |
| **5.26.27** | **5.26.0** | **推荐：稳定匹配** |
| 4.4.48 | 4.x 系列 | 旧版，不推荐 |

---

## 二、Docker 安装可行性评估

### 结论：✅ 可行

**方案选择：**

| 方案 | 优点 | 缺点 | 推荐 |
|------|------|------|------|
| A. 自定义 Dockerfile | 可复现、一键构建、版本锁定 | 首次构建稍慢 | ✅ **推荐** |
| B. docker-compose + volume 挂载 | 灵活、无需构建 | 每次启动需确保文件就位 | 备选 |
| C. 直接运行 + 手动拷贝 jar | 简单 | 不可复现、容器重启可能丢失 | ❌ 不推荐 |

---

## 三、安装计划

### Phase 1：环境准备（5 min）

**目标**：确认 Docker 环境就绪

```powershell
# 检查 Docker 是否安装并运行
docker --version
docker info

# 检查 Docker Desktop 是否启动（Windows）
# 如未启动，从开始菜单启动 Docker Desktop
```

**验证**：`docker info` 正常返回，无报错。

---

### Phase 2：构建自定义 Docker 镜像（10 min）

**目标**：构建包含 neosemantics 的 Neo4j 镜像

**创建目录结构：**

```
D:\mydoc\workskill\neo4j-n10s\
├── Dockerfile
├── plugins/              ← 存放 neosemantics jar
└── conf/
    └── neo4j-custom.conf ← 自定义配置
```

**Dockerfile 内容：**

```dockerfile
FROM neo4j:5.26.27

# 下载 neosemantics 5.26.0 jar
ADD https://github.com/neo4j-labs/neosemantics/releases/download/5.26.0/neosemantics-5.26.0.jar /plugins/

# 复制自定义配置
COPY conf/neo4j-custom.conf /conf/

# 暴露端口
EXPOSE 7474 7687
```

**neo4j-custom.conf 内容：**

```properties
# 启用 neosemantics 过程（无限制执行）
dbms.security.procedures.unrestricted=n10s.*,apoc.*

# 挂载 RDF HTTP 端点
dbms.unmanaged_extension_classes=n10s.endpoint=/rdf

# 插件发现路径（默认已包含 /plugins）
dbms.plugin.path=/plugins
```

**构建命令：**

```powershell
cd D:\mydoc\workskill\neo4j-n10s
docker build -t neo4j-n10s:5.26 .
```

**验证**：`docker images | findstr neo4j-n10s` 显示镜像。

---

### Phase 3：启动容器（5 min）

**启动命令：**

```powershell
docker run -d \
  --name neo4j-n10s \
  --publish 7474:7474 \
  --publish 7687:7687 \
  --volume $HOME/neo4j-n10s/data:/data \
  --volume $HOME/neo4j-n10s/logs:/logs \
  --env NEO4J_AUTH=neo4j/password123 \
  neo4j-n10s:5.26
```

> ⚠️ 生产环境请替换 `password123` 为强密码，并通过环境变量或 secret 管理。

**验证**：
```powershell
# 容器状态
docker ps | findstr neo4j-n10s

# 日志无报错
docker logs neo4j-n10s --tail 20
```

---

### Phase 4：验证插件加载（5 min）

**访问 Neo4j Browser**：http://localhost:7474  
使用账号 `neo4j` / 密码 `password123` 登录。

**验证步骤：**

```cypher
// 1. 检查 neosemantics 过程是否加载
CALL dbms.procedures() YIELD name, signature
WHERE name STARTS WITH 'n10s'
RETURN name, signature;

// 2. 测试 RDF 端点
:GET http://localhost:7474/rdf/ping

// 3. 初始化图配置（使用前必须执行）
CREATE CONSTRAINT n10s_unique_uri FOR (r:Resource) REQUIRE r.uri IS UNIQUE;
CALL n10s.graphconfig.init();
```

**验证结果**：
- 步骤 1 返回 20+ 条 `n10s.*` 过程
- 步骤 2 返回 `{"message":"pong"}`
- 步骤 3 无报错

---

### Phase 5：功能测试（10 min）

**导入测试 RDF 数据：**

```cypher
// 加载远程 RDF 示例（DBpedia）
CALL n10s.rdf.import.fetch(
  "https://raw.githubusercontent.com/neo4j-labs/neosemantics/4.3/src/test/resources/schema/schema.org.ntriples",
  "N-Triples"
);

// 查看导入的类
MATCH (n:Class) RETURN n.uri, n.name LIMIT 10;
```

---

## 四、风险与注意事项

| 风险 | 等级 | 应对措施 |
|------|------|----------|
| neosemantics 5.26.0 与 Neo4j 5.26.27 小版本不匹配 | LOW | jar 包按主版本号匹配，通常兼容 |
| 容器重启后配置丢失 | MEDIUM | 数据已通过 volume 持久化；配置固化在镜像中 |
| 端口冲突（7474/7687 被占用） | LOW | 修改映射端口，如 `8474:7474` |
| APOC 未安装导致 JSON-LD 失败 | LOW | 后续按需添加 APOC jar |

---

## 五、后续扩展（✅ 已完成）

1. ~~**APOC 插件**~~：✅ 已安装 `apoc-5.26.0-extended.jar`（238 个过程）
2. ~~**docker-compose.yml**~~：✅ 已创建，封装启动参数与数据卷
3. ~~**数据持久化**~~：✅ D 盘挂载 `D:\neo4j-data\`（data/logs/conf）
4. **备份策略**：定期备份 `D:\neo4j-data\data` 目录
5. **监控**：接入 Prometheus + Grafana（Neo4j 原生支持）

---

## 六、执行步骤总结

| # | 步骤 | 预计耗时 | 验证点 |
|---|------|----------|--------|
| 1 | 环境检查（Docker） | 5 min | `docker info` 正常 |
| 2 | 创建项目目录 + Dockerfile | 5 min | 文件就位 |
| 3 | 构建镜像 | 10 min | `docker images` 显示镜像 |
| 4 | 启动容器 | 5 min | `docker ps` 运行中 |
| 5 | 浏览器访问验证 | 5 min | http://localhost:7474 可访问 |
| 6 | 插件功能验证 | 5 min | n10s 过程列表返回 |
| 7 | 导入测试数据 | 5 min | RDF 数据查询成功 |
| **总计** | | **~40 min** | |

---

## 七、实际执行结果（2026-06-25）

### 7.1 安装结果

| 步骤 | 状态 | 说明 |
|------|------|------|
| 环境检查 | ✅ | Docker v29.5.3 已安装 |
| 目录创建 | ✅ | `neo4j-n10s/` 结构就位 |
| 下载 jar | ✅ | neosemantics-5.26.0.jar（12.8MB） |
| 构建镜像 | ✅ | `neo4j-n10s:5.26` 构建成功（< 2s，缓存命中） |
| 启动容器 | ✅ | 4 秒完成启动 |
| 插件验证 | ✅ | **55 个 n10s 过程已加载** |
| 图配置初始化 | ✅ | `n10s.graphconfig.init()` 成功 |
| RDF 导入 | ✅ | 5 三元组导入并解析成功 |
| 数据查询 | ✅ | 节点和关系查询正常 |

### 7.2 遇到的问题与解决

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| Docker Desktop 未运行 | daemon 未启动 | 自动启动 Docker Desktop |
| jar 文件无效（ZipException） | `ADD` 指令下载了 GitHub 重定向 HTML | 改为 `curl -L` 预下载 + `COPY` |
| `dbms.procedures()` 不存在 | Neo4j 5.x 语法变更 | 改用 `SHOW PROCEDURES` |
| RDF HTTP 端点 404 | Neo4j 5.x 移除 `unmanaged_extension_classes` | 使用 Cypher 过程替代（核心功能不受影响） |
| 外部 RDF URL 导入失败 | 容器网络无法访问外部 URL | 使用 `n10s.rdf.import.inline` 内联导入验证 |

### 7.3 当前运行状态（最终版）

```
镜像:      neo4j-n10s:5.26（含 neosemantics + APOC）
容器:      neo4j-n10s，运行正常（docker-compose 管理）
端口:      7474（Browser）、7687（Bolt）
认证:      neo4j / password123
数据卷:    D:\neo4j-data\data（数据库）、D:\neo4j-data\logs（日志）、D:\neo4j-data\conf（配置）
插件:      neosemantics（55 过程）+ APOC extended（238 过程）
测试数据:  2 个 Person 节点（张三、李四）+ 关系
持久化:    ✅ 容器重启后数据完整保留
```

### 7.4 访问方式

- **Neo4j Browser**: http://localhost:7474
- **Bolt 协议**: `bolt://localhost:7687`
- **Cypher Shell**: `docker exec neo4j-n10s cypher-shell -u neo4j -p password123`

### 7.5 注意事项

1. **Neo4j 5.x 变更**：`dbms.unmanaged_extension_classes` 已移除，RDF HTTP 端点不可用，所有 RDF 操作通过 Cypher 过程完成
2. **APOC 版本**：使用 extended 版（含 couchbase、bolt 等扩展连接器），核心文本/数学工具过程不在该版本中
3. **数据卷**：数据、日志、配置均持久化到 `D:\neo4j-data\`，容器删除重建不影响数据
4. **管理命令**：`docker compose up -d` 启动、`docker compose down` 停止、`docker compose logs -f` 查看日志
