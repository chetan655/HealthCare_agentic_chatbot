
from fastapi import FastAPI, Form, File, UploadFile, Request
from fastapi.responses import StreamingResponse
from fastapi import HTTPException

import os
import time
import uuid
from pathlib import Path
from typing import Annotated
from passlib.context import CryptContext
from datetime import datetime
import secrets

from pydantic import BaseModel, EmailStr

from typing import Optional
from contextlib import asynccontextmanager

# from langgraph.checkpoint.mongodb import AsyncMongoDBSaver
# from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_core.messages import AIMessage, AIMessageChunk
from langchain_core.messages import HumanMessage

from pinecone import Pinecone

from app.main import builder
# builder = None

from dotenv import load_dotenv

# After imports
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

########### load dotenv ################
try:
    load_dotenv()
except Exception as e:
    raise Exception("Failed to load .env", e)

# # print("this is apikey: ", os.getenv("GOOGLE_API_KEY"))

# try:
#     PostgresURL = os.getenv("PostgresURL")
# except Exception as e:
#     raise Exception("PostgresURL not found.")


########### init ##############
from app.services.embedding_service import LocalEmbeddingService
from app.services.file_service import FileService
from app.services.pinecone_service import PineconeService

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

from contextlib import asynccontextmanager
# from psycopg_pool import AsyncConnectionPool
# from psycopg.rows import dict_row
# from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "checkpointer.db")


######## models
class UserSignUp(BaseModel):
    email: EmailStr
    full_name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    access_token: str


@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.file_service = FileService(upload_path=Path("temp"))
    app.state.embedding_service = LocalEmbeddingService()
    app.state.pinecone_service = PineconeService()

    # checkpointer = AsyncSqliteSaver.from_conn_string(SQLITE_DB_PATH)

    async with AsyncSqliteSaver.from_conn_string(SQLITE_DB_PATH) as checkpointer:
        await checkpointer.setup()
        print("sqlite checkpointer setup complted.")
        # async with checkpointer._get_conn() as conn:
        #     await conn.execute("""
        #         create table if not exists users (
        #                        if integer primary key autoincrement,
        #                        usere_id text unique not null,
        #                        email text unique not null,
        #                        hashed_password text not null,
        #                        full_name text,
        #                        created_at timestamp default current_timestamp)
        #         """)
        #     print("users table ready")
        import sqlite3
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        print("Users table is ready")

        app.state.checkpointer = checkpointer
        app.state.graph = builder.compile(checkpointer=checkpointer)

        print("application startup completed.")

        yield

    print("application shutdown completed.")

app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def home():
    return {"message": "API working."}

# class ChatModel(BaseModel):
#     question: Annotated[str, Form()]
#     lat: Annotated[float, Form()]
#     long: Annotated[float, Form()]
#     image: Annotated[UploadFile, File()]

@app.post("/auth/signup")
async def signup(request: Request, user: UserSignUp):
    import sqlite3
    conn = sqlite3.connect(SQLITE_DB_PATH)
    # checkpointer = request.app.state.checkpointer

    try:
        result = conn.execute(
            "select user_id from users where email = ?", (user.email,)
        )
        if result.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user_id = f"user_{secrets.token_hex(8)}"
        hashed_password = pwd_context.hash(user.password)

        conn.execute("""
                insert into users (user_id, email, hashed_password, full_name) values (?, ?, ?, ?)""", (user_id, user.email, hashed_password, user.full_name))
        conn.commit()
        
        return {
            "message": "user created successfully",
            "user_id": user_id,
            "email": user.email
        }
    finally:
        conn.close()
    
