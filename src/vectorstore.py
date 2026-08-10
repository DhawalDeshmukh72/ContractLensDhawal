import os
import faiss
import numpy as np
import pickle
import requests
from typing import List, Any
from src.embedding import EmbeddingPipeline

class FaissVectorStore:
    def __init__(self, persist_dir: str = "faiss_store", embedding_model: str = "all-MiniLM-L6-v2", chunk_size: int = 1000, chunk_overlap: int = 200):
        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        self.index = None
        self.metadata = []
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.api_url = f"https://api-inference.huggingface.co/models/sentence-transformers/{embedding_model}"
        self.headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN', '')}"}
        print(f"[INFO] Initialized API-based FaissVectorStore: {embedding_model}")

    def build_from_documents(self, documents: List[Any]):
        print(f"[INFO] Building vector store from {len(documents)} raw documents...")
        emb_pipe = EmbeddingPipeline(model_name=self.embedding_model, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        chunks = emb_pipe.chunk_documents(documents)
        embeddings = emb_pipe.embed_chunks(chunks)
        metadatas = [{"text": chunk.page_content} for chunk in chunks]
        self.add_embeddings(np.array(embeddings).astype('float32'), metadatas)
        self.save()
        print(f"[INFO] Vector store built and saved to {self.persist_dir}")

    def add_embeddings(self, embeddings: np.ndarray, metadatas: List[Any] = None):
        dim = embeddings.shape[1]
        if self.index is None:
            self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        if metadatas:
            self.metadata.extend(metadatas)
        print(f"[INFO] Added {embeddings.shape[0]} vectors to Faiss index.")

    def save(self):
        faiss_path = os.path.join(self.persist_dir, "faiss.index")
        meta_path = os.path.join(self.persist_dir, "metadata.pkl")
        faiss.write_index(self.index, faiss_path)
        with open(meta_path, "wb") as f:
            pickle.dump(self.metadata, f)
        print(f"[INFO] Saved Faiss index and metadata to {self.persist_dir}")

    def load(self):
        faiss_path = os.path.join(self.persist_dir, "faiss.index")
        meta_path = os.path.join(self.persist_dir, "metadata.pkl")
        self.index = faiss.read_index(faiss_path)
        with open(meta_path, "rb") as f:
            self.metadata = pickle.load(f)
        print(f"[INFO] Loaded Faiss index and metadata from {self.persist_dir}")

    def search(self, query_embedding: np.ndarray, top_k: int = 5):
        D, I = self.index.search(query_embedding, top_k)
        results = []
        for idx, dist in zip(I[0], D[0]):
            meta = self.metadata[idx] if idx < len(self.metadata) else None
            results.append({"index": idx, "distance": dist, "metadata": meta})
        return results

    def query(self, query_text: str, top_k: int = 5):
        print(f"[INFO] Querying vector store for: '{query_text}'")
        
        # Try HF Inference API first (may not be available on restricted networks)
        hf_token = os.getenv('HF_TOKEN', '')
        if hf_token:
            try:
                response = requests.post(
                    self.api_url, 
                    headers=self.headers, 
                    json={"inputs": [query_text], "options": {"wait_for_model": True}},
                    timeout=10
                )
                if response.status_code == 200:
                    query_emb = np.array(response.json()).astype('float32')
                    return self.search(query_emb, top_k=top_k)
            except Exception as e:
                print(f"[WARNING] HF API unavailable, falling back to keyword search: {e}")
        
        # Offline fallback: keyword-based TF-IDF scoring
        print(f"[INFO] Using offline keyword search fallback")
        query_words = set(query_text.lower().split())
        scored = []
        for i, meta in enumerate(self.metadata):
            text = meta.get("text", "") if meta else ""
            doc_words = text.lower().split()
            # Simple overlap score
            matches = sum(1 for w in doc_words if w in query_words)
            score = matches / (len(doc_words) + 1)
            scored.append((i, score, meta))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        results = []
        for idx, score, meta in scored[:top_k]:
            results.append({"index": idx, "distance": 1 - score, "metadata": meta})
        return results

# Example usage
if __name__ == "__main__":
    from data_loader import load_all_documents
    docs = load_all_documents("../data")
    store = FaissVectorStore("faiss_store")
    store.build_from_documents(docs)
    store.load()
    print(store.query("What is attention mechanism?", top_k=3))