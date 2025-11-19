# from fastapi import FastAPI
# from fastapi.responses import StreamingResponse

# import os 
# from dotenv import load_dotenv

# from pydantic import BaseModel

# from main import AIMessage, AIMessageChunk, builder

# from langgraph.checkpoint.mongodb import MongoDBSaver, AsyncMongoDBSaver

# from fastapi import FastAPI, UploadFile, File, Form
# from fastapi.responses import StreamingResponse


# # import pinecone
# from pinecone import Pinecone
# # from langchain_community.vectorstores import Pinecone as PineconeVectorStore
# import time
# import uuid
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from pathlib import Path

# emb_model = GoogleGenerativeAIEmbeddings(
#     model='models/text-embedding-004'
# )

# UPLOAD_PATH = Path("temp")
# UPLOAD_PATH.mkdir(exist_ok=True)

# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# PINECONE_ENV = os.getenv("PINECONE_ENV")  # e.g. "us-west1-gcp"
# PINECONE_INDEX = os.getenv("PINECONE_INDEX", "healthcare-agentic")
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# # print("gfeijsijfsiojf", GOOGLE_API_KEY)



# # -------------------------
# # Init Pinecone (serverless)
# # -------------------------
# _pinecone_initialized = False
# pc = None
# _index = None


# if PINECONE_API_KEY:
#     try:
#         pc = Pinecone(api_key=PINECONE_API_KEY)


#     # create index if missing
#         existing = [idx["name"] for idx in pc.list_indexes()]
#         if PINECONE_INDEX not in existing:
#             pc.create_index(
#             name=PINECONE_INDEX,
#             dimension=768,
#             metric="cosine",
#             spec={
#             "serverless": {"cloud": "aws", "region": "us-east-1"}
#             }
#             )
#             # brief pause for index readiness
#             time.sleep(2)


#         _index = pc.Index(PINECONE_INDEX)
#         _pinecone_initialized = True
#     except Exception as e:
#         print("Pinecone init/create failed:", e)
#         _pinecone_initialized = False
# else:
#     _pinecone_initialized = False
# def _get_embedding(text=None):
#     if text:
#         try:
#             return emb_model.embed_query(text)
#         except Exception as e:
#             print('failed to embed', e)
#     return None

# # -------------------------
# # Helper to upsert into Pinecone
# # -------------------------
# def _save_to_pinecone(upsert_id: str, vector: list, meta: dict, namespace: str = None):
#     if not _pinecone_initialized or vector is None:
#         return
#     # Ensure page_content exists for LangChain integration
#     if "page_content" not in meta and "text" in meta:
#      meta["page_content"] = meta.pop("text")

#     try:
#     # new Pinecone Index.upsert accepts list of tuples (id, vector, metadata)
#         _index.upsert(vectors=[(upsert_id, vector, meta)], namespace=namespace)
#     except Exception as e:
#         print("Pinecone upsert failed:", e)


# app = FastAPI()

# class ChatSchema(BaseModel):
#     question: str 
#     thread_id: str

# try:
#     load_dotenv()
# except Exception as e:
#     print(f"Faild to load .env: {e}")


# MONGODB_URL = os.getenv('MONGODB_URL')

# @app.get("/")
# async def home():
#     return {"message": "api working"}


# @app.post("/chat")
# async def chat(
#     question: str = Form(...),
#     thread_id: str = Form(...),
#     image: UploadFile = File(None)   # <-- optional image
# ):
#     config = {"configurable": {"thread_id": thread_id}}

#     # Read image bytes here (while request is active), then close UploadFile
#     # image_bytes = None
#     # if image:
#     #     image_bytes = await image.read()
#     #     try:
#     #         await image.close()
#     #     except Exception:
#     #         pass

#     image_path = None
#     if image:
#         image_path = UPLOAD_PATH / image.filename
#         with open(image_path, "wb") as f:
#             f.write(await image.read())
#         try:
#             await image.close()
#         except Exception:
#             pass

#     async def fn():
#         try:
#             async with AsyncMongoDBSaver.from_conn_string(conn_string=MONGODB_URL) as checkpointer:
#                 graph = builder.compile(checkpointer=checkpointer)
#                 fulltext = ""
#                 user_id = '12345'  # this should be different for each user

#                 # Pass image bytes to your graph
#                 async for chunk, metadata in graph.astream(
#                     {
#                         "question": question,
#                         "image": image_path     # <-- send already-read image bytes
#                     },
#                     config=config,
#                     stream_mode='messages'
#                 ):
#                     if isinstance(chunk, (AIMessage, AIMessageChunk)):
#                         if metadata['langgraph_node'] in [
#                             "general",
#                             "emergency",
#                             "formatter_node",
#                             "nearby_hospitals"
#                         ]:
#                             fulltext += chunk.content or ""
#                             yield chunk.content
#                 if fulltext.strip():
#                     question_upsert_id = str(uuid.uuid4())
#                     if question:
#                         question_vec = _get_embedding(question)
#                     if question_vec:
#                         question_meta = {
#                             "user_id": user_id,
#                             "thread_id": thread_id,
#                             "role": "user",
#                             "timestamp": int(time.time() * 1000),
#                             "page_content": question
#                         }
#                         _save_to_pinecone(question_upsert_id, question_vec, question_meta)

