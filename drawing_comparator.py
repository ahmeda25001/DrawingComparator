import os
from PIL import Image
from typing import Dict, List, Tuple
import difflib
from dataclasses import dataclass
import json
from datetime import datetime
import hashlib

@dataclass
class ComparisonResult:
    similarity_score: float
    differences: List[str]
    timestamp: str
    file1_text: str
    file2_text: str

class DrawingComparator:
    def __init__(self):
        """Initialize the DrawingComparator for image comparison."""
        pass

    def extract_image_info(self, image_path: str) -> str:
        """Extract basic image information for comparison."""
        try:
            with Image.open(image_path) as img:
                # Get basic image properties
                width, height = img.size
                format_type = img.format
                mode = img.mode
                
                # Calculate a simple hash of the image data
                img_data = img.tobytes()
                img_hash = hashlib.md5(img_data).hexdigest()[:16]  # First 16 chars
                
                # Create a text representation for comparison
                info = f"Image: {os.path.basename(image_path)}\n"
                info += f"Size: {width}x{height}\n"
                info += f"Format: {format_type}\n"
                info += f"Mode: {mode}\n"
                info += f"Hash: {img_hash}\n"
                
                return info
        except Exception as e:
            raise Exception(f"Error processing image {image_path}: {str(e)}")

    def compare_drawings(self, file1_path: str, file2_path: str) -> ComparisonResult:
        """Compare two drawings and return the comparison results."""
        # Extract image information from both files
        info1 = self.extract_image_info(file1_path)
        info2 = self.extract_image_info(file2_path)

        # Calculate similarity using difflib
        similarity = difflib.SequenceMatcher(None, info1, info2).ratio()

        # Get differences
        differences = []
        for line in difflib.unified_diff(
            info1.splitlines(),
            info2.splitlines(),
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
            file1_text=info1,
            file2_text=info2
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