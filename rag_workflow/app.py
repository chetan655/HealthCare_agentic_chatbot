from fastapi import FastAPI
from fastapi.responses import StreamingResponse

import os 
from dotenv import load_dotenv

from pydantic import BaseModel

from main import AIMessage, AIMessageChunk, builder

from langgraph.checkpoint.mongodb import MongoDBSaver, AsyncMongoDBSaver

app = FastAPI()

class ChatSchema(BaseModel):
    question: str 
    thread_id: str

try:
    load_dotenv()
except Exception as e:
    print(f"Faild to load .env: {e}")


MONGODB_URL = os.getenv('MONGODB_URL')

@app.get("/")
async def home():
    return {"message": "api working"}

@app.post("/chat")  
async def chat(chatschema: ChatSchema):
    question = chatschema.question
    thread_id = chatschema.thread_id
    config = {'configurable': {'thread_id': thread_id}}

    async def fn():
        async with AsyncMongoDBSaver.from_conn_string(conn_string=MONGODB_URL) as checkpointer:
            graph = builder.compile(checkpointer=checkpointer)
            async for chunk, metadata in graph.astream(
                {'question': question},
                config=config,
                stream_mode='messages'
            ):
                if isinstance(chunk, (AIMessage, AIMessageChunk)):
                    if metadata['langgraph_node'] == 'general' or 'emergency' or 'formatter_node' or 'nearby_hospital_finder_node':
                        yield(chunk.content)
                
    return StreamingResponse(fn(), media_type='text/plain')

    # async def fn():
    #     async for chunk, metadata in graph.astream({'question': 'hello'}, config=config, stream_mode='messages'):
    #         if isinstance(chunk, (AIMessage, AIMessageChunk)):
    #             if metadata['langgraph_node'] == 'general':
    #                 yield(chunk.content)

    # return StreamingResponse(fn(), media_type='text/plain')