from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from utils.state import GraphState
from utils.router import router_node
from utils.nodes import market_node, disease_node, weather_node, scheme_node, chat_node

def route_decision(state: GraphState):
    """Determine the next node based on the intent."""
    intent = state.get("intent", "general")
    # If intent is 'end', we finish.
    if intent == "end":
        return END
    return intent

# Define the graph
workflow = StateGraph(GraphState)

# Add nodes
workflow.add_node("router", router_node)
workflow.add_node("market", market_node)
workflow.add_node("disease", disease_node)
workflow.add_node("weather", weather_node)
workflow.add_node("scheme", scheme_node)
workflow.add_node("chat", chat_node)

# Add edges
workflow.add_edge(START, "router")

# Conditional edges from router
workflow.add_conditional_edges(
    "router",
    route_decision,
    {
        "market": "market",
        "disease": "disease",
        "weather": "weather",
        "scheme": "scheme",
        "general": "chat",
    }
)

# Connect tools back to chat for synthesis
workflow.add_edge("market", "chat")
workflow.add_edge("disease", "chat")
workflow.add_edge("weather", "chat")
workflow.add_edge("scheme", "chat")

# NEW: Conditional edges from chat_node (the "Smart Loop")
# If chat_node decides to call a tool, it updates 'intent'.
# If it answers, it sets 'intent': 'end'.
workflow.add_conditional_edges(
    "chat",
    route_decision,
    {
        "market": "market",
        "disease": "disease",
        "weather": "weather",
        "scheme": "scheme",
        END: END, # If route_decision returns END
    }
)

# Compile with memory
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)
