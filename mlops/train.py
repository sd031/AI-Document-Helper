#!/usr/bin/env python3
"""
MLOps Training Pipeline for AI Document Helper
Processes documents and indexes them into the vector database
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict
import uuid

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import PyPDF2
import docx
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process various document formats"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_document(self, file_path: str) -> List[Dict]:
        """Process a document and return chunks"""
        file_ext = Path(file_path).suffix.lower()
        
        logger.info(f"Processing {file_path}")
        
        if file_ext == '.pdf':
            text = self._extract_pdf(file_path)
        elif file_ext == '.docx':
            text = self._extract_docx(file_path)
        elif file_ext in ['.txt', '.md']:
            text = self._extract_text(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_ext}")
            return []
        
        chunks = self._create_chunks(text)
        logger.info(f"Created {len(chunks)} chunks from {Path(file_path).name}")
        
        return chunks
    
    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from TXT or MD files"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _create_chunks(self, text: str) -> List[Dict]:
        """Split text into overlapping chunks"""
        chunks = []
        words = text.split()
        
        start = 0
        chunk_id = 0
        
        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "chunk_id": chunk_id,
                    "start_word": start,
                    "end_word": end
                }
            })
            
            chunk_id += 1
            start += self.chunk_size - self.chunk_overlap
        
        return chunks

class TrainingPipeline:
    """MLOps training pipeline"""
    
    def __init__(self):
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        self.collection_name = "documents"
        self.embedding_dim = 384
        
        logger.info("Initializing training pipeline...")
        
        # Wait for Qdrant to be ready
        self._wait_for_qdrant()
        
        # Initialize components
        self.qdrant_client = QdrantClient(
            host=self.qdrant_host,
            port=self.qdrant_port
        )
        
        logger.info("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        self.doc_processor = DocumentProcessor()
        
        # Ensure collection exists
        self._setup_collection()
    
    def _wait_for_qdrant(self, max_retries: int = 30, delay: int = 2):
        """Wait for Qdrant to be ready"""
        logger.info(f"Waiting for Qdrant at {self.qdrant_host}:{self.qdrant_port}")
        
        for i in range(max_retries):
            try:
                client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
                client.get_collections()
                logger.info("Qdrant is ready!")
                return
            except Exception as e:
                if i < max_retries - 1:
                    logger.info(f"Waiting for Qdrant... ({i+1}/{max_retries})")
                    time.sleep(delay)
                else:
                    logger.error(f"Failed to connect to Qdrant: {e}")
                    raise
    
    def _setup_collection(self):
        """Create collection if it doesn't exist"""
        collections = self.qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            logger.info(f"Creating collection: {self.collection_name}")
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
        else:
            logger.info(f"Collection {self.collection_name} already exists")
    
    def _create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for texts"""
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
    
    def index_documents(self, document_dir: str):
        """Index all documents in a directory"""
        doc_path = Path(document_dir)
        
        if not doc_path.exists():
            logger.error(f"Directory not found: {document_dir}")
            return
        
        # Find all supported documents
        supported_extensions = ['.pdf', '.txt', '.docx', '.md']
        documents = []
        
        for ext in supported_extensions:
            documents.extend(doc_path.glob(f"**/*{ext}"))
        
        if not documents:
            logger.warning(f"No documents found in {document_dir}")
            return
        
        logger.info(f"Found {len(documents)} documents to process")
        
        # Process each document
        total_chunks = 0
        
        for doc_file in tqdm(documents, desc="Processing documents"):
            try:
                # Process document
                chunks = self.doc_processor.process_document(str(doc_file))
                
                if not chunks:
                    continue
                
                # Create embeddings
                texts = [chunk["text"] for chunk in chunks]
                embeddings = self._create_embeddings(texts)
                
                # Create points for Qdrant
                points = []
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    point = PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={
                            "text": chunk["text"],
                            "source": doc_file.name,
                            "chunk_index": i,
                            "metadata": chunk.get("metadata", {})
                        }
                    )
                    points.append(point)
                
                # Upload to Qdrant
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                
                total_chunks += len(chunks)
                logger.info(f"Indexed {len(chunks)} chunks from {doc_file.name}")
                
            except Exception as e:
                logger.error(f"Error processing {doc_file}: {e}")
                continue
        
        logger.info(f"Training complete! Indexed {total_chunks} total chunks from {len(documents)} documents")
    
    def get_stats(self):
        """Get collection statistics"""
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            logger.info(f"Collection stats: {collection_info.points_count} points")
            return collection_info
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return None

def main():
    """Main training pipeline"""
    logger.info("=" * 60)
    logger.info("AI Document Helper - MLOps Training Pipeline")
    logger.info("=" * 60)
    
    # Initialize pipeline
    pipeline = TrainingPipeline()
    
    # Index documents from data directory
    data_dir = "/data/sample_docs"
    
    if not os.path.exists(data_dir):
        logger.warning(f"Sample docs directory not found: {data_dir}")
        logger.info("Creating sample docs directory...")
        os.makedirs(data_dir, exist_ok=True)
    
    # Also check for uploaded docs
    uploaded_dir = "/data/uploaded_docs"
    
    # Index both directories
    for directory in [data_dir, uploaded_dir]:
        if os.path.exists(directory):
            logger.info(f"\nIndexing documents from: {directory}")
            pipeline.index_documents(directory)
    
    # Show final stats
    logger.info("\n" + "=" * 60)
    logger.info("Training Pipeline Complete!")
    pipeline.get_stats()
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
