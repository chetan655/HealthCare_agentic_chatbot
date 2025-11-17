import os
import asyncio

from typing import Annotated, Optional

from langgraph.graph import StateGraph, START, END 
from langgraph.graph.message import add_messages
from langgraph.checkpoint.mongodb import MongoDBSaver, AsyncMongoDBSaver

from dotenv import load_dotenv

from utils import  check_query_category
from schema.schema import State
from node.node import (
    refiner, 
    classifier, 
    general_query_node, 
    summarize_conv,
    emergency_query_node,
    formatter_node,
    nearby_hospital_finder_node
)
from models.models import tool_node, tools_condition

from langchain_core.messages import AIMessage, AIMessageChunk

try:
    load_dotenv()
except Exception as e:
    print(f"Failed to load .env: {e}")


# env variables
MONGODB_URL = os.getenv('MONGODB_URL')
# MONGODB_NAME = os.getenv('MONGODB_NAME')
# MONGODB_COLLECTION_NAME = os.getenv('MONGODB_COLLECTION_NAME')


# async mongodb connection
# connection = get_mongo_connection(MONGODB_URL, MONGODB_NAME, MONGODB_COLLECTION_NAME


    




#------------------graph------------------
builder = StateGraph(State)

builder.add_node('refiner', refiner)
builder.add_node('classifier', classifier)
builder.add_node('general', general_query_node)
builder.add_node('summarize_conv', summarize_conv)
builder.add_node('emergency_node', emergency_query_node)
builder.add_node('formatter_node', formatter_node)
builder.add_node('nearby_hospitals', nearby_hospital_finder_node)
builder.add_node('tools', tool_node)

builder.set_entry_point("classifier")
builder.add_conditional_edges('classifier', check_query_category)

builder.add_conditional_edges('general', tools_condition)
builder.add_edge("general", "summarize_conv")

builder.add_conditional_edges('emergency_node', tools_condition)
builder.add_edge("emergency_node", "summarize_conv")

builder.add_conditional_edges('nearby_hospitals', tools_condition)
builder.add_edge("nearby_hospitals", "summarize_conv")
# builder.add_conditional_edges('nearby_hospitals', tools_condition, {"tools": "tools", None: "summarize_conv"})



builder.add_edge('tools', 'formatter_node')
builder.add_edge('formatter_node', 'summarize_conv')
builder.add_edge('summarize_conv', END)

# graph = builder.compile()


# graph = builder.compile()

# config={'configurable': {'thread_id': '4'}}

# async def fn():
#     async with AsyncMongoDBSaver.from_conn_string(conn_string=MONGODB_URL) as checkpointer:
#         graph = builder.compile(checkpointer=checkpointer)

#         async for chunk, metadata in graph.astream(
#             {'question': 'what is my name?'},
#             config=config,
#             stream_mode='messages'
#         ):
#             if isinstance(chunk, (AIMessage, AIMessageChunk)):
#                 if metadata['langgraph_node'] == 'general':
#                     yield(chunk.content)

# # async def main(graph, config):
# #     async for chunk, metadata in graph.astream({'query': 'what is 3 + 3?'}, config=config, stream_mode='messages'):
# #         # print("metadata", metadata)
# #         if isinstance(chunk, (AIMessage, AIMessageChunk)):
# #             if metadata['langgraph_node'] == 'general':
# #                 yield(chunk.content)


# # if __name__ == "__main__":
# #     # def
# #     # for chunk, metadata in  graph.stream({'query': 'hi my name is jora'}, config=config, stream_mode='messages'):
# #     #     if isinstance(chunk, (AIMessage, AIMessageChunk)):
# #     #         print(chunk.content)
# #     #     # pass
# #     # fn = main(graph=graph, config=config)
# #     for m in main(graph=graph, config=config):
# #         print(m, end="", flush=True)
# #         # pass

# if __name__ == "__main__":
#     async def run():
#         async for m in main(graph=graph, config=config):
#             print(m, end="", flush=True)
#     asyncio.run(run())
# if __name__ == "__main__":
#     async def run():
#         async for m in fn():
#             print(m, end="", flush=True)
#     asyncio.run(run())

