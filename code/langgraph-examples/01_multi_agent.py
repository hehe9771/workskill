"""
LangGraph 示例 1：多 Agent 协作 - 研究-写作-审核流水线

三个 Agent 分工协作，审核不满意就打回重写，最多循环 3 次防止死循环。

数据流：
START → researcher → writer → reviewer ─┬─ PASS → END
                                        └─ REVISE → writer（循环）

依赖：pip install langgraph langchain-openai
"""
import os
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END, START


# ===== 状态定义 =====

class State(TypedDict):
    topic: str           # 主题
    research: str        # 研究结果
    draft: str           # 草稿
    review: str          # 审核意见
    revision_count: int  # 修订次数


# ===== LLM 初始化 =====

llm = ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7,
)


# ===== 节点定义 =====

def researcher(state: State) -> dict:
    """研究 Agent：收集主题相关信息"""
    response = llm.invoke([
        SystemMessage(content="你是研究员。针对给定主题，列出 3-5 个核心要点。"),
        HumanMessage(content=f"主题：{state['topic']}")
    ])
    return {"research": response.content}


def writer(state: State) -> dict:
    """写作 Agent：根据研究和审核意见撰写文章"""
    feedback = f"\n\n审核意见（请改进）：{state['review']}" if state["review"] else ""
    response = llm.invoke([
        SystemMessage(content="你是作者。根据研究要点写一篇文章，200字以内。"),
        HumanMessage(content=f"研究要点：{state['research']}{feedback}")
    ])
    return {"draft": response.content}


def reviewer(state: State) -> dict:
    """审核 Agent：评估文章质量"""
    response = llm.invoke([
        SystemMessage(content="你是审核员。评估文章质量，给出 PASS 或 REVISE + 改进建议。"),
        HumanMessage(content=f"文章：{state['draft']}")
    ])
    return {"review": response.content}


# ===== 路由逻辑 =====

def route_review(state: State) -> str:
    """根据审核结果决定下一步"""
    if "PASS" in state["review"].upper():
        return "done"
    if state["revision_count"] >= 3:
        print("⚠️  已达到最大修订次数，强制结束")
        return "done"  # 防止无限循环
    return "revise"


# ===== 构建图 =====

def build_graph() -> StateGraph:
    graph = StateGraph(State)

    # 添加节点
    graph.add_node("researcher", researcher)
    graph.add_node("writer", writer)
    graph.add_node("reviewer", reviewer)

    # 添加边
    graph.add_edge(START, "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "reviewer")
    graph.add_conditional_edges("reviewer", route_review, {
        "revise": "writer",      # 打回重写
        "done": END              # 通过
    })

    return graph.compile()


# ===== 运行 =====

if __name__ == "__main__":
    app = build_graph()

    result = app.invoke({
        "topic": "LangGraph 在企业的落地场景",
        "review": "",
        "research": "",
        "draft": "",
        "revision_count": 0
    })

    print("=" * 60)
    print(f"主题：{result['topic']}")
    print(f"修订次数：{result['revision_count']}")
    print("=" * 60)
    print(f"\n研究要点：\n{result['research']}")
    print(f"\n最终文章：\n{result['draft']}")
    print(f"\n审核意见：\n{result['review']}")
