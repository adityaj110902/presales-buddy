FROM python:3.10-slim

RUN apt-get update && apt-get install -y curl wget git && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://ollama.ai/install.sh | sh || echo "Ollama install"

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000 11434

RUN mkdir -p /app && cat > /app/start.sh << 'EOF'
#!/bin/bash
set -e

echo "Starting Ollama..."
ollama serve &
OLLAMA_PID=$!

echo "Waiting for Ollama to start..."
sleep 10

echo "Pulling TinyLlama model..."
ollama pull tinyllama:latest

echo "Starting Flask backend..."
exec python backend_api.py
EOF

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
