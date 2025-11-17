import os
import httpx
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import logging
import uuid

logger = logging.getLogger(__name__)

class RAGEngine:
    """Retrieval Augmented Generation Engine"""
    
    def __init__(self):
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        self.ollama_host = os.getenv("OLLAMA_HOST", "localhost")
        self.ollama_port = int(os.getenv("OLLAMA_PORT", "11434"))
        self.collection_name = "documents"
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        
        self.qdrant_client = None
        self.ollama_url = f"http://{self.ollama_host}:{self.ollama_port}"
    
    async def initialize(self):
        """Initialize Qdrant client and create collection"""
        try:
            self.qdrant_client = QdrantClient(
                host=self.qdrant_host,
                port=self.qdrant_port
            )
            
            # Create collection if it doesn't exist
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Error initializing RAG engine: {e}")
            raise
    
    async def check_services(self) -> Dict[str, bool]:
        """Check if all services are available"""
        services = {
            "qdrant": False,
            "ollama": False,
            "embedding_model": False
        }
        
        # Check Qdrant
        try:
            if self.qdrant_client:
                self.qdrant_client.get_collections()
                services["qdrant"] = True
        except:
            pass
        
        # Check Ollama
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ollama_url}/api/tags", timeout=5.0)
                services["ollama"] = response.status_code == 200
        except:
            pass
        
        # Check embedding model
        try:
            if self.embedding_model:
                services["embedding_model"] = True
        except:
            pass
        
        return services
    
    def _create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for texts"""
        embeddings = self.embedding_model.encode(texts)
        return embeddings.tolist()
    
    async def add_documents(self, chunks: List[Dict], source: str):
        """Add document chunks to vector database"""
        try:
            points = []
            
            for i, chunk in enumerate(chunks):
                # Create embedding
                embedding = self._create_embeddings([chunk["text"]])[0]
                
                # Create point
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "text": chunk["text"],
                        "source": source,
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
            
            logger.info(f"Added {len(points)} chunks from {source}")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    async def _retrieve_context(self, query: str, top_k: int = 3) -> List[Dict]:
        """Retrieve relevant context from vector database"""
        try:
            # Create query embedding
            query_embedding = self._create_embeddings([query])[0]
            
            # Search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k
            )
            
            # Format results
            contexts = []
            for result in search_results:
                contexts.append({
                    "text": result.payload["text"],
                    "source": result.payload["source"],
                    "score": result.score,
                    "chunk_index": result.payload.get("chunk_index", 0)
                })
            
            return contexts
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    async def _generate_answer(self, query: str, contexts: List[Dict]) -> str:
        """Generate answer using Ollama"""
        try:
            # Prepare context
            context_text = "\n\n".join([
                f"[Source: {ctx['source']}]\n{ctx['text']}"
                for ctx in contexts
            ])
            
            # Create prompt
            prompt = f"""Based on the following context, answer the question. If the answer cannot be found in the context, say so.

Context:
{context_text}

Question: {query}

Answer:"""
            
            # Call Ollama API
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": "llama3.2",
                        "prompt": prompt,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "Sorry, I couldn't generate an answer.")
                else:
                    logger.error(f"Ollama API error: {response.status_code}")
                    return "Sorry, the AI service is currently unavailable."
                    
        except httpx.TimeoutException:
            logger.error("Ollama request timed out")
            return "Sorry, the request timed out. Please try again."
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"Sorry, an error occurred: {str(e)}"
    
    async def query(self, question: str, top_k: int = 3) -> Dict:
        """Query documents and generate answer"""
        try:
            # Retrieve relevant contexts
            contexts = await self._retrieve_context(question, top_k)
            
            if not contexts:
                return {
                    "answer": "I couldn't find any relevant information in the documents to answer your question.",
                    "sources": []
                }
            
            # Generate answer
            answer = await self._generate_answer(question, contexts)
            
            # Format sources
            sources = [
                {
                    "source": ctx["source"],
                    "relevance_score": round(ctx["score"], 3),
                    "excerpt": ctx["text"][:200] + "..." if len(ctx["text"]) > 200 else ctx["text"]
                }
                for ctx in contexts
            ]
            
            return {
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error in query: {e}")
            raise
    
    async def get_stats(self) -> Dict:
        """Get statistics about the vector database"""
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            
            return {
                "total_documents": collection_info.points_count,
                "vector_dimension": self.embedding_dim,
                "collection_name": self.collection_name
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "total_documents": 0,
                "vector_dimension": self.embedding_dim,
                "collection_name": self.collection_name
            }
