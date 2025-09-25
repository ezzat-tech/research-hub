#!/usr/bin/env python3
"""
Debug script to test the research functionality
"""

import asyncio
import os
from dotenv import load_dotenv
from main import OpenRouterClient, TavilyClient

async def test_research():
    """Test the research functionality step by step"""
    print("🔍 Testing AI Research Agent Components")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check API keys
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    print(f"✅ OPENROUTER_API_KEY: {'Set' if openrouter_key and openrouter_key != 'your_openrouter_api_key_here' else 'Not set'}")
    print(f"✅ TAVILY_API_KEY: {'Set' if tavily_key and tavily_key != 'your_tavily_api_key_here' else 'Not set'}")
    
    print("\n🤖 Using FREE DeepSeek models:")
    print("   - deepseek/deepseek-chat (Primary - Great for research planning)")
    print("   - deepseek/deepseek-coder (Fallback - Excellent reasoning)")
    print("   - meta-llama/llama-3.1-8b-instruct (Fallback - Reliable)")
    print("   - microsoft/phi-3-medium-128k-instruct (Fallback - Fast)")
    
    if not openrouter_key or openrouter_key == "your_openrouter_api_key_here":
        print("❌ OpenRouter API key not set properly")
        return
    
    if not tavily_key or tavily_key == "your_tavily_api_key_here":
        print("❌ Tavily API key not set properly")
        return
    
    # Initialize clients
    print("\n🚀 Initializing API clients...")
    openrouter_client = OpenRouterClient(openrouter_key)
    tavily_client = TavilyClient(tavily_key)
    
    # Test topic
    test_topic = "Artificial Intelligence in Healthcare"
    print(f"\n📝 Testing with topic: {test_topic}")
    
    try:
        # Step 1: Test research plan generation
        print("\n1️⃣ Testing research plan generation...")
        research_questions = await openrouter_client.generate_research_plan(test_topic)
        print(f"✅ Generated {len(research_questions)} research questions:")
        for i, q in enumerate(research_questions, 1):
            print(f"   {i}. {q}")
        
        # Step 2: Test web search
        print("\n2️⃣ Testing web search...")
        if research_questions:
            search_results = await tavily_client.search(research_questions[0], max_results=2)
            print(f"✅ Found {len(search_results)} search results")
            for i, result in enumerate(search_results, 1):
                print(f"   {i}. {result.get('title', 'No title')}")
        
        # Step 3: Test report generation
        print("\n3️⃣ Testing report generation...")
        report = await openrouter_client.generate_report(test_topic, search_results)
        print(f"✅ Generated report ({len(report)} characters)")
        print(f"Preview: {report[:200]}...")
        
        print("\n🎉 All tests passed! The research agent is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_research())
