# LangGraph 学习笔记

> 整理日期：2026-07-09
> 代码示例：`code/langgraph-examples/`

---

## 一、什么是 LangGraph

LangGraph 是 LangChain 团队开发的框架，用于构建**有状态、多参与者**的 LLM 应用程序。它基于**图论**概念，将 LLM 工作流建模为**节点（Nodes）**和**边（Edges）**组成的图结构。

### 核心特性

| 特性 | 说明 |
|------|------|
| 循环支持 | 可以创建循环逻辑（不同于线性 Chain） |
| 持久化状态 | 内置状态管理，支持跨轮次记忆 |
| 人工介入 | 支持 Human-in-the-loop 模式 |
| 多 Agent 协作 | 天然支持多个 Agent 协同工作 |
| 时间旅行 | 回溯到任意历史状态重新执行 |

### 在 LangChain 生态中的定位

```
LangChain:  组件库（LLM、工具、检索器）
     ↓
LCEL:       组件编排（线性链，适合简单顺序流程）
     ↓
LangGraph:  复杂工作流（循环、多 Agent、状态管理）
```

LangGraph **不是替代** LangChain，而是在其基础上处理更复杂的场景。它底层依然可以使用 LangChain 的各种组件（LLM、Tool、Retriever 等）。

---

## 二、核心概念

### 2.1 图（Graph）

整个工作流被建模为一个有向图。

- **StateGraph**：最常用的图类型，状态驱动
- **MessageGraph**：专为消息列表设计的图（已不推荐，用 StateGraph 替代）

### 2.2 状态（State）

状态是图中所有节点共享的数据结构，通常用 `TypedDict` 定义：

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]  # 自动追加消息
    topic: str
    count: int
```

`Annotated[list, add_messages]` 是 LangGraph 的 reducer 机制 —— 节点返回新消息时会**追加**而非**覆盖**。

### 2.3 节点（Node）

节点是执行具体逻辑的函数，接收当前状态，返回状态更新（字典）：

```python
def my_node(state: State) -> dict:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}
```

### 2.4 边（Edge）

边定义节点之间的路由关系：

| 类型 | API | 说明 |
|------|-----|------|
| 普通边 | `add_edge(A, B)` | A 执行完必定到 B |
| 入口边 | `set_entry_point(A)` / `add_edge(START, A)` | 定义起始节点 |
| 条件边 | `add_conditional_edges(A, fn, {...})` | 根据函数返回值路由 |

### 2.5 编译与执行

```python
app = graph.compile()
result = app.invoke({"messages": ["你好"]})

# 流式执行
for chunk in app.stream({"messages": ["你好"]}):
    print(chunk)
```

---

## 三、适用场景

### 适合使用 LangGraph

| 场景 | 说明 |
|------|------|
| 多 Agent 协作 | 多个 Agent 分工合作（研究员+写手+审核员） |
| 需要人工介入 | 关键节点暂停等待人工审批 |
| 循环工作流 | 根据中间结果决定是否重试 |
| 复杂 RAG | 自适应检索、多路召回、相关性判断 |
| 长对话记忆 | 需要跨轮次状态管理 |
| 多步骤推理 | Agent 自我反思、自我修正 |

### 不适合使用 LangGraph

| 场景 | 建议方案 |
|------|----------|
| 单次 LLM 调用 | 直接调 API |
| 纯线性工作流 | LCEL（LangChain Expression Language） |
| 简单工具调用 | LangChain 的 AgentExecutor |

---

## 四、实战示例

> 完整代码见 `code/langgraph-examples/`

### 4.1 多 Agent 协作：研究-写作-审核流水线

三个 Agent 分工协作，审核不满意就打回重写，最多循环 3 次防止死循环。

**数据流：**
```
START → researcher → writer → reviewer ─┬─ PASS → END
                                        └─ REVISE → writer（循环）
```

**核心要点：**
- 每个 Agent 是一个独立的节点函数
- 通过 `add_conditional_edges` 实现条件路由
- 状态中增加 `revision_count` 字段控制循环上限

### 4.2 人工介入（Human-in-the-loop）

在关键操作（如发邮件）前暂停，等待人工确认后再执行。

**核心 API：**

```python
from langgraph.types import Command, interrupt

# 节点内暂停
human_decision = interrupt({"draft": draft, "message": "请审批"})

# 恢复执行
app.invoke(Command(resume="approve"), config)
```

**关键约束：**
- 必须配置 `checkpointer`（如 `MemorySaver`、`PostgresSaver`）
- 状态可跨进程、跨时间恢复
- 生产环境推荐用 `PostgresSaver`

### 4.3 自适应 RAG：检索质量不足时自动重试

先做向量检索，LLM 评估相关性，不够则降级到网络搜索。

**数据流：**
```
retrieve → grade ─┬─ YES → generate → END
                  └─ NO  → web_search → generate → END
```

**核心要点：**
- `grade_relevance` 节点让 LLM 判断检索质量
- 条件路由决定走生成还是降级搜索
- 避免"垃圾进垃圾出"的 RAG 问题

---

## 五、生产环境关键点

| 关注点 | 方案 |
|--------|------|
| 状态持久化 | `PostgresSaver` / `SqliteSaver` 替代 `MemorySaver` |
| 流式输出 | `app.stream()` 替代 `invoke()`，实现打字机效果 |
| 可视化 | `app.get_graph().draw_mermaid()` 生成流程图 |
| 错误处理 | 每个节点内部 try-except，返回错误状态字段 |
| 可观测性 | 接入 LangSmith 追踪每一步 token 消耗和延迟 |
| 子图 | 复杂工作流拆分为子图（Subgraph），提高可维护性 |
| 并行执行 | 用 `Send` API 实现节点并行 |

### 状态持久化配置示例

```python
from langgraph.checkpoint.postgres import PostgresSaver

# 开发环境
memory = MemorySaver()

# 生产环境
checkpointer = PostgresSaver.from_conn_string("postgresql://...")
app = graph.compile(checkpointer=checkpointer)
```

### 可视化示例

```python
# 生成 mermaid 格式流程图
mermaid_text = app.get_graph().draw_mermaid()
print(mermaid_text)

# 或在 Jupyter 中直接显示
from IPython.display import Image, display
display(Image(app.get_graph().draw_mermaid_png()))
```

---

## 六、安装与快速开始

```bash
# 安装
pip install langgraph langchain-openai

# 最小示例
from langgraph.graph import StateGraph, END, START
from typing import TypedDict

class State(TypedDict):
    count: int

def add_one(state: State):
    return {"count": state["count"] + 1}

graph = StateGraph(State)
graph.add_node("add", add_one)
graph.add_edge(START, "add")
graph.add_edge("add", END)
app = graph.compile()

print(app.invoke({"count": 0}))  # {'count': 1}
```

---

## 七、参考资料

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph)
- [LangChain 教程](https://python.langchain.com/docs/)
- [LangGraph 教程 - 构建有状态 Agent](https://langchain-ai.github.io/langgraph/tutorials/)
