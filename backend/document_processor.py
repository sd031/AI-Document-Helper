import os
from typing import List, Dict
import PyPDF2
import docx
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process various document formats into chunks"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_document(self, file_path: str) -> List[Dict]:
        """Process a document and return chunks"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            text = self._extract_pdf(file_path)
        elif file_ext == '.docx':
            text = self._extract_docx(file_path)
        elif file_ext in ['.txt', '.md']:
            text = self._extract_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Split into chunks
        chunks = self._create_chunks(text)
        
        return chunks
    
    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise
    
    def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"Error extracting DOCX: {e}")
            raise
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from TXT or MD files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            raise
    
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
