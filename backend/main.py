from utils.graph import graph as chatbot
import traceback

# -------------------------------
# Run pipeline with persistent memory
# -------------------------------
def get_response(user_input: str, language="English", thread_id="farmer_session_1"):
    # Initial state matching GraphState
    state = {
        "transcript": user_input,
        "language": language,
        "messages": [], # MemorySaver will handle history if thread_id is same
        "response": "",
        "intent": None,
        "tool_data": None
    }

    # Use a unique session key to retain conversation across turns
    # thread_id = "farmer_session_1"

    try:
        print(f"🤔 Processing: {state['transcript']}")
        # Config must include thread_id for MemorySaver
        final_state = chatbot.invoke(state, config={"configurable": {"thread_id": thread_id}})

        answer = final_state.get("response", "No response generated")
        print(f"✅ Response: {answer}")
        return answer

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return "Error processing request"
