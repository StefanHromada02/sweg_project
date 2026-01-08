FROM python:3.11-slim

WORKDIR /app

# Install Ollama
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://ollama.com/install.sh | sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 8001

# Start script
CMD ["sh", "-c", "ollama serve & sleep 5 && ollama pull tinyllama && python app.py"]
