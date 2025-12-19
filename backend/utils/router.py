from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from utils.llm import Base_llm
from utils.state import GraphState
import json


class RouteQuery(BaseModel):
    """Route the user query to the most relevant datasource."""
    datasource: Literal["market", "disease", "scheme", "weather", "general"] = Field(
        ...,
        description="Given a user question, choose which datasource would be most relevant for answering their question",
    )


def router_node(state: GraphState) -> GraphState:
    print("---ROUTER NODE---")
    query = state["transcript"]

    # Simple structured output if supported, else JSON prompt
    structured_llm_router = Base_llm.with_structured_output(RouteQuery)

    system = """You are an expert at routing a user question to the appropriate data source.
    
    data sources:
    - 'market': for questions about crop prices, market rates, mandi prices using getMarketPrice/getCropLocations.
    - 'disease': for questions about plant diseases, crop health issues (often accompanied by an image).
    - 'weather': for questions about weather forecast, rain, temperature.
    - 'scheme': for questions about government schemes, subsidies, financial aid.
    - 'general': for greetings, general farming advice not covered above, or if unsure.
    
    Return the datasource name.
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{question}"),
        ]
    )

    router = prompt | structured_llm_router

    try:
        result = router.invoke({"question": query})
        intent = result.datasource
    except Exception as e:
        print(f"Router error: {e}, defaulting to general")
        intent = "general"

    print(f"Intent classified: {intent}")
    return {"intent": intent}
