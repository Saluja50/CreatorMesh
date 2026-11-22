from typing import TypedDict


from langgraph.graph import END, START, StateGraph
from app.models.planner import ContentPlan
from app.llm.client import get_llm
from app.graph.state import WorkflowState
from app.agents.editor import review_draft
from app.agents.fact_checker import fact_check_claims
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt

State = WorkflowState


def planner_node(state: State):
    llm = get_llm()

    structured_llm = llm.with_structured_output(ContentPlan)

    plan = structured_llm.invoke(
        f"""
Create a content plan specifically suited to the selected platform.
Platform: {state['platform']}
Target Audience: {state['target_audience']}

Consider the platform's audience, content style, tone, and format.
"""
    )

    return {
        "plan": plan.model_dump_json(),
        "agent_activity": state.get("agent_activity", []) + [
        {
            "agent": "Planner",
            "status": "Completed"
        }
    ]
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
    "agent_activity": state.get("agent_activity", []) + [
        {
            "agent": "Researcher",
            "status": "Completed"
        }
    ]
}

def fact_checker_node(state: State):
    result = fact_check_claims(
        draft=state["draft"],
        research=state["research"],
    )
    print("\n--- FACT CHECK RESULTS ---")
    print(result)

    return {
    "fact_check_results": [result],
    "status": "FACT_CHECK_COMPLETED",
    "agent_activity": state.get("agent_activity", []) + [
        {
            "agent": "Fact Checker",
            "status": "Completed"
        }
    ]
    }

def quality_check(draft: str, platform: str):
    issues = []

    if not draft.strip():
        issues.append("Content is empty.")

    if platform == "X (Twitter)" and len(draft) > 280:
        issues.append("X post exceeds 280 characters.")

    if platform == "Instagram":
        if "#" not in draft:
            issues.append("Instagram caption should include hashtags.")
        if not any(word in draft.lower() for word in ["comment", "save", "share", "follow"]):
            issues.append("Instagram caption should include a CTA.")

    if platform == "LinkedIn":
        if "?" not in draft:
            issues.append("LinkedIn post should encourage discussion with a question.")

    return {
        "passed": len(issues) == 0,
        "issues": issues
    }





def planner_node(state: State):
    llm = get_llm()

    structured_llm = llm.with_structured_output(ContentPlan)

    plan = structured_llm.invoke(
        f"""
Create a content plan specifically suited to the selected platform.
Platform: {state['platform']}
Target Audience: {state['target_audience']}

Consider the platform's audience, content style, tone, and format.
"""
    )
    
    return {
        "plan": plan.model_dump_json(),
        "agent_activity": state.get("agent_activity", []) + [
        {
            "agent": "Planner",
            "status": "Completed"
        }
    ]
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
    "agent_activity": state.get("agent_activity", []) + [
        {
            "agent": "Researcher",
            "status": "Completed"
        }
    ]
}

def fact_checker_node(state: State):
    result = fact_check_claims(
        draft=state["draft"],
        research=state["research"],
    )
    print("\n--- FACT CHECK RESULTS ---")
    print(result)

    return {
    "fact_check_results": [result],
    "status": "FACT_CHECK_COMPLETED",
    "agent_activity": state.get("agent_activity", []) + [
        {
            "agent": "Fact Checker",
            "status": "Completed"
        }
    ]
    }


