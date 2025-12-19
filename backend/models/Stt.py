import os
import json
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from groq import Groq

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
groq_client = Groq()
# audio_file_path = "farmer_response.mp3"

def transcribe_multilingual(file_path: str, model="whisper-large-v3"):
    with open(file_path, "rb") as f:
        resp = groq_client.audio.transcriptions.create(
            file=f,
            model=model,
            response_format="verbose_json",
        )
    return resp

def speech_to_text(audio_file:str):
    resp = transcribe_multilingual(audio_file)
    doc = Document(
        page_content=resp.text,
        metadata={"language": resp.language, "source": "audio"}
    )
    return doc
