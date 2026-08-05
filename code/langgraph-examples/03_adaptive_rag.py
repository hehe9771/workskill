"""
LangGraph 示例 3：自适应 RAG - 检索质量不足时自动重试

先做向量检索，LLM 评估相关性，不够则降级到网络搜索。

数据流：
retrieve → grade ─┬─ YES → generate → END
                  └─ NO  → web_search → generate → END

依赖：pip install langgraph langchain-openai
"""
import os
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END, START


# ===== 状态定义 =====

class RAGState(TypedDict):
    question: str
    documents: list[str]
    is_relevant: bool
    web_search: bool
    answer: str


# ===== LLM 初始化 =====

llm = ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
)


# ===== 模拟检索工具 =====
# 实际项目中替换为你的 retriever 和搜索工具

def mock_vector_search(query: str) -> list[str]:
    """模拟向量检索（实际项目中用 FAISS/Chroma/Pinecone 等）"""
    # 模拟：某些问题检索不到相关内容
    if "langgraph" in query.lower():
        return [
            "LangGraph 是 LangChain 团队开发的框架，用于构建有状态的多 Agent 应用。",
            "LangGraph 基于图论概念，支持循环、条件分支和状态持久化。"
        ]
    return []  # 模拟检索失败


def mock_web_search(query: str) -> list[str]:
    """模拟网络搜索（实际项目中用 Tavily/Serper/Bing API）"""
    return [
        f"网络搜索结果：关于 '{query}' 的最新信息...",
        "LangGraph 最新版本支持子图、并行执行和更好的可视化功能。"
    ]


# ===== 节点定义 =====

def retrieve(state: RAGState) -> dict:
    """向量检索"""
    docs = mock_vector_search(state["question"])
    return {"documents": docs}


def grade_relevance(state: RAGState) -> dict:
    """LLM 评估检索结果是否相关"""
    if not state["documents"]:
        return {"is_relevant": False}

    context = "\n".join(state["documents"])
    response = llm.invoke([
        SystemMessage(content="判断以下文档是否包含回答问题的信息，只回答 YES 或 NO"),
        HumanMessage(content=f"问题：{state['question']}\n文档：{context}")
    ])
    is_relevant = "YES" in response.content.upper()
    return {"is_relevant": is_relevant}


def web_search(state: RAGState) -> dict:
    """向量检索失败时降级到网络搜索"""
    print("⚠️  向量检索质量不足，降级到网络搜索...")
    results = mock_web_search(state["question"])
    return {"web_search": True, "documents": results}


def generate(state: RAGState) -> dict:
    """基于文档生成答案"""
    context = "\n".join(state["documents"])
    response = llm.invoke([
        SystemMessage(content="根据提供的上下文回答问题。如果上下文信息不足，说明无法回答。"),
        HumanMessage(content=f"问题：{state['question']}\n上下文：{context}")
    ])
    return {"answer": response.content}


# ===== 路由逻辑 =====

def route_after_grade(state: RAGState) -> str:
    """根据相关性判断决定下一步"""
    if state["is_relevant"]:
        return "generate"
    if state.get("web_search"):
        return "generate"  # 网络搜索后强制生成
    return "web_search"    # 向量库不够，降级网络搜索


# ===== 构建图 =====

def build_graph():
    graph = StateGraph(RAGState)

    graph.add_node("retrieve", retrieve)
    graph.add_node("grade", grade_relevance)
    graph.add_node("generate", generate)
    graph.add_node("web_search", web_search)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "grade")
    graph.add_conditional_edges("grade", route_after_grade, {
        "generate": "generate",
        "web_search": "web_search"
    })
    graph.add_edge("web_search", "generate")
    graph.add_edge("generate", END)

    return graph.compile()


# ===== 运行 =====

if __name__ == "__main__":
    app = build_graph()

    # 测试 1：能检索到的问题
    print("=" * 60)
    print("测试 1：能检索到的问题")
    print("=" * 60)
    result = app.invoke({
        "question": "什么是 LangGraph？",
        "documents": [],
        "is_relevant": False,
        "web_search": False,
        "answer": ""
    })
    print(f"\n✅ 答案：\n{result['answer']}")

    # 测试 2：检索不到，触发降级
    print("\n" + "=" * 60)
    print("测试 2：检索不到，触发网络搜索降级")
    print("=" * 60)
    result = app.invoke({
        "question": "LangGraph 最新版本有什么新功能？",
        "documents": [],
        "is_relevant": False,
        "web_search": False,
        "answer": ""
    })
    print(f"\n✅ 答案：\n{result['answer']}")
