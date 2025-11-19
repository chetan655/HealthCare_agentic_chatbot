# # from fastapi import FastAPI
# # from fastapi.responses import StreamingResponse

# # import os 
# # from dotenv import load_dotenv

# # from pydantic import BaseModel

# # from main import AIMessage, AIMessageChunk, builder

# # from langgraph.checkpoint.mongodb import MongoDBSaver, AsyncMongoDBSaver

# # from fastapi import FastAPI, UploadFile, File, Form
# # from fastapi.responses import StreamingResponse


# # # import pinecone
# # from pinecone import Pinecone
# # # from langchain_community.vectorstores import Pinecone as PineconeVectorStore
# # import time
# # import uuid
# # from langchain_google_genai import GoogleGenerativeAIEmbeddings
# # from pathlib import Path

# # emb_model = GoogleGenerativeAIEmbeddings(
# #     model='models/text-embedding-004'
# # )

# # UPLOAD_PATH = Path("temp")
# # UPLOAD_PATH.mkdir(exist_ok=True)

# # PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# # PINECONE_ENV = os.getenv("PINECONE_ENV")  # e.g. "us-west1-gcp"
# # PINECONE_INDEX = os.getenv("PINECONE_INDEX", "healthcare-agentic")
# # GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# # # print("gfeijsijfsiojf", GOOGLE_API_KEY)



# # # -------------------------
# # # Init Pinecone (serverless)
# # # -------------------------
# # _pinecone_initialized = False
# # pc = None
# # _index = None


# # if PINECONE_API_KEY:
# #     try:
# #         pc = Pinecone(api_key=PINECONE_API_KEY)


# #     # create index if missing
# #         existing = [idx["name"] for idx in pc.list_indexes()]
# #         if PINECONE_INDEX not in existing:
# #             pc.create_index(
# #             name=PINECONE_INDEX,
# #             dimension=768,
# #             metric="cosine",
# #             spec={
# #             "serverless": {"cloud": "aws", "region": "us-east-1"}
# #             }
# #             )
# #             # brief pause for index readiness
# #             time.sleep(2)


# #         _index = pc.Index(PINECONE_INDEX)
# #         _pinecone_initialized = True
# #     except Exception as e:
# #         print("Pinecone init/create failed:", e)
# #         _pinecone_initialized = False
# # else:
# #     _pinecone_initialized = False
# # def _get_embedding(text=None):
# #     if text:
# #         try:
# #             return emb_model.embed_query(text)
# #         except Exception as e:
# #             print('failed to embed', e)
# #     return None

# # # -------------------------
# # # Helper to upsert into Pinecone
# # # -------------------------
# # def _save_to_pinecone(upsert_id: str, vector: list, meta: dict, namespace: str = None):
# #     if not _pinecone_initialized or vector is None:
# #         return
# #     # Ensure page_content exists for LangChain integration
# #     if "page_content" not in meta and "text" in meta:
# #      meta["page_content"] = meta.pop("text")

# #     try:
# #     # new Pinecone Index.upsert accepts list of tuples (id, vector, metadata)
# #         _index.upsert(vectors=[(upsert_id, vector, meta)], namespace=namespace)
# #     except Exception as e:
# #         print("Pinecone upsert failed:", e)


# # app = FastAPI()

# # class ChatSchema(BaseModel):
# #     question: str 
# #     thread_id: str

# # try:
# #     load_dotenv()
# # except Exception as e:
# #     print(f"Faild to load .env: {e}")


# # MONGODB_URL = os.getenv('MONGODB_URL')

# # @app.get("/")
# # async def home():
# #     return {"message": "api working"}


# # @app.post("/chat")
# # async def chat(
# #     question: str = Form(...),
# #     thread_id: str = Form(...),
# #     image: UploadFile = File(None)   # <-- optional image
# # ):
# #     config = {"configurable": {"thread_id": thread_id}}

# #     # Read image bytes here (while request is active), then close UploadFile
# #     # image_bytes = None
# #     # if image:
# #     #     image_bytes = await image.read()
# #     #     try:
# #     #         await image.close()
# #     #     except Exception:
# #     #         pass

# #     image_path = None
# #     if image:
# #         image_path = UPLOAD_PATH / image.filename
# #         with open(image_path, "wb") as f:
# #             f.write(await image.read())
# #         try:
# #             await image.close()
# #         except Exception:
# #             pass

# #     async def fn():
# #         try:
# #             async with AsyncMongoDBSaver.from_conn_string(conn_string=MONGODB_URL) as checkpointer:
# #                 graph = builder.compile(checkpointer=checkpointer)
# #                 fulltext = ""
# #                 user_id = '12345'  # this should be different for each user

