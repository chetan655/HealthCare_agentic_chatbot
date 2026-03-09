import os
import time
from pinecone import Pinecone

class PineconeService:
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX")
        # Pinecone index is a vector database storage space
        self.pc = None # this is pinecone client
        self.index = None # this is name of db
        self.pinecone_initialized = False

        if not self.api_key:
            raise Exception("Pinecone api key not found.")
        
        if not self.index_name:
            raise Exception("Pinecone index_name is None.")

        if self.api_key:
            self._initialize()

    def _initialize(self):
        try:
            self.pc = Pinecone(api_key=self.api_key)
            existing_index = [idx["name"] for idx in self.pc.list_indexes()]
            if self.index_name not in existing_index:
                self.pc.create_index(
                    name=self.index_name,
                    dimension=768,
                    metric="cosine",
                    spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
                )
                # creating index can take time it's best to wait for 2-3 sec
                time.sleep(2)
            self.index = self.pc.Index(self.index_name)
            self.pinecone_initialized = True
        except Exception as e:
            raise Exception("Pinecone init error: ")
        
    def get_index(self):
        if not self.pinecone_initialized:
            raise Exception("Pinecone not initialized.")
        print("pinecone index success.")
        return self.index
    
    def upsert(
            self,
            upsert_id: str, # each doc have unique id
            vector,  # embedding got from emb model
            metadata: dict,
            namespace: str | None = None # this is like folder inside db
    ):
        if not self.pinecone_initialized:
            raise Exception("Pinecone not initialized.")
        
        if vector is None:
            raise ValueError("Vector cannot be None.")
        
        try:
            self.index.upsert(
                [(upsert_id, vector, metadata)],
                namespace=namespace
            )
        except Exception as e:
            raise Exception("Pinecone upsert error: ",e)