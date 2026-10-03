from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from app.models.planner import ContentPlan
from app.llm.client import get_llm
from app.graph.state import WorkflowState

State = WorkflowState


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

from app.agents.researcher import create_research_agent


research_agent = create_research_agent()


def researcher_node(state: State):
    result = research_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Research this topic: {state['topic']}. "
                        "Use the search tool and return structured research."
                    ),
                }
            ]
        }
    )

    research = result["structured_response"]

    return {
        "research": research.model_dump(),
        "status": "RESEARCH_COMPLETED",
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
graph_builder.add_node("researcher", researcher_node)
graph_builder.add_node("writer", writer_node)

graph_builder.add_edge(START, "planner")
graph_builder.add_edge("planner", "researcher")
graph_builder.add_edge("researcher", "writer")
graph_builder.add_edge("writer", END)
graph = graph_builder.compile()


if __name__ == "__main__":
    result = graph.invoke({
    "topic": "ICPC programming competitions",
    "platform": "LinkedIn",
    "target_audience": "Computer science students",
    "plan": {},
    "research": {},
    "draft": "",
    "editor_feedback": [],
    "revision_count": 0,
    "fact_check_results": [],
    "status": "STARTED",
})

    print("\n--- FINAL STATE ---")
    print(result)