# #                 # Pass image bytes to your graph
# #                 async for chunk, metadata in graph.astream(
# #                     {
# #                         "question": question,
# #                         "image": image_path     # <-- send already-read image bytes
# #                     },
# #                     config=config,
# #                     stream_mode='messages'
# #                 ):
# #                     if isinstance(chunk, (AIMessage, AIMessageChunk)):
# #                         if metadata['langgraph_node'] in [
# #                             "general",
# #                             "emergency",
# #                             "formatter_node",
# #                             "nearby_hospitals"
# #                         ]:
# #                             fulltext += chunk.content or ""
# #                             yield chunk.content
# #                 if fulltext.strip():
# #                     question_upsert_id = str(uuid.uuid4())
# #                     if question:
# #                         question_vec = _get_embedding(question)
# #                     if question_vec:
# #                         question_meta = {
# #                             "user_id": user_id,
# #                             "thread_id": thread_id,
# #                             "role": "user",
# #                             "timestamp": int(time.time() * 1000),
# #                             "page_content": question
# #                         }
# #                         _save_to_pinecone(question_upsert_id, question_vec, question_meta)

# #                     fulltext = fulltext.strip()
# #                     vec = _get_embedding(fulltext)
# #                     if vec is not None and _pinecone_initialized:
# #                         upsert_id = str(uuid.uuid4())
# #                         pine_meta = {
# #                             "user_id": user_id,
# #                             "thread_id": thread_id,
# #                             "role": "ai",
# #                             "timestamp": int(time.time() * 1000),
# #                             "page_content": fulltext
# #                         }
# #                         _save_to_pinecone(upsert_id, vec, pine_meta)
# #         finally:
# #             # delete temporary file after response generator finishes
# #             if image_path is not None:
# #                 try:
# #                     if image_path.exists():
# #                         image_path.unlink()
# #                 except Exception as e:
# #                     print("Failed to delete temp image:", e)
# # # ...existing code...   
# #     return StreamingResponse(fn(), media_type='text/plain')
# # # ...existing code...


# from fastapi import FastAPI, UploadFile, File, Form
# from fastapi.responses import StreamingResponse
# from starlette.background import BackgroundTask

# import os
# import time
# import uuid
# from pathlib import Path
# from dotenv import load_dotenv
# from pydantic import BaseModel

# from main import AIMessage, AIMessageChunk, builder
# from langgraph.checkpoint.mongodb import AsyncMongoDBSaver, MongoDBSaver

# from pinecone import Pinecone
# from langchain_google_genai import GoogleGenerativeAIEmbeddings

# # Load env early
# try:
#     load_dotenv()
# except Exception as e:
#     print(f"Failed to load .env: {e}")

# # Embedding model
# emb_model = GoogleGenerativeAIEmbeddings(model='models/text-embedding-004')

# UPLOAD_PATH = Path("temp")
# UPLOAD_PATH.mkdir(exist_ok=True)

# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# PINECONE_ENV = os.getenv("PINECONE_ENV")
# PINECONE_INDEX = os.getenv("PINECONE_INDEX", "healthcare-agentic")
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# # Pinecone init
# _pinecone_initialized = False
# pc = None
# _index = None

# if PINECONE_API_KEY:
#     try:
#         pc = Pinecone(api_key=PINECONE_API_KEY)
#         existing = [idx["name"] for idx in pc.list_indexes()]
#         if PINECONE_INDEX not in existing:
#             pc.create_index(
#                 name=PINECONE_INDEX,
#                 dimension=768,
#                 metric="cosine",
#                 spec={"serverless": {"cloud": "aws", "region": "us-east-1"}},
#             )
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
#             print("failed to embed", e)
#     return None

# def _save_to_pinecone(upsert_id: str, vector: list, meta: dict, namespace: str = None):
#     if not _pinecone_initialized or vector is None:
#         return
#     if "page_content" not in meta and "text" in meta:
#         meta["page_content"] = meta.pop("text")
#     try:
#         _index.upsert(vectors=[(upsert_id, vector, meta)], namespace=namespace)
#     except Exception as e:
#         print("Pinecone upsert failed:", e)

# def _cleanup_file(path: Path | None):
#     try:
#         if path and path.exists():
#             path.unlink()
#     except Exception as e:
#         print("Failed to delete temp image (background):", e)

# app = FastAPI()

# class ChatSchema(BaseModel):
#     question: str
#     thread_id: str

# MONGODB_URL = os.getenv('MONGODB_URL')

# @app.get("/")
# async def home():
#     return {"message": "api working"}

# @app.post("/chat")
# async def chat(
#     question: str = Form(...),
#     thread_id: str = Form(...),
#     image: UploadFile = File(None)
# ):
#     config = {"configurable": {"thread_id": thread_id}}

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
#                 user_id = '12345'  # set per-user in real usage

#                 async for chunk, metadata in graph.astream(
#                     {
#                         "question": question,
#                         "image": image_path
#                     },
#                     config=config,
#                     stream_mode='messages'
#                 ):
#                     if isinstance(chunk, (AIMessage, AIMessageChunk)):
#                         if metadata.get('langgraph_node') in [
#                             "general",
#                             "emergency",
#                             "formatter_node",
#                             "nearby_hospitals"
#                         ]:
#                             fulltext += chunk.content or ""
#                             yield chunk.content

