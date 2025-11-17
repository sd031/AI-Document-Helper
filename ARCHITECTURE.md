# System Architecture

## Overview

The AI Document Helper is a microservices-based application that uses RAG (Retrieval Augmented Generation) to enable users to chat with their documents.

## Architecture Diagram

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│              Frontend (React)                        │
│  - Modern UI with TailwindCSS                       │
│  - Document upload interface                        │
│  - Chat interface                                   │
│  - Real-time status monitoring                      │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              Backend (FastAPI)                       │
│  - REST API endpoints                               │
│  - Document processing                              │
│  - RAG engine                                       │
│  - Query handling                                   │
└──────┬────────────────┬─────────────────────────────┘
       │                │
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│   Qdrant    │  │   Ollama    │
│  (Vector    │  │    (LLM)    │
│   Database) │  │             │
└─────────────┘  └─────────────┘
       ▲
       │
┌──────┴──────────────────────────────────────────────┐
│         MLOps Training Pipeline                      │
│  - Document ingestion                               │
│  - Text extraction                                  │
│  - Chunking                                         │
│  - Embedding generation                             │
│  - Vector indexing                                  │
└─────────────────────────────────────────────────────┘
```

## Components

### 1. Frontend (React + TailwindCSS)

**Technology Stack:**
- React 18
- TailwindCSS for styling
- Axios for API calls
- Lucide React for icons

**Responsibilities:**
- User interface for document upload
- Chat interface for querying documents
- Display of answers with source citations
- System health monitoring
- Document management

**Key Features:**
- Responsive design
- Real-time status updates
- File upload with drag-and-drop
- Message history
- Source highlighting

### 2. Backend (FastAPI)

**Technology Stack:**
- FastAPI (Python)
- Uvicorn (ASGI server)
- Pydantic for data validation
- AsyncIO for concurrent operations

**Responsibilities:**
- API endpoint management
- Request validation
- Document processing orchestration
- RAG query handling
- Error handling and logging

**Key Endpoints:**
- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /upload` - Upload documents
- `POST /query` - Query documents
- `GET /documents` - List documents
- `DELETE /documents/{filename}` - Delete document
- `GET /stats` - System statistics

### 3. RAG Engine

**Components:**

**a. Document Processor**
- Extracts text from PDF, DOCX, TXT, MD files
- Splits text into overlapping chunks
- Preserves document metadata

**b. Embedding Model**
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Dimension: 384
- Fast and efficient for semantic search

**c. Vector Database (Qdrant)**
- Stores document embeddings
- Enables similarity search
- Supports filtering and metadata

**d. LLM (Ollama)**
- Model: llama3.2 (configurable)
- Generates natural language answers
- Context-aware responses

**RAG Workflow:**
1. User submits a question
2. Question is embedded using the same model
3. Similar chunks are retrieved from Qdrant
4. Retrieved chunks are used as context
5. LLM generates answer based on context
6. Answer and sources are returned to user

### 4. Vector Database (Qdrant)

**Features:**
- High-performance vector similarity search
- Supports filtering and metadata
- REST and gRPC APIs
- Persistent storage

**Configuration:**
- Collection: "documents"
- Distance metric: Cosine similarity
- Vector dimension: 384

### 5. LLM Service (Ollama)

**Features:**
- Local LLM inference
- No external API dependencies
- Privacy-preserving
- Multiple model support

**Supported Models:**
- llama3.2 (default)
- mistral
- codellama
- And many others

### 6. MLOps Training Pipeline

**Technology Stack:**
- Python 3.11
- sentence-transformers
- Qdrant client
- Document processing libraries

**Workflow:**
1. Scan document directories
2. Process each document:
   - Extract text
   - Split into chunks
   - Generate embeddings
3. Index chunks in Qdrant
4. Log statistics

**Execution:**
- Triggered manually via Docker Compose
- Can be scheduled with cron
- Supports incremental updates

## Data Flow

### Document Upload Flow

```
User uploads file
    ↓
Frontend sends to /upload
    ↓
Backend validates file type
    ↓
File saved to disk
    ↓
Document processor extracts text
    ↓
Text split into chunks
    ↓
Embeddings generated
    ↓
Chunks indexed in Qdrant
    ↓
Success response to user
```

### Query Flow

```
User asks question
    ↓
Frontend sends to /query
    ↓
Question embedded
    ↓
Similarity search in Qdrant
    ↓
Top-k relevant chunks retrieved
    ↓
Context prepared for LLM
    ↓
LLM generates answer
    ↓
Answer + sources returned
    ↓
Displayed in UI
```

## Scalability Considerations

### Current Architecture
- Single-node deployment
- Suitable for small to medium workloads
- All services on one machine

### Scaling Options

**Horizontal Scaling:**
- Multiple backend instances behind load balancer
- Qdrant cluster for distributed vector search
- Separate Ollama instances for LLM inference

**Vertical Scaling:**
- Increase container resources
- Use larger LLM models
- Increase Qdrant memory

**Optimization:**
- Cache frequently asked questions
- Batch document processing
- Implement rate limiting
- Use CDN for frontend

## Security Considerations

### Current Implementation
- CORS enabled for development
- No authentication (suitable for local use)
- File type validation
- Input sanitization

### Production Recommendations
- Add authentication (JWT, OAuth)
- Implement rate limiting
- Use HTTPS
- Restrict CORS origins
- Add API key management
- Implement user quotas
- Scan uploaded files for malware
- Encrypt sensitive data

## Monitoring and Observability

### Health Checks
- Service availability checks
- Component status monitoring
- Database connectivity

### Metrics to Monitor
- Request latency
- Document processing time
- Query response time
- Vector database size
- LLM inference time
- Error rates

### Logging
- Structured logging with timestamps
- Log levels: INFO, WARNING, ERROR
- Request/response logging
- Error stack traces

## Deployment

### Development
```bash
docker-compose up -d
```

### Production
- Use production-grade ASGI server (Gunicorn + Uvicorn)
- Set up reverse proxy (Nginx)
- Configure SSL/TLS
- Use environment variables for secrets
- Set up monitoring (Prometheus, Grafana)
- Configure backups for Qdrant data

## Technology Choices

### Why FastAPI?
- High performance
- Automatic API documentation
- Type safety with Pydantic
- Async support
- Easy to learn and use

### Why Qdrant?
- Purpose-built for vector search
- High performance
- Easy to deploy
- Good documentation
- Active development

### Why Ollama?
- Local inference (privacy)
- No API costs
- Easy model management
- Good performance
- Multiple model support

### Why React?
- Component-based architecture
- Large ecosystem
- Good performance
- Easy to maintain
- Wide adoption

## Future Enhancements

1. **Multi-user Support**
   - User authentication
   - Document isolation
   - User-specific collections

2. **Advanced Features**
   - Conversation history
   - Follow-up questions
   - Document summarization
   - Multi-language support

3. **Performance**
   - Query caching
   - Batch processing
   - GPU acceleration for embeddings

4. **Integration**
   - Cloud storage (S3, GCS)
   - Webhook notifications
   - API integrations
   - Export functionality

5. **Analytics**
   - Usage statistics
   - Popular queries
   - Document insights
   - User behavior tracking
