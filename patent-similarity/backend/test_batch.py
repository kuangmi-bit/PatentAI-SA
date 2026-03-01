"""
Batch import test script
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8000"


async def test_batch_import():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60) as client:
        print("=" * 60)
        print("Batch Import Test")
        print("=" * 60)
        
        # 1. Create library
        print("\n1. Create Library")
        resp = await client.post("/libraries", json={
            "name": "Batch Import Test",
            "description": "Testing batch import"
        })
        lib = resp.json()
        lib_id = lib["id"]
        print(f"   Library ID: {lib_id}")
        
        # 2. Get import template
        print("\n2. Import Template")
        resp = await client.get("/batch/template")
        template = resp.json()
        fields = list(template["template"].keys())
        print(f"   Template fields: {fields}")
        
        # 3. Batch import
        print("\n3. Batch Import")
        patents_data = [
            {
                "title": "SMARTPHONE VIDEO EDITING METHOD",
                "application_no": "CN202410000001",
                "publication_no": "CN111111111A",
                "ipc": "H04N 21/472",
                "applicant": "Huawei",
                "inventors": ["Zhang San", "Li Si"],
                "abstract": "A smartphone video editing method...",
                "claims": ["1. A video editing method...", "2. According to claim 1..."],
                "quality_score": 88
            },
            {
                "title": "PORTABLE MEDIA EDITING DEVICE",
                "application_no": "CN202410000002",
                "publication_no": "CN222222222A",
                "ipc": "H04N 21/43",
                "applicant": "Xiaomi",
                "inventors": ["Wang Wu"],
                "abstract": "Portable media editing device...",
                "quality_score": 85
            }
        ]
        
        resp = await client.post(f"/batch/import/json/{lib_id}", json={
            "patents": patents_data,
            "generate_embeddings": True
        })
        print(f"   Status: {resp.status_code}")
        result = resp.json()
        print(f"   Total: {result['total']}")
        print(f"   Success: {result['success']}")
        print(f"   Failed: {result['failed']}")
        
        # 4. Verify patents in library
        print("\n4. Verify Patents")
        resp = await client.get(f"/patents?library_id={lib_id}")
        patents = resp.json()
        print(f"   Patents in library: {len(patents)}")
        for p in patents:
            print(f"   - {p['title'][:40]}... ({p['applicant']})")
        
        print("\n" + "=" * 60)
        print("Batch Import Test Completed!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_batch_import())
