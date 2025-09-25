#!/usr/bin/env python3
"""
Startup script for AI Research Agent
"""

import uvicorn
import os
from dotenv import load_dotenv

def main():
    """Start the AI Research Agent server"""
    print("🚀 Starting AI Research Agent...")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check if API keys are set
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not openrouter_key or openrouter_key == "your_openrouter_api_key_here":
        print("⚠️  Warning: OPENROUTER_API_KEY not set")
        print("   Please set your OpenRouter API key in the .env file")
        print("   Get your key from: https://openrouter.ai/")
    
    if not tavily_key or tavily_key == "your_tavily_api_key_here":
        print("⚠️  Warning: TAVILY_API_KEY not set")
        print("   Please set your Tavily API key in the .env file")
        print("   Get your key from: https://tavily.com/")
    
    print("\n🌐 Server will be available at: http://localhost:8000")
    print("📖 Open the URL in your browser to use the AI Research Agent")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 40)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
