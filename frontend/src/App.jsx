import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { 
  Send, 
  Upload, 
  FileText, 
  Trash2, 
  Loader2, 
  CheckCircle2, 
  XCircle,
  MessageSquare,
  Database
} from 'lucide-react';
import { cn } from './lib/utils';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [health, setHealth] = useState(null);
  const [stats, setStats] = useState(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchDocuments();
    checkHealth();
    fetchStats();
    
    // Add welcome message
    setMessages([{
      role: 'assistant',
      content: 'Hello! I\'m your AI document assistant. Upload some documents and ask me questions about them.',
      timestamp: new Date().toISOString()
    }]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const checkHealth = async () => {
    try {
      const response = await axios.get(`${API_URL}/health`);
      setHealth(response.data);
    } catch (error) {
      console.error('Health check failed:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${API_URL}/documents`);
      setDocuments(response.data);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    }
  };

  const handleUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post(`${API_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setMessages(prev => [...prev, {
        role: 'system',
        content: `Document "${file.name}" uploaded and processed successfully!`,
        timestamp: new Date().toISOString()
      }]);
      
      fetchDocuments();
      fetchStats();
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'system',
        content: `Failed to upload document: ${error.response?.data?.detail || error.message}`,
        timestamp: new Date().toISOString(),
        error: true
      }]);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDelete = async (filename) => {
    try {
      await axios.delete(`${API_URL}/documents/${filename}`);
      setMessages(prev => [...prev, {
        role: 'system',
        content: `Document "${filename}" deleted successfully.`,
        timestamp: new Date().toISOString()
      }]);
      fetchDocuments();
      fetchStats();
    } catch (error) {
      console.error('Failed to delete document:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/query`, {
        question: input
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.answer,
        sources: response.data.sources,
        timestamp: response.data.timestamp
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your question. Please try again.',
        timestamp: new Date().toISOString(),
        error: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-slate-200 flex flex-col">
        <div className="p-6 border-b border-slate-200">
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <MessageSquare className="w-7 h-7 text-blue-600" />
            AI Doc Helper
          </h1>
          <p className="text-sm text-slate-600 mt-1">Chat with your documents</p>
        </div>

        {/* Health Status */}
        <div className="p-4 border-b border-slate-200">
          <div className="text-xs font-semibold text-slate-700 mb-2">System Status</div>
          {health && (
            <div className="space-y-1">
              {Object.entries(health.services).map(([service, status]) => (
                <div key={service} className="flex items-center justify-between text-xs">
                  <span className="text-slate-600 capitalize">{service}</span>
                  {status ? (
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                  ) : (
                    <XCircle className="w-4 h-4 text-red-500" />
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Stats */}
        {stats && (
          <div className="p-4 border-b border-slate-200">
            <div className="flex items-center gap-2 text-sm text-slate-700">
              <Database className="w-4 h-4" />
              <span>{stats.total_documents} document chunks indexed</span>
            </div>
          </div>
        )}

        {/* Upload */}
        <div className="p-4 border-b border-slate-200">
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleUpload}
            accept=".pdf,.txt,.docx,.md"
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className={cn(
              "flex items-center justify-center gap-2 w-full px-4 py-3 rounded-lg",
              "bg-blue-600 text-white font-medium cursor-pointer",
              "hover:bg-blue-700 transition-colors",
              uploading && "opacity-50 cursor-not-allowed"
            )}
          >
            {uploading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4" />
                Upload Document
              </>
            )}
          </label>
          <p className="text-xs text-slate-500 mt-2 text-center">
            PDF, TXT, DOCX, MD
          </p>
        </div>

        {/* Documents List */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="text-xs font-semibold text-slate-700 mb-2">
            Documents ({documents.length})
          </div>
          <div className="space-y-2">
            {documents.map((doc) => (
              <div
                key={doc}
                className="flex items-center justify-between p-3 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors"
              >
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <FileText className="w-4 h-4 text-slate-400 flex-shrink-0" />
                  <span className="text-sm text-slate-700 truncate">{doc}</span>
                </div>
                <button
                  onClick={() => handleDelete(doc)}
                  className="p-1 hover:bg-red-100 rounded transition-colors flex-shrink-0"
                >
                  <Trash2 className="w-4 h-4 text-red-500" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={cn(
                "flex",
                message.role === 'user' ? "justify-end" : "justify-start"
              )}
            >
              <div
                className={cn(
                  "max-w-2xl rounded-lg px-4 py-3",
                  message.role === 'user' && "bg-blue-600 text-white",
                  message.role === 'assistant' && "bg-white border border-slate-200",
                  message.role === 'system' && message.error && "bg-red-50 border border-red-200 text-red-800",
                  message.role === 'system' && !message.error && "bg-green-50 border border-green-200 text-green-800"
                )}
              >
                <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-200">
                    <div className="text-xs font-semibold text-slate-600 mb-2">Sources:</div>
                    <div className="space-y-2">
                      {message.sources.map((source, idx) => (
                        <div key={idx} className="text-xs bg-slate-50 p-2 rounded">
                          <div className="font-medium text-slate-700">{source.source}</div>
                          <div className="text-slate-600 mt-1">{source.excerpt}</div>
                          <div className="text-slate-500 mt-1">
                            Relevance: {(source.relevance_score * 100).toFixed(1)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="text-xs opacity-60 mt-2">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border border-slate-200 rounded-lg px-4 py-3">
                <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-slate-200 bg-white p-4">
          <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask a question about your documents..."
                className="flex-1 px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className={cn(
                  "px-6 py-3 bg-blue-600 text-white rounded-lg font-medium",
                  "hover:bg-blue-700 transition-colors",
                  "disabled:opacity-50 disabled:cursor-not-allowed",
                  "flex items-center gap-2"
                )}
              >
                <Send className="w-4 h-4" />
                Send
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;
