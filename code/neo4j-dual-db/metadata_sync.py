"""
方案 C：元数据同步（消除跨库需求）

核心思路：把本体库的元数据定期复制到业务库，
让业务库自给自足，彻底消除跨库查询。
"""

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

    async def close(self):
        await self._driver.close()


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


if __name__ == "__main__":
    import asyncio
    asyncio.run(scheduled_sync())
