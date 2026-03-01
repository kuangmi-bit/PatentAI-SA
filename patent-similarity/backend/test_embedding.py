"""
Test script for Kimi embedding and vector store
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services import ZhipuClient, PatentEmbedder, get_vector_store
from app.core.config import settings


async def test_embedding():
    """Test Zhipu embedding"""
    print("\n" + "="*60)
    print("Testing Zhipu Embedding")
    print("="*60)
    
    if not settings.zhipu_api_key:
        print("\n[SKIP] Zhipu API key not configured")
        print("Please set ZHIPU_API_KEY in .env file")
        return False
    
    client = ZhipuClient()
    
    try:
        # Test single embedding
        text = "一种视频编辑方法，包括获取视频数据、进行剪辑处理、输出编辑后的视频。"
        print(f"\nInput text: {text[:50]}...")
        
        embedding = await client.create_embedding(text)
        print(f"[OK] Embedding created with Zhipu")
        print(f"  Model: {settings.zhipu_embedding_model}")
        print(f"  Dimensions: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")
        
        # Test batch embedding
        texts = [
            "视频编辑系统和方法",
            "多媒体处理技术",
            "社交媒体分享功能"
        ]
        
        print(f"\nBatch embedding {len(texts)} texts with Zhipu...")
        embeddings = await client.create_embeddings(texts)
        print(f"[OK] Batch embeddings created: {len(embeddings)}")
        print(f"  Dimensions per embedding: {len(embeddings[0])}")
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Embedding failed: {e}")
        return False
    finally:
        await client.close()


async def test_vector_store():
    """Test vector store"""
    print("\n" + "="*60)
    print("Testing Vector Store")
    print("="*60)
    
    store = get_vector_store()
    
    try:
        # Add test patents
        test_patents = [
            {
                "id": "patent_001",
                "embedding": [0.1] * 1536,  # Mock embedding
                "metadata": {
                    "title": "视频编辑方法",
                    "applicant": "公司A",
                    "ipc": "H04N21/43"
                },
                "document": "一种视频编辑方法..."
            },
            {
                "id": "patent_002",
                "embedding": [0.2] * 1536,
                "metadata": {
                    "title": "多媒体处理系统",
                    "applicant": "公司B",
                    "ipc": "G06F17/30"
                },
                "document": "一种多媒体处理系统..."
            },
            {
                "id": "patent_003",
                "embedding": [0.15] * 1536,
                "metadata": {
                    "title": "视频剪辑装置",
                    "applicant": "公司C",
                    "ipc": "H04N5/93"
                },
                "document": "一种视频剪辑装置..."
            }
        ]
        
        print(f"\nAdding {len(test_patents)} test patents...")
        count = await store.add_patents_batch(test_patents)
        print(f"[OK] Added {count} patents")
        
        # Search
        query_embedding = [0.12] * 1536  # Close to patent_001 and patent_003
        print(f"\nSearching with query embedding...")
        results = await store.search_similar(query_embedding, top_k=3)
        
        print(f"[OK] Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['id']} (score: {result['score']:.4f})")
            print(f"     Title: {result['metadata'].get('title')}")
        
        # Count
        total = await store.count()
        print(f"\n[OK] Total patents in store: {total}")
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Vector store test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_patent_embedder():
    """Test patent embedder"""
    print("\n" + "="*60)
    print("Testing Patent Embedder (Zhipu)")
    print("="*60)
    
    if not settings.zhipu_api_key:
        print("\n[SKIP] Zhipu API key not configured")
        return False
    
    embedder = PatentEmbedder()
    
    try:
        # Test patent embedding
        patent_data = {
            "title": "移动端视频编辑和分享系统",
            "abstract": "一种用于社交媒体的移动视频编辑和分享系统，允许用户使用智能手机创建、编辑和发布视频文件。",
            "claims": [
                "一种移动视频编辑方法，包括：接收视频数据；对视频进行剪辑处理；添加音乐轨道；输出编辑后的视频。",
                "根据权利要求1所述的方法，还包括接收音量控制配置文件。"
            ],
            "description": "本发明涉及社交媒体内容，特别是适用于使用移动计算设备创建、编辑和发布视频文件的移动视频编辑和分享系统。"
        }
        
        print(f"\nEmbedding patent: {patent_data['title']}")
        embeddings = await embedder.embed_patent(
            title=patent_data["title"],
            abstract=patent_data["abstract"],
            claims=patent_data["claims"],
            description=patent_data["description"]
        )
        
        print(f"[OK] Patent embedded successfully with Zhipu")
        print(f"  Model: {settings.zhipu_embedding_model} ({settings.zhipu_embedding_dimensions}d)")
        for section, emb in embeddings.items():
            print(f"  {section}: {len(emb)} dimensions")
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Patent embedder test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await embedder.close()


async def main():
    """Main test function"""
    print("PatentAI Embedding & Vector Store Test")
    print("=" * 60)
    
    results = []
    
    # Test 1: Kimi Embedding
    results.append(("Kimi Embedding", await test_embedding()))
    
    # Test 2: Vector Store
    results.append(("Vector Store", await test_vector_store()))
    
    # Test 3: Patent Embedder
    results.append(("Patent Embedder", await test_patent_embedder()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")
    
    all_passed = all(r[1] for r in results)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    asyncio.run(main())
