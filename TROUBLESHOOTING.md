# Troubleshooting Guide

## Common Issues and Solutions

### 1. Backend Import Error: `cached_download`

**Error Message:**
```
ImportError: cannot import name 'cached_download' from 'huggingface_hub'
```

**Cause:** Version incompatibility between `sentence-transformers` and `huggingface_hub`.

**Solution:** Already fixed in the current version. The requirements files have been updated to use compatible versions:
- `sentence-transformers==2.3.1`
- `huggingface-hub==0.20.0`

If you encounter this, rebuild the containers:
```bash
docker-compose build backend mlops
docker-compose up -d
```

### 2. Services Won't Start

**Check if ports are in use:**
```bash
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :6333  # Qdrant
lsof -i :11434 # Ollama
```

**Solution:** Stop conflicting services or change ports in `docker-compose.yml`

### 3. Ollama Model Not Found

**Error:** Model not available when querying

**Solution:**
```bash
docker exec ollama ollama pull llama3.2
```

### 4. First Query Times Out

**Symptom:** First query returns "request timed out"

**Cause:** Ollama needs to load the model into memory on first use

**Solution:** This is normal. Try the query again - subsequent queries will be faster.

### 5. Out of Memory

**Symptom:** Containers crash or system becomes slow

**Solution:**
1. Open Docker Desktop
2. Go to Settings → Resources
3. Increase Memory to at least 8GB
4. Click "Apply & Restart"

### 6. Frontend Can't Connect to Backend

**Check backend health:**
```bash
curl http://localhost:8000/health
```

**View logs:**
```bash
docker-compose logs backend
```

**Solution:** Ensure backend is running and healthy

### 7. No Documents Indexed

**Check stats:**
```bash
curl http://localhost:8000/stats
```

**Solution:** Run the training pipeline:
```bash
docker-compose --profile training up mlops
```

### 8. Slow Query Responses

**Causes:**
- First query (model loading): 30-60 seconds
- Large documents
- Limited CPU/RAM

**Solutions:**
- Wait for model warm-up
- Use smaller documents
- Increase Docker resources

### 9. Build Failures

**Network timeout during build:**
```bash
# Try building again
docker-compose build

# Or build with no cache
docker-compose build --no-cache
```

### 10. Container Restart Loops

**View logs:**
```bash
docker-compose logs [service-name]
```

**Common causes:**
- Missing dependencies
- Port conflicts
- Configuration errors

**Solution:** Check logs for specific error messages

## Debugging Commands

### View All Logs
```bash
docker-compose logs -f
```

### View Specific Service Logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f ollama
docker-compose logs -f qdrant
```

### Check Service Status
```bash
docker-compose ps
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild Specific Service
```bash
docker-compose build [service-name]
docker-compose up -d [service-name]
```

### Access Container Shell
```bash
# Backend
docker-compose exec backend bash

# Frontend
docker-compose exec frontend sh

# Ollama
docker exec -it ollama bash
```

### Check API Health
```bash
curl http://localhost:8000/health
```

### Test Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI?"}'
```

### Check Qdrant
```bash
# List collections
curl http://localhost:6333/collections

# Get collection info
curl http://localhost:6333/collections/documents
```

## Clean Start

If all else fails, clean everything and start fresh:

```bash
# Stop and remove everything
docker-compose down -v

# Remove images (optional)
docker-compose down --rmi all

# Rebuild and start
docker-compose build
docker-compose up -d

# Pull model
docker exec ollama ollama pull llama3.2

# Run training
docker-compose --profile training up mlops
```

## Performance Optimization

### Increase Timeout for Ollama

Edit `backend/rag_engine.py` and increase the timeout:
```python
async with httpx.AsyncClient(timeout=120.0) as client:  # Increase from 60 to 120
```

### Use Smaller Model

Edit `docker-compose.yml` and change the model:
```yaml
environment:
  - OLLAMA_MODEL=llama3.2:1b  # Smaller, faster model
```

Then pull the new model:
```bash
docker exec ollama ollama pull llama3.2:1b
```

### Reduce Chunk Size

Edit `backend/document_processor.py`:
```python
def __init__(self, chunk_size: int = 300, chunk_overlap: int = 30):  # Smaller chunks
```

## Getting Help

1. **Check Documentation:**
   - README.md
   - GETTING_STARTED.md
   - ARCHITECTURE.md

2. **View Logs:**
   ```bash
   docker-compose logs -f
   ```

3. **Run Tests:**
   ```bash
   ./scripts/run_tests.sh
   ```

4. **Check GitHub Issues:**
   - Search for similar problems
   - Open a new issue with logs

## Known Limitations

1. **First Query Delay:** Model loading takes 30-60 seconds
2. **Memory Usage:** Requires at least 8GB RAM
3. **CPU-Only:** No GPU acceleration by default
4. **Single User:** No authentication or multi-user support
5. **Local Only:** Not configured for production deployment

## Success Indicators

Your system is working correctly if:

- ✅ All services show "Up" in `docker-compose ps`
- ✅ Health check returns all services as healthy
- ✅ Training pipeline completes without errors
- ✅ Queries return answers (after model warm-up)
- ✅ Frontend loads at http://localhost:3000
- ✅ Tests pass (most of them)

## Still Having Issues?

1. Check this troubleshooting guide
2. Review the logs carefully
3. Try a clean restart
4. Open an issue with:
   - Error messages
   - Logs
   - Steps to reproduce
   - System information
