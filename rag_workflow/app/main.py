import os
import asyncio

from typing import Annotated, Optional

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_core.messages import AIMessage, AIMessageChunk

from app.utils import (
    check_query_category,
    route_after_tools
)

from dotenv import load_dotenv

load_dotenv()

# PostgresURL = os.getenv("PostgresURL")

# tools = []

from app.schema.schema import State

from app.node.node import (
    classifier,
    general,
    general_formatter,
    find_nearby_hospitals,
    formatter_node,
    hospital_formatter,
    oc_node,
    ocr_formatter,
    sumarize_conv,
    memory
)

from app.models.model import tool_node


builder = StateGraph(State)

builder.add_node("classifier", classifier)
builder.add_node("memory", memory)
builder.add_node("general", general)
builder.add_node("general_formatter", general_formatter)
builder.add_node("find_nearby_hospitals", find_nearby_hospitals)
builder.add_node("formatter_node", formatter_node)
builder.add_node("hospital_formatter", hospital_formatter)
builder.add_node("oc_node", oc_node)
builder.add_node("ocr_formatter", ocr_formatter)
builder.add_node("sumarize_conv", sumarize_conv)
builder.add_node("tools", tool_node)

builder.add_edge(START, "classifier")
builder.add_edge("classifier", "memory")
builder.add_conditional_edges(
    "memory",
    check_query_category,
    {
        "general": "general",
        # "emergency": "emergency",
        "find_nearby_hospitals": "find_nearby_hospitals",
        "ocr": "oc_node"
    }
)

routing_logic = {"tools": "tools", END: "sumarize_conv"}

builder.add_conditional_edges("find_nearby_hospitals", tools_condition, routing_logic)
builder.add_conditional_edges("oc_node", tools_condition, routing_logic)

# builder.add_conditional_edges("general", tools_condition, routing_logic)

builder.add_conditional_edges(
    "tools",
    route_after_tools,
    {
        "hospital_formatter": "hospital_formatter",
        "ocr_formatter": "ocr_formatter",
        # "general_formatter": "general_formatter",
        # "emergency_formatter": "emergency_formatter",
        END: END
    }
)


# builder.add_edge("tools", "formatter_node")

builder.add_edge("hospital_formatter", "sumarize_conv")
builder.add_edge("ocr_formatter", "sumarize_conv")
# builder.add_edge("general_formatter", "sumarize_conv")

builder.add_edge("sumarize_conv", END)
builder.add_edge("general", "sumarize_conv")  # to remove
builder.add_edge("general", END)  # to remove



# graph = builder.compile()

# async def main():
#     async for chunk in graph.astream(
#     {'question': "I have fever, headache, and body pain. What could it be?"}
#     ):
#      print(chunk)

# asyncio.run(main())

# async def fn():
#     fulltext = ""
#     async with AsyncPostgresSaver.from_conn_string(conn_string=PostgresURL) as checkpointer:
#         # how postgres is saving data -> to study later
#         await checkpointer.setup()

#         graph = builder.compile(checkpointer=checkpointer)

#         config = {"configurable": {"thread_id": "id0", "user_id": "id0"}}

#         async for chunk, metadata in graph.astream(
#             {"question": "hello how are you?"},
#             config=config,
#             stream_mode = "messages"
#         ):
#             print(metadata)
#             if isinstance(chunk, (AIMessage, AIMessageChunk)):
#                 node = metadata.get("langgraph_node", None) if metadata else None
#                 if node in ["general"]:
#                     text = chunk.content or ""
#                     fulltext += text
#                     yield text

# async def main():
#     async for token in fn():
#         print(token, end="", flush=True)

# asyncio.run(main())