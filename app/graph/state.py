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

    status: str