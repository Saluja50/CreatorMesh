from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from app.models.planner import ContentPlan
from app.llm.client import get_llm
from app.graph.state import WorkflowState
from app.agents.editor import review_draft
from app.graph.human_review import get_human_feedback

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

    feedback = state.get("editor_feedback", [])
    human_feedback = state.get("human_feedback", "").strip()

    
    if human_feedback and human_feedback.lower() != "approve":
        instruction = f"""
Revise the previous draft using this human feedback:
{human_feedback}

Also address the editor feedback where relevant:
{feedback}

Return only the revised LinkedIn post.
"""
    elif feedback:
        instruction = f"""
Revise the previous draft using this editor feedback:
{feedback}

Address every relevant point.
Return only the revised LinkedIn post.
"""
    else:
        instruction = """
Write a concise, engaging LinkedIn post based on the plan and research.
Use factual claims supported by the research.
Return only the post.
"""

    response = llm.invoke(
        f"""
Topic: {state['topic']}
Platform: {state['platform']}
Target audience: {state['target_audience']}

Content plan:
{state['plan']}

Research evidence:
{state['research']}

Previous draft:
{state['draft']}

{instruction}
"""
    )

    return {
    "draft": response.content,
    "revision_count": state.get("revision_count", 0) + 1,
    "human_feedback": "",
}
def editor_node(state: State):
    result = review_draft(
        draft=state["draft"],
        topic=state["topic"],
        platform=state["platform"],
    )

    return {
        "editor_approved": result.approved,
        "editor_feedback": result.feedback,
        "status": (
            "EDITOR_APPROVED"
            if result.approved
            else "EDITOR_REJECTED"
        ),
    }





def route_after_editor(state: State):
    if state.get("editor_approved"):
        return "end"

    if state.get("human_revision_count", 0) > 0:
        return "end"

    if state.get("revision_count", 0) >= 3:
        return "human_review"

    return "revise"

def route_after_human_review(state: State):
    if state.get("editor_approved"):
        return "end"

    if state.get("human_revision_count", 0) > 0:
        return "revise"

    return "end"

def revision_limit_node(state: State):
    return {
        "status": "REVISION_LIMIT_REACHED"
    }


def human_review_node(state: State):
    feedback = get_human_feedback(state).strip()

    if feedback.lower() == "approve":
        return {
            "human_feedback": "approve",
            "editor_approved": True,
            "status": "HUMAN_APPROVED",
        }

    return {
        "human_feedback": feedback,
        "editor_approved": False,
        "human_revision_count": state.get("human_revision_count", 0) + 1,
        "status": "HUMAN_FEEDBACK_RECEIVED",
    }


graph_builder = StateGraph(State)

graph_builder.add_node("planner", planner_node)
graph_builder.add_node("researcher", researcher_node)
graph_builder.add_node("writer", writer_node)
graph_builder.add_node("editor", editor_node)
# graph_builder.add_node("revision_limit", revision_limit_node)
graph_builder.add_node("human_review", human_review_node)

graph_builder.add_edge(START, "planner")
graph_builder.add_edge("planner", "researcher")
graph_builder.add_edge("researcher", "writer")
graph_builder.add_edge("writer", "editor")


graph_builder.add_conditional_edges(
    "editor",
    route_after_editor,
    {
        "end": END,
        "revise": "writer",
        "human_review": "human_review",
    },
)

graph_builder.add_conditional_edges(
    "human_review",
    route_after_human_review,
    {
        "end": END,
        "revise": "writer",
    },
)


graph = graph_builder.compile()

if __name__ == "__main__":
    print(graph.get_graph().draw_mermaid())

if __name__ == "__main__":
    result = graph.invoke({
    "topic": "ICPC programming competitions",
    "platform": "LinkedIn",
    "target_audience": "Computer science students",
    "plan": {},
    "research": {},
    "draft": "",
    "editor_feedback": [],
    "editor_approved": False,
    "revision_count": 0,
    "fact_check_results": [],
    "status": "STARTED",
    "human_feedback": "",
"human_revision_count": 0,
})

    print(result)
    print("Status:", result.get("status"))
    print("Human feedback:", result.get("human_feedback"))
    print("Editor approved:", result.get("editor_approved"))
    print("Human revisions:", result.get("human_revision_count"))