def writer_node(state: State):
    llm = get_llm()

    feedback = state.get("editor_feedback", [])
    human_feedback = state.get("human_feedback", "").strip()
    platform = state["platform"]

    platform_guidelines = {
        "LinkedIn": """
FORMAT:
- Start with a professional, attention-grabbing hook.
- Use short paragraphs with meaningful insights.
- Explain the topic with practical examples.
- Include 3-5 actionable takeaways.
- End with a thoughtful question to encourage discussion.
- Use minimal hashtags (3-5).
- Avoid excessive emojis.
""",
        "Instagram": """
FORMAT:
- Start with a catchy, curiosity-driven first line.
- Write like you're talking directly to a friend.
- Use very short paragraphs and line breaks.
- Make the caption relatable and engaging.
- Include a clear call-to-action (save, share, comment, or follow).
- Add 8-12 relevant hashtags at the end.
- Use emojis naturally.
- Do not write a formal professional article.
""",
        "X (Twitter)": """
FORMAT:
- Write as a single concise, punchy post.
- Maximum 280 characters, including spaces and hashtags.
- Start with a strong opinion, insight, or surprising statement.
- Avoid headings, long paragraphs, and lengthy explanations.
- Use at most 1-2 relevant hashtags.
- No Instagram-style caption or call-to-action.
- Prioritize one memorable idea over detailed explanation.
"""
    }

    platform_style = platform_guidelines.get(
        platform,
        "Write engaging content appropriate for the selected platform."
    )

    if human_feedback and human_feedback.lower() != "approve":
        instruction = f"""
Revise the previous draft using this human feedback:
{human_feedback}

Also consider the editor feedback:
{feedback}

Follow these platform guidelines:
{platform_style}
Return only the revised content.
"""
    elif feedback:
        instruction = f"""
Revise the previous draft using this editor feedback:
{feedback}

Follow these platform guidelines:
{platform_style}
Return only the revised content.
"""
    else:
        instruction = f"""
Create a high-quality social media post using the content plan
and research evidence.

Follow these platform guidelines:
{platform_style}
Return only the final content.
"""

    response = llm.invoke(
        f"""
Topic: {state['topic']}
Platform: {platform}
Target audience: {state['target_audience']}

Content plan:
{state['plan']}

Research evidence:
{state['research']}

Previous draft:
{state.get('draft', '')}

{instruction}
"""
    )

    draft = response.content.strip()

    if platform == "X (Twitter)" and len(draft) > 280:
        retry_response = llm.invoke(
            f"""
Rewrite this post in 250 characters or less.
Preserve the main idea and make it a complete, impactful post.
Return only the post.

Original post:
{draft}
"""
        )

        draft = retry_response.content.strip()

        if len(draft) > 280:
            draft = draft[:277].rstrip() + "..."

    quality_result = quality_check(draft, platform)

    print("\n--- CONTENT QUALITY CHECK ---")
    print(quality_result)

    return {
        "draft": draft,
        "revision_count": state.get("revision_count", 0) + 1,
        "human_feedback": "",
        "agent_activity": state.get("agent_activity", []) + [
            {"agent": "Writer", "status": "Completed"}
        ]
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
    "agent_activity": state.get("agent_activity", []) + [
        {
            "agent": "Editor",
            "status": (
                "Approved"
                if result.approved
                else "Rejected"
            )
        }
    ]
    }


def route_after_fact_checker(state: State):
    results = state.get("fact_check_results", [])

    if not results:
        return "editor"

    latest_result = results[-1]
    checks = latest_result.get("checks", [])

    has_unsupported = any(
        check.get("status") in {"unsupported", "uncertain"}
        for check in checks
    )

    if has_unsupported:
        if state.get("fact_revision_count", 0) < 1:
            return "revise"
        return "human_review"

    return "editor"

def mark_fact_revision(state: State):
    return {
        "fact_revision_count": state.get("fact_revision_count", 0) + 1,
        "fact_check_revision_requested": True,
    }

def route_after_editor(state: State):
    if state.get("editor_approved"):
        return "end"

    # Human-guided revision ke baad Editor ka decision final hai
    if state.get("human_revision_count", 0) > 0:
        return "end"

    if state.get("revision_count", 0) >= 3:
        return "human_review"

    return "revise"


def route_after_human_review(state: State):
    if state.get("human_feedback", "").lower() == "approve":
        return "end"

    if state.get("human_revision_count", 0) > 0:
        return "revise"

    return "end"

def revision_limit_node(state: State):
    return {
        "status": "REVISION_LIMIT_REACHED"
    }



def human_review_node(state: State):
    feedback = interrupt({
        "draft": state["draft"],
        "editor_feedback": state.get("editor_feedback", []),
        "message": "Review the draft and enter feedback or approve."
    })

    feedback = feedback.strip()

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
graph_builder.add_node("fact_checker", fact_checker_node)
graph_builder.add_node("editor", editor_node)
graph_builder.add_node("human_review", human_review_node)
graph_builder.add_node("mark_fact_revision", mark_fact_revision)


