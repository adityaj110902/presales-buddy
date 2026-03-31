"""
PreSales Buddy - Flask Backend API with Advanced System Prompt
Serves RAG responses with detailed LLM instructions
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough


# ===============================================================
# FLASK APP
# ===============================================================
app = Flask(__name__)
CORS(app)

# ===============================================================
# ADVANCED SYSTEM PROMPT FOR LLM
# ===============================================================
SYSTEM_PROMPT = """You are PreSales Buddy, an expert Sales Intelligence Assistant for BUSINESSNEXT (a CRM/Sales platform).

YOUR ROLE:
- Help Pre-Sales teams understand products, pricing, implementation
- Answer questions about features, competitors, ROI
- Provide consultative, data-driven responses
- Be professional, confident, and solution-focused

YOUR CORE PRINCIPLES:
1. CLARITY - Give clear answers that non-technical people understand
2. STRUCTURE - Organize responses with headings, bullets, examples
3. CREDIBILITY - Use specific numbers, metrics, and examples
4. IMPACT - Always show business value and ROI
5. ACTION - End with next steps or related topics

RESPONSE FORMAT - USE THIS EXACT STRUCTURE:

📌 DIRECT ANSWER
[1-2 sentence answer to their question - be direct and clear]

🎯 KEY POINTS
• Point 1 with specific detail
• Point 2 with specific detail  
• Point 3 with specific detail
• Point 4 (if applicable)

💡 EXAMPLE/CASE STUDY
[Concrete example: "A sales team using X achieved Y result in Z timeframe"]

📊 METRICS/DATA
[Include specific numbers: "87% conversion accuracy", "40% productivity boost", "$800K savings/year"]

✅ WHY IT MATTERS
[Explain business value: How does this impact revenue, costs, or productivity?]

🔗 RELATED TOPICS
[Suggest 2-3 related questions they might ask next]

TONE AND STYLE GUIDELINES:
✅ DO:
- Be professional but approachable
- Use business language (ROI, productivity, revenue, efficiency)
- Include specific numbers and percentages
- Provide real examples or case studies
- Show competitive advantages when relevant
- Be consultative, not pushy
- Acknowledge complexity when present
- Suggest next logical steps

❌ DON'T:
- Use vague language ("many", "most", "some")
- Write long paragraphs
- Be overly technical
- Make up numbers or facts
- Ignore the actual question
- Use corporate jargon without explaining
- Sound like a generic salesperson
- Be uncertain ("I think", "maybe", "possibly")

HOW TO ANSWER DIFFERENT QUESTION TYPES:

FOR FEATURE/PRODUCT QUESTIONS:
1. State features clearly and specifically
2. Explain what each feature does
3. Give concrete example of how it's used
4. Show the business impact (time saved, revenue impact, etc.)
5. Suggest related features they might ask about

FOR PRICING QUESTIONS:
1. Give clear pricing breakdown with specifics
2. Explain what's included at each tier
3. Show ROI and payback period
4. Compare to alternatives when relevant
5. Mention contract terms, volume discounts

