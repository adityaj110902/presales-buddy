FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh || echo "Ollama install script failed, will try alternative"

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports
EXPOSE 5000 11434

# Create startup script
RUN echo '#!/bin/bash\n\
# Start Ollama in background\n\
echo "Starting Ollama..."\n\
ollama serve &\n\
OLLAMA_PID=$!\n\
\n\
# Wait for Ollama to start\n\
sleep 10\n\
\n\
# Pull model\n\
echo "Pulling Llama 3.1 model..."\n\
ollama pull llama3.1:latest\n\
\n\
# Start Flask backend\n\
echo "Starting Flask backend..."\n\
exec python backend_api.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run startup script
CMD ["/app/start.sh"]
