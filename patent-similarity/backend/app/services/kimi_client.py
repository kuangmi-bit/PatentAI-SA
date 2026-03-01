"""
Kimi API Client (Moonshot AI)
Handles text embedding and chat completion for patent analysis
"""
import asyncio
from typing import List, Dict, Optional, AsyncGenerator
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class KimiError(Exception):
    """Kimi API error"""
    pass


class KimiClient:
    """
    Client for Kimi (Moonshot AI) API
    
    Features:
    - Text embedding for patent similarity
    - Chat completion for patent analysis
    - Async support with retry logic
    """
    
    def __init__(self):
        self.api_key = settings.kimi_api_key
        self.base_url = settings.kimi_base_url.rstrip('/')
        self.model = settings.kimi_model
        self.embedding_model = settings.kimi_embedding_model
        
        if not self.api_key:
            logger.warning("Kimi API key not configured")
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def create_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """
        Create embeddings for text list
        
        Args:
            texts: List of texts to embed
            model: Embedding model name (default: moonshot-v1-embedding)
            
        Returns:
            List of embedding vectors
            
        Raises:
            KimiError: If API call fails
        """
        if not self.api_key:
            raise KimiError("Kimi API key not configured")
        
        model = model or self.embedding_model
        
        # Kimi embedding API has limit on input length
        # Truncate texts if too long
        processed_texts = []
        for text in texts:
            # Limit to ~8000 tokens (roughly 24000 chars for Chinese)
            if len(text) > 24000:
                text = text[:24000]
            processed_texts.append(text)
        
        logger.info(
            "Creating embeddings",
            model=model,
            text_count=len(processed_texts),
            avg_length=sum(len(t) for t in processed_texts) // len(processed_texts)
        )
        
        try:
            response = await self.client.post(
                "/embeddings",
                json={
                    "model": model,
                    "input": processed_texts
                }
            )
            response.raise_for_status()
            
            data = response.json()
            embeddings = [item["embedding"] for item in data["data"]]
            
            logger.info(
                "Embeddings created successfully",
                count=len(embeddings),
                dimensions=len(embeddings[0]) if embeddings else 0
            )
            
            return embeddings
            
        except httpx.HTTPStatusError as e:
            logger.error(
                "Kimi API HTTP error",
                status=e.response.status_code,
                response=e.response.text
            )
            raise KimiError(f"Kimi API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error("Kimi API error", error=str(e))
            raise KimiError(f"Failed to create embeddings: {e}")
    
    async def create_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """
        Create embedding for single text
        
        Args:
            text: Text to embed
            model: Embedding model name
            
        Returns:
            Embedding vector
        """
        embeddings = await self.create_embeddings([text], model)
        return embeddings[0]
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Create chat completion
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Chat model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        if not self.api_key:
            raise KimiError("Kimi API key not configured")
        
        model = model or self.model
        
        logger.info(
            "Creating chat completion",
            model=model,
            message_count=len(messages)
        )
        
        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    **({"max_tokens": max_tokens} if max_tokens else {})
                }
            )
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            logger.info(
                "Chat completion successful",
                prompt_tokens=data["usage"]["prompt_tokens"],
                completion_tokens=data["usage"]["completion_tokens"]
            )
            
            return content
            
        except httpx.HTTPStatusError as e:
            logger.error(
                "Kimi API HTTP error",
                status=e.response.status_code,
                response=e.response.text
            )
            raise KimiError(f"Kimi API error: {e.response.status_code}")
        except Exception as e:
            logger.error("Kimi API error", error=str(e))
            raise KimiError(f"Failed to create chat completion: {e}")
    
    async def analyze_patent_similarity(
        self,
        target_patent: str,
        comparison_patent: str
    ) -> Dict:
        """
        Analyze similarity between two patents using LLM
        
        Args:
            target_patent: Target patent text
            comparison_patent: Patent to compare against
            
        Returns:
            Dict with similarity analysis
        """
        prompt = f"""作为专利分析专家，请分析以下两份专利的相似度。

目标专利：
{target_patent[:2000]}

对比专利：
{comparison_patent[:2000]}

请从以下维度分析：
1. 技术领域相似度（0-100分）
2. 技术问题相似度（0-100分）
3. 技术方案相似度（0-100分）
4. 侵权风险评估（高/中/低）
5. 相似的技术特征列表

请以JSON格式返回：
{{
    "technical_field_score": 分数,
    "technical_problem_score": 分数,
    "technical_solution_score": 分数,
    "overall_similarity": 综合相似度,
    "risk_level": "高/中/低",
    "matched_features": ["特征1", "特征2"],
    "analysis": "详细分析说明"
}}"""

        messages = [
            {"role": "system", "content": "你是一个专业的专利分析专家，擅长评估专利相似度和侵权风险。"},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat_completion(messages, temperature=0.2)
        
        # Try to parse JSON from response
        import json
        import re
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
                return result
            except json.JSONDecodeError:
                pass
        
        # Fallback: return raw response
        return {
            "analysis": response,
            "overall_similarity": 50,
            "risk_level": "中"
        }


class PatentEmbedder:
    """
    Patent text embedder with chunking support
    Handles long patent documents by splitting into chunks
    """
    
    def __init__(self, kimi_client: Optional[KimiClient] = None):
        self.kimi = kimi_client or KimiClient()
        self.chunk_size = 2000  # Characters per chunk
        self.chunk_overlap = 200  # Overlap between chunks
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Long text to split
            
        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence ending
                for i in range(min(end + 100, len(text)) - 1, end - 1, -1):
                    if text[i] in '.。!！?？\n':
                        end = i + 1
                        break
            
            chunks.append(text[start:end].strip())
            start = end - self.chunk_overlap
        
        return chunks
    
    async def embed_patent(
        self,
        title: str,
        abstract: str,
        claims: List[str],
        description: Optional[str] = None
    ) -> Dict[str, List[float]]:
        """
        Create embeddings for patent sections
        
        Args:
            title: Patent title
            abstract: Patent abstract
            claims: List of claims
            description: Patent description
            
        Returns:
            Dict with embeddings for each section
        """
        result = {}
        
        # Embed title + abstract
        title_abstract = f"标题：{title}\n摘要：{abstract}"
        result["title_abstract"] = await self.kimi.create_embedding(title_abstract)
        
        # Embed claims
        claims_text = "\n".join([f"权利要求{i+1}：{c}" for i, c in enumerate(claims[:10])])
        result["claims"] = await self.kimi.create_embedding(claims_text)
        
        # Embed description (chunked if long)
        if description:
            chunks = self._chunk_text(description)
            chunk_embeddings = await self.kimi.create_embeddings(chunks)
            # Average chunk embeddings
            import numpy as np
            avg_embedding = np.mean(chunk_embeddings, axis=0).tolist()
            result["description"] = avg_embedding
        
        return result
    
    async def close(self):
        """Close client"""
        await self.kimi.close()


# Convenience functions
async def create_patent_embedding(patent_text: str) -> List[float]:
    """
    Create embedding for patent text
    
    Args:
        patent_text: Full patent text
        
    Returns:
        Embedding vector
    """
    client = KimiClient()
    try:
        embedding = await client.create_embedding(patent_text)
        return embedding
    finally:
        await client.close()


async def create_patent_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Create embeddings for multiple patents
    
    Args:
        texts: List of patent texts
        
    Returns:
        List of embedding vectors
    """
    client = KimiClient()
    try:
        embeddings = await client.create_embeddings(texts)
        return embeddings
    finally:
        await client.close()
