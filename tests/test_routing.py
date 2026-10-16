
from app.graph.first_graph import (
    route_after_editor,
    route_after_human_review,
)


def test_editor_approval_ends_workflow():
    state = {
        "editor_approved": True,
        "revision_count": 1,
        "human_revision_count": 0,
    }
    assert route_after_editor(state) == "end"


def test_editor_rejection_revises_before_limit():
    state = {
        "editor_approved": False,
        "revision_count": 2,
        "human_revision_count": 0,
    }
    assert route_after_editor(state) == "revise"


def test_editor_rejection_at_limit_goes_to_human():
    state = {
        "editor_approved": False,
        "revision_count": 3,
        "human_revision_count": 0,
    }
    assert route_after_editor(state) == "human_review"


def test_human_approval_ends_workflow():
    state = {
        "editor_approved": True,
        "human_revision_count": 0,
    }
    assert route_after_human_review(state) == "end"


def test_human_feedback_routes_to_writer():
    state = {
        "editor_approved": False,
        "human_revision_count": 1,
    }
    assert route_after_human_review(state) == "revise"
