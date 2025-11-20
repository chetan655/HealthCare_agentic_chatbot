from typing import Annotated, Optional, TypedDict, Literal, List
from pydantic import BaseModel, Field

from langgraph.graph.message import add_messages
from langchain_core.documents import Document

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
    image: str
    memory_docs = List[Document]
    lat: Optional[str]
    long: Optional[str]

class ClassifierModelSchema(BaseModel):
    category: Literal['general', 'emergency', 'diagnostic', 'ocr', 'nearby_hospitals'] = Field(description="return category of the question.")