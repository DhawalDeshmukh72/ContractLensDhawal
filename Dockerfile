# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables to limit library threading and save RAM
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1
ENV VECLIB_MAXIMUM_THREADS=1
ENV NUMEXPR_NUM_THREADS=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU-only version first to save massive RAM and disk space
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy requirements file and install the rest of Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download SpaCy model for Presidio Analyzer
RUN python -m spacy download en_core_web_sm

# Copy the rest of the application code
COPY . .

# Expose the application port (Hugging Face Spaces expects 7860 by default)
EXPOSE 7860

# Run the application using uvicorn
CMD ["uvicorn", "main2:app", "--host", "0.0.0.0", "--port", "7860"]
