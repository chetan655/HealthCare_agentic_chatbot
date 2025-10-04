from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from pydantic import BaseModel

from main import graph, AIMessage, AIMessageChunk

app = FastAPI()

class ChatSchema(BaseModel):
    query: str 


@app.get("/")
async def home():
    return {"message": "api working"}

@app.post("/chat")
async def chat(chatschema: ChatSchema):
    query = chatschema.query
    config = {'configurable': {'thread_id': '12'}}

    async def fn():
        async for chunk, metadata in graph.astream({'query': query}, config=config, stream_mode='messages'):
            if isinstance(chunk, (AIMessage, AIMessageChunk)):
                if metadata['langgraph_node'] == 'general':
                    yield(chunk.content)

    return StreamingResponse(fn(), media_type='text/plain')