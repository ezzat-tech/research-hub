#!/usr/bin/env python3
"""
Test script to verify the AI Research Agent setup
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test if environment variables are properly set"""
    print("🔍 Testing environment setup...")
    
    # Load environment variables
    load_dotenv()
    
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not openrouter_key or openrouter_key == "your_openrouter_api_key_here":
        print("❌ OPENROUTER_API_KEY not set or using placeholder value")
        print("   Please set your OpenRouter API key in the .env file")
        return False
    else:
        print("✅ OPENROUTER_API_KEY is set")
    
    if not tavily_key or tavily_key == "your_tavily_api_key_here":
        print("❌ TAVILY_API_KEY not set or using placeholder value")
        print("   Please set your Tavily API key in the .env file")
        return False
    else:
        print("✅ TAVILY_API_KEY is set")
    
    return True

def test_dependencies():
    """Test if required packages are installed"""
    print("\n📦 Testing dependencies...")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "httpx",
        "python-dotenv",
        "pydantic"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def test_file_structure():
    """Test if all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        "main.py",
        "frontend/index.html",
        "frontend/style.css", 
        "frontend/script.js",
        "requirements.txt",
        "README.md"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} is missing")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n💡 Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 AI Research Agent Setup Test")
    print("=" * 40)
    
    tests = [
        test_file_structure,
        test_dependencies,
        test_environment
    ]
    
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 To start the application, run:")
        print("   python main.py")
        print("\n🌐 Then open http://localhost:8000 in your browser")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
