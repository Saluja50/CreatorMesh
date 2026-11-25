
from app.llm.client import get_llm
from app.models.research import FactCheckResult



from app.llm.client import get_llm
from app.models.research import FactCheckResult


def fact_check_claims(draft: str, research: dict) -> dict:
    llm = get_llm().with_structured_output(FactCheckResult)

    result = llm.invoke(
        f"""
        You are the Fact Checker Agent for CreatorMesh.

Your job is to identify and verify factual claims in the DRAFT
using ONLY the supplied RESEARCH.

DRAFT:
{draft}

RESEARCH:
{research}

RESEARCH STRUCTURE:
- Each research claim contains its supporting evidence.
- Each claim contains its relevant source URLs.
- Match draft claims against the specific research evidence.
- Never use evidence from an unrelated research claim.
- Only return source URLs associated with relevant evidence.

STRICT EXTRACTION RULES:

1. Extract ONLY explicit, verifiable statements about real-world facts.
2. Copy every extracted claim exactly as written in the DRAFT.
3. The "claim" and "draft_quote" fields MUST contain the same
   exact original text. Never paraphrase, summarize, or rewrite.
4. Extract one sentence at a time. Never combine sentences.

SKIP THESE COMPLETELY:

- Questions, including rhetorical questions.
- Opinions, personal views, and subjective statements.
- Motivational or inspirational language.
- Slogans, hooks, and promotional statements.
- Calls to action and recommendations.
- Hashtags and emojis.
- Statements that merely encourage or invite the reader.

Examples that MUST be skipped:
- "Balance is key!"
- "Strive for balance!"
- "Find the right balance."
- "Use AI responsibly."
- "Ready to code your future?"
- "Unlock your potential in tech!"
- "Your grades will thank you!"
- "Explore the world of AI!"
- "Stay curious and keep learning."

FACT CHECKING RULES:

1. Compare each extracted factual claim with the supplied RESEARCH.
2. supported: relevant research evidence directly supports the claim.
3. unsupported: research contradicts the claim or provides no
   relevant supporting evidence.
4. uncertain: research is ambiguous or conflicting.
5. Never invent evidence or source URLs.
6. Use only URLs actually present in the supplied RESEARCH.
7. Do not treat a source as supporting a claim unless it is relevant
   to that specific claim.
8. Mark a claim as supported ONLY if the evidence
   directly supports every important part of the claim.

9. If evidence supports only some parts of a claim,
   mark it as uncertain.

10. Never infer missing details from general context.
11. A claim may contain multiple factual parts or clauses.
    Evaluate every part independently.

12. Mark a claim as supported ONLY when the evidence
    directly supports ALL factual parts of that claim.

13. If even one important factual part is missing from
    the evidence, mark the entire claim as uncertain.

14. Shared keywords or a similar overall topic do NOT
    count as evidence of direct support.

15. Before assigning supported, verify that every
    important detail in the claim can be traced to
    the supplied evidence.
16. Verify the strength and certainty of every factual claim.

17. Strong words such as "revolutionizing", "significantly",
    "always", "never", and "guaranteed" require direct evidence
    supporting that exact level of certainty or impact.

18. If the evidence supports the general idea but not the
    strength of the wording, mark the claim as uncertain.

19. Never treat promotional or exaggerated wording as
    established fact.

IMPORTANT:

- Do not classify a sentence as factual merely because it contains
  words like "AI", "students", "learn", or "technology".
- Do not mark skipped content as unsupported.
- If no factual claims remain, return an empty checks list.
- Every check must have an exact draft_quote copied from the DRAFT.

Return only the structured FactCheckResult.
"""
    )

    result_data = result.model_dump()

    result_data["checks"] = [
        check
        for check in result_data["checks"]
        if (
            check["claim"] == check["draft_quote"]
            and check["draft_quote"] in draft
        )
    ]

    return result_data





