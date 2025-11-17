# Quick Start Guide

Get the AI Document Helper running in 5 minutes!

## Prerequisites

- Docker Desktop installed and running
- At least 8GB RAM available
- 10GB free disk space

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run setup script
./scripts/setup.sh
```

This will:
1. Build all Docker images
2. Start all services
3. Pull the LLM model
4. Run the training pipeline with sample documents

### Option 2: Manual Setup

```bash
# 1. Build images
docker-compose build

# 2. Start services
docker-compose up -d

# 3. Pull LLM model
docker exec ollama ollama pull llama3.2

# 4. Run training
docker-compose --profile training up mlops
```

### Option 3: Using Makefile

```bash
make setup
```

## Verify Installation

Run the test suite:

```bash
./scripts/run_tests.sh
```

Or using Make:

```bash
make test
```

## Access the Application

Once setup is complete:

- **Web UI**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## First Steps

### 1. Open the Web Interface

Navigate to http://localhost:3000 in your browser.

### 2. Try Sample Documents

The system comes pre-loaded with sample documents about:
- Artificial Intelligence basics
- Python programming
- Docker fundamentals

### 3. Ask Questions

Try these sample questions:

- "What is machine learning?"
- "How do I create a Python function?"
- "What are the benefits of Docker?"
- "Explain deep learning"

### 4. Upload Your Own Documents

Click the "Upload Document" button and select:
- PDF files
- Text files (.txt)
- Word documents (.docx)
- Markdown files (.md)

### 5. Query Your Documents

After uploading, ask questions about your documents!

## Common Commands

### Start Services
```bash
docker-compose up -d
# or
make start
```

### Stop Services
```bash
docker-compose down
# or
make stop
```

### View Logs
```bash
docker-compose logs -f
# or
make logs
```

### Restart Services
```bash
docker-compose restart
# or
make restart
```

### Process New Documents
```bash
docker-compose --profile training up mlops
# or
make train
```

## Troubleshooting

### Services Won't Start

Check if ports are available:
```bash
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :6333  # Qdrant
lsof -i :11434 # Ollama
```

### Ollama Model Not Found

Pull the model manually:
```bash
docker exec ollama ollama pull llama3.2
# or
make pull-model
```

### Out of Memory

Increase Docker memory limit in Docker Desktop settings to at least 8GB.

### Slow Responses

First query after startup may be slow as the model loads. Subsequent queries will be faster.

### Frontend Can't Connect to Backend

Check if backend is running:
```bash
curl http://localhost:8000/health
```

## Next Steps

- Read the [README.md](README.md) for detailed documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- See [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute

## Getting Help

- Check existing documentation
- Review Docker logs: `docker-compose logs`
- Open an issue on GitHub

## Clean Up

To completely remove all containers and data:

```bash
docker-compose down -v
# or
make clean
```

**Note**: This will delete all uploaded documents and indexed data!

## Performance Tips

1. **First Run**: Initial setup takes 5-10 minutes due to model download
2. **Warm Up**: First query may take 30-60 seconds as the model loads
3. **Optimal**: After warm-up, queries typically take 5-15 seconds
4. **Documents**: Larger documents take longer to process

## System Requirements

### Minimum
- 4 CPU cores
- 8GB RAM
- 10GB disk space

### Recommended
- 8 CPU cores
- 16GB RAM
- 20GB disk space

## What's Included

- ✅ Modern React UI
- ✅ FastAPI backend
- ✅ RAG implementation
- ✅ Vector database (Qdrant)
- ✅ Local LLM (Ollama)
- ✅ MLOps pipeline
- ✅ Sample documents
- ✅ Test suite
- ✅ Complete documentation

Enjoy using AI Document Helper! 🚀
