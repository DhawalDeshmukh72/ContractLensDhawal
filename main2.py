import json
import os
import shutil
from pathlib import Path
from typing import Optional
import torch

# Limit PyTorch CPU threads to save RAM on memory-constrained hosting (e.g. 512MB limit)
torch.set_num_threads(1)
torch.set_num_interop_threads(1)

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.data_loader import load_all_documents
from src.vectorstore import FaissVectorStore
from src.search import RAGSearch

from src.anonymization import anonymize_pdf
from src.clause_splitter import split_clauses

BASE_DIR = Path(__file__).resolve().parent

# Load vector store and search globally once at startup to minimize memory overhead
FAISS_PATH = BASE_DIR / "src" / "faiss_store"
global_store = FaissVectorStore(str(FAISS_PATH))
try:
    global_store.load()
except Exception as e:
    print(f"[WARNING] Could not load Faiss vector store: {e}")

global_rag_search = RAGSearch(persist_dir=str(FAISS_PATH), store=global_store)

app = FastAPI(title="Legalease API")

# Add CORS middleware to allow calls from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str
    contract_context: Optional[dict] = None


STRUCTURED_PROMPT = """
You are a legal AI assistant specialized in contract analysis.

Analyze the contract clause using the legal context provided.

Clause:
{clause}

Legal Context:
{context}

Tasks:
1. Determine the risk level for the tenant (LOW, MEDIUM, HIGH)
2. Assign a numerical risk score out of 100 for this clause based on severity (0-33=Low, 34-66=Medium, 67-100=High).
3. Explain the reason for the risk level
4. Determine if the clause is illegal
5. If illegal, mention the law or regulation violated

Return ONLY valid JSON in this format:

{{
 "risk_level": "",
 "risk_score": 0,
 "reason": "",
 "illegal": true/false,
 "law_reference": ""
}}
"""


def analyze_contract(pdf_path):

    # -------- Step 1: Anonymize PDF --------
    masked_text, pii_map = anonymize_pdf(pdf_path)

    # -------- Step 2: Split clauses --------
    clauses = split_clauses(masked_text)

    # -------- Step 3: Use Global Vector Store & RAG --------
    # Reusing global_store and global_rag_search to prevent high memory usage

    results = []

    # -------- Step 4: Process each clause --------
    for idx, clause in enumerate(clauses):

        # Retrieve legal context
        retrieved_docs = global_store.query(clause, top_k=3)

        context = "\n".join([doc["metadata"]["text"] for doc in retrieved_docs if doc.get("metadata")])

        prompt = STRUCTURED_PROMPT.format(
            clause=clause,
            context=context
        )

        # Ask LLM
        response = global_rag_search.llm.invoke(prompt)
        content = response.content

        # Clean JSON markdown (if exists)
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        try:
            parsed = json.loads(content)

        except Exception as e:
            parsed = {
                "risk_level": "UNKNOWN",
                "risk_score": 0,
                "reason": f"LLM output parsing failed: {e}. Raw content: {content}",
                "illegal": False,
                "law_reference": ""
            }

        results.append({
            "clause_id": idx + 1,
            "clause_text": clause,
            "risk_level": parsed.get("risk_level"),
            "risk_score": parsed.get("risk_score", 0),  # Default to 0 if key is somehow missing
            "reason": parsed.get("reason"),
            "illegal": parsed.get("illegal"),
            "law_reference": parsed.get("law_reference")
        })

    return {
        "total_clauses": len(results),
        "analysis": results,
        "pii_map": pii_map
    }

@app.post("/analyze_contract")
async def api_analyze_contract(file: UploadFile = File(...)):
    # Save the uploaded file to a temporary path in a dedicated tmp folder
    tmp_dir = BASE_DIR / "tmp"
    tmp_dir.mkdir(exist_ok=True)
    temp_pdf_path = tmp_dir / f"temp_{file.filename}"
    with open(temp_pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        report = analyze_contract(temp_pdf_path)
    finally:
        # Clean up the temp file
        if temp_pdf_path.exists():
            os.remove(temp_pdf_path)
            
    return report

@app.post("/ask_question")
async def ask_question(req: QuestionRequest):
    # Reuse global_rag_search to prevent high memory usage
    
    # Extract context from the contract_context (JSON analysis data) provided by the frontend
    context_text = ""
    if req.contract_context and "analysis" in req.contract_context:
        clauses = req.contract_context["analysis"]
        context_parts = []
        for c in clauses:
            context_parts.append(f"Clause {c.get('clause_id')}: {c.get('clause_text')}")
        context_text = "\n".join(context_parts)
    
    if not context_text:
        # If no explicit contract context passed, fallback to vectorstore search
        answer = global_rag_search.search_and_summarize(req.question)
    else:
        # Ask LLM with the uploaded contract context
        prompt = f"""You are a helpful legal AI assistant for a contract analysis tool.
Use the following contract context to answer the user's question.
IMPORTANT: Explain your answer in very simple, plain English that a non-lawyer can easily understand. Avoid complex legal jargon, keep it brief, and be direct.
Please use structured Markdown formatting (bullet points, bold text) to organize your answer.

Contract Context:
{context_text}

Question: {req.question}

Answer:"""
        try:
            response = global_rag_search.llm.invoke([prompt])
            answer = response.content
        except Exception as e:
            answer = f"Error processing question: {str(e)}"
            
    return {"answer": answer}

# Serve frontend static files
app.mount("/", StaticFiles(directory=str(BASE_DIR / "frontend"), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main2:app", host="0.0.0.0", port=8000, reload=False)