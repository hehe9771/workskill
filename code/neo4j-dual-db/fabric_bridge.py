"""
方案 B：Neo4j Fabric 跨库视图（企业版）

Fabric 是 Neo4j 企业版功能，可以在一条查询里引用不同数据库。
限制：不能做跨库 JOIN，只能 UNION 或多次 USE。
"""

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

    async def close(self):
        await self._driver.close()


async def demo():
    driver = AsyncGraphDatabase.driver(
        "bolt://localhost:7687", auth=("neo4j", "password")
    )
    bridge = FabricBridge(driver)
    try:
        rows = await bridge.cross_db_query("三一集团有限公司")
        for row in rows:
            print(row)
    finally:
        await bridge.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())
