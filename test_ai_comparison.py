#!/usr/bin/env python3
"""
Test script for AI-powered semantic comparison of technical drawings.
This script demonstrates the difference between basic text comparison and AI semantic analysis.
"""

import os
import sys
from semantic_comparator import SemanticComparator, format_semantic_result

def test_ai_comparison():
    """Test the AI comparison with sample technical drawing texts."""
    print("🧪 Testing AI Semantic Comparison for Technical Drawings")
    print("=" * 60)
    
    # Check if OpenAI API key is available
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not found.")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Initialize the semantic comparator
    try:
        comparator = SemanticComparator(api_key)
        print("✅ AI Semantic Comparator initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize AI comparator: {e}")
        return
    
    # Test cases with different levels of similarity
    test_cases = [
        {
            "name": "Identical Content (Different Format)",
            "text1": "Steel beam W14x30\nSpan: 20 feet\nDead Load: 50 PSF\nLive Load: 40 PSF\nDeflection: L/360",
            "text2": "W14x30 steel beam, span=20ft, DL=50psf, LL=40psf, deflection limit L/360"
        },
        {
            "name": "Similar Design (Different Beam Size)",
            "text1": "Steel beam W14x30\nSpan: 20 feet\nDead Load: 50 PSF\nLive Load: 40 PSF",
            "text2": "Steel beam W16x26\nSpan: 20 feet\nDead Load: 50 PSF\nLive Load: 40 PSF"
        },
        {
            "name": "Different Materials",
            "text1": "Steel beam W14x30\nSpan: 20 feet\nDead Load: 50 PSF\nLive Load: 40 PSF",
            "text2": "Concrete beam 12x24\nSpan: 20 feet\nDead Load: 50 PSF\nLive Load: 40 PSF\nf'c = 4000 psi"
        },
        {
            "name": "Completely Different Structures",
            "text1": "Steel beam W14x30\nSpan: 20 feet\nResidential building",
            "text2": "Foundation wall\nHeight: 8 feet\nConcrete block\nRebar #5 @ 16 in OC"
        }
    ]
    
    print(f"\n🔬 Running {len(test_cases)} test cases...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test Case {i}: {test_case['name']}")
        print("-" * 50)
        
        try:
            # Perform AI comparison
            result = comparator.compare_with_gpt(test_case['text1'], test_case['text2'])
            
            # Display results
            print(f"📊 AI Similarity Score: {result.similarity_score:.1%}")
            print(f"🎯 AI Confidence: {result.confidence:.1%}")
            print(f"📋 Raw Text Similarity: {result.raw_similarity:.1%}")
            
            if result.reasoning:
                print(f"💭 AI Reasoning: {result.reasoning[:200]}...")
            
            if result.semantic_differences:
                print(f"🔍 Key Differences:")
                for diff in result.semantic_differences[:3]:
                    print(f"  • {diff}")
            
            print()
            
        except Exception as e:
            print(f"❌ Error in test case {i}: {e}\n")
    
    print("🎉 AI Comparison Testing Complete!")
    print("\nTo use AI comparison in your Drawing Comparator:")
    print("1. Set OPENAI_API_KEY environment variable")
    print("2. The app will automatically use AI comparison when available")
    print("3. Fallback to basic text comparison if AI fails")

def demo_category_analysis():
    """Demonstrate category-based analysis."""
    print("\n🎯 Demonstrating Category Analysis")
    print("=" * 40)
    
    # Sample structural drawing text
    drawing_text = """
    STRUCTURAL PLAN - LEVEL 2
    
    BEAMS:
    - W14x30 @ Grid A, Span: 25'-0"
    - W16x26 @ Grid B, Span: 30'-0"
    
    COLUMNS:
    - HSS 8x8x1/2 @ Grid 1
    - W14x90 @ Grid 2
    
    LOADS:
    - Dead Load: 50 PSF
    - Live Load: 40 PSF
    - Snow Load: 30 PSF
    
    MATERIALS:
    - Steel: ASTM A992 Gr. 50
    - Concrete: f'c = 4000 psi
    
    CONNECTIONS:
    - Beam to column: Bolted shear connection
    - Base plates: 18"x18"x1.5"
    
    NOTES:
    - All welding per AWS D1.1
    - Fire rating: 2 hours
    """
    
    modified_text = """
    STRUCTURAL PLAN - LEVEL 2 (REVISED)
    
    BEAMS:
    - W16x31 @ Grid A, Span: 25'-0"  # Changed beam size
    - W16x26 @ Grid B, Span: 30'-0"
    
    COLUMNS:
    - HSS 8x8x1/2 @ Grid 1
    - W14x90 @ Grid 2
    
    LOADS:
    - Dead Load: 55 PSF  # Increased load
    - Live Load: 40 PSF
    - Snow Load: 30 PSF
    
    MATERIALS:
    - Steel: ASTM A992 Gr. 50
    - Concrete: f'c = 5000 psi  # Higher strength concrete
    
    CONNECTIONS:
    - Beam to column: Welded moment connection  # Different connection
    - Base plates: 20"x20"x1.5"  # Larger base plates
    
    NOTES:
    - All welding per AWS D1.1
    - Fire rating: 3 hours  # Increased fire rating
    """
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY required for category analysis demo")
        return
    
    try:
        comparator = SemanticComparator(api_key)
        result = comparator.compare_with_gpt(drawing_text, modified_text)
        
        print("📊 Category-wise Analysis Results:")
        if result.categories:
            for category, score in result.categories.items():
                bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
                print(f"  {category.replace('_', ' ').title():.<20} {score:.1%} [{bar}]")
        
        print(f"\n🔍 Technical Analysis:")
        if result.technical_analysis:
            ta = result.technical_analysis
            if ta.get('major_differences'):
                print("  Major Differences:")
                for diff in ta['major_differences'][:3]:
                    print(f"    • {diff}")
    
    except Exception as e:
        print(f"❌ Error in category analysis: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo-categories":
        demo_category_analysis()
    else:
        test_ai_comparison()
        
    print("\n" + "=" * 60)
    print("💡 Tips for better AI comparison:")
    print("1. Ensure drawing text is clear and well-formatted")
    print("2. Include technical specifications and dimensions")
    print("3. AI works best with structured engineering content")
    print("4. Consider using GPT-4 for more accurate analysis")
    print("5. Review AI confidence scores - low confidence may indicate unclear input")
