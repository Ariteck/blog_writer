import os
from typing import Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

api_key = os.getenv("OPENROUTER_API_KEY")
# 1. Define Tools
@tool
def calculate_area(length: float, width: float) -> float:
    """Calculates area of a rectangle."""
    return length * width

tools = [calculate_area]

# 2. Initialize LLM with OpenRouter Auto-Router
llm = ChatOpenAI(
    model="openrouter/free",  # <--- Dynamically selects an available free model
    openai_api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:8000",  # Required by OpenRouter for ranking/tracking
        "X-Title": "Sales Agent",                 # Shows your app name in OpenRouter logs
    },
)

llm_with_tools = llm.bind_tools(tools)

# 3. Define Graph State & Nodes
class AgentState(TypedDict):
    input_text: str
    messages: Annotated[list, add_messages]

def chatbot_node(state: AgentState):
    print(f"Chatbot Node: Invoking LLM with input: {state['input_text']}")
    return {"messages": [llm_with_tools.invoke(state["input_text"])]}

# 4. Build LangGraph
builder = StateGraph(AgentState)
builder.add_node("chatbot", chatbot_node)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition)
builder.add_edge("tools", "chatbot")

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# 5. Run Agent
async def run_agent(input_text: str):
    print(f"Input to Agent: {input_text}")
    initial_state: AgentState = {"input_text": input_text}
    thread_config = {"configurable": {"thread_id": "sales_agent_run"}}
    result = await graph.ainvoke(initial_state, thread_config)
    print(f"Graph Result: {result['messages']}")
   # Extract the string content from AIMessage
    last_message = result['messages'][-1].content
    print(f"Agent Response: {last_message}")

    # MUST return a plain dictionary with primitive types (strings, ints)
    return {"response": str(last_message)}