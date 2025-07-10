#!/usr/bin/env python3
"""
File Size Limit Testing Script for Drawing Comparator

This script helps you understand and test the file size limits in your project.
Run this script to see current limits and test files against them.
"""

import os
import sys
from config import Config
from error_monitor import ErrorMonitor, quick_file_check

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_limits_summary():
    """Print a summary of all file size limits."""
    print_header("CURRENT FILE SIZE LIMITS")
    
    limits = Config.get_limits_info()
    
    print(f"Flask Maximum Upload Size: {limits['flask_limit']}")
    print(f"Google Vision API Limit:   {limits['google_vision_limit']}")
    print(f"Effective Limit (Most Restrictive): {limits['effective_limit']}")
    print(f"Vercel Hobby Plan Limit:   {limits['vercel_hobby_limit']}")
    print(f"Vercel Pro Plan Limit:     {limits['vercel_pro_limit']}")
    
    print(f"\nAllowed File Extensions: {', '.join(limits['allowed_extensions'])}")
    
    print("\nRecommendations:")
    for i, rec in enumerate(limits['recommendations'], 1):
        print(f"  {i}. {rec}")

def test_file_size(file_path):
    """Test a specific file against all limits."""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print_header(f"TESTING FILE: {os.path.basename(file_path)}")
    
    result = quick_file_check(file_path)
    
    print(f"File Path: {result['file_path']}")
    print(f"File Size: {result['file_size_formatted']} ({result['file_size']:,} bytes)")
    
    if result['is_valid']:
        print("✅ File passes all size checks!")
    else:
        print("❌ File violates size limits:")
        for violation in result['violations']:
            print(f"  - {violation['limit_type']}: "
                  f"Exceeds {violation['limit_formatted']} by {violation['exceeded_by_formatted']}")
    
    print("\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  • {rec}")

def show_error_scenarios():
    """Show common error scenarios and their causes."""
    print_header("COMMON ERROR SCENARIOS")
    
    scenarios = [
        {
            "error": "413 Request Entity Too Large",
            "cause": f"File exceeds Flask limit ({Config.format_bytes(Config.FLASK_MAX_CONTENT_LENGTH)})",
            "solution": "Increase Flask MAX_CONTENT_LENGTH or compress the file",
            "location": "Flask application level (before processing)"
        },
        {
            "error": "Google Vision API Error",
            "cause": f"File exceeds Google Vision limit ({Config.format_bytes(Config.GOOGLE_VISION_MAX_FILE_SIZE)})",
            "solution": "Compress or resize the image/PDF",
            "location": "Google Cloud Vision API call"
        },
        {
            "error": "Vercel Function Timeout",
            "cause": "Processing takes longer than allowed time limit",
            "solution": "Use smaller files or upgrade to Pro plan",
            "location": "Vercel serverless function execution"
        },
        {
            "error": "Out of Memory",
            "cause": "Large files consume too much memory during processing",
            "solution": "Process files in chunks or use streaming",
            "location": "Python application during file processing"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['error']}")
        print(f"   Cause: {scenario['cause']}")
        print(f"   Location: {scenario['location']}")
        print(f"   Solution: {scenario['solution']}")

def generate_test_files():
    """Generate test files of different sizes for testing."""
    print_header("GENERATING TEST FILES")
    
    test_dir = "/tmp/file_size_tests"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create files of different sizes
    test_sizes = [
        (1024 * 1024, "1MB_test.txt"),           # 1MB
        (5 * 1024 * 1024, "5MB_test.txt"),       # 5MB
        (15 * 1024 * 1024, "15MB_test.txt"),     # 15MB
        (20 * 1024 * 1024, "20MB_test.txt"),     # 20MB (at limit)
        (25 * 1024 * 1024, "25MB_test.txt"),     # 25MB (over limit)
    ]
    
    created_files = []
    
    for size, filename in test_sizes:
        file_path = os.path.join(test_dir, filename)
        try:
            with open(file_path, 'wb') as f:
                f.write(b'0' * size)
            created_files.append(file_path)
            print(f"✅ Created: {filename} ({Config.format_bytes(size)})")
        except Exception as e:
            print(f"❌ Failed to create {filename}: {e}")
    
    print(f"\nTest files created in: {test_dir}")
    print("You can now test these files with: python file_size_test.py <file_path>")
    
    return created_files

def main():
    """Main function to run the file size testing script."""
    print_header("DRAWING COMPARATOR - FILE SIZE LIMIT TESTING")
    
    if len(sys.argv) > 1:
        # Test specific file
        file_path = sys.argv[1]
        test_file_size(file_path)
    else:
        # Show general information
        print_limits_summary()
        show_error_scenarios()
        
        print("\n" + "🔧 USAGE" + "\n" + "-" * 10)
        print("To test a specific file: python file_size_test.py <file_path>")
        print("To generate test files: python file_size_test.py --generate-tests")
        
        if len(sys.argv) > 1 and sys.argv[1] == "--generate-tests":
            test_files = generate_test_files()
            
            # Test one of the generated files as an example
            if test_files:
                print("\nExample test of generated 15MB file:")
                test_file_size(test_files[2])  # 15MB file

if __name__ == "__main__":
    main()
