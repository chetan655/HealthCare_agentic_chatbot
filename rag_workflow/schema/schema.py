from typing import Annotated, Optional, TypedDict, Literal, List

# typing library is used to add type hint 
# literal means This variable can only be one of these exact values.

from langchain_core.documents import Document
# Document store a piece of text and metadata associated with it.

from pydantic import BaseModel, Field
# pydantic helps in data validation

from langgraph.graph import MessagesState


class State(MessagesState):
    question: str
    category: str
    image: str
    memory_docs: List[Document]
    lat: Optional[str]
    long: Optional[str]
    summary: Optional[str]


class ClassifierModelSchema(BaseModel):
    category: Literal['general', 'emergency', 'diagnostic', 'ocr', 'nearby_hospitals'] = Field(description="The classification label for the user's message. Must be exactly one of: general, ocr, nearby_hospitals.")