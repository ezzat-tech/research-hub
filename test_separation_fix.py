#!/usr/bin/env python3
"""
Test the title separation fix - Bold titles separated from normal body text
"""

import webbrowser
import time

def main():
    print("🎯 TITLE SEPARATION FIX TEST")
    print("=" * 50)
    
    print("📋 What should be fixed:")
    print("   ✅ Executive Summary (13pt, BOLD) - on separate line")
    print("   ✅ Body text (11pt, NORMAL weight) - below heading")
    print("   ✅ Introduction (13pt, BOLD) - on separate line")
    print("   ✅ Body text (11pt, NORMAL weight) - below heading")
    print("   ✅ Key Findings (13pt, BOLD) - on separate line")
    print("   ✅ Body text (11pt, NORMAL weight) - below heading")
    print("   ✅ Conclusion (13pt, BOLD) - on separate line")
    print("   ✅ Body text (11pt, NORMAL weight) - below heading")
    print("   ✅ Thesis (13pt, BOLD) - on separate line")
    print("   ✅ Body text (11pt, NORMAL weight) - below heading")
    print()
    
    print("🚀 Testing Steps:")
    print()
    
    print("1️⃣ Clear Browser Cache:")
    print("   • Press Ctrl + Shift + R (hard refresh)")
    print("   • Or: F12 → Right-click refresh → 'Empty Cache and Hard Reload'")
    print()
    
    print("2️⃣ Test Main App:")
    print("   • Go to: http://localhost:8000")
    print("   • Generate a research report")
    print("   • Check that titles are BOLD and on separate lines")
    print("   • Verify body text is NORMAL weight")
    print()
    
    print("3️⃣ Test PDF Download:")
    print("   • Click 'Download PDF' button")
    print("   • Check same formatting in PDF")
    print()
    
    print("🎯 Expected Report Structure:")
    print("   📌 Executive Summary (13pt, BOLD)")
    print("   📌 [Body text: 11pt, NORMAL weight]")
    print("   📌 Introduction (13pt, BOLD)")
    print("   📌 [Body text: 11pt, NORMAL weight]")
    print("   📌 Key Findings (13pt, BOLD)")
    print("   📌 [Body text: 11pt, NORMAL weight]")
    print("   📌 Conclusion (13pt, BOLD)")
    print("   📌 [Body text: 11pt, NORMAL weight]")
    print("   📌 Thesis (13pt, BOLD)")
    print("   📌 [Body text: 11pt, NORMAL weight]")
    print()
    
    print("🔧 Key Changes Made:")
    print("   • Enhanced JavaScript to detect inline headers")
    print("   • Added regex to separate headers from content")
    print("   • Ensured body text is NOT bold")
    print("   • Added Times New Roman font for body text")
    print("   • Updated both web and PDF formatting")
    print()
    
    print("🚀 Opening main app...")
    try:
        webbrowser.open("http://localhost:8000")
        print("✅ Main app opened!")
        print("   Generate a report and check the proper separation")
    except:
        print("❌ Could not open browser automatically")
        print("   Please manually go to: http://localhost:8000")
    
    print("\n📝 If titles are still inline:")
    print("   1. Try incognito/private browsing mode")
    print("   2. Clear all browser data")
    print("   3. Restart server: python start.py")
    print("   4. Check browser console for 'CSS loaded with academic formatting v9'")
    print("   5. Use browser dev tools to inspect the HTML structure")

if __name__ == "__main__":
    main()
