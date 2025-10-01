from motor.motor_asyncio import AsyncIOMotorClient
import os
from functools import lru_cache

from schema.schema import State
from langgraph.graph import END

@lru_cache(maxsize=1)
def get_mongo_connection(MONGODB_URL: str, MONGODB_NAME: str, MONGODB_COLLECTION_NAME: str):
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGODB_NAME]
    return db[MONGODB_COLLECTION_NAME]

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