graph_builder.add_edge(START, "planner")
graph_builder.add_edge("planner", "researcher")
graph_builder.add_edge("researcher", "writer")
graph_builder.add_edge("writer", "fact_checker")

graph_builder.add_conditional_edges(
    "fact_checker",
    route_after_fact_checker,
    {
        "revise": "mark_fact_revision",
        "editor": "editor",
        "human_review": "human_review",
    },
)

graph_builder.add_edge("mark_fact_revision", "writer")


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


checkpointer = InMemorySaver()

graph = graph_builder.compile(
    checkpointer=checkpointer
)

if __name__ == "__main__":
    print(graph.get_graph().draw_mermaid())

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
        "fact_revision_count": 0,
        "fact_check_revision_requested": False,
        "status": "STARTED",
        "human_feedback": "",
        "human_revision_count": 0,
    })

    print("\n--- FINAL RESULT ---")
    print("Draft:\n", result.get("draft"))
    print("Status:", result.get("status"))
    print("Editor approved:", result.get("editor_approved"))
    print("Human revisions:", result.get("human_revision_count"))



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
    "agent_activity": state.get("agent_activity", []) + [
        {
            "agent": "Editor",
            "status": (
                "Approved"
                if result.approved
                else "Rejected"
            )
        }
    ]
    }


def route_after_fact_checker(state: State):
    results = state.get("fact_check_results", [])

    if not results:
        return "editor"

    latest_result = results[-1]
    checks = latest_result.get("checks", [])

    has_unsupported = any(
        check.get("status") in {"unsupported", "uncertain"}
        for check in checks
    )

    if has_unsupported:
        if state.get("fact_revision_count", 0) < 1:
            return "revise"
        return "human_review"

    return "editor"

def mark_fact_revision(state: State):
    return {
        "fact_revision_count": state.get("fact_revision_count", 0) + 1,
        "fact_check_revision_requested": True,
    }

def route_after_editor(state: State):
    if state.get("editor_approved"):
        return "end"

    # Human-guided revision ke baad Editor ka decision final hai
    if state.get("human_revision_count", 0) > 0:
        return "end"

    if state.get("revision_count", 0) >= 3:
        return "human_review"

    return "revise"


def route_after_human_review(state: State):
    if state.get("human_feedback", "").lower() == "approve":
        return "end"

    if state.get("human_revision_count", 0) > 0:
        return "revise"

    return "end"

def revision_limit_node(state: State):
    return {
        "status": "REVISION_LIMIT_REACHED"
    }



def human_review_node(state: State):
    feedback = interrupt({
        "draft": state["draft"],
        "editor_feedback": state.get("editor_feedback", []),
        "message": "Review the draft and enter feedback or approve."
    })

    feedback = feedback.strip()

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
graph_builder.add_node("fact_checker", fact_checker_node)
graph_builder.add_node("editor", editor_node)
graph_builder.add_node("human_review", human_review_node)
graph_builder.add_node("mark_fact_revision", mark_fact_revision)


graph_builder.add_edge(START, "planner")
graph_builder.add_edge("planner", "researcher")
graph_builder.add_edge("researcher", "writer")
graph_builder.add_edge("writer", "fact_checker")

graph_builder.add_conditional_edges(
    "fact_checker",
    route_after_fact_checker,
    {
        "revise": "mark_fact_revision",
        "editor": "editor",
        "human_review": "human_review",
    },
)

graph_builder.add_edge("mark_fact_revision", "writer")


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


checkpointer = InMemorySaver()

graph = graph_builder.compile(
    checkpointer=checkpointer
)

if __name__ == "__main__":
    print(graph.get_graph().draw_mermaid())

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
        "fact_revision_count": 0,
        "fact_check_revision_requested": False,
        "status": "STARTED",
        "human_feedback": "",
        "human_revision_count": 0,
    })

    print("\n--- FINAL RESULT ---")
    print("Draft:\n", result.get("draft"))
    print("Status:", result.get("status"))
    print("Editor approved:", result.get("editor_approved"))
    print("Human revisions:", result.get("human_revision_count"))