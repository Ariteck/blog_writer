import os
from typing import Annotated, TypedDict

class BlogState(TypedDict):
    input_niche: str
    topic_candidates: str
    selected_topic: str
    raw_research_and_draft: str
    final_blog: str
    human_feedback: str