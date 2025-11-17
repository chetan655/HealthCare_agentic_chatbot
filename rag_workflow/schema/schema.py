from typing import Annotated, Optional, TypedDict, Literal
from pydantic import BaseModel, Field

from langgraph.graph.message import add_messages

from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState

# state schema
class State(MessagesState):
    query: str
    question: str
    summary: str
    # messages: Annotated[list[BaseMessage], add_messages]
    # messages: Annotated[list[dict[str, str]], add_messages]
    last_messages: list[str]  # later to change to BaseMessge
    category: str


class ClassifierModelSchema(BaseModel):
    category: Literal['general', 'emergency', 'diagnostic', 'medicine_info', 'nearby_hospitals'] = Field(description="return category of the question.")