"""
Full pipeline test script
Tests: Library -> Patent Upload -> Task Creation -> Analysis
"""
import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000"


async def test_full_pipeline():
    """Test complete workflow"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60) as client:
        print("=" * 60)
        print("Full Pipeline Test")
        print("=" * 60)
        
        # 1. Health check
        print("\n1. Health Check")
        resp = await client.get("/health")
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"   API: {resp.json()['version']}")
        
        # 2. Create library
        print("\n2. Create Library")
        resp = await client.post("/libraries", json={
            "name": "视频编辑技术库",
            "description": "移动端视频编辑相关专利"
        })
        print(f"   Status: {resp.status_code}")
        library = resp.json()
        library_id = library["id"]
        print(f"   Library ID: {library_id}")
        print(f"   Name: {library['name']}")
        
        # 3. List libraries
        print("\n3. List Libraries")
        resp = await client.get("/libraries")
        libraries = resp.json()
        print(f"   Count: {len(libraries)}")
        for lib in libraries:
            print(f"   - {lib['name']} ({lib['patent_count']} patents)")
        
        # 4. Create a patent directly (simulating upload + parse + save)
        print("\n4. Create Patent Document")
        from app.db.database import init_db, close_db
        from app.services.db_service import PatentService
        
        init_db()
        patent = await PatentService.create_patent(
            library_id=library_id,
            title="MOBILE DEVICE VIDEO EDITING SYSTEM",
            application_no="US14/123,456",
            publication_no="US9,716,909 B2",
            ipc="H04N 21/472",
            applicant="Apple Inc.",
            inventors="John Smith, Jane Doe",
            abstract="A system for editing video content on mobile devices...",
            claims="1. A method comprising...\n\n2. The method of claim 1...",
            description="Detailed description of video editing system...",
            quality_score=90
        )
        print(f"   Patent ID: {patent.id}")
        print(f"   Title: {patent.title}")
        print(f"   Library: {patent.library_id}")
        
        # Create another patent for comparison
        patent2 = await PatentService.create_patent(
            library_id=library_id,
            title="PORTABLE VIDEO EDITING APPARATUS",
            application_no="US15/789,012",
            publication_no="US10,123,456 B1",
            ipc="H04N 21/43",
            applicant="Samsung Electronics",
            inventors="Bob Wilson",
            abstract="An apparatus for portable video editing with touch interface...",
            claims="1. An apparatus comprising...",
            description="Description of portable editing apparatus...",
            quality_score=85
        )
        print(f"   Patent 2 ID: {patent2.id}")
        
        await close_db()
        
        # 5. List patents in library
        print("\n5. List Patents")
        resp = await client.get(f"/patents?library_id={library_id}")
        patents = resp.json()
        print(f"   Count: {len(patents)}")
        for p in patents:
            print(f"   - {p['title'][:40]}... (Score: {p['quality_score']})")
        
        # 6. Create analysis task
        print("\n6. Create Analysis Task")
        resp = await client.post("/tasks", json={
            "name": "视频编辑专利相似度分析",
            "library_id": library_id,
            "config": {"threshold": 0.7}
        })
        print(f"   Status: {resp.status_code}")
        task = resp.json()
        task_id = task["id"]
        print(f"   Task ID: {task_id}")
        print(f"   Status: {task['status']}")
        
        # 7. Submit task for analysis
        print("\n7. Submit Task")
        resp = await client.post(f"/tasks/{task_id}/submit", params={
            "target_patent_id": patent.id
        })
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 200:
            task = resp.json()
            print(f"   New Status: {task['status']}")
            print(f"   Progress: {task['progress']}%")
        
        # 8. Get task status (poll a few times)
        print("\n8. Task Status (Polling)")
        for i in range(3):
            await asyncio.sleep(2)
            resp = await client.get(f"/tasks/{task_id}")
            task = resp.json()
            print(f"   Poll {i+1}: {task['status']} ({task['progress']}%)")
            
            if task['status'] in ['completed', 'failed', 'cancelled']:
                break
        
        # 9. Get task result if completed
        if task['status'] == 'completed':
            print("\n9. Analysis Results")
            resp = await client.get(f"/tasks/{task_id}/result")
            if resp.status_code == 200:
                result = resp.json()
                print(f"   Total Compared: {result['total_compared']}")
                print(f"   Successful: {result['successful_compared']}")
                print(f"\n   Top Similar Patents:")
                for r in result['top_results'][:5]:
                    print(f"   {r['rank']}. {r['title'][:40]}...")
                    print(f"      Score: {r['similarity_score']}% | Risk: {r['risk_level']}")
        
        print("\n" + "=" * 60)
        print("Test Completed!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
