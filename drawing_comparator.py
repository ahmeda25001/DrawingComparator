import os
import easyocr
from PIL import Image
from typing import Dict, List, Tuple
import difflib
from dataclasses import dataclass
import json
from datetime import datetime

@dataclass
class ComparisonResult:
    similarity_score: float
    differences: List[str]
    timestamp: str
    file1_text: str
    file2_text: str

class DrawingComparator:
    def __init__(self):
        """Initialize the DrawingComparator with EasyOCR reader."""
        # Initialize EasyOCR reader (downloads models on first use)
        self.reader = easyocr.Reader(['en'])

    def extract_text(self, image_path: str) -> str:
        """Extract text from an image using EasyOCR."""
        try:
            # Read text from image
            results = self.reader.readtext(image_path)
            
            # Extract text from results
            text_lines = []
            for (bbox, text, prob) in results:
                if prob > 0.5:  # Only include text with >50% confidence
                    text_lines.append(text)
            
            return '\n'.join(text_lines).strip()
        except Exception as e:
            raise Exception(f"Error processing image {image_path}: {str(e)}")

    def compare_drawings(self, file1_path: str, file2_path: str) -> ComparisonResult:
        """Compare two drawings and return the comparison results."""
        # Extract text from both files
        text1 = self.extract_text(file1_path)
        text2 = self.extract_text(file2_path)

        # Calculate similarity using difflib
        similarity = difflib.SequenceMatcher(None, text1, text2).ratio()

        # Get differences
        differences = []
        for line in difflib.unified_diff(
            text1.splitlines(),
            text2.splitlines(),
            fromfile='File 1',
            tofile='File 2',
            lineterm=''
        ):
            differences.append(line)

        # Create comparison result
        result = ComparisonResult(
            similarity_score=similarity,
            differences=differences,
            timestamp=datetime.now().isoformat(),
            file1_text=text1,
            file2_text=text2
        )

        return result

# Example usage
if __name__ == "__main__":
    comparator = DrawingComparator()
    # Example paths - replace with actual paths
    file1 = "Example_Drawings/structural-Drawing.jpg"
    file2 = "Example_Drawings/structural-drawings.png"
    
    try:
        result = comparator.compare_drawings(file1, file2)
        print(f"Similarity score: {result.similarity_score:.2%}")
        print("\nDifferences found:")
        for diff in result.differences[:10]:  # Show first 10 differences
            print(diff)
    except Exception as e:
        print(f"Error: {str(e)}") 