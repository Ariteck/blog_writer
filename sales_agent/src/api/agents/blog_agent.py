import asyncio
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

from src.api.config.config import llm
from src.api.models.state import BlogState
from src.api.agents.research_agent import agent_research_topics
from src.api.agents.selector_agent import agent_select_topic
from src.api.agents.writer_agent import agent_research_and_draft
from src.api.agents.editor_agent import agent_review_and_format

def human_review_node(state: BlogState) -> dict:
    """Pauses execution for human inspection."""
    user_response = interrupt({
        "action": "Please review the formatted blog post.",
        "blog_content": state["final_blog"]
    })
    return {"human_feedback": user_response}

# Build Graph
builder = StateGraph(BlogState)

builder.add_node("agent_1", agent_research_topics)
builder.add_node("agent_2", agent_select_topic)
builder.add_node("agent_3", agent_research_and_draft)
builder.add_node("agent_4", agent_review_and_format)
#builder.add_node("human_review", human_review_node)

builder.add_edge(START, "agent_1")
builder.add_edge("agent_1", "agent_2")
builder.add_edge("agent_2", "agent_3")
builder.add_edge("agent_3", "agent_4")
builder.add_edge("agent_4", END)
#builder.add_edge("human_review", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# Execute
async def run_blog_pipeline(query: str):
    thread_config = {"configurable": {"thread_id": "run_1"}}
    initial_input = {"input_niche": query}

    print("Running pipeline...")

    try:
        # Add timeout to prevent 504 Gateway Timeout
        final_blog = await graph.ainvoke(initial_input, thread_config)
    except AttributeError:
        final_blog = await asyncio.to_thread(graph.invoke, initial_input, thread_config)
    except asyncio.TimeoutError:
        print("ERROR: Graph execution timed out after 60 seconds")
        raise Exception("Pipeline execution timed out. The graph may be stuck or the API is slow.")
    except Exception as e:
        print(f"ERROR: Pipeline execution failed: {str(e)}")
        raise

    # for event in graph.stream(initial_input, thread_config):
    #     print(f"Completed node: {list(event.keys())[0]}")
    # print(f"Current state: {graph.get_state(thread_config)}")
    # final_blog = graph.get_state(thread_config)["agent_4"]
    
    print(f"Final blog content: {final_blog['final_blog']}")
    return {"final_blog": final_blog["final_blog"]}
    # Inspect pause state
    # state = graph.get_state(thread_config)
    # if state.next:
    #     payload = state.tasks[0].interrupts[0].value
    #     print("\n--- FINAL DRAFT FOR REVIEW ---\n")
    #     print(payload["blog_content"])
        
    #     user_input = input("\nEnter feedback / approve: ")
    #     final_state = graph.invoke(Command(resume=user_input), thread_config)
    #     print("Done. Human feedback captured:", final_state["agent_4"])
    #     return final_state["agent_4"]