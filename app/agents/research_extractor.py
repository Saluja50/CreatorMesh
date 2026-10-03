from app.llm.client import get_llm
from app.models.research import ResearchResult


def extract_research(raw_research: str) -> ResearchResult:
    llm = get_llm().with_structured_output(ResearchResult)

    return llm.invoke(
        f"""
Convert the following research into structured research data.

Extract:
- factual claims
- supporting sources
- evidence from each source

Do not add facts that are not present in the research.

Research:
{raw_research}
"""
    )