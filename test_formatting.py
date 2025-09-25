#!/usr/bin/env python3
"""
Test script to demonstrate the improved markdown formatting
"""

def test_markdown_formatting():
    """Test the markdown formatting functions"""
    print("🧪 Testing Markdown Formatting")
    print("=" * 40)
    
    # Sample report with markdown formatting
    sample_report = """# Executive Summary

This report provides a **comprehensive analysis** of artificial intelligence in healthcare. The findings reveal *significant opportunities* for improvement.

## Key Findings

The research identified several important trends:

- **Machine Learning** applications are growing rapidly
- *Natural Language Processing* is becoming more sophisticated
- **Computer Vision** shows promising results in medical imaging

### Detailed Analysis

The analysis shows that **AI technologies** are transforming healthcare delivery. Key areas include:

- Diagnostic accuracy improvements
- Treatment optimization
- Patient monitoring systems

## Conclusion

The research demonstrates that **artificial intelligence** will play a crucial role in the future of healthcare."""
    
    print("📝 Sample Report with Markdown:")
    print("-" * 30)
    print(sample_report)
    print("-" * 30)
    
    # Test the formatting function
    from main import format_report_html
    
    formatted_html = format_report_html(sample_report)
    
    print("\n🎨 Formatted HTML Output:")
    print("-" * 30)
    print(formatted_html)
    print("-" * 30)
    
    print("\n✅ Markdown formatting test completed!")
    print("The report should now display with proper formatting:")
    print("- Bold text (**text**) becomes <strong>text</strong>")
    print("- Italic text (*text*) becomes <em>text</em>")
    print("- Bullet points (- item) become <ul><li>item</li></ul>")
    print("- Headers (# ## ###) become <h1><h2><h3>")

if __name__ == "__main__":
    test_markdown_formatting()
