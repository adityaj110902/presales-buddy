const express = require('express');
const cors = require('cors');
const axios = require('axios');
const multer = require('multer');
const pdfParse = require('pdf-parse');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.static('.'));

// Setup file upload
const upload = multer({ dest: 'documents/' });

const OLLAMA_URL = 'http://localhost:11434';
const MODEL = 'llama3.1:latest';
const PORT = 3001;

const conversations = {};
let documents = []; // In-memory store

// Load documents from disk on startup
function loadDocumentsFromDisk() {
  const docFolder = './documents';
  if (!fs.existsSync(docFolder)) {
    fs.mkdirSync(docFolder);
  }
  
  const files = fs.readdirSync(docFolder);
  files.forEach(file => {
    const filepath = path.join(docFolder, file);
    const stats = fs.statSync(filepath);
    if (stats.isFile()) {
      documents.push({
        id: Date.now() + Math.random(),
        filename: file,
        filepath: filepath,
        type: 'pdf',
        uploadedAt: stats.mtime,
        content: null // Will be loaded on demand
      });
    }
  });
  console.log(`📁 Loaded ${documents.length} documents from disk`);
}

// Extract text from PDF
async function extractPdfText(filepath) {
  try {
    const buffer = fs.readFileSync(filepath);
    const pdfParse = require('pdf-parse/lib/pdf-parse.js');
    const data = await pdfParse(buffer);
    return data.text;
  } catch (error) {
    console.error('Error parsing PDF:', error.message);
    return 'Could not extract text from PDF';
  }
}

// Upload PDF file
app.post('/api/upload', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const filename = req.file.originalname;
    const filepath = req.file.path;

    // Extract text from PDF
    let content = '';
    if (filename.toLowerCase().endsWith('.pdf')) {
      content = await extractPdfText(filepath);
    } else {
      content = fs.readFileSync(filepath, 'utf-8');
    }

    documents.push({
      id: Date.now(),
      filename: filename,
      filepath: filepath,
      type: filename.endsWith('.pdf') ? 'pdf' : 'text',
      uploadedAt: new Date(),
      content: content
    });

    res.json({
      status: 'success',
      message: `Document '${filename}' uploaded successfully`,
      totalDocs: documents.length
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get all documents
app.get('/api/documents', (req, res) => {
  res.json({
    count: documents.length,
    documents: documents.map(d => ({
      id: d.id,
      filename: d.filename,
      type: d.type,
      uploadedAt: d.uploadedAt,
      size: d.content ? d.content.length : 0
    }))
  });
});

// Delete document
app.delete('/api/documents/:id', (req, res) => {
  const { id } = req.params;
  const index = documents.findIndex(d => d.id == id);
  
  if (index === -1) {
    return res.status(404).json({ error: 'Document not found' });
  }

  const doc = documents[index];
  const filename = doc.filename;
  
  // Delete file from disk
  if (fs.existsSync(doc.filepath)) {
    fs.unlinkSync(doc.filepath);
  }
  
  documents.splice(index, 1);
  
  res.json({ status: 'success', message: `Document '${filename}' deleted` });
});

// Helper: Find relevant documents
function findRelevantDocs(query, maxDocs = 3) {
  if (documents.length === 0) return [];

  const queryWords = query.toLowerCase().split(' ');
  const scored = documents.map(doc => {
    const content = (doc.content || '').toLowerCase();
    const score = queryWords.filter(word => content.includes(word)).length;
    return { ...doc, score };
  });

  return scored
    .filter(d => d.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, maxDocs);
}

// Chat with documents
app.post('/api/chat', async (req, res) => {
  try {
    const { message, conversationId } = req.body;
    
    if (!message) return res.status(400).json({ error: 'Message required' });
    if (!conversations[conversationId]) conversations[conversationId] = [];
    
    const conv = conversations[conversationId];
    conv.push({ role: 'user', content: message });

    // Find relevant documents
    const relevantDocs = findRelevantDocs(message);
    let docContext = '';
    if (relevantDocs.length > 0) {
      docContext = '\n\nRELEVANT INFORMATION FROM DOCUMENTS:\n';
      relevantDocs.forEach(doc => {
        const text = doc.content || '';
        docContext += `\n[${doc.filename}]\n${text.substring(0, 1000)}\n`;
      });
    }

    const systemPrompt = `You are PreSales Buddy. Help the sales team based on documents provided.
Be friendly and concise. Use the provided documents to answer questions.${docContext}`;

    const response = await axios.post(`${OLLAMA_URL}/api/chat`, {
      model: MODEL,
      messages: [
        { role: 'system', content: systemPrompt },
        ...conv
      ],
      stream: false,
      temperature: 0.7
    });

    const assistantMessage = response.data.message.content;
    conv.push({ role: 'assistant', content: assistantMessage });
    
    if (conv.length > 20) {
      conv.shift();
      conv.shift();
    }
    
    res.json({
      conversationId,
      message: assistantMessage,
      docsUsed: relevantDocs.length,
      timestamp: new Date()
    });

  } catch (error) {
    console.error('Error:', error.message);
    res.status(500).json({ error: 'Failed', details: error.message });
  }
});

// Health check
app.get('/api/health', async (req, res) => {
  try {
    await axios.post(`${OLLAMA_URL}/api/chat`, {
      model: MODEL,
      messages: [{ role: 'user', content: 'test' }],
      stream: false
    }, { timeout: 5000 });
    res.json({ status: 'ok', ollama: 'connected', model: MODEL, docs: documents.length });
  } catch (error) {
    res.status(503).json({ status: 'error', ollama: 'disconnected' });
  }
});

app.listen(PORT, () => {
  loadDocumentsFromDisk();
  console.log(`\n✨ Backend running on http://localhost:${PORT}`);
  console.log(`📁 Documents folder: ./documents`);
  console.log(`📝 Connected to Ollama at: ${OLLAMA_URL}`);
  console.log(`🤖 Using model: ${MODEL}\n`);
});