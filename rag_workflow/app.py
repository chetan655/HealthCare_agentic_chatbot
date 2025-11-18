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

# @app.post("/chat")  
# async def chat(chatschema: ChatSchema):
#     question = chatschema.question
#     thread_id = chatschema.thread_id
#     config = {'configurable': {'thread_id': thread_id}}

#     async def fn():
#         async with AsyncMongoDBSaver.from_conn_string(conn_string=MONGODB_URL) as checkpointer:
#             graph = builder.compile(checkpointer=checkpointer)
#             async for chunk, metadata in graph.astream(
#                 {'question': question},
#                 config=config,
#                 stream_mode='messages'
#             ):
#                 if isinstance(chunk, (AIMessage, AIMessageChunk)):
#                     if metadata['langgraph_node'] in [
#                         "general",
#                         "emergency",
#                         "formatter_node",
#                         "nearby_hospitals"
#                     ]:
#                         yield(chunk.content)
                
#     return StreamingResponse(fn(), media_type='text/plain')

#     # async def fn():
#     #     async for chunk, metadata in graph.astream({'question': 'hello'}, config=config, stream_mode='messages'):
#     #         if isinstance(chunk, (AIMessage, AIMessageChunk)):
#     #             if metadata['langgraph_node'] == 'general':
#     #                 yield(chunk.content)

#     # return StreamingResponse(fn(), media_type='text/plain')


from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse

# @app.post("/chat")
# # async def chat(
#     question: str = Form(...),
#     thread_id: str = Form(...),
#     image: UploadFile = File(None)   # <-- optional image
# ):
#     config = {"configurable": {"thread_id": thread_id}}

#     async def fn():
#         # Read image bytes only if provided
#         image_bytes = None
#         if image:
#             image_bytes = await image.read()

#         async with AsyncMongoDBSaver.from_conn_string(conn_string=MONGODB_URL) as checkpointer:
#             graph = builder.compile(checkpointer=checkpointer)

#             # Pass image bytes to your graph
#             async for chunk, metadata in graph.astream(
#                 {
#                     "question": question,
#                     "image": image_bytes     # <-- send image to LangGraph
#                 },
#                 config=config,
#                 stream_mode='messages'
#             ):
#                 if isinstance(chunk, (AIMessage, AIMessageChunk)):
#                     if metadata['langgraph_node'] in [
#                         "general",
#                         "emergency",
#                         "formatter_node",
#                         "nearby_hospitals"
#                     ]:
#                         yield chunk.content

#     return StreamingResponse(fn(), media_type='text/plain')

# ...existing code...
@app.post("/chat")
async def chat(
    question: str = Form(...),
    thread_id: str = Form(...),
    image: UploadFile = File(None)   # <-- optional image
):
    config = {"configurable": {"thread_id": thread_id}}

    # Read image bytes here (while request is active), then close UploadFile
    image_bytes = None
    if image:
        image_bytes = await image.read()
        try:
            await image.close()
        except Exception:
            pass

    async def fn():
        async with AsyncMongoDBSaver.from_conn_string(conn_string=MONGODB_URL) as checkpointer:
            graph = builder.compile(checkpointer=checkpointer)

            # Pass image bytes to your graph
            async for chunk, metadata in graph.astream(
                {
                    "question": question,
                    "image": image_bytes     # <-- send already-read image bytes
                    # "image": image_bytes if image_bytes is not None else b''    # <-- send already-read image bytes
                },
                config=config,
                stream_mode='messages'
            ):
                if isinstance(chunk, (AIMessage, AIMessageChunk)):
                    if metadata['langgraph_node'] in [
                        "general",
                        "emergency",
                        "formatter_node",
                        "nearby_hospitals"
                    ]:
                        yield chunk.content

    return StreamingResponse(fn(), media_type='text/plain')
# ...existing code...