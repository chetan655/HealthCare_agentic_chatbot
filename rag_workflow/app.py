

from fastapi import FastAPI, Form, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import os
import time
import uuid
import traceback # Added for debugging
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, AsyncGenerator
from twilio.rest import Client
from pydantic import BaseModel

# LangGraph & AI Imports
# Ensure 'main' works correctly and builder is compiled properly in main.py
from main import AIMessage, AIMessageChunk, builder 
from langgraph.checkpoint.mongodb import AsyncMongoDBSaver
from pinecone import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# --- Setup & Init ---
try:
    load_dotenv()
except Exception as e:
    print("Failed to load .env:", e)

# Initialize Embedding Model
emb_model = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

UPLOAD_PATH = Path("temp")
UPLOAD_PATH.mkdir(exist_ok=True)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "healthcare-agentic")
MONGODB_URL = os.getenv("MONGODB_URL")

app = FastAPI()

#=====================sos interg===============
TWILIO_SID = "ACc27766jfudca5e71ea89719fb93b6665"  
TWILIO_TOKEN = "6a63c5b4a21jnnu016eda3cb261f41a8"         
TWILIO_FROM = "whatsapp:+14098238886"     

EMERGENCY_CONTACTS = [
    "whatsapp:+919739487638", # Person A (You)
    "whatsapp:+919375986354"  # Person B (Friend)
]

class LocationData(BaseModel):
    latitude: float
    longitude: float

def send_whatsapp_broadcast(lat: float, lng:float):
    """Sends the SOS message to everyone in the list"""
    # We use the global variables defined above
    client = Client(TWILIO_SID, TWILIO_TOKEN)

    google_maps_link = f"https://www.google.com/maps?q={lat},{lng}"


    message_body = (
        f"🚨 EMERGENCY SOS 🚨\n\n"
        f"I need help immediately.\n"
        f"Here is my current location:\n{google_maps_link}"
    )

    for contact in EMERGENCY_CONTACTS:
        try:
            message = client.messages.create(
                body=message_body,
                from_=TWILIO_FROM,
                to=contact
            )
            # print(f"Success: Sent to {contact} (ID: {message.sid})")
        except Exception as e:
            print(f"Failed to send to {contact}: {e}")

@app.post("/sos")
async def trigger_sos(location: LocationData, background_tasks: BackgroundTasks):
    # Run the sending function in the background
    lat = location.latitude
    lng = location.longitude
    background_tasks.add_task(send_whatsapp_broadcast, lat, lng)

    return {
        "status": 200,
        "message": "Broadcasting SOS to contacts list."
    }



# Initialize Pinecone (Global)
pc = None
_index = None
_pinecone_initialized = False

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
        print(f"Pinecone init warning: {e}")

# --- Helper Functions ---

def _get_embedding(text: Optional[str] = None):
    if not text: return None
    try:
        return emb_model.embed_query(text)
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

def _save_to_pinecone(upsert_id: str, vector, meta: dict, namespace: Optional[str] = None):
    if not _pinecone_initialized or vector is None: return
    try:
        _index.upsert([(upsert_id, vector, meta)], namespace=namespace)
    except Exception as e:
        print(f"Pinecone upsert error: {e}")

def _cleanup_file(path: Optional[Path]):
    if path and path.exists():
        try:
            path.unlink()
            print(f"Cleaned up file: {path}")
        except Exception as e:
            print(f"File cleanup failed: {e}")



@app.get("/")
async def home():
    return {"message": "API Robust and Running"}

@app.post("/chat")
async def chat(
    question: str = Form(...),
    thread_id: str = Form(...),
    lat: str = Form(...),
    long: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    """
     Robust endpoint accepting multipart/form-data.
    """
    
    # 1. Handle Image Upload Safely (Async)
    image_path: Optional[Path] = None
    
    # Logic: Only process if image object exists AND has a filename
    if image and image.filename:
        try:
            file_extension = os.path.splitext(image.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            image_path = UPLOAD_PATH / unique_filename
            
            # FIX: Use await read() instead of shutil for async safety
            content = await image.read()
            with open(image_path, "wb") as f:
                f.write(content)
                
        except Exception as e:
            print(f"Error saving file: {e}")
            image_path = None
    
    # 2. Prepare LangGraph Config
    config = {"configurable": {"thread_id": thread_id}}
    
    # 3. Define the Streaming Generator
    async def response_generator() -> AsyncGenerator[str, None]:
        fulltext = ""
        
        # Determine the argument to pass to LangGraph
        # If path exists, pass string path. If not, pass None.
        image_arg = str(image_path) if (image_path and image_path.exists()) else None
        
        try:
            if not MONGODB_URL:
                raise ValueError("MONGODB_URL is not set in environment variables.")

            async with AsyncMongoDBSaver.from_conn_string(MONGODB_URL) as saver:
                graph = builder.compile(checkpointer=saver)
                
                # Stream from LangGraph
                async for chunk, metadata in graph.astream(
                    {"question": question, "image": image_arg, "lat": lat, "long": long},
                    config=config,
                    stream_mode="messages",
                ):
                    if isinstance(chunk, (AIMessage, AIMessageChunk)):
                        node = metadata.get("langgraph_node") if metadata else None
                        # Adjust these node names based on your actual graph in main.py
                        if node in ["general", "emergency", "formatter_node", "nearby_hospitals", "agent"]: 
                            text = chunk.content or ""
                            fulltext += text
                            yield text

        except Exception as e:
            # FIX: Print traceback to console to find the EXACT line in main.py failing
            print("---------- ERROR TRACEBACK ----------")
            traceback.print_exc()
            print("-------------------------------------")
            yield f"\n[System Error]: An error occurred while processing: {str(e)}"
        
        finally:
            # 4. Cleanup & Post-Processing
            
            # A. Cleanup File immediately
            _cleanup_file(image_path)
            
            # B. Save to Pinecone
            if fulltext.strip():
                try:
                    # Save User Query
                    q_vec = _get_embedding(question)
                    if q_vec:
                        _save_to_pinecone(
                            str(uuid.uuid4()), q_vec,
                            {
                                "user_id": "12345",
                                "thread_id": thread_id,
                                "role": "user",
                                "timestamp": int(time.time() * 1000),
                                "page_content": question
                            }
                        )
                    
                    # Save AI Response
                    ai_vec = _get_embedding(fulltext)
                    if ai_vec:
                        _save_to_pinecone(
                            str(uuid.uuid4()), ai_vec,
                            {
                                "user_id": "12345",
                                "thread_id": thread_id,
                                "role": "ai",
                                "timestamp": int(time.time() * 1000),
                                "page_content": fulltext
                            }
                        )
                except Exception as e:
                    print(f"Post-processing (Pinecone) error: {e}")

    return StreamingResponse(response_generator(), media_type="text/plain")