from typing import Annotated, Optional, TypedDict
from pydantic import BaseModel, Field

from langgraph.graph.message import add_messages

from langchain_core.messages import BaseMessage

# state schema
class State(TypedDict):
    query: str
    messages: Annotated[list[BaseMessage], add_messages]
    last_messages: list[str]  # later to change to BaseMessge
    category: str