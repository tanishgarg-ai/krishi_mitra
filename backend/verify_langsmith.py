
import os
from dotenv import load_dotenv

# Load env vars to ensure LangSmith keys are present
load_dotenv()

# Verify keys are loaded
if not os.getenv("LANGCHAIN_API_KEY"):
    print("❌ LANGCHAIN_API_KEY is missing. Please set it in .env")
    exit(1)

print("✅ LANGCHAIN_API_KEY found.")
print(f"Project: {os.getenv('LANGCHAIN_PROJECT')}")

try:
    from main import chatbot
    
    # Define a simple state similar to what the app uses
    state = {
        "transcript": "Hello, are you connected to LangSmith?",
        "language": "English",
        "messages": [],
        "response": "",
        "intent": None,
        "tool_data": None
    }
    
    print("🚀 Invoking chatbot to generate trace...")
    final_state = chatbot.invoke(state, config={"configurable": {"thread_id": "verify_trace_1"}})
    
    print("✅ Chatbot response received:")
    print(final_state.get("response", "No response"))
    print("\n🎉 Verification complete! Check your LangSmith dashboard to see the trace.")

except Exception as e:
    print(f"❌ Error during invocation: {e}")
    import traceback
    traceback.print_exc()
