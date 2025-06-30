import os
import base64
from typing import List
import difflib
from dataclasses import dataclass
from datetime import datetime
from google.cloud import vision

@dataclass
class ComparisonResult:
    similarity_score: float
    differences: List[str]
    timestamp: str
    file1_text: str
    file2_text: str

class DrawingComparator:
    def __init__(self):
        """Initialize the DrawingComparator with Google Cloud Vision client."""
        # Decode the base64-encoded key from the environment variable
        encoded_key = os.environ.get("GOOGLE_CLOUD_VISION_KEY_BASE64")
        if not encoded_key:
            raise Exception("Environment variable GOOGLE_CLOUD_VISION_KEY_BASE64 is not set.")
        
        key_path = "/tmp/google-cloud-vision-key.json"
        with open(key_path, "wb") as key_file:
            key_file.write(base64.b64decode(encoded_key))
        
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
        self.client = vision.ImageAnnotatorClient()

    def extract_text_from_image(self, file_path: str) -> str:
        """Extract text from an image using Google Cloud Vision."""
        with open(file_path, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = self.client.text_detection(image=image)
        if response.error.message:
            raise Exception(f"Google Vision API error: {response.error.message}")
        return response.full_text_annotation.text

    def compare_drawings(self, file1_path: str, file2_path: str) -> ComparisonResult:
        """Compare two images by extracting and comparing their text."""
        text1 = self.extract_text_from_image(file1_path)
        text2 = self.extract_text_from_image(file2_path)

        similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
        differences = list(difflib.unified_diff(
            text1.splitlines(),
            text2.splitlines(),
            fromfile='File 1',
            tofile='File 2',
            lineterm=''
        ))

        return ComparisonResult(
            similarity_score=similarity,
            differences=differences,
            timestamp=datetime.now().isoformat(),
            file1_text=text1,
            file2_text=text2
        )

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