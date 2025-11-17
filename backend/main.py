from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import aiofiles
from datetime import datetime
import logging

from rag_engine import RAGEngine
from document_processor import DocumentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Document Helper API",
    description="RAG-based document Q&A system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
rag_engine = RAGEngine()
doc_processor = DocumentProcessor()

# Data models
class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    timestamp: str

class DocumentInfo(BaseModel):
    filename: str
    size: int
    upload_date: str
    chunks: int

class HealthResponse(BaseModel):
    status: str
    services: dict
    timestamp: str

# Ensure upload directory exists
UPLOAD_DIR = "/data/uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting AI Document Helper API...")
    try:
        await rag_engine.initialize()
        logger.info("RAG Engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG Engine: {e}")
        raise

@app.get("/", tags=["General"])
async def root():
    """Root endpoint"""
    return {
        "message": "AI Document Helper API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint"""
    services_status = await rag_engine.check_services()
    
    return HealthResponse(
        status="healthy" if all(services_status.values()) else "degraded",
        services=services_status,
        timestamp=datetime.now().isoformat()
    )

@app.post("/upload", tags=["Documents"])
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.txt', '.docx', '.md']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not supported. Allowed: {allowed_extensions}"
            )
        
        # Save file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        logger.info(f"File saved: {file_path}")
        
        # Process document
        chunks = doc_processor.process_document(file_path)
        logger.info(f"Document processed into {len(chunks)} chunks")
        
        # Add to vector database
        await rag_engine.add_documents(chunks, file.filename)
        logger.info(f"Document indexed: {file.filename}")
        
        return {
            "message": "Document uploaded and processed successfully",
            "filename": file.filename,
            "chunks": len(chunks),
            "size": len(content)
        }
    
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_documents(request: QueryRequest):
    """Query documents using RAG"""
    try:
        logger.info(f"Processing query: {request.question}")
        
        # Get answer from RAG engine
        result = await rag_engine.query(request.question, top_k=request.top_k)
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", response_model=List[str], tags=["Documents"])
async def list_documents():
    """List all uploaded documents"""
    try:
        files = os.listdir(UPLOAD_DIR)
        return [f for f in files if not f.startswith('.')]
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{filename}", tags=["Documents"])
async def delete_document(filename: str):
    """Delete a document"""
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Document not found")
        
        os.remove(file_path)
        logger.info(f"Document deleted: {filename}")
        
        return {"message": f"Document {filename} deleted successfully"}
    
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats", tags=["General"])
async def get_stats():
    """Get system statistics"""
    try:
        stats = await rag_engine.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
