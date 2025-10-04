from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from pydantic import BaseModel

from main import graph, AIMessage, AIMessageChunk

app = FastAPI()

class ChatSchema(BaseModel):
    query: str 


@app.get("/")
def home():
    return {"message": "api working"}

@app.post("/chat")
def chat(chatschema: ChatSchema):
    query = chatschema.query
    config = {'configurable': {'thread_id': '12'}}

    def fn():
        for chunk, metadata in graph.stream({'query': query}, config=config, stream_mode='messages'):
            if isinstance(chunk, (AIMessage, AIMessageChunk)):
                if metadata['langgraph_node'] == 'general':
                    yield(chunk.content)

    return StreamingResponse(fn(), media_type='text/plain')