
from fastapi import FastAPI, Form, File, UploadFile, Request
from fastapi.responses import StreamingResponse

import os
import time
import uuid
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel

from typing import Optional
from contextlib import asynccontextmanager

# from langgraph.checkpoint.mongodb import AsyncMongoDBSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_core.messages import AIMessage, AIMessageChunk

from pinecone import Pinecone

from main import builder
# builder = None

from dotenv import load_dotenv

########### load dotenv ################
try:
    load_dotenv()
except Exception as e:
    raise Exception("Failed to load .env", e)

# print("this is apikey: ", os.getenv("GOOGLE_API_KEY"))

try:
    PostgresURL = os.getenv("PostgresURL")
except Exception as e:
    raise Exception("PostgresURL not found.")


########### init ##############
from services.embedding_service import EmbeddingService
from services.file_service import FileService
from services.pinecone_service import PineconeService

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     app.state.file_service = FileService(upload_path=Path("temp"))
#     app.state.embedding_service = EmbeddingService()
#     app.state.pinecone_service = PineconeService()

#     async with AsyncPostgresSaver.from_conn_string(
#         conn_string=PostgresURL
#     ) as checkpointer:

#         await checkpointer.setup()
#         app.state.checkpointer = checkpointer

#         app.state.graph = builder.compile(
#             checkpointer=app.state.checkpointer
#         )

#         print("Application startup completed.")
#         yield

#     # await app.state.checkpointer.close()
#     print("Application shutdown.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.file_service = FileService(upload_path=Path("temp"))
    app.state.embedding_service = EmbeddingService()
    app.state.pinecone_service = PineconeService()

    async with AsyncPostgresSaver.from_conn_string(
        conn_string=PostgresURL
    ) as checkpointer:

        # ✅ run only once
        if not hasattr(app.state, "checkpointer_initialized"):
            await checkpointer.setup()
            app.state.checkpointer_initialized = True

        app.state.checkpointer = checkpointer

        app.state.graph = builder.compile(
            checkpointer=app.state.checkpointer
        )

        print("Application startup completed.")
        yield

    print("Application shutdown.")

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def home():
    return {"message": "API working."}

# class ChatModel(BaseModel):
#     question: Annotated[str, Form()]
#     lat: Annotated[float, Form()]
#     long: Annotated[float, Form()]
#     image: Annotated[UploadFile, File()]

@app.post("/chat")
async def chat(
    request: Request,
    question: Annotated[str, Form()],
    # lat: Annotated[float, Form()],
    # long: Annotated[float, Form()],
    # lat: str = "29.9478",
    # long: str = "76.8170",
    thread_id: Annotated[str, Form()],
    lat: Annotated[str, Form()], #= "29.9478",
    long: Annotated[str, Form()], #= "76.8170"
    image: Annotated[UploadFile | None, File()] = None,
    
    # chatModel: ChatModel
):
    # question = chatModel.question
    # lat = chatModel.lat
    # long = chatModel.long
    # image = chatModel.image
    
    # config = {"configurable": {"thread_id": "id0", "user_id": "id0"}}

    print("lat and long", lat, long)

    graph = request.app.state.graph
    file_service = request.app.state.file_service
    embedding_service = request.app.state.embedding_service
    pinecone_service = request.app.state.pinecone_service

    image_path = None
    if image:
        image_path = await file_service.save_image(image)
    print("this is image_path: ", image_path)

    config = {"configurable": {"thread_id": thread_id}}

    async def response_generator():
        response = ""        

        try:
            async for chunk, metadata in graph.astream(
            {"question": question,
            "lat": lat,
            "long": long,
            "image": str(image_path) if image_path else None},
            config=config,
            stream_mode="messages"
            ):
                if isinstance(chunk, (AIMessage, AIMessageChunk)):
                    node = metadata.get("langgraph_node") if metadata else None
                    if node in ["general", "general_formatter", "hospital_formatter", "ocr_formatter"]:
                        text = chunk.content or ""
                        response += text
                        yield text
        except Exception as e:
            raise Exception("Error generating response: ", e)
        finally:
            # delete image
            file_service.cleanup_file(image_path)
            # get embedding
            # embedding = embedding_service.get_embedding(response)
            # print("this is embedding: ", len(embedding))
            # save to vector db
            # if response.strip():
            #     try:
            #         q_vec = embedding_service.get_embedding(question)
            #         if q_vec:
            #             pinecone_service.upsert(
            #                 str(uuid.uuid4()), q_vec,
            #                 {
            #                     "user_id": "12345",
            #                     "thread_id": thread_id,
            #                     "role": "user",
            #                     "timestamp": int(time.time() * 1000),
            #                     "page_content": question
            #                 }
            #             )

            #         ai_vec = embedding_service.get_embedding(response)
            #         if ai_vec:
            #             pinecone_service.upsert(
            #                 str(uuid.uuid4()), ai_vec,
            #                 {
            #                     "user_id": "12345",
            #                     "thread_id": thread_id,
            #                     "role": "ai",
            #                     "timestamp": int(time.time() * 1000),
            #                     "page_content": response
            #                 }
            #             )
            #     except Exception as e:
            #         print(f"Post-porcessing pinecone error: {e}")

        
    return StreamingResponse(response_generator())
    

    