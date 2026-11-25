
from app.llm.client import get_llm
from app.models.editor import EditorResult


def review_draft(
    draft: str,
    topic: str,
    platform: str,
    fact_check_results: dict | None = None,
) -> EditorResult:

    # Deterministic fact-check validation
    checks = (fact_check_results or {}).get("checks", [])

    problematic_claims = [
        check
        for check in checks
        if check.get("status", "").lower()
        in {"unsupported", "uncertain"}
    ]

    # Editor cannot approve unresolved factual claims
    if problematic_claims:
        feedback = [
            (
                f"Fact Checker marked this claim as "
                f"{check.get('status')}: "
                f"{check.get('claim')}. "
                f"Evidence: {check.get('evidence')}"
            )
            for check in problematic_claims
        ]

        return EditorResult(
            approved=False,
            feedback=feedback,
        )

    llm = get_llm().with_structured_output(EditorResult)

    return llm.invoke(
        f"""
You are the Editor Agent for CreatorMesh.

Review this {platform} post about: {topic}

FACT CHECK RESULTS:
{fact_check_results}

DRAFT:
{draft}

Evaluate:
1. Clarity and readability.
2. Platform suitability.
3. Structure and engagement.
4. Factual accuracy.
5. Publication readiness.

RULES:
- Do not invent factual problems.
- Do not reject merely due to writing preferences.
- Do not reject hooks, opinions, or calls to action unnecessarily.
- Approve if the content is clear, engaging, and publishable.
- Give specific, actionable feedback when rejecting.
- Do not rewrite the post yourself.

Return the decision using EditorResult.
"""
    )
