from langchain_core.prompts import ChatPromptTemplate

from src.api.config.config import llm, search_tool
from src.api.models.state import BlogState


def _format_search_results(search_results) -> str:
    """Normalize Exa results into a compact prompt-friendly string."""
    source = getattr(search_results, "results", search_results)

    if not source:
        return "No web search results returned."

    if isinstance(source, list):
        formatted_segments = []
        for item in source:
            if not isinstance(item, dict):
                continue

            title = item.get("title") or item.get("url") or "Untitled"
            url = item.get("url") or ""
            summary = item.get("summary") or item.get("text") or ""
            highlights = item.get("highlights")

            if isinstance(highlights, list):
                highlights = " ".join(str(h) for h in highlights)

            snippet = summary or highlights or ""
            if len(snippet) > 500:
                snippet = snippet[:497] + "..."

            if url:
                formatted_segments.append(f"- {title} ({url})\n  {snippet}")
            else:
                formatted_segments.append(f"- {title}\n  {snippet}")

        return "\n".join(formatted_segments)

    return str(source)


def agent_research_topics(state: BlogState) -> dict:
    """Agent 1: Searches current web trends and lists 10 blog ideas."""
    niche = state["input_niche"]

    # Tool call to gather current live trends
    search_query = f"latest trending technology topics and news in {niche}"
    search_results = search_tool.invoke(
        {
            "query": search_query,
            "num_results": 3,
            "text_contents_options": {"max_characters": 500},
            "summary": True,
            "highlights": True,
        }
    )
    formatted_results = _format_search_results(search_results)

    prompt = ChatPromptTemplate.from_template(
        "You are a trend research agent. Based on these real-time web search results:\n"
        "{search_results}\n\n"
        "Generate 10 highly engaging blog post topic titles for the niche '{niche}'. "
        "Keep the output as a numbered list from 1 to 10. Focus on fresh, high-interest angles."
    )

    chain = prompt | llm
    response = chain.invoke({"search_results": formatted_results, "niche": niche})
    return {"topic_candidates": response.content}