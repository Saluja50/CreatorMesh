from app.llm.client import get_llm
from app.models.editor import EditorResult


def review_draft(draft: str, topic: str, platform: str) -> EditorResult:
    llm = get_llm().with_structured_output(EditorResult)

    return llm.invoke(
        f"""
You are the Editor Agent for CreatorMesh.

Review this {platform} post about: {topic}

Evaluate:
1. Clarity and readability
2. Platform suitability
3. Structure and engagement
4. Unsupported or suspicious factual claims
5. Whether the draft is ready to publish

Approve only if the draft is publishable.
If rejected, provide specific, actionable feedback.
Do not rewrite the post yourself.

Draft:
{draft}
"""
    )