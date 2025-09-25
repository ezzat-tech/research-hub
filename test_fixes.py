#!/usr/bin/env python3
"""
Test script to verify the fixes for loading button and PDF download
"""

import asyncio
import httpx
import json

async def test_api_endpoints():
    """Test the API endpoints"""
    print("🧪 Testing API Endpoints")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test health endpoint
        print("1️⃣ Testing health endpoint...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/health")
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print("❌ Health endpoint failed")
                return
        
        # Test research endpoint
        print("\n2️⃣ Testing research endpoint...")
        test_data = {"topic": "Artificial Intelligence"}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{base_url}/api/research",
                json=test_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Research endpoint working")
                print(f"   Report length: {len(result.get('report', ''))} characters")
            else:
                print(f"❌ Research endpoint failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return
        
        # Test PDF download endpoint
        print("\n3️⃣ Testing PDF download endpoint...")
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{base_url}/api/download-pdf",
                json=test_data
            )
            
            if response.status_code == 200:
                print("✅ PDF download endpoint working")
                print(f"   Content type: {response.headers.get('content-type', 'unknown')}")
                print(f"   Content length: {len(response.content)} bytes")
            else:
                print(f"❌ PDF download endpoint failed: {response.status_code}")
                print(f"   Error: {response.text}")
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing AI Research Agent Fixes")
    print("Make sure the server is running: python start.py")
    print("=" * 50)
    
    asyncio.run(test_api_endpoints())
