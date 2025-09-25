#!/usr/bin/env python3
"""
Startup script for Research Hub
"""

import uvicorn
import os

def main():
    """Start the Research Hub server"""
    print("🚀 Starting Research Hub...")
    print("=" * 40)
    
    # Try to load environment variables, but don't fail if .env has issues
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception as e:
        print(f"⚠️  Warning: Could not load .env file: {e}")
        print("   Make sure to set environment variables manually or fix the .env file")
    
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
    
    print("\n🌐 Server will be available at: http://localhost:8001")
    print("📖 Open the URL in your browser to use Research Hub")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 40)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,  # Changed to match main.py
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()