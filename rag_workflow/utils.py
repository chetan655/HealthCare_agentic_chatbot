# from motor.motor_asyncio import AsyncIOMotorClient
import os
# from functools import lru_cache

from schema.schema import State
from langgraph.graph import END

from langchain_core.messages import ToolMessage

from models.models import tools
from tools.tools import calculator

# @lru_cache(maxsize=1)
# def get_mongo_connection(MONGODB_URL: str, MONGODB_NAME: str, MONGODB_COLLECTION_NAME: str):
#     client = AsyncIOMotorClient(MONGODB_URL)
#     db = client[MONGODB_NAME]
#     return db[MONGODB_COLLECTION_NAME]

def check_query_category(state: State):
    category = state['category'] 
    if category == 'general':
        return 'general_query_node'
    else:
        END

def check_query_category(state: State) -> str:
    """This function return node for the current category."""
    category = state['category']
    # print("this is categoty -> ", category)
    if category == 'emergency':
        return 'emergency_node'
    elif category == 'diagnostic':
        return 'diagnostic_node'
    elif category == 'medicine_info':
        return 'medicine_info'
    else:
        return 'general'
    
# def tool_condition(state):
#     # print("state ->", state)
#     message = state['messages'][-1]
#     print("messages -> ", message)

#     # print("this is additional_kwargs -> ", message['additional_kwargs'])

#     # print("this is tool call", message.tool_calls)

#     if hasattr(message, 'tool_calls') and message.tool_calls:
#         for call in message.tool_calls:
#             tool_name = call['name']
#             tool_args = call['args']
#             tool_call_id = call['id']

#         print("message -> ", message)
#         print("tool_name -> ", tool_name)
#         print("tool_args -> ", tool_args)

#         if tool_name == 'calculator':

#             res = calculator.invoke(tool_args)

#             tool_msg = ToolMessage(content=res, tool_name=tool_name, tool_call_id=tool_call_id)
#             print("tool_mst -> ", tool_msg)

#             state['message'] = [tool_msg]
#             return 'general'
#     else:
#         return END


# from langchain_core.messages import AIMessage

# def sanitize_ai_message(ai_msg: AIMessage, keep_tool_calls=True) -> AIMessage:
#     """Remove unnecessary metadata from AIMessage to save tokens."""
#     # new_kwargs = {}
#     # print("this is ai msg -=> ", ai_msg.tool_calls)
#     # if keep_tool_calls and 'tool_calls' in ai_msg.tool_calls:
#     #     new_kwargs['tool_calls'] = ai_msg.tool_calls[]

#     return AIMessage(
#         content=ai_msg.content,
#         tool_calls=ai_msg.tool_calls
#     )