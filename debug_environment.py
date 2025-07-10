#!/usr/bin/env python3
"""
Debug script to check environment variables and AI initialization.
"""

import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_environment():
    """Check all required environment variables."""
    print("🔍 Environment Variables Check")
    print("=" * 40)
    
    # Check OpenAI API Key
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        print(f"✅ OPENAI_API_KEY: Set (length: {len(openai_key)})")
        print(f"   Preview: {openai_key[:8]}...{openai_key[-4:]}")
    else:
        print("❌ OPENAI_API_KEY: Not set")
    
    # Check Google Cloud Vision Key
    google_key = os.environ.get("GOOGLE_CLOUD_VISION_KEY_BASE64")
    if google_key:
        print(f"✅ GOOGLE_CLOUD_VISION_KEY_BASE64: Set (length: {len(google_key)})")
    else:
        print("❌ GOOGLE_CLOUD_VISION_KEY_BASE64: Not set")
    
    # Check Google Cloud Storage Bucket
    bucket = os.environ.get("GOOGLE_CLOUD_STORAGE_BUCKET")
    if bucket:
        print(f"✅ GOOGLE_CLOUD_STORAGE_BUCKET: {bucket}")
    else:
        print("❌ GOOGLE_CLOUD_STORAGE_BUCKET: Not set")
    
    print()
    
    # Test AI initialization
    print("🤖 AI Initialization Test")
    print("=" * 40)
    
    try:
        from semantic_comparator import SemanticComparator
        
        if openai_key:
            try:
                semantic_comp = SemanticComparator(openai_key)
                print("✅ SemanticComparator initialized successfully")
            except Exception as e:
                print(f"❌ SemanticComparator initialization failed: {e}")
        else:
            print("⚠️  Cannot test SemanticComparator - no API key")
            
    except ImportError as e:
        print(f"❌ Cannot import SemanticComparator: {e}")
    
    print()
    
    # Test DrawingComparator initialization
    print("📐 DrawingComparator Initialization Test")
    print("=" * 40)
    
    try:
        from drawing_comparator import DrawingComparator
        
        # Test without AI (should work if Google Cloud is set up)
        try:
            comparator = DrawingComparator(use_ai_comparison=False)
            print("✅ DrawingComparator (no AI) initialized successfully")
        except Exception as e:
            print(f"❌ DrawingComparator (no AI) failed: {e}")
        
        # Test with AI
        try:
            comparator = DrawingComparator(use_ai_comparison=True)
            if comparator.semantic_comparator:
                print("✅ DrawingComparator (with AI) initialized successfully")
            else:
                print("⚠️  DrawingComparator initialized but AI not available")
        except Exception as e:
            print(f"❌ DrawingComparator (with AI) failed: {e}")
            
    except ImportError as e:
        print(f"❌ Cannot import DrawingComparator: {e}")
    
    print()
    print("🔧 Recommendations")
    print("=" * 40)
    
    if not openai_key:
        print("• Set OPENAI_API_KEY environment variable for AI features")
    
    if not google_key:
        print("• Set GOOGLE_CLOUD_VISION_KEY_BASE64 for text extraction")
    
    if not bucket:
        print("• Set GOOGLE_CLOUD_STORAGE_BUCKET for PDF processing")
    
    print("\n✨ Debug complete!")

if __name__ == "__main__":
    check_environment()
