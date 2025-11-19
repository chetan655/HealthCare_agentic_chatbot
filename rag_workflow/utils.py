# Full rewritten file with correct Pinecone serverless + Gemini embeddings + compressed retriever

import os
import time
import uuid

from schema.schema import State
from langgraph.graph import END

# LangChain + Gemini
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
# from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# Pinecone serverless client
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore

from langchain_core.messages import ToolMessage
from models.models import tools
from tools.tools import calculator

# -------------------------
# ENV VARS
# -------------------------
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "memory-index")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Example: you should replace this with real user ID in your app
user_id = "12345"

# -------------------------
# CATEGORY ROUTING
# -------------------------
def check_query_category(state: State) -> str:
    """Return next node based on category in state."""
    category = state.get("category", "")

    if category == 'emergency':
        return 'emergency_node'
    elif category == 'diagnostic':
        return 'diagnostic_node'
    elif category == 'medicine_info':
        return 'medicine_info'
    elif category == 'nearby_hospitals':
        return 'nearby_hospitals'
    elif category == 'ocr':
        return 'ocr'
    else:
        return 'general'

# -------------------------
# EMBEDDINGS (Gemini 004)
# -------------------------
gem_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=GOOGLE_API_KEY
)

# -------------------------
# PINECONE SERVERLESS INIT
# -------------------------
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create serverless index if missing
existing_indexes = [idx["name"] for idx in pc.list_indexes()]

if PINECONE_INDEX not in existing_indexes:
    pc.create_index(
        name=PINECONE_INDEX,
        dimension=768,
        metric="cosine",
        spec={
            "serverless": {
                "cloud": "aws",
                "region": "us-east-1"
            }
        }
    )

# Connect to the index
index = pc.Index(PINECONE_INDEX)

# -------------------------
# VECTOR STORE
# -------------------------
pinecone_vs = PineconeVectorStore(
    index=index,
    embedding=gem_embeddings,
    text_key="page_content"
)

# -------------------------
# COMPRESSOR LLM
# -------------------------
compressor_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GOOGLE_API_KEY
)

compressor = LLMChainExtractor.from_llm(compressor_llm)

# -------------------------
# GLOBAL COMPRESSED RETRIEVER
# -------------------------
# def get_global_compressed_retriever(k: int = 3):
#     try:
#         base = pinecone_vs.as_retriever(
#             search_type="similarity",
#             search_kwargs={
#                 "k": k,
#                 "filter": {"user_id": user_id}  # Retrieve only this user's memory
#             }
#         )

#         return ContextualCompressionRetriever(
#             base_retriever=base,
#             base_compressor=compressor
#         )
#     except Exception as e:
#         print(f"Error in get_global_compressed_retriever: {e}")
#         return None  # or handle it as needed

# # Create retriever instance
# retriever = get_global_compressed_retriever()

retriever = pinecone_vs.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)
