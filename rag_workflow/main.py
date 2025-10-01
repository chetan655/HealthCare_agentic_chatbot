import os

from typing import Annotated, Optional

from langgraph.graph import StateGraph, START, END 
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from dotenv import load_dotenv

from utils import get_mongo_connection, check_query_category
from models.models import chat_node_model
from schema.schema import State
from node.node import refiner, classifier, general_query_node

from langchain_core.messages import AIMessage, AIMessageChunk

try:
    load_dotenv()
except Exception as e:
    print(f"Failed to load .env: {e}")


# env variables
# MONGODB_URL = os.getenv('MONGODB_URL')
# MONGODB_NAME = os.getenv('MONGODB_NAME')
# MONGODB_COLLECTION_NAME = os.getenv('MONGODB_COLLECTION_NAME')


# async mongodb connection
# connection = get_mongo_connection(MONGODB_URL, MONGODB_NAME, MONGODB_COLLECTION_NAME)


#---------------model_with_tools------------------------
tools = []

tool_node = ToolNode(tools)

model_with_tools = chat_node_model.bind_tools(tools)

    




#------------------graph------------------
builder = StateGraph(State)

builder.add_node('refiner', refiner)
builder.add_node('classifier', classifier)
builder.add_node('general', general_query_node)
builder.add_node('tools', tool_node)

builder.add_edge(START, 'refiner')
builder.add_edge('refiner', 'classifier')
builder.add_conditional_edges('classifier', check_query_category)
# builder.add_edge('general_query_node', tools_condition)
# builder.add_edge('tools', 'general_query_node')
builder.add_edge('general', END)

graph = builder.compile()

config={'configurable': {'thread_id': '1'}}


if "__name__" == "__name__":
    for chunk, metadata in  graph.stream({'query': 'hello how are you?'}, config=config, stream_mode='messages'):
        if isinstance(chunk, (AIMessage, AIMessageChunk)):
            print(chunk.content)
        # pass