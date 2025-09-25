#!/usr/bin/env python3
"""
Diagnostic script to identify the 500 error issue
"""

import os
import asyncio
from dotenv import load_dotenv

async def diagnose_issue():
    """Diagnose the 500 error issue"""
    print("🔍 Diagnosing 500 Internal Server Error")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check API keys
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    print("1️⃣ Checking API Keys:")
    print(f"   OPENROUTER_API_KEY: {'✅ Set' if openrouter_key and openrouter_key != 'your_openrouter_api_key_here' else '❌ Not set or placeholder'}")
    print(f"   TAVILY_API_KEY: {'✅ Set' if tavily_key and tavily_key != 'your_tavily_api_key_here' else '❌ Not set or placeholder'}")
    
    if not openrouter_key or openrouter_key == "your_openrouter_api_key_here":
        print("\n❌ ISSUE FOUND: OpenRouter API key not configured!")
        print("   Solution: Set your OpenRouter API key in the .env file")
        return
    
    if not tavily_key or tavily_key == "your_tavily_api_key_here":
        print("\n❌ ISSUE FOUND: Tavily API key not configured!")
        print("   Solution: Set your Tavily API key in the .env file")
        return
    
    # Test OpenRouter connection
    print("\n2️⃣ Testing OpenRouter Connection:")
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "AI Research Agent"
                },
                json={
                    "model": "deepseek/deepseek-chat",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                }
            )
            
            if response.status_code == 200:
                print("   ✅ OpenRouter connection successful")
            else:
                print(f"   ❌ OpenRouter connection failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
    except Exception as e:
        print(f"   ❌ OpenRouter connection error: {str(e)}")
    
    # Test Tavily connection
    print("\n3️⃣ Testing Tavily Connection:")
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": tavily_key,
                    "query": "test",
                    "max_results": 1
                }
            )
            
            if response.status_code == 200:
                print("   ✅ Tavily connection successful")
            else:
                print(f"   ❌ Tavily connection failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
    except Exception as e:
        print(f"   ❌ Tavily connection error: {str(e)}")
    
    print("\n4️⃣ Checking Server Status:")
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/health")
            if response.status_code == 200:
                print("   ✅ Server is running")
            else:
                print(f"   ❌ Server health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Server not running: {str(e)}")
        print("   Solution: Start the server with 'python start.py'")
    
    print("\n🎯 Diagnosis Complete!")
    print("If all checks pass, the issue might be:")
    print("- Rate limiting from API providers")
    print("- Network connectivity issues")
    print("- Model availability issues")

if __name__ == "__main__":
    asyncio.run(diagnose_issue())
