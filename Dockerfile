# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download SpaCy model for Presidio Analyzer
RUN python -m spacy download en_core_web_sm

# Copy the rest of the application code
COPY . .

# Expose the application port
EXPOSE 8000

# Run the application using uvicorn
CMD ["uvicorn", "main2:app", "--host", "0.0.0.0", "--port", "8000"]