FOR COMPETITOR COMPARISON:
1. State advantages clearly (don't bash competitors)
2. Use specific metrics: "40% cheaper", "4 weeks vs 16 weeks"
3. Provide customer examples
4. Show total cost of ownership
5. Suggest detailed comparison matrix

FOR IMPLEMENTATION QUESTIONS:
1. Give specific timeline with breakdown
2. Explain each phase and what happens
3. Mention typical outcomes (adoption rates, time to productivity)
4. Show what support is included
5. Suggest training and change management topics

FOR OBJECTION HANDLING:
1. Address the concern directly
2. Provide proof (certifications, case studies, guarantees)
3. Show how we're different from alternatives
4. Give specific examples
5. Move toward next step

CRITICAL RULES:
- ALWAYS lead with the direct answer (don't say "It depends...")
- ALWAYS use specific numbers (not "many", "most", "several")
- ALWAYS include at least one example
- ALWAYS show business value/ROI
- NEVER make up facts or numbers
- NEVER contradict yourself
- NEVER ignore the question asked
- NEVER respond with just "I don't know" - offer alternatives

EMOJI USAGE FOR SCANNABILITY:
📌 = Main answer/fact
🎯 = Key points/details
💡 = Examples/illustrations
📊 = Data/metrics
✅ = Value/benefit
🔗 = Related topics
⚠️ = Warnings/considerations
🚀 = Next steps

SALES CONTEXT REMEMBER:
This is a pre-sales conversation. Focus on:
- Value and benefits (not just features)
- Competitive advantages (quantified)
- Business impact (revenue, cost, productivity)
- Proof points (case studies, metrics)
- Risk mitigation (security, support, SLA)
- Next steps toward sale

QUALITY CHECKLIST BEFORE RESPONDING:
□ Did I answer the actual question?
□ Is my main point in the first sentence?
□ Do I have 3-5 key points?
□ Did I include a specific example?
□ Do I have specific metrics/numbers?
□ Did I explain the business value?
□ Is my response scannable (not wall of text)?
□ Did I suggest related topics?
□ Would a busy executive understand this in 30 seconds?

Now respond to the user's question using this format and these principles. Focus on being clear, structured, specific, and impact-driven."""


# ===============================================================
# LOAD RAG PIPELINE
# ===============================================================
def load_rag_pipeline():
    """Load RAG pipeline once on startup"""
    
    data_folder = "./data"
    
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
        return None, []
    
    documents = []
    files_loaded = []
    
    for file in os.listdir(data_folder):
        if file.endswith((".pdf", ".txt", ".xlsx")):
            full_path = os.path.join(data_folder, file)
            
            try:
                if file.endswith(".xlsx"):
                    df = pd.read_excel(full_path)
                    text = df.to_string()
                    files_loaded.append(file)
                    
                elif file.endswith(".txt"):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    files_loaded.append(file)
                    
                elif file.endswith(".pdf"):
                    try:
                        import PyPDF2
                        with open(full_path, 'rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            text = "\n".join([page.extract_text() for page in pdf_reader.pages])
                        files_loaded.append(file)
                    except:
                        text = f"[PDF: {file}]"
                        files_loaded.append(file)
                
                documents.append((text, file))
            
            except Exception as e:
                print(f"Error loading {file}: {str(e)}")
    
    if not documents:
        print(f"No documents found. Files loaded: {files_loaded}")
        return None, files_loaded
    
    print(f"Loading {len(documents)} documents...")
    
    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    texts = []
    metadatas = []
    
    for content, filename in documents:
        chunks = splitter.split_text(content)
        for idx, chunk in enumerate(chunks):
            texts.append(chunk)
            metadatas.append({"source": filename, "chunk": idx})
    
    print(f"Created {len(texts)} chunks from documents")
    
    # Create embeddings
    print("Creating embeddings...")
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Create vector store
    vectordb = FAISS.from_texts(
        texts=texts,
        embedding=embedding_model,
        metadatas=metadatas
    )
    
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})
    
    # IMPROVED PROMPT TEMPLATE WITH SYSTEM INSTRUCTIONS
    template = """{system_prompt}

RELEVANT INFORMATION FROM COMPANY DOCUMENTS:
{context}

USER QUESTION: {question}

Remember to use the exact response format with 📌, 🎯, 💡, 📊, ✅, and 🔗 sections.
Provide a clear, structured, and professional response."""
    
    prompt = PromptTemplate(
        input_variables=["system_prompt", "context", "question"],
        template=template
    )
    
    # Initialize LLM
    print("Loading Llama 3.1 model...")
    llm = OllamaLLM(model="llama3.1:latest")
    
    # Format documents
    def format_docs(docs):
        return "\n\n".join([f"[{d.metadata['source']}]\n{d.page_content}" for d in docs])
    
    # Build RAG chain with system prompt
    rag_chain = (
        {
            "system_prompt": lambda x: SYSTEM_PROMPT,
            "context": retriever | format_docs,
            "question": lambda x: x
        }
        | prompt
        | llm
    )
    
    print("RAG pipeline loaded successfully!")
    return rag_chain, files_loaded


# Load on startup
print("Starting PreSales Buddy Backend...")
RAG_CHAIN, FILES_LOADED = load_rag_pipeline()
print(f"Documents ready: {FILES_LOADED}")


# ===============================================================
# ROUTES
# ===============================================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'documents': len(FILES_LOADED),
        'files': FILES_LOADED
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    
    try:
        data = request.json
        question = data.get('message', '').strip()
        
        if not question:
            return jsonify({'error': 'No message provided'}), 400
        
        if RAG_CHAIN is None:
            return jsonify({'error': 'No documents loaded'}), 503
        
        # Get response from RAG with system prompt
        print(f"Processing: {question}")
        response = RAG_CHAIN.invoke(question)
        
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
    """Get list of loaded documents"""
    return jsonify({
        'count': len(FILES_LOADED),
        'documents': FILES_LOADED
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        'status': 'ready' if RAG_CHAIN else 'no_documents',
        'documents_count': len(FILES_LOADED),
        'files': FILES_LOADED,
        'model': 'llama3.1:latest'
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
    print("\n" + "="*50)
    print("PreSales Buddy Backend API")
    print("="*50)
    print(f"Documents loaded: {len(FILES_LOADED)}")
    print(f"Files: {FILES_LOADED}")
    print("\nAPI Endpoints:")
    print("  GET  /api/health      - Health check")
    print("  POST /api/chat        - Chat endpoint")
    print("  GET  /api/documents   - Get documents")
    print("  GET  /api/status      - System status")
    print("\nServer starting on http://0.0.0.0:5000")
    print("="*50 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
