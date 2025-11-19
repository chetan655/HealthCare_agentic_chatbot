from fastapi import FastAPI
from fastapi.responses import StreamingResponse

import os 
from dotenv import load_dotenv

from pydantic import BaseModel

from main import AIMessage, AIMessageChunk, builder

from langgraph.checkpoint.mongodb import MongoDBSaver, AsyncMongoDBSaver

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse


import pinecone
import time
import uuid
from langchain_google_genai import GoogleGenerativeAIEmbeddings

emb_model = GoogleGenerativeAIEmbeddings(
    model='models/embedding-004'
)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")  # e.g. "us-west1-gcp"
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "healthcare-agentic")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

_pinecone_initialized = False
if PINECONE_API_KEY and PINECONE_ENV:
    try:
        pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
        # create index if it doesn't exist (default dimension placeholder 1536)
        if PINECONE_INDEX not in pinecone.list_indexes():
            # If using OpenAI embeddings, dimension 1536 is common; adjust if you use different embedder.
            pinecone.create_index(name=PINECONE_INDEX, dimension=1536)
            # give the index a moment to become ready
            time.sleep(2)
        _pinecone_initialized = True
        _pinecone_index = pinecone.Index(PINECONE_INDEX)
    except Exception as e:
        print(f"Pinecone init failed: {e}")
else:
    _pinecone_initialized = False

def _get_embedding(text=None):
    if text:
        try:
            return emb_model.embed_query(text)
        except Exception as e:
            print('failed to embed')
    return None

def _save_to_pinecone(upsert_id, vector, meta, namespace=None):
    if not _pinecone_initialized or vector is None:
        return
    try:
        _pinecone_index.upsert(vectors=[(upsert_id, vector, meta)], namespace=namespace)
    except Exception as e:
        print("faild to unsert", {e})


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
            fulltex = ""

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
                        fulltext += chunk.content or ""
                        yield chunk.content
            if fulltext.strip():
                question_upsert_id = str(uuid.uuid4())
                if question:
                    question_vec = _get_embedding(question)
                if question_vec:
                    question_meta = {
                        "thread_id": thread_id,
                        "role": "user",
                        "timestamp": int(time.time() * 1000)
                    }
                    _save_to_pinecone(question_upsert_id, question_vec, question_meta)

                fulltext = fulltext.strip()
                vec = _get_embedding(fulltext)
                if vec is not None and _pinecone_initialized:
                    upsert_id = str(uuid.uuid4())
                    pine_meta = {
                        "thread_id": thread_id,
                        "role": "ai",
                        "timestamp": int(time.time() * 1000)
                    }
                    _save_to_pinecone(upsert_id, vec, pine_meta)
                    
    return StreamingResponse(fn(), media_type='text/plain')
# ...existing code...
































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

