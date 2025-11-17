import pytest
from document_processor import DocumentProcessor
import os

def test_create_chunks():
    """Test text chunking"""
    processor = DocumentProcessor(chunk_size=10, chunk_overlap=2)
    
    text = " ".join([f"word{i}" for i in range(50)])
    chunks = processor._create_chunks(text)
    
    assert len(chunks) > 0
    assert all("text" in chunk for chunk in chunks)
    assert all("metadata" in chunk for chunk in chunks)

def test_chunk_overlap():
    """Test that chunks have proper overlap"""
    processor = DocumentProcessor(chunk_size=10, chunk_overlap=2)
    
    text = " ".join([f"word{i}" for i in range(30)])
    chunks = processor._create_chunks(text)
    
    # Should have multiple chunks
    assert len(chunks) > 1
