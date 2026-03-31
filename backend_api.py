"""
PreSales Buddy - Flask Backend (Simplified - No langchain-community conflicts)
Direct FAISS + sentence-transformers + Ollama
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
import warnings
import json

warnings.filterwarnings('ignore')

from sentence_transformers import SentenceTransformer
from faiss import IndexFlatL2
import numpy as np
import requests

# PDF reading
try:
    import PyPDF2
except:
    PyPDF2 = None


# ===============================================================
# FLASK APP
# ===============================================================
app = Flask(__name__)
CORS(app)

# ===============================================================
# CONFIGURATION
# ===============================================================
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
MODEL_NAME = 'tinyllama:latest'  # Lighter model - fits in 4GB Docker limit
EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'

# ===============================================================
# SYSTEM PROMPT
# ===============================================================
SYSTEM_PROMPT = """You are PreSales Buddy, an expert Sales Intelligence Assistant for BUSINESSNEXT.

YOUR ROLE:
- Help Pre-Sales teams understand products, pricing, implementation
- Answer questions about features, competitors, ROI
- Provide consultative, data-driven responses
- Be professional, confident, and solution-focused

RESPONSE FORMAT - USE THIS EXACT STRUCTURE:

📌 DIRECT ANSWER
[1-2 sentence answer - be direct and clear]

🎯 KEY POINTS
• Point 1 with specific detail
• Point 2 with specific detail  
• Point 3 with specific detail

💡 EXAMPLE/CASE STUDY
[Concrete example with numbers]

📊 METRICS/DATA
[Include specific numbers and percentages]

✅ WHY IT MATTERS
[Explain business value and impact]

🔗 RELATED TOPICS
[Suggest 2-3 related questions they might ask next]

TONE:
✅ Professional but approachable
✅ Use specific numbers (not "many", "most")
✅ Include real examples
✅ Show competitive advantages
✅ Be consultative, not pushy

CRITICAL RULES:
- ALWAYS lead with the direct answer
- ALWAYS use specific numbers
- ALWAYS include at least one example
- ALWAYS show business value/ROI
- NEVER make up facts or numbers"""


# ===============================================================
# VECTOR DATABASE
# ===============================================================
class SimpleRAG:
    def __init__(self):
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        self.index = None
        self.documents = []
        self.metadata = []
    
    def add_documents(self, texts, metadatas):
        """Add documents to the vector store"""
        print(f"Creating embeddings for {len(texts)} chunks...")
        embeddings = self.embedder.encode(texts, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = IndexFlatL2(dimension)
        self.index.add(embeddings)
        
        self.documents = texts
        self.metadata = metadatas
        print(f"Vector store ready with {len(texts)} documents")
    
    def search(self, query, k=5):
        """Search for relevant documents"""
        if self.index is None:
            return []
        
        query_embedding = self.embedder.encode([query])[0].astype('float32')
        distances, indices = self.index.search(np.array([query_embedding]), k)
        
        results = []
        for idx in indices[0]:
            if idx < len(self.documents):
                results.append({
                    'text': self.documents[idx],
                    'metadata': self.metadata[idx]
                })
        return results


# ===============================================================
# LOAD DOCUMENTS
# ===============================================================
def load_documents():
    """Load documents from data folder"""
    rag = SimpleRAG()
    data_folder = "./data"
    
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
        return rag, []
    
    all_texts = []
    all_metadatas = []
    files_loaded = []
    
    # Load all files
    for file in os.listdir(data_folder):
        if file.endswith((".pdf", ".txt", ".xlsx")):
            full_path = os.path.join(data_folder, file)
            
            try:
                text = ""
                
                if file.endswith(".xlsx"):
                    df = pd.read_excel(full_path)
                    text = df.to_string()
                
                elif file.endswith(".txt"):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                
                elif file.endswith(".pdf") and PyPDF2:
                    with open(full_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        text = "\n".join([page.extract_text() for page in pdf_reader.pages])
                
                if text:
                    # Split into chunks
                    chunk_size = 1000
                    overlap = 200
                    
                    for i in range(0, len(text), chunk_size - overlap):
                        chunk = text[i:i + chunk_size]
                        if len(chunk) > 100:  # Only add non-trivial chunks
                            all_texts.append(chunk)
                            all_metadatas.append({"source": file, "chunk": i // chunk_size})
                    
                    files_loaded.append(file)
                    print(f"Loaded: {file}")
            
            except Exception as e:
                print(f"Error loading {file}: {str(e)}")
    
    if all_texts:
        rag.add_documents(all_texts, all_metadatas)
    else:
        print("No documents found")
    
    return rag, files_loaded


# Load on startup
print("Starting PreSales Buddy Backend...")
RAG, FILES_LOADED = load_documents()


# ===============================================================
# OLLAMA INTEGRATION
# ===============================================================
def chat_with_ollama(system_prompt, user_message, context=""):
    """Call Ollama for chat completion"""
    try:
        full_prompt = f"""{system_prompt}

CONTEXT FROM DOCUMENTS:
{context}

USER QUESTION: {user_message}

Remember to use the exact response format with 📌 🎯 💡 📊 ✅ and 🔗 sections."""
        
        response = requests.post(
            f'{OLLAMA_URL}/api/generate',
            json={
                'model': 'llama2:latest',
                'prompt': full_prompt,
                'stream': False,
                'temperature': 0.7
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'No response from Ollama')
        else:
            return f"Ollama error: {response.status_code}"
    
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"


# ===============================================================
# API ROUTES
# ===============================================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'documents': len(FILES_LOADED),
        'files': FILES_LOADED,
        'rag_ready': RAG.index is not None,
        'llm': 'Ollama (Llama 2 7B)'
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.json
        question = data.get('message', '').strip()
        
        if not question:
            return jsonify({'error': 'No message provided'}), 400
        
        if RAG.index is None:
            return jsonify({'error': 'No documents loaded'}), 503
        
        # Search for relevant documents
        print(f"Searching for: {question}")
        results = RAG.search(question, k=5)
        
        # Format context
        context = "\n\n".join([
            f"[{r['metadata']['source']}]\n{r['text']}" 
            for r in results
        ])
        
        # Get response from Ollama
        print("Calling Ollama...")
        response = chat_with_ollama(SYSTEM_PROMPT, question, context)
        
        return jsonify({
            'success': True,
            'response': response,
            'source': 'Knowledge Base'
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get loaded documents"""
    return jsonify({
        'count': len(FILES_LOADED),
        'documents': FILES_LOADED
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        'status': 'ready' if RAG.index else 'no_documents',
        'documents_count': len(FILES_LOADED),
        'files': FILES_LOADED,
        'llm': 'Ollama (Llama 2 7B)',
        'embedding_model': 'all-MiniLM-L6-v2'
    })


# ===============================================================
# ERROR HANDLERS
# ===============================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500


# ===============================================================
# RUN
# ===============================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("PreSales Buddy Backend API (Simplified)")
    print("="*60)
    print(f"Documents loaded: {len(FILES_LOADED)}")
    print(f"Files: {FILES_LOADED}")
    print(f"RAG Status: {'Ready' if RAG.index else 'No documents'}")
    print("\nAPI Endpoints:")
    print("  GET  /api/health      - Health check")
    print("  POST /api/chat        - Chat endpoint")
    print("  GET  /api/documents   - Get documents")
    print("  GET  /api/status      - System status")
    print("\nServer starting on http://0.0.0.0:5000")
    print("="*60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
