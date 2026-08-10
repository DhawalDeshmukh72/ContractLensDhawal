import os
import requests
from typing import List, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
import numpy as np
from src.data_loader import load_all_documents

class EmbeddingPipeline:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/models/sentence-transformers/{model_name}"
        self.headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN', '')}"}
        print(f"[INFO] Initialized API-based embedding pipeline: {model_name}")

    def chunk_documents(self, documents: List[Any]) -> List[Any]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(documents)
        print(f"[INFO] Split {len(documents)} documents into {len(chunks)} chunks.")
        return chunks

    def embed_chunks(self, chunks: List[Any]) -> np.ndarray:
        texts = [chunk.page_content for chunk in chunks]
        print(f"[INFO] Generating embeddings for {len(texts)} chunks via HF Inference API...")
        
        response = requests.post(self.api_url, headers=self.headers, json={"inputs": texts, "options": {"wait_for_model": True}})
        if response.status_code == 200:
            embeddings = response.json()
            return np.array(embeddings)
        else:
            raise Exception(f"Failed to generate embeddings: {response.text}")

# Example usage
if __name__ == "__main__":
    docs = load_all_documents("../data")
    emb_pipe = EmbeddingPipeline()
    chunks = emb_pipe.chunk_documents(docs)
    embeddings = emb_pipe.embed_chunks(chunks)
    print("[INFO] Example embedding:", embeddings[0] if len(embeddings) > 0 else None)