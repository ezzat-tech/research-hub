#!/usr/bin/env python3
"""
Script to help clear cache and test formatting
"""

import webbrowser
import time

def main():
    print("🔧 Cache Clearing and Formatting Test")
    print("=" * 40)
    
    print("📋 Steps to see the formatting changes:")
    print()
    
    print("1️⃣ Clear Browser Cache:")
    print("   • Chrome/Edge: Press Ctrl + Shift + R")
    print("   • Firefox: Press Ctrl + Shift + R")
    print("   • Or: F12 → Right-click refresh → 'Empty Cache and Hard Reload'")
    print()
    
    print("2️⃣ Test Formatting:")
    print("   • Go to: http://localhost:8000/test-formatting")
    print("   • This page shows the new academic formatting")
    print("   • Check if text is Times New Roman and justified")
    print("   • Check if headings are bold and properly spaced")
    print()
    
    print("3️⃣ Test Main App:")
    print("   • Go to: http://localhost:8000")
    print("   • Generate a research report")
    print("   • Check the formatting in the results")
    print()
    
    print("4️⃣ If formatting still doesn't change:")
    print("   • Click 'Force CSS Reload' button on test page")
    print("   • Or try incognito/private browsing mode")
    print("   • Or clear all browser data")
    print()
    
    print("🎯 What you should see:")
    print("   ✅ Times New Roman font for body text")
    print("   ✅ Bold headings with proper spacing")
    print("   ✅ Justified text with paragraph indentation")
    print("   ✅ Professional academic appearance")
    print()
    
    print("🚀 Opening test page in browser...")
    try:
        webbrowser.open("http://localhost:8000/test-formatting")
        print("✅ Test page opened!")
    except:
        print("❌ Could not open browser automatically")
        print("   Please manually go to: http://localhost:8000/test-formatting")
    
    print("\n📝 If you still don't see changes:")
    print("   1. Try incognito/private browsing mode")
    print("   2. Clear all browser data")
    print("   3. Restart the server: python start.py")
    print("   4. Check browser console for errors")

if __name__ == "__main__":
    main()
