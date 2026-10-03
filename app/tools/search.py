from langchain_core.tools import tool
from tavily import TavilyClient

from app.config.settings import TAVILY_API_KEY


@tool
def search_web(query: str) -> str:
    """Search the web and return relevant sources for a research query."""

    client = TavilyClient(api_key=TAVILY_API_KEY)

    response = client.search(
        query=query,
        max_results=3,
        search_depth="advanced",
    )

    results = []

    for result in response["results"]:
        results.append(
            f"Title: {result['title']}\n"
            f"URL: {result['url']}\n"
            f"Content: {result['content'][:2000]}\n"
        )

    return "\n---\n".join(results)