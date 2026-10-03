from langchain.agents import create_agent

from app.llm.client import get_llm
from app.models.research import ResearchResult
from app.tools.search import search_web


def create_research_agent():
    llm = get_llm()

    return create_agent(
        model=llm,
        tools=[search_web],
        system_prompt=(
            "You are a research agent for CreatorMesh. "
            "Research the given topic using the search tool. "
            "Extract important factual claims and the sources that support them. "
            "Do not write the final social media post."
        ),
        response_format=ResearchResult,
    )