# import getpass
# import os
# from langchain_google_genai import ChatGoogleGenerativeAI
#
# if "GOOGLE_API_KEY" not in os.environ:
#     os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")
#
#
# Base_llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     temperature=0,
#     max_tokens=None,
#     timeout=None,
#     max_retries=2,
#     # other params...
# )

from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY=os.getenv("GROQ_API_KEY")

Base_llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="qwen/qwen3-32b",
    temperature=0.5
)

# chotu_llm = ChatGroq(
#     api_key=GROQ_API_KEY,
#     model="",
# )