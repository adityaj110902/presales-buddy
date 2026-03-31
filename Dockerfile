FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh || echo "Ollama install script failed"

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports
EXPOSE 5000 11434

# Create startup script with Llama 2 (lighter model)
RUN echo '#!/bin/bash\n\
# Start Ollama in background\n\
echo "Starting Ollama..."\n\
ollama serve &\n\
OLLAMA_PID=$!\n\
\n\
# Wait for Ollama to start\n\
sleep 10\n\
\n\
# Pull Llama 2 model (lighter than Llama 3.1)\n\
echo "Pulling Llama 2 model..."\n\
ollama pull tinyllama:latest
\n\
# Start Flask backend\n\
echo "Starting Flask backend..."\n\
exec python backend_api_simple.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run startup script
CMD ["/app/start.sh"]
