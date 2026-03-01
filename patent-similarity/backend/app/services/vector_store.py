"""
Vector Database Service - In-memory version (MVP)
Note: ChromaDB disabled due to Python 3.14 compatibility
TODO: Re-enable ChromaDB when compatible or migrate to alternative
"""
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import numpy as np

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class VectorStoreError(Exception):
    """Vector store error"""
    pass


class PatentVectorStore:
    """
    In-memory vector store for patent embeddings (MVP)
    
    Features:
    - Store patent embeddings with metadata
    - Cosine similarity search
    - Simple and fast for MVP
    
    Note: Data is lost on restart. For production, use persistent storage.
    """
    
    def __init__(self):
        self.db_path = settings.chroma_db_path
        self.collection_name = settings.collection_name
        
        # In-memory storage
        self._memory_store: Dict[str, Dict] = {}
        
        logger.info("In-memory vector store initialized")
    
    async def add_patent(
        self,
        patent_id: str,
        embedding: List[float],
        metadata: Dict,
        document: Optional[str] = None
    ) -> bool:
        """
        Add patent embedding to store
        
        Args:
            patent_id: Unique patent ID
            embedding: Embedding vector
            metadata: Patent metadata (title, applicant, etc.)
            document: Original text (optional)
            
        Returns:
            True if successful
        """
        try:
            self._memory_store[patent_id] = {
                "id": patent_id,
                "embedding": embedding,
                "metadata": metadata,
                "document": document,
                "added_at": datetime.utcnow().isoformat()
            }
            
            logger.info("Patent added to vector store", patent_id=patent_id)
            return True
            
        except Exception as e:
            logger.error("Failed to add patent", patent_id=patent_id, error=str(e))
            return False
    
    async def add_patents_batch(
        self,
        patents: List[Dict]
    ) -> int:
        """
        Add multiple patents in batch
        
        Args:
            patents: List of patent dicts with 'id', 'embedding', 'metadata'
            
        Returns:
            Number of successfully added patents
        """
        if not patents:
            return 0
        
        try:
            for patent in patents:
                self._memory_store[patent["id"]] = {
                    "id": patent["id"],
                    "embedding": patent["embedding"],
                    "metadata": patent["metadata"],
                    "document": patent.get("document"),
                    "added_at": datetime.utcnow().isoformat()
                }
            
            logger.info("Batch patents added", count=len(patents))
            return len(patents)
            
        except Exception as e:
            logger.error("Failed to add patents batch", error=str(e))
            return 0
    
    async def search_similar(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar patents using cosine similarity
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filters: Metadata filters (optional)
            
        Returns:
            List of similar patents with scores
        """
        try:
            query_vec = np.array(query_embedding)
            
            scores = []
            for patent_id, data in self._memory_store.items():
                # Apply filters
                if filters:
                    match = True
                    for key, value in filters.items():
                        if data["metadata"].get(key) != value:
                            match = False
                            break
                    if not match:
                        continue
                
                # Calculate cosine similarity
                patent_vec = np.array(data["embedding"])
                similarity = np.dot(query_vec, patent_vec) / (
                    np.linalg.norm(query_vec) * np.linalg.norm(patent_vec)
                )
                
                scores.append((patent_id, similarity, data))
            
            # Sort by similarity (descending) and take top_k
            scores.sort(key=lambda x: x[1], reverse=True)
            
            results = []
            for patent_id, score, data in scores[:top_k]:
                results.append({
                    "id": patent_id,
                    "score": float(score),
                    "metadata": data["metadata"],
                    "document": data.get("document")
                })
            
            return results
                
        except Exception as e:
            logger.error("Search failed", error=str(e))
            return []
    
    async def delete_patent(self, patent_id: str) -> bool:
        """
        Delete patent from store
        
        Args:
            patent_id: Patent ID to delete
            
        Returns:
            True if successful
        """
        try:
            if patent_id in self._memory_store:
                del self._memory_store[patent_id]
                logger.info("Patent deleted", patent_id=patent_id)
                return True
            return False
            
        except Exception as e:
            logger.error("Failed to delete patent", patent_id=patent_id, error=str(e))
            return False
    
    async def get_patent(self, patent_id: str) -> Optional[Dict]:
        """
        Get patent by ID
        
        Args:
            patent_id: Patent ID
            
        Returns:
            Patent data or None
        """
        try:
            data = self._memory_store.get(patent_id)
            if data:
                return {
                    "id": data["id"],
                    "metadata": data["metadata"],
                    "document": data.get("document")
                }
            return None
            
        except Exception as e:
            logger.error("Failed to get patent", patent_id=patent_id, error=str(e))
            return None
    
    async def count(self) -> int:
        """Get total number of patents in store"""
        return len(self._memory_store)
    
    async def clear(self):
        """Clear all patents from store"""
        try:
            self._memory_store.clear()
            logger.info("Vector store cleared")
            
        except Exception as e:
            logger.error("Failed to clear store", error=str(e))


# Singleton instance
_vector_store: Optional[PatentVectorStore] = None


def get_vector_store() -> PatentVectorStore:
    """Get vector store singleton"""
    global _vector_store
    if _vector_store is None:
        _vector_store = PatentVectorStore()
    return _vector_store


# Simple alias for task processor
VectorStore = PatentVectorStore
