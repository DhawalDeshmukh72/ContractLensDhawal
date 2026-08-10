# ContractLens (formerly LegalEase)

ContractLens is an AI system that simplifies legal agreements. It extracts and anonymizes text from PDFs, divides them into clauses, retrieves relevant sections using embeddings and FAISS, and uses an LLM to generate clear explanations.

## Key Features

- **Privacy Protection:** Sensitive data (Aadhaar, IFSC, PAN, names, etc.) is anonymized before leaving the local environment.
- **RAG-based Risk Detection:** Retrieves context from a local FAISS vector store to assess and score clause risks.
- **Interactive QA:** Query specific terms or ask questions about the contract.
- **Unified Server Architecture:** Both the backend API and frontend static files are served together on a single port for easy deployment.

---

## Getting Started

### 1. Prerequisites
- Python 3.11+
- A Groq API Key (get it from [Console Groq](https://console.groq.com/))

### 2. Setup
Create a `.env` file in the root directory based on `.env.example`:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL_NAME=llama-3.1-8b-instant
```

Install the dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Running Locally
To run the unified server:
```bash
python main2.py
```
Then open your browser and navigate to **`http://localhost:8000`**.

---

## Hosting & Deployment

Since the backend serves the frontend static assets directly, hosting is simple and can be done on a single service.

### Option A: Hosting with Docker (Recommended)
Build and run the container:
```bash
# Build the image
docker build -t contractlens .

# Run the container
docker run -p 8000:8000 --env-file .env contractlens
```

### Option B: Hosting on Render / Railway
1. Push your repository to GitHub.
2. Create a new **Web Service** on Render or Railway.
3. Connect your repository.
4. Set the **Build Command** to:
   ```bash
   pip install -r requirements.txt && python -m spacy download en_core_web_sm
   ```
5. Set the **Start Command** to:
   ```bash
   uvicorn main2:app --host 0.0.0.0 --port $PORT
   ```
6. Add the following **Environment Variables**:
   - `GROQ_API_KEY`: Your Groq API key.
   - `GROQ_MODEL_NAME`: `llama-3.1-8b-instant`
