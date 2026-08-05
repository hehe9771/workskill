"""
方案 A：应用层编排（推荐，90% 场景够用）

最简单也最可控：Python 层分别查两个库，在内存中合并结果。
"""

from neo4j import AsyncGraphDatabase
from dataclasses import dataclass
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
        """用本体约束校验业务数据，返回违规列表"""
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
