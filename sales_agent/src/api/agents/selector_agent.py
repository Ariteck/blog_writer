from langchain_core.prompts import ChatPromptTemplate

from src.api.config.config import llm
from src.api.models.state import BlogState


def agent_select_topic(state: BlogState) -> dict:
    """Agent 2: Selects the single best topic from the 10 choices."""
    prompt = ChatPromptTemplate.from_template(
        "You are an editorial director. Review these 10 topic candidates:\n\n{candidates}\n\n"
        "Select the single best topic with maximum engagement potential. "
        "Return ONLY the selected topic title and a 1-sentence rationale."
    )

    chain = prompt | llm
    response = chain.invoke({"candidates": state["topic_candidates"]})
    return {"selected_topic": response.content}