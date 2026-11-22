from typing import TypedDict


class WorkflowState(TypedDict):
    topic: str
    platform: str
    target_audience: str

    plan: dict
    research: dict
    draft: str

    editor_feedback: list[str]
    revision_count: int

    fact_check_results: list[dict]
    fact_revision_count: int
    fact_check_revision_requested: bool

    status: str


    editor_approved: bool

    human_feedback: str

    human_revision_count: int
    agent_activity: list[dict]
    