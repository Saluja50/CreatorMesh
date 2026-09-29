from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from app.models.planner import ContentPlan
from app.llm.client import get_llm


class State(TypedDict):
    topic: str
    plan: str
    draft: str


def planner_node(state: State):
    llm = get_llm()

    structured_llm = llm.with_structured_output(ContentPlan)

    plan = structured_llm.invoke(
        f"""
Create a content plan for a LinkedIn post about:

{state['topic']}

The target audience is computer science students.
"""
    )

    return {
        "plan": plan.model_dump_json()
    }

def writer_node(state: State):
    llm = get_llm()

    response = llm.invoke(
        f"""
Write a short LinkedIn post based on this plan:

{state['plan']}
"""
    )

    return {
        "draft": response.text
    }


graph_builder = StateGraph(State)

graph_builder.add_node("planner", planner_node)
graph_builder.add_node("writer", writer_node)

graph_builder.add_edge(START, "planner")
graph_builder.add_edge("planner", "writer")
graph_builder.add_edge("writer", END)

graph = graph_builder.compile()


if __name__ == "__main__":
    result = graph.invoke({
        "topic": "ICPC programming competitions",
        "plan": "",
        "draft": "",
    })

    print("\n--- FINAL STATE ---")
    print(result)