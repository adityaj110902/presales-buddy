"""
PreSales Buddy - Compact Streamlit UI (No White Space)
Optimized layout, full-width, professional
"""

import streamlit as st
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
# PAGE CONFIG - FULL WIDTH
# ===============================================================
st.set_page_config(
    page_title="PreSales Buddy",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ===============================================================
# COMPACT STYLING - NO WHITE SPACE
# ===============================================================
st.markdown("""
    <style>
    /* Remove all margins and padding */
    html, body, [data-testid="stAppViewContainer"] {
        margin: 0;
        padding: 0;
    }
    
    [data-testid="stAppViewContainer"] {
        padding: 0 !important;
    }
    
    .main {
        padding: 0 !important;
        gap: 0 !important;
        background: #ffffff;
    }
    
    .stApp {
        background: #ffffff;
        padding: 0;
        margin: 0;
    }
    
    /* ===== HEADER ===== */
    .header-wrapper {
        background: #ffffff;
        border-bottom: 1px solid #e5e5e5;
        padding: 12px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .header-left {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .header-icon {
        width: 36px;
        height: 36px;
        background: #c2185b;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        color: white;
    }
    
    .header-title {
        font-size: 18px;
        font-weight: 700;
        color: #1f1f1f;
    }
    
    .header-subtitle {
        font-size: 11px;
        color: #999;
    }
    
    .header-right {
        font-size: 11px;
        color: #666;
        font-weight: 500;
    }
    
    .status-dot {
        width: 6px;
        height: 6px;
        background: #4caf50;
        border-radius: 50%;
        display: inline-block;
        margin-right: 4px;
    }
    
    /* ===== MAIN LAYOUT ===== */
    [data-testid="stVerticalBlock"] {
        gap: 0;
    }
    
    .main-content {
        display: flex;
        flex-direction: column;
        height: calc(100vh - 80px);
        padding: 0;
        margin: 0;
    }
    
    /* ===== CHAT CONTAINER ===== */
    .chat-container {
        flex: 1;
        overflow-y: auto;
        padding: 16px 20px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        background: #ffffff;
    }
    
    /* ===== EMPTY STATE ===== */
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100%;
        gap: 8px;
        color: #999;
    }
    
    .empty-state-icon {
        font-size: 48px;
        opacity: 0.5;
    }
    
    .empty-state-title {
        font-size: 20px;
        font-weight: 600;
        color: #1f1f1f;
    }
    
    .empty-state-subtitle {
        font-size: 13px;
        color: #999;
    }
    
    /* ===== SUGGESTED QUESTIONS ===== */
    .suggested-questions {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-top: 16px;
    }
    
    .question-btn {
        background: #f5f5f5;
        border: 1px solid #e5e5e5;
        border-radius: 6px;
        padding: 10px 14px;
        text-align: left;
        cursor: pointer;
        font-size: 13px;
        color: #1f1f1f;
        transition: all 0.2s;
        font-weight: 500;
    }
    
    .question-btn:hover {
        background: #f0f0f0;
        border-color: #c2185b;
        color: #c2185b;
    }
    
    /* ===== MESSAGES ===== */
    .message-group {
        display: flex;
        margin-bottom: 6px;
        animation: slideIn 0.2s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(6px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .message-content {
        padding: 10px 14px;
        border-radius: 6px;
        max-width: 65%;
        word-wrap: break-word;
        line-height: 1.4;
        font-size: 13px;
    }
    
    .user-message {
        background: #c2185b;
        color: white;
        margin-left: auto;
        border-radius: 6px 3px 6px 6px;
    }
    
    .assistant-message {
        background: #f5f5f5;
        color: #1f1f1f;
        border-radius: 3px 6px 6px 6px;
    }
    
    .message-source {
        font-size: 10px;
        color: #999;
        margin-top: 4px;
        padding-top: 4px;
        border-top: 1px solid rgba(0,0,0,0.1);
    }
    
    /* ===== INPUT SECTION ===== */
    .input-wrapper {
        border-top: 1px solid #e5e5e5;
        background: #ffffff;
        padding: 12px 20px;
        display: flex;
        gap: 8px;
        flex-shrink: 0;
    }
    
    .stTextInput > div > div > input {
        background: #f5f5f5 !important;
        border: 1px solid #e5e5e5 !important;
        border-radius: 6px !important;
        padding: 10px 12px !important;
        font-size: 13px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #c2185b !important;
        background: #ffffff !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #999;
    }
    
    .stButton > button {
        background: #c2185b !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 10px 18px !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        height: 40px !important;
        min-height: 40px !important;
    }
    
    .stButton > button:hover {
        background: #a01849 !important;
    }
    
    /* ===== FOOTER ===== */
    .footer-info {
        display: flex;
        justify-content: flex-start;
        gap: 20px;
        padding: 8px 20px;
        border-top: 1px solid #e5e5e5;
        font-size: 11px;
        color: #999;
        background: #ffffff;
        flex-shrink: 0;
    }
    
    .footer-item {
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .footer-value {
        color: #1f1f1f;
        font-weight: 600;
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #fafafa;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #d5d5d5;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #999;
    }
    
    </style>
""", unsafe_allow_html=True)


# ===============================================================
# LOAD RAG
# ===============================================================
@st.cache_resource
def load_rag_from_folder():
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
                st.error(f"Error: {str(e)}")
    
    if not documents:
        return None, files_loaded
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = []
    metadatas = []
    
    for content, filename in documents:
        chunks = splitter.split_text(content)
        for idx, chunk in enumerate(chunks):
            texts.append(chunk)
            metadatas.append({"source": filename, "chunk": idx})
    
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    vectordb = FAISS.from_texts(texts=texts, embedding=embedding_model, metadatas=metadatas)
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})
    
    template = """You are a professional sales assistant. Be helpful, concise, and professional.

Use ONLY the information provided. If unavailable, say so clearly.

Question: {question}

Context:
{context}

Answer:"""
    
    prompt = PromptTemplate(input_variables=["context", "question"], template=template)
    llm = OllamaLLM(model="llama3.1:latest")
    
    def format_docs(docs):
        return "\n\n".join([f"[{d.metadata['source']}]\n{d.page_content}" for d in docs])
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
    )
    
    return rag_chain, files_loaded


