# ContractLens ⚖️

> **AI-powered contract risk detection and analysis for everyone.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-contract--lens--rihn.onrender.com-blue?style=for-the-badge)](https://contract-lens-rihn.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-green?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)

---

## 🚀 Live Demo

**[https://contract-lens-rihn.onrender.com/](https://contract-lens-rihn.onrender.com/)**

---

## What is ContractLens?

ContractLens is an AI system that simplifies legal agreements. Upload any rent/leave & license agreement PDF and get:

- **Clause-by-clause risk scoring** (Low / Medium / High) with explanations
- **PII Anonymization** — Aadhaar, PAN, IFSC, phone numbers, names masked before any API call
- **RAG-based Legal Context** — FAISS vector store retrieves relevant Indian legal clauses
- **Interactive QA** — Ask questions about your specific contract in plain English
- **Illegal clause detection** — Flags clauses that violate Indian rental laws

---

## Key Features

| Feature | Description |
|---|---|
| 🔒 **Privacy First** | All PII is masked locally before leaving your device |
| 📊 **Risk Scoring** | Each clause scored 0–100 with risk level and reason |
| ⚖️ **Legal RAG** | Retrieves from a curated FAISS store of Indian rental laws |
| 💬 **Contract QA** | Chat about your specific contract with an AI assistant |
| 🚀 **Unified Server** | Frontend + backend served on a single port |

---

## Tech Stack

- **Backend**: FastAPI + Uvicorn
- **LLM**: Groq (`llama-3.1-8b-instant`)
- **Vector Store**: FAISS (pre-built, offline)
- **PII Detection**: Microsoft Presidio + SpaCy (`en_core_web_sm`)
- **Embeddings**: Hugging Face Inference API (with offline keyword fallback)
- **PDF Processing**: PyMuPDF
- **Frontend**: Vanilla HTML/CSS/JS

---

## Getting Started

### Prerequisites
- Python 3.11+
- A [Groq API Key](https://console.groq.com/)

### Setup

```bash
# Clone the repo
git clone https://github.com/DhawalDeshmukh72/ContractLensDhawal.git
cd ContractLensDhawal

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Create a `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL_NAME=llama-3.1-8b-instant
HF_TOKEN=your_hugging_face_token_here   # Optional, for better embeddings
```

### Run Locally

```bash
python main2.py
```
Then open **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## Deployment

### Render (Current — Free Tier)
1. Push the repository to GitHub.
2. Create a new **Web Service** on [Render](https://render.com).
3. Connect the repository.
4. Set the **Build Command**:
   ```bash
   pip install -r requirements.txt && python -m spacy download en_core_web_sm
   ```
5. Set the **Start Command**:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port $PORT
   ```
6. Add these **Environment Variables**:
   - `GROQ_API_KEY` — Your Groq API key
   - `GROQ_MODEL_NAME` — `llama-3.1-8b-instant`
   - `HF_TOKEN` — Your Hugging Face access token (optional)

---

## Project Structure

```
ContractLens/
├── app.py               # Main FastAPI application (production entry point)
├── main2.py             # Alternative local entry point
├── requirements.txt     # Python dependencies
├── frontend/            # Static HTML/CSS/JS frontend
│   ├── index.html
│   ├── styles.css
│   └── script.js
└── src/
    ├── anonymization.py # PII detection & masking (Presidio)
    ├── clause_splitter.py
    ├── data_loader.py   # Document ingestion pipeline
    ├── embedding.py     # HF Inference API embeddings
    ├── search.py        # RAG search with Groq LLM
    ├── vectorstore.py   # FAISS vector store
    └── faiss_store/     # Pre-built FAISS index (legal context)
```

