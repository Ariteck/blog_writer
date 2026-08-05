from langchain_core.prompts import ChatPromptTemplate

from src.api.config.config import llm
from src.api.models.state import BlogState


def agent_review_and_format(state: BlogState) -> dict:
    """Agent 4: Reviews, formats Markdown structure, and polishes language."""
    prompt = ChatPromptTemplate.from_template(
        "You are a publication editor. Review and format this draft for publishing:\n\n{draft}\n\n"
        "Fix formatting, adjust headings, improve readability, summarize it in 500-800 words. clean Markdown format."
    )

    chain = prompt | llm
    response = chain.invoke({"draft": state["raw_research_and_draft"]})
    return {"final_blog": response.content}