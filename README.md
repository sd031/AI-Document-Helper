# AI Document Helper

A complete AI-powered document assistant with a modern UI, MLOps pipeline, and end-to-end testing. Built entirely with open-source technologies.

## Features

- 🤖 **AI Chat Interface**: Interactive chat with your documents using RAG (Retrieval Augmented Generation)
- 📄 **Document Processing**: Support for PDF, TXT, DOCX, and Markdown files
- 🎨 **Modern UI**: Beautiful React interface with TailwindCSS and shadcn/ui components
- 🔄 **MLOps Pipeline**: Automated training pipeline for processing new documents
- 🐳 **Docker Compose**: One-command deployment
- ✅ **End-to-End Testing**: Comprehensive test suite

## Tech Stack

- **Frontend**: React, TailwindCSS, shadcn/ui, Lucide Icons
- **Backend**: FastAPI (Python)
- **LLM**: Ollama (llama3.2 or mistral)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Vector DB**: Qdrant
- **Document Processing**: PyPDF2, python-docx, langchain

## Quick Start

### Prerequisites

- Docker and Docker Compose
- At least 8GB RAM (16GB recommended for larger models)
- 10GB free disk space

### Installation

1. **Clone and navigate to the project**:
   ```bash
   cd /Users/sandipdas/simple_ai_doument_helper
   ```

2. **Start all services**:
   ```bash
   docker-compose up -d
   ```

3. **Pull the LLM model** (first time only):
   ```bash
   docker exec -it ollama ollama pull llama3.2
   ```

4. **Process sample documents**:
   ```bash
   docker-compose --profile training up mlops
   ```

5. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Qdrant Dashboard: http://localhost:6333/dashboard

### Running Tests

```bash
# Run end-to-end tests
./scripts/run_tests.sh

# Or manually
docker-compose exec backend pytest tests/ -v
```

## Project Structure

```
.
├── backend/              # FastAPI backend
│   ├── main.py          # API endpoints
│   ├── rag_engine.py    # RAG implementation
│   ├── document_processor.py
│   └── tests/           # Backend tests
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   └── App.jsx      # Main app
│   └── package.json
├── mlops/               # Training pipeline
│   ├── train.py         # Training script
│   └── Dockerfile
├── data/                # Document storage
│   ├── sample_docs/     # Sample documents
│   └── test_docs/       # Test documents
├── scripts/             # Utility scripts
│   └── run_tests.sh     # Test runner
└── docker-compose.yml
```

## Usage

### Adding New Documents

1. **Via UI**: Upload documents through the web interface
2. **Via API**: 
   ```bash
   curl -X POST -F "file=@document.pdf" http://localhost:8000/upload
   ```
3. **Via File System**: Place files in `data/documents/` and run training pipeline

### Training Pipeline

Process new documents and update the vector database:

```bash
docker-compose --profile training up mlops
```

### Querying Documents

Use the web interface or API:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic of the documents?"}'
```

## Configuration

Edit environment variables in `docker-compose.yml`:

- `OLLAMA_MODEL`: Change LLM model (default: llama3.2)
- `EMBEDDING_MODEL`: Change embedding model
- `CHUNK_SIZE`: Document chunk size for processing
- `CHUNK_OVERLAP`: Overlap between chunks

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm start
```

## Troubleshooting

### Ollama model not found
```bash
docker exec -it ollama ollama pull llama3.2
```

### Port already in use
Change ports in `docker-compose.yml`

### Out of memory
Reduce model size or increase Docker memory limit

## License

MIT License - feel free to use for any purpose

## Contributing

Contributions welcome! Please open an issue or PR.
