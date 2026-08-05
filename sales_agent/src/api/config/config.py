import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_exa import ExaSearchResults

load_dotenv()

# --- LLM Config ---
API_KEY = os.environ.get("OPENROUTER_API_KEY", "your-openrouter-key")

llm = ChatOpenAI(
    model="openrouter/free",
    openai_api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1",
    temperature=0.7,
    default_headers={
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Blog Agent",
    },
)

# --- Search Tool Config ---
search_tool = ExaSearchResults()