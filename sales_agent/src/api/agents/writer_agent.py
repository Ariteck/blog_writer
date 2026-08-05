from langchain_core.prompts import ChatPromptTemplate

from src.api.config.config import llm, search_tool
from src.api.models.state import BlogState


def _format_search_results(search_results) -> str:
    """Normalize Exa results into clear, prompt-friendly research notes."""
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
            if len(snippet) > 600:
                snippet = snippet[:597] + "..."

            if url:
                formatted_segments.append(f"- {title} ({url})\n  {snippet}")
            else:
                formatted_segments.append(f"- {title}\n  {snippet}")

        return "\n".join(formatted_segments)

    return str(source)


def agent_research_and_draft(state: BlogState) -> dict:
    """Agent 3: Gathers live web research for the topic and drafts the article."""
    topic = state["selected_topic"]

    # Tool call for deep research on the selected topic
    search_results = search_tool.invoke(
        {
            "query": f"detailed facts and context about {topic}",
            "num_results": 3,
            "text_contents_options": {"max_characters": 600},
            "summary": True,
            "highlights": True,
        }
    )
    formatted_results = _format_search_results(search_results)

    prompt = ChatPromptTemplate.from_template(
        "You are an SEO content writer. Draft a polished, publication-ready blog post using only the research context below.\n"
        "Research Context:\n{search_results}\n\n"
        "Topic: {topic}\n\n"
        "Requirements:\n"
        "- Write a strong title and a concise intro\n"
        "- Create 3-5 well-structured sections with practical insights\n"
        "- End with a useful conclusion or call to action\n"
        "- Keep the article factual, readable, and polished in Markdown."
        "- Ensure the final draft is between 800- 1000 words."
    )

    chain = prompt | llm
    response = chain.invoke({
        "search_results": formatted_results,
        "topic": topic,
    })
    return {"raw_research_and_draft": response.content}