#                 if fulltext.strip():
#                     question_upsert_id = str(uuid.uuid4())
#                     question_vec = _get_embedding(question) if question else None
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
#         except Exception as e:
#             print("Error in chat generator:", e)

#     background = BackgroundTask(_cleanup_file, image_path) if image_path is not None else None
#     return StreamingResponse(fn(), media_type='text/plain', background=background)


# ---------------------------
# IMPORTS# ---------------------------
# IMPORTS
# ---------------------------
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask

import os
import time
import uuid
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel
import anyio

from main import AIMessage, AIMessageChunk, builder
from langgraph.checkpoint.mongodb import MongoDBSaver  # Use MongoDBSaver instead

from pinecone import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    print("Failed to load .env:", e)

# Embedding model
emb_model = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# Temporary folder for uploads
UPLOAD_PATH = Path("temp")
UPLOAD_PATH.mkdir(exist_ok=True)

# Environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "healthcare-agentic")
MONGODB_URL = os.getenv("MONGODB_URL")

# Pinecone setup
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
        print("Pinecone init failed:", e)

# Embedding helpers
def _get_embedding(text=None):
    if not text:
        return None
    try:
        return emb_model.embed_query(text)
    except Exception as e:
        print("Embedding failed:", e)
        return None

def _save_to_pinecone(upsert_id, vector, meta, namespace=None):
    if not _pinecone_initialized or vector is None:
        return
    try:
        _index.upsert([(upsert_id, vector, meta)], namespace=namespace)
    except Exception as e:
        print("Pinecone upsert failed:", e)

# Cleanup temporary files
def _cleanup_file(path: Path | None):
    if path and path.exists():
        try:
            path.unlink()
            print(f"Deleted temp file: {path}")
        except Exception as e:
            print("Failed to delete temp file:", e)

# FastAPI app
app = FastAPI()

class ChatSchema(BaseModel):
    question: str
    thread_id: str

@app.get("/")
async def home():
    return {"message": "API working"}

@app.post("/chat")
async def chat(
    question: str = Form(...),
    thread_id: str = Form(...),
    image: UploadFile = File(None),
):
    config = {"configurable": {"thread_id": thread_id}}

    # Save uploaded image locally
    image_path = None
    if image:
        image_path = UPLOAD_PATH / image.filename
        with open(image_path, "wb") as f:
            f.write(await image.read())
        await image.close()

    async def fn():
        send_stream, receive_stream = anyio.create_memory_object_stream(50)

        async with anyio.create_task_group() as tg:
            # Worker thread for processing
            async def worker():
                try:
                    if image_path and image_path.exists():  # Check if the file exists
                        with MongoDBSaver.from_conn_string(MONGODB_URL) as saver:
                            graph = builder.compile(checkpointer=saver)

                            async for chunk, metadata in graph.astream(
                                {"question": question, "image": str(image_path)},  # Pass the image path as a string
                                config=config,
                                stream_mode="messages",
                            ):
                                await send_stream.send((chunk, metadata))

                            # Stream finished
                            await send_stream.send(("__END__", None))
                    else:
                        await send_stream.send(("__ERROR__", "Image file not found."))  # Send error if file not found

                except Exception as e:
                    print("Worker error:", e)
                    await send_stream.send(("__ERROR__", str(e)))  # Await the send

            tg.start_soon(worker)

            # Async streaming back to client
            fulltext = ""
            async with receive_stream:
                async for item in receive_stream:
                    chunk, metadata = item

                    if chunk == "__END__":
                        break

                    if chunk == "__ERROR__":
                        print("Graph error:", metadata)
                        break

                    if isinstance(chunk, (AIMessage, AIMessageChunk)):
                        node = metadata.get("langgraph_node")
                        if node in ["general", "emergency", "formatter_node", "nearby_hospitals"]:
                            fulltext += chunk.content or ""
                            yield chunk.content

            # Save to Pinecone after streaming
            if fulltext.strip():
                q_vec = _get_embedding(question)
                if q_vec:
                    _save_to_pinecone(
                        str(uuid.uuid4()),
                        q_vec,
                        {
                            "user_id": "12345",
                            "thread_id": thread_id,
                            "role": "user",
                            "timestamp": int(time.time() * 1000),
                            "page_content": question,
                        },
                    )

                ai_vec = _get_embedding(fulltext)
                if ai_vec:
                    _save_to_pinecone(
                        str(uuid.uuid4()),
                        ai_vec,
                        {
                            "user_id": "12345",
                            "thread_id": thread_id,
                            "role": "ai",
                            "timestamp": int(time.time() * 1000),
                            "page_content": fulltext,
                        },
                    )

    # Delete image after stream ends
    background = BackgroundTask(_cleanup_file, image_path) if image_path else None

    return StreamingResponse(fn(), media_type="text/plain", background=background)