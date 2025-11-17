# Getting Started with AI Document Helper

Welcome! This guide will help you get the AI Document Helper up and running.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [First Run](#first-run)
4. [Using the System](#using-the-system)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)
7. [Next Steps](#next-steps)

## Prerequisites

Before you begin, ensure you have:

### Required
- **Docker Desktop**: [Download here](https://www.docker.com/products/docker-desktop)
- **8GB RAM**: Minimum available memory
- **10GB Disk Space**: For images and models

### Verify Installation
```bash
# Check Docker
docker --version
# Should show: Docker version 20.x.x or higher

# Check Docker Compose
docker-compose --version
# Should show: Docker Compose version 2.x.x or higher
```

## Installation

### Step 1: Navigate to Project Directory

```bash
cd /Users/sandipdas/simple_ai_doument_helper
```

### Step 2: Choose Your Installation Method

#### Option A: Automated Setup (Recommended) ⭐

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run setup
./scripts/setup.sh
```

This will:
- Build all Docker images (~5 minutes)
- Start all services
- Download the LLM model (~2GB, ~5 minutes)
- Process sample documents
- Verify everything works

**Total time**: ~10-15 minutes

#### Option B: Using Makefile

```bash
make setup
```

#### Option C: Manual Step-by-Step

```bash
# 1. Build images
docker-compose build

# 2. Start services
docker-compose up -d

# 3. Wait for services (30 seconds)
sleep 30

# 4. Download LLM model
docker exec ollama ollama pull llama3.2

# 5. Process sample documents
docker-compose --profile training up mlops
```

## First Run

### 1. Verify Services are Running

```bash
docker-compose ps
```

You should see:
- ✅ qdrant (Up)
- ✅ ollama (Up)
- ✅ ai_backend (Up)
- ✅ ai_frontend (Up)

### 2. Check Health

```bash
curl http://localhost:8000/health
```

Should return JSON with all services healthy.

### 3. Open the Web Interface

Open your browser and navigate to:
```
http://localhost:3000
```

You should see the AI Document Helper interface!

## Using the System

### Your First Query

The system comes with pre-loaded sample documents. Try asking:

1. **About AI**:
   - "What is machine learning?"
   - "Explain deep learning"
   - "What are the applications of AI?"

2. **About Python**:
   - "How do I create a Python function?"
   - "What are Python data types?"
   - "Explain Python classes"

3. **About Docker**:
   - "What is a Docker container?"
   - "What are the benefits of Docker?"
   - "Explain Docker vs virtual machines"

### Uploading Your Own Documents

1. Click the **"Upload Document"** button in the sidebar
2. Select a file (PDF, DOCX, TXT, or MD)
3. Wait for processing (usually a few seconds)
4. Start asking questions about your document!

### Tips for Better Results

**Good Questions**:
- ✅ "What is the main topic of the document?"
- ✅ "Explain the concept of X mentioned in the document"
- ✅ "What are the key points about Y?"

**Less Effective**:
- ❌ "Tell me everything" (too broad)
- ❌ Questions about information not in documents
- ❌ Very short questions like "What?"

## Testing

### Quick Test

```bash
# Run all tests
./scripts/run_tests.sh
```

This tests:
- ✅ API endpoints
- ✅ Document upload
- ✅ Query functionality
- ✅ MLOps pipeline
- ✅ Vector database

### Detailed API Tests

```bash
python scripts/test_api.py
```

### Backend Unit Tests

```bash
docker-compose exec backend pytest tests/ -v
```

## Troubleshooting

### Problem: Services won't start

**Check if ports are in use**:
```bash
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :6333  # Qdrant
lsof -i :11434 # Ollama
```

**Solution**: Stop conflicting services or change ports in `docker-compose.yml`

### Problem: "Ollama model not found"

**Solution**: Pull the model manually
```bash
docker exec ollama ollama pull llama3.2
```

### Problem: Out of memory

**Solution**: Increase Docker memory
1. Open Docker Desktop
2. Go to Settings → Resources
3. Increase Memory to at least 8GB
4. Click "Apply & Restart"

### Problem: Slow responses

**Causes**:
- First query after startup (model loading)
- Large documents
- Limited CPU/RAM

**Solutions**:
- Wait for model to warm up (~30 seconds)
- Use smaller documents
- Increase Docker resources

### Problem: Frontend shows "Cannot connect"

**Check backend**:
```bash
curl http://localhost:8000/health
```

**View logs**:
```bash
docker-compose logs backend
```

### Problem: No documents indexed

**Re-run training**:
```bash
docker-compose --profile training up mlops
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f ollama
```

## Common Commands

### Service Management

```bash
# Start services
docker-compose up -d
# or
make start

# Stop services
docker-compose down
# or
make stop

# Restart services
docker-compose restart
# or
make restart

# View status
docker-compose ps
# or
make status
```

### Maintenance

```bash
# View logs
make logs

# Run tests
make test

# Process new documents
make train

# Check stats
make stats

# Clean everything
make clean
```

### Accessing Containers

```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh

# Ollama shell
docker exec -it ollama bash
```

## Understanding the Interface

### Sidebar (Left)
- **System Status**: Shows health of all services
- **Document Count**: Number of indexed chunks
- **Upload Button**: Upload new documents
- **Document List**: Manage uploaded documents

### Main Area (Right)
- **Chat Messages**: Conversation history
- **Input Box**: Type your questions
- **Send Button**: Submit queries

### Message Types
- **Blue**: Your questions
- **White**: AI answers with sources
- **Green**: System success messages
- **Red**: Error messages

## Next Steps

### 1. Explore Sample Documents

Try different questions about the pre-loaded documents to understand the system's capabilities.

### 2. Upload Your Documents

Start with a few small documents (1-10 pages) to test the system.

### 3. Experiment with Queries

Try different types of questions:
- Factual: "What is X?"
- Comparative: "What's the difference between X and Y?"
- Explanatory: "Explain how X works"
- Listing: "What are the benefits of X?"

### 4. Check the Documentation

- **README.md**: Complete user guide
- **ARCHITECTURE.md**: System architecture
- **QUICKSTART.md**: Quick reference
- **PROJECT_SUMMARY.md**: Project overview

### 5. Customize the System

Edit `docker-compose.yml` to:
- Change ports
- Use different LLM models
- Adjust chunk sizes
- Modify environment variables

### 6. Explore the API

Visit http://localhost:8000/docs for interactive API documentation.

### 7. Monitor with Qdrant

Visit http://localhost:6333/dashboard to see the vector database.

## Performance Expectations

### Initial Setup
- Image build: ~5 minutes
- Model download: ~5 minutes
- First startup: ~1 minute

### During Use
- Document upload: ~1-5 seconds per page
- First query: ~30-60 seconds (model loading)
- Subsequent queries: ~5-15 seconds
- Document processing: ~1 second per page

### Optimization Tips
1. Keep documents under 50 pages for best performance
2. Use specific questions rather than broad ones
3. Wait for model warm-up on first query
4. Increase Docker resources if slow

## System Architecture

```
User Browser
    ↓
React Frontend (Port 3000)
    ↓
FastAPI Backend (Port 8000)
    ↓
    ├─→ Qdrant (Vector DB, Port 6333)
    └─→ Ollama (LLM, Port 11434)
```

## Data Flow

1. **Upload**: Document → Backend → Processing → Qdrant
2. **Query**: Question → Backend → Qdrant (search) → Ollama (answer) → User

## Security Notes

### Current Setup (Development)
- ⚠️ No authentication
- ⚠️ CORS enabled for all origins
- ⚠️ Suitable for local use only

### For Production
- ✅ Add authentication
- ✅ Restrict CORS
- ✅ Use HTTPS
- ✅ Add rate limiting
- ✅ Scan uploaded files

## Getting Help

### Documentation
1. Check this guide
2. Read README.md
3. Review ARCHITECTURE.md
4. Check TROUBLESHOOTING section

### Logs
```bash
docker-compose logs -f
```

### Community
- Open an issue on GitHub
- Check existing issues
- Review discussions

## Useful Resources

### Documentation Files
- `README.md` - Main documentation
- `QUICKSTART.md` - Quick reference
- `ARCHITECTURE.md` - Technical details
- `CONTRIBUTING.md` - Development guide
- `PROJECT_SUMMARY.md` - Overview

### API Documentation
- http://localhost:8000/docs - Interactive API docs
- http://localhost:8000/redoc - Alternative API docs

### Dashboards
- http://localhost:3000 - Main UI
- http://localhost:6333/dashboard - Qdrant dashboard

## Success Checklist

Before considering setup complete, verify:

- [ ] All services running (`docker-compose ps`)
- [ ] Health check passes (`curl http://localhost:8000/health`)
- [ ] Frontend loads (http://localhost:3000)
- [ ] Sample documents indexed
- [ ] Can ask questions and get answers
- [ ] Tests pass (`./scripts/run_tests.sh`)

## What's Next?

Now that you're set up:

1. **Explore**: Try the sample documents
2. **Upload**: Add your own documents
3. **Experiment**: Test different queries
4. **Customize**: Adjust settings
5. **Develop**: Extend functionality (see CONTRIBUTING.md)

## Congratulations! 🎉

You now have a fully functional AI document assistant running locally!

**Happy querying!** 🚀

---

**Need help?** Check the documentation or open an issue on GitHub.
