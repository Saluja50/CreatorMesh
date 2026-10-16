
from langgraph.graph import END, START, StateGraph
from typing import TypedDict


class GraphState(TypedDict):
    steps: list[str]
    approved: bool


def planner(state: GraphState):
    return {"steps": state["steps"] + ["planner"]}


def researcher(state: GraphState):
    return {"steps": state["steps"] + ["researcher"]}


def writer(state: GraphState):
    return {"steps": state["steps"] + ["writer"]}


def editor(state: GraphState):
    return {
        "steps": state["steps"] + ["editor"],
        "approved": True,
    }


def test_graph_runs_nodes_in_order():
    builder = StateGraph(GraphState)

    builder.add_node("planner", planner)
    builder.add_node("researcher", researcher)
    builder.add_node("writer", writer)
    builder.add_node("editor", editor)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "researcher")
    builder.add_edge("researcher", "writer")
    builder.add_edge("writer", "editor")
    builder.add_edge("editor", END)

    graph = builder.compile()

    result = graph.invoke({
        "steps": [],
        "approved": False,
    })

    assert result["steps"] == [
        "planner",
        "researcher",
        "writer",
        "editor",
    ]
    assert result["approved"] is True
