import os
from typing import Optional

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sentence_transformers import SentenceTransformer

from google import genai

load_dotenv(override=True)


class GeminiEmbeddingService:
    def __init__(self):

        self._api_key = os.getenv("GOOGLE_API_KEY")

        if not self._api_key:
            raise Exception("Google_API_KEY not found.")
        
        self.model = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-2-preview",
            google_api_key=self._api_key
        )

    def get_embedding(self, text: Optional[str] = None):
        if not text:
            return None
        
        try:
            return self.model.embed_query(text)
        except Exception as e:
            raise Exception("Embedding error: ", {str(e)})
        
class LocalEmbeddingService:

    def __init__(self):
        self.model = SentenceTransformer("BAAI/bge-small-en")

    def get_embedding(self, text: str | None = None) -> None | str:
        if not text:
            return None
        
        try:
            emb = self.model.encode(text)
            # print("this is embedding: ", emb[:20])
            # print(f"this is length of embedding: {len(emb)}")
            return emb.tolist()
        except Exception as e:
            raise Exception(f"Embedding Error: {str(e)}")
        


