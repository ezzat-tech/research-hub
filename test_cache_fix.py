#!/usr/bin/env python3
"""
Test script to verify the cache fix for PDF download
"""

import asyncio
import httpx

async def test_cache_fix():
    """Test that the PDF endpoint is no longer being called"""
    print("🧪 Testing Cache Fix for PDF Download")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    try:
        print("1️⃣ Testing that PDF endpoint is removed...")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{base_url}/api/download-pdf",
                json={"topic": "test"}
            )
            
            if response.status_code == 404:
                print("✅ PDF endpoint correctly removed (404 Not Found)")
                print("   This is expected - the endpoint no longer exists")
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                print(f"   Response: {response.text}")
        
        print("\n2️⃣ Testing server health...")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/api/health")
            
            if response.status_code == 200:
                print("✅ Server is running normally")
            else:
                print(f"❌ Server health check failed: {response.status_code}")
        
        print("\n🎉 Cache fix test completed!")
        print("\n📋 What to do now:")
        print("   1. Restart your browser or clear cache (Ctrl+F5)")
        print("   2. Go to http://localhost:8000")
        print("   3. Generate a research report")
        print("   4. Click 'Download PDF'")
        print("   5. You should see: 'Generating PDF using client-side method...'")
        print("   6. Print dialog should open (no 404 error)")
        
        print("\n🎯 Expected Behavior:")
        print("   ✅ No more 404 errors")
        print("   ✅ Client-side PDF generation")
        print("   ✅ Print dialog opens")
        print("   ✅ Professional PDF formatting")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing Cache Fix for PDF Download")
    print("Make sure the server is running: python start.py")
    print("=" * 50)
    
    asyncio.run(test_cache_fix())