#                     fulltext = fulltext.strip()
#                     vec = _get_embedding(fulltext)
#                     if vec is not None and _pinecone_initialized:
#                         upsert_id = str(uuid.uuid4())
#                         pine_meta = {
#                             "user_id": user_id,
#                             "thread_id": thread_id,
#                             "role": "ai",
#                             "timestamp": int(time.time() * 1000),
#                             "page_content": fulltext
#                         }
#                         _save_to_pinecone(upsert_id, vec, pine_meta)
#         finally:
#             # delete temporary file after response generator finishes
#             if image_path is not None:
#                 try:
#                     if image_path.exists():
#                         image_path.unlink()
#                 except Exception as e:
#                     print("Failed to delete temp image:", e)
# # ...existing code...   
#     return StreamingResponse(fn(), media_type='text/plain')
# # ...existing code...


from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask

import os
import time
import uuid
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

from main import AIMessage, AIMessageChunk, builder
from langgraph.checkpoint.mongodb import AsyncMongoDBSaver

from pinecone import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load env early
try:
    load_dotenv()
except Exception as e:
    print(f"Failed to load .env: {e}")

# Embedding model
emb_model = GoogleGenerativeAIEmbeddings(model='models/text-embedding-004')

UPLOAD_PATH = Path("temp")
UPLOAD_PATH.mkdir(exist_ok=True)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "healthcare-agentic")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Pinecone init
_pinecone_initialized = False
pc = None
_index = None

if PINECONE_API_KEY:
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        existing = [idx["name"] for idx in pc.list_indexes()]
        if PINECONE_INDEX not in existing:
            pc.create_index(
                name=PINECONE_INDEX,
                dimension=768,
                metric="cosine",
                spec={"serverless": {"cloud": "aws", "region": "us-east-1"}},
            )
            time.sleep(2)
        _index = pc.Index(PINECONE_INDEX)
        _pinecone_initialized = True
    except Exception as e:
        print("Pinecone init/create failed:", e)
        _pinecone_initialized = False
else:
    _pinecone_initialized = False

def _get_embedding(text=None):
    if text:
        try:
            return emb_model.embed_query(text)
        except Exception as e:
            print("failed to embed", e)
    return None

def _save_to_pinecone(upsert_id: str, vector: list, meta: dict, namespace: str = None):
    if not _pinecone_initialized or vector is None:
        return
    if "page_content" not in meta and "text" in meta:
        meta["page_content"] = meta.pop("text")
    try:
        _index.upsert(vectors=[(upsert_id, vector, meta)], namespace=namespace)
    except Exception as e:
        print("Pinecone upsert failed:", e)

def _cleanup_file(path: Path | None):
    try:
        if path and path.exists():
            path.unlink()
    except Exception as e:
        print("Failed to delete temp image (background):", e)

app = FastAPI()

class ChatSchema(BaseModel):
    question: str
    thread_id: str

MONGODB_URL = os.getenv('MONGODB_URL')

@app.get("/")
async def home():
    return {"message": "api working"}

@app.post("/chat")
async def chat(
    question: str = Form(...),
    thread_id: str = Form(...),
    image: UploadFile = File(None)
):
    config = {"configurable": {"thread_id": thread_id}}

    image_path = None
    if image:
        image_path = UPLOAD_PATH / image.filename
        with open(image_path, "wb") as f:
            f.write(await image.read())
        try:
            await image.close()
        except Exception:
            pass

    async def fn():
        try:
            async with AsyncMongoDBSaver.from_conn_string(conn_string=MONGODB_URL) as checkpointer:
                graph = builder.compile(checkpointer=checkpointer)
                fulltext = ""
                user_id = '12345'  # set per-user in real usage

                async for chunk, metadata in graph.astream(
                    {
                        "question": question,
                        "image": image_path
                    },
                    config=config,
                    stream_mode='messages'
                ):
                    if isinstance(chunk, (AIMessage, AIMessageChunk)):
                        if metadata.get('langgraph_node') in [
                            "general",
                            "emergency",
                            "formatter_node",
                            "nearby_hospitals"
                        ]:
                            fulltext += chunk.content or ""
                            yield chunk.content

                if fulltext.strip():
                    question_upsert_id = str(uuid.uuid4())
                    question_vec = _get_embedding(question) if question else None
                    if question_vec:
                        question_meta = {
                            "user_id": user_id,
                            "thread_id": thread_id,
                            "role": "user",
                            "timestamp": int(time.time() * 1000),
                            "page_content": question
                        }
                        _save_to_pinecone(question_upsert_id, question_vec, question_meta)

                    fulltext = fulltext.strip()
                    vec = _get_embedding(fulltext)
                    if vec is not None and _pinecone_initialized:
                        upsert_id = str(uuid.uuid4())
                        pine_meta = {
                            "user_id": user_id,
                            "thread_id": thread_id,
                            "role": "ai",
                            "timestamp": int(time.time() * 1000),
                            "page_content": fulltext
                        }
                        _save_to_pinecone(upsert_id, vec, pine_meta)
        except Exception as e:
            print("Error in chat generator:", e)

    background = BackgroundTask(_cleanup_file, image_path) if image_path is not None else None
    return StreamingResponse(fn(), media_type='text/plain', background=background)