# ===============================================================
# INIT
# ===============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

rag, files_loaded = load_rag_from_folder()


# ===============================================================
# HEADER
# ===============================================================
st.markdown("""
    <div class="header-wrapper">
        <div class="header-left">
            <div class="header-icon">💼</div>
            <div>
                <div class="header-title">PreSales Buddy</div>
                <div class="header-subtitle">Sales Intelligence Assistant</div>
            </div>
        </div>
        <div class="header-right">
            <span class="status-dot"></span>AI ASSISTANT
        </div>
    </div>
""", unsafe_allow_html=True)


# ===============================================================
# CHAT
# ===============================================================
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

if len(st.session_state.messages) == 0:
    st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">💬</div>
            <div class="empty-state-title">Start a Conversation</div>
            <div class="empty-state-subtitle">Ask about products, pricing, or sales strategies</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="suggested-questions">', unsafe_allow_html=True)
    
    questions = [
        "📋 Tell me about our product features",
        "📈 What pricing plans do we offer?",
        "🎯 How do we compare to competitors?"
    ]
    
    for q in questions:
        if st.button(q, use_container_width=True, key=q):
            st.session_state.messages.append({"role": "user", "content": q})
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
                <div class="message-group">
                    <div class="message-content user-message">{msg["content"]}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            source = msg.get("source", "Knowledge Base")
            st.markdown(f"""
                <div class="message-group">
                    <div class="message-content assistant-message">
                        {msg["content"]}
                        <div class="message-source">📄 {source}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ===============================================================
# INPUT
# ===============================================================
st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)

col1, col2 = st.columns([5, 1], gap="small")

with col1:
    user_input = st.text_input("", placeholder="Ask a question...", label_visibility="collapsed", key="inp")

with col2:
    send = st.button("Send", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)


# ===============================================================
# FOOTER
# ===============================================================
st.markdown(f"""
    <div class="footer-info">
        <div class="footer-item">
            <span>📁</span>
            <span><span class="footer-value">{len(files_loaded)}</span> documents</span>
        </div>
        <div class="footer-item">
            <span>💬</span>
            <span><span class="footer-value">{len(st.session_state.messages)}</span> messages</span>
        </div>
        <div class="footer-item">
            <span>🟢</span>
            <span>Ready</span>
        </div>
    </div>
""", unsafe_allow_html=True)


# ===============================================================
# PROCESS
# ===============================================================
if send and user_input:
    if rag is None:
        st.error("⚠️ No documents loaded")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.spinner("Processing..."):
            try:
                response = rag.invoke(user_input)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "source": "Knowledge Base"
                })
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")