@app.post("/auth/login")
async def login(request: Request, user: UserLogin):
    import sqlite3
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    # checkpointer = request.app.state.checkpointer

    try:
        result = conn.execute(
            "select user_id, email, full_name, hashed_password from users where email = ?", (user.email,)
        )
        db_user = result.fetchone()

        if not db_user or not pwd_context.verify(user.password, db_user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        access_token = secrets.token_hex(32)

        return {
            "user_id": db_user["user_id"],
            "email": db_user["email"],
            "full_name": db_user["full_name"],
            "access_token": access_token
        }
    finally:
        conn.close()


@app.get("/chat/history")
async def get_chat_history(
    request: Request,
    thread_id: str,
    limit: int = 50
):
    checkpointer = request.app.state.checkpointer
    
    if not checkpointer:
        print("checkpointer not found.")
        raise HTTPException(status_code=500, detail="Checkpointer not initialized")

    try:
        checkpointer = await checkpointer.aget(
            {"configurable": {"thread_id": thread_id}}
        )

        if not checkpointer or "channel_values" not in checkpointer:
            return {
                "thread_id": thread_id,
                "messages": [],
                "message": "No history found for this thread."
            }
        
        state = checkpointer["channel_values"]
        messages = state.get("messages", [])

        history = []
        for msg in messages[-limit:]:
            if hasattr(msg, "content"):
                history.append(
                    {
                        "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                        "content": msg.content,
                    }
                )

        return {
            "thread_id": thread_id,
            "total_messages": len(messages),
            "returned": len(history),
            "messages": history
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}") 
    
@app.get("/chat/user/threads")
async def get_user_threads(
    request: Request,
    user_id: str,
    limit: int = 30
):
    checkpointer = request.app.state.checkpointer
    if not checkpointer:
        raise HTTPException(status_code=500, detail="Checkpointer not initialized")

    try:
        threads = []
        
        # Correct way using public API
        async for checkpoint_tuple in checkpointer.alist(limit=limit * 3):
            thread_id = checkpoint_tuple.config["configurable"]["thread_id"]

            if user_id not in thread_id and user_id.lower() != "all":
                continue

            state = checkpoint_tuple.checkpoint.get("channel_values", {})
            messages = state.get("messages", [])

            if not messages:
                continue

            first_user_msg = next((msg.content for msg in messages if isinstance(msg, HumanMessage)), "New Conversation")
            title = first_user_msg.strip()[:60]
            if len(first_user_msg) > 60:
                title += "..."

            threads.append({
                "thread_id": thread_id,
                "title": title,
                "message_count": len(messages)
            })

        return {
            "user_id": user_id,
            "total_threads": len(threads),
            "threads": threads
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching threads: {str(e)}")
    

@app.post("/chat")
async def chat(
    request: Request,
    question: Annotated[str, Form()],
    # lat: Annotated[float, Form()],
    # long: Annotated[float, Form()],
    # lat: str = "29.9478",
    # long: str = "76.8170",
    thread_id: Annotated[str, Form()],
    user_id: Annotated[str, Form()],
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
            # user_id = None   # to remove
            if response.strip():
                try:
                    q_vec = embedding_service.get_embedding(question)
                    if q_vec:
                        pinecone_service.upsert(
                            str(uuid.uuid4()), q_vec,
                            {
                                "user_id": user_id,
                                "thread_id": thread_id,
                                "role": "user",
                                "timestamp": int(time.time() * 1000),
                                "page_content": question
                            },
                            namespace=f"user_{user_id}"
                        )
                        print("question upserted")

                    ai_vec = embedding_service.get_embedding(response)
                    if ai_vec:
                        pinecone_service.upsert(
                            str(uuid.uuid4()), ai_vec,
                            {
                                "user_id": user_id,
                                "thread_id": thread_id,
                                "role": "ai",
                                "timestamp": int(time.time() * 1000),
                                "page_content": response
                            },
                            namespace=f"user_{user_id}"
                        )
                        print("response unserted")
                except Exception as e:
                    print(f"Post-porcessing pinecone error: {e}")
                    raise Exception(f"error: {e}")

        
    return StreamingResponse(response_generator())
    

    