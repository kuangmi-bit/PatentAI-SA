"""
PatentAI Integration Test
Tests all API endpoints to verify frontend-backend connectivity
"""
import asyncio
import httpx

API_BASE = 'http://localhost:8000'


async def integration_test():
    print('=' * 60)
    print('PatentAI Integration Test')
    print('=' * 60)
    
    async with httpx.AsyncClient(base_url=API_BASE) as client:
        # 1. Health Check
        print('\n[1] Health Check')
        try:
            r = await client.get('/health')
            data = r.json()
            print(f'  Status: {data["status"]}')
            print(f'  Version: {data["version"]}')
            print('  [OK] Backend is running')
        except Exception as e:
            print(f'  [FAIL] Connection failed: {e}')
            return
        
        # 2. Create Library
        print('\n[2] Create Library')
        try:
            r = await client.post('/libraries', json={
                'name': 'Integration Test Library',
                'description': 'Integration test library'
            })
            lib = r.json()
            lib_id = lib['id']
            print(f'  Created: {lib["name"]}')
            print(f'  ID: {lib_id}')
            print('  [OK] Library created')
        except Exception as e:
            print(f'  [FAIL] Create failed: {e}')
            return
        
        # 3. List Libraries
        print('\n[3] List Libraries')
        try:
            r = await client.get('/libraries')
            libs = r.json()
            print(f'  Total: {len(libs)} libraries')
            for l in libs[:3]:
                print(f'    - {l["name"]} ({l["patent_count"]} patents)')
            print('  [OK] List retrieved')
        except Exception as e:
            print(f'  [FAIL] List failed: {e}')
        
        # 4. Batch Import
        print('\n[4] Batch Import Patents')
        try:
            r = await client.post(f'/batch/import/json/{lib_id}', json={
                'patents': [
                    {
                        'title': 'Integration Test Patent 1',
                        'application_no': 'CN202410000001',
                        'applicant': 'Test Company',
                        'abstract': 'This is a test patent for integration testing.',
                        'quality_score': 90
                    },
                    {
                        'title': 'Integration Test Patent 2',
                        'application_no': 'CN202410000002',
                        'applicant': 'Test Company',
                        'abstract': 'Another test patent for integration testing.',
                        'quality_score': 85
                    }
                ],
                'generate_embeddings': False
            })
            result = r.json()
            print(f'  Total: {result["total"]}')
            print(f'  Success: {result["success"]}')
            print(f'  Failed: {result["failed"]}')
            print('  [OK] Batch import successful')
        except Exception as e:
            print(f'  [FAIL] Import failed: {e}')
        
        # 5. List Patents
        print('\n[5] List Patents')
        try:
            r = await client.get(f'/patents?library_id={lib_id}')
            patents = r.json()
            print(f'  Total: {len(patents)} patents')
            for p in patents:
                print(f'    - {p["title"]}')
            print('  [OK] Patent list retrieved')
        except Exception as e:
            print(f'  [FAIL] List failed: {e}')
        
        # 6. Create Task
        print('\n[6] Create Analysis Task')
        try:
            r = await client.post('/tasks', json={
                'name': 'Integration Test Task',
                'library_id': lib_id,
                'config': {'threshold': 0.7}
            })
            task = r.json()
            task_id = task['id']
            print(f'  Created: {task["name"]}')
            print(f'  ID: {task_id}')
            print(f'  Status: {task["status"]}')
            print('  [OK] Task created')
        except Exception as e:
            print(f'  [FAIL] Create failed: {e}')
            return
        
        # 7. List Tasks
        print('\n[7] List Tasks')
        try:
            r = await client.get('/tasks')
            tasks = r.json()
            print(f'  Total: {tasks["total"]} tasks')
            for t in tasks['items'][:3]:
                print(f'    - {t["name"]} [{t["status"]}]')
            print('  [OK] Task list retrieved')
        except Exception as e:
            print(f'  [FAIL] List failed: {e}')
        
        # 8. Get Import Template
        print('\n[8] Get Import Template')
        try:
            r = await client.get('/batch/template')
            template = r.json()
            print(f'  Template fields: {list(template["template"].keys())}')
            print('  [OK] Template retrieved')
        except Exception as e:
            print(f'  [FAIL] Get template failed: {e}')
        
        print('\n' + '=' * 60)
        print('Integration test completed!')
        print('=' * 60)


if __name__ == '__main__':
    asyncio.run(integration_test())
