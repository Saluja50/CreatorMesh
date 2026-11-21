
from app.llm.client import get_llm
from app.models.research import FactCheckResult


def fact_check_claims(draft: str, research: dict) -> dict:
    llm = get_llm().with_structured_output(FactCheckResult)

    result = llm.invoke(
        f"""
You are the Fact Checker Agent for CreatorMesh.

Compare every factual claim in this draft against the supplied research.

DRAFT:
{draft}

RESEARCH:
{research}

Instructions:
- Extract factual claims from the draft.
- Mark each claim as supported, unsupported, or uncertain.
- Use supported only when the research contains relevant evidence.
- If evidence is missing, mark unsupported.
- If evidence is ambiguous or conflicting, mark uncertain.
- Include a short explanation in evidence.
- Include source URLs only if they appear in the research.
- Never invent facts, evidence, or URLs.
"""
    )

    return result.model_dump()
