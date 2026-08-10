import os
from langchain_groq import ChatGroq
from src.vectorstore import FaissVectorStore
from dotenv import load_dotenv

load_dotenv()

class RAGSearch:
    def __init__(self, persist_dir: str):
        self.persist_dir = persist_dir
        self.store = FaissVectorStore(persist_dir)
        try:
            self.store.load()
        except Exception as e:
            print(f"[WARNING] Could not load Faiss vector store: {e}. You may need to build it first.")
        
        # Initialize Groq LLM
        # Groq API key will be read from environment variable GROQ_API_KEY
        api_key = os.getenv("GROQ_API_KEY")
        model_name = os.getenv("GROQ_MODEL_NAME", "llama3-8b-8192")
        
        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name=model_name,
            temperature=0.1
        )
        print(f"[INFO] RAGSearch initialized with model: {model_name}")

    def search_and_summarize(self, query: str) -> str:
        # Retrieve context from vector store
        try:
            docs = self.store.query(query, top_k=4)
        except Exception as e:
            return f"Error querying vector store: {str(e)}"
        
        # Construct context string
        context_parts = []
        for doc in docs:
            if doc.get("metadata") and doc["metadata"].get("text"):
                context_parts.append(doc["metadata"]["text"])
        
        context_text = "\n\n".join(context_parts)
        
        if not context_text:
            return "No relevant legal context found to answer the question."
            
        prompt = f"""You are a helpful legal AI assistant for a contract analysis tool.
Use the following legal context (laws, regulations, guidelines) to answer the user's question.
IMPORTANT: Explain your answer in very simple, plain English that a non-lawyer can easily understand. Avoid complex legal jargon, keep it brief, and be direct.
Please use structured Markdown formatting (bullet points, bold text) to organize your answer.

Legal Context:
{context_text}

Question: {query}

Answer:"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Error executing search and summarize: {str(e)}"
