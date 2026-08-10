---
title: ContractLens
emoji: ⚖️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

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

### Option A: Hosting on Hugging Face Spaces (Free 16GB RAM - Recommended)
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **Create New Space**.
2. Set the **Space SDK** to **Docker** (choose the blank template).
3. Clone the Space repository locally, or connect your GitHub repository using GitHub Actions.
4. Add your **`GROQ_API_KEY`** in the Space's **Settings -> Variables and Secrets** as a **Secret**.
5. Once pushed, Hugging Face will build the Docker container and host it automatically.

### Option B: Hosting with Docker
Build and run the container locally:
```bash
# Build the image
docker build -t contractlens .

# Run the container
docker run -p 7860:7860 --env-file .env contractlens
```
Then navigate to **`http://localhost:7860`**.
