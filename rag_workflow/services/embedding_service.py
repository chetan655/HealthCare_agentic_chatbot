import os
from typing import Optional

from langchain_google_genai import GoogleGenerativeAIEmbeddings

class EmbeddingService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")

        if not self.api_key:
            raise Exception("Google_API_KEY not found.")
        
        self.model = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=self.api_key
        )

    def get_embedding(self, text: Optional[str] = None):
        if not text:
            return None
        
        try:
            return self.model.embed_query(text)
        except Exception as e:
            raise Exception("Embedding error: ", e)