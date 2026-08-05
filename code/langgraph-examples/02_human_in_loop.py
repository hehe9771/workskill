"""
LangGraph 示例 2：人工介入（Human-in-the-loop）

关键操作（如发邮件）前暂停，等待人工确认。

核心 API：
- interrupt()：节点内暂停，保存状态
- Command(resume=...)：传入人工决策，恢复执行

依赖：pip install langgraph langchain-openai
"""
import os
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END, START
from langgraph.types import Command, interrupt


# ===== 状态定义 =====

class EmailState(TypedDict):
    recipient: str
    subject: str
    draft: str
    approved: bool


# ===== LLM 初始化 =====

llm = ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.5,
)


# ===== 节点定义 =====

def draft_email(state: EmailState) -> dict:
    """LLM 起草邮件"""
    response = llm.invoke([
        SystemMessage(content="根据主题起草一封专业邮件，简洁得体。"),
        HumanMessage(content=f"收件人：{state['recipient']}\n主题：{state['subject']}")
    ])
    return {"draft": response.content}


def human_approval(state: EmailState) -> dict:
    """暂停等待人工审批

    interrupt() 会保存当前状态并返回，
    需要人工通过 Command(resume=...) 恢复执行。
    """
    human_decision = interrupt({
        "draft": state["draft"],
        "message": "请审核邮件内容，输入 approve 发送 / reject 退回修改"
    })
    return {"approved": human_decision == "approve"}


def send_email(state: EmailState) -> dict:
    """发送邮件（此处模拟）"""
    print(f"\n✅ 已发送到 {state['recipient']}")
    print(f"📧 内容：\n{state['draft']}")
    return {}


# ===== 构建图 =====

def build_graph():
    graph = StateGraph(EmailState)

    graph.add_node("draft", draft_email)
    graph.add_node("approve", human_approval)
    graph.add_node("send", send_email)

    graph.set_entry_point("draft")
    graph.add_edge("draft", "approve")
    graph.add_conditional_edges(
        "approve",
        lambda s: "send" if s["approved"] else "draft"
    )

    # 关键：必须配置 checkpointer 才能使用 interrupt
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


# ===== 运行 =====

if __name__ == "__main__":
    app = build_graph()
    config = {"configurable": {"thread_id": "email-001"}}

    print("📨 开始起草邮件...\n")

    # 第一次执行，会在 approve 节点暂停
    result = app.invoke(
        {
            "recipient": "boss@company.com",
            "subject": "周报",
            "draft": "",
            "approved": False
        },
        config
    )

    print("⏸  邮件起草完成，等待审批...")
    print(f"📝 草稿预览：\n{result['draft'][:200]}...")
    print("\n" + "=" * 60)

    # 人工审批
    user_input = input("请输入 approve / reject：").strip()

    # 通过 Command 恢复执行
    print("\n恢复执行...")
    app.invoke(Command(resume=user_input), config)
