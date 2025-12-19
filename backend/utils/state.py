from typing import TypedDict, List, Optional, Any
from langchain_core.messages import BaseMessage

class GraphState(TypedDict):
    messages: List[BaseMessage]
    transcript: str
    language: str
    intent: Optional[str]
    tool_data: Optional[Any]
    response: Optional[str]
    image_path: Optional[str]