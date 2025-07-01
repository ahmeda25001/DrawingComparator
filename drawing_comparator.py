import os
import base64
from typing import List
import difflib
from dataclasses import dataclass
from datetime import datetime
from google.cloud import vision
from google.cloud import storage  # Import Google Cloud Storage client
import tempfile  # For creating temporary files in serverless environments
import json  # Import json module for decoding the key

@dataclass
class ComparisonResult:
    similarity_score: float
    differences: List[str]
    timestamp: str
    file1_text: str
    file2_text: str

class DrawingComparator:
    def __init__(self):
        """Initialize the DrawingComparator with Google Cloud Vision and Storage clients."""
        # Decode the base64-encoded key from the environment variable
        encoded_key = os.environ.get("GOOGLE_CLOUD_VISION_KEY_BASE64")
        if not encoded_key:
            raise Exception("Environment variable GOOGLE_CLOUD_VISION_KEY_BASE64 is not set.")
        
        # Decode the key and initialize the Vision client with credentials
        decoded_key = base64.b64decode(encoded_key).decode("utf-8")
        self.client = vision.ImageAnnotatorClient.from_service_account_info(json.loads(decoded_key))
        
        # Initialize Google Cloud Storage client
        self.storage_client = storage.Client.from_service_account_info(json.loads(decoded_key))
        
        # Get the bucket name from the environment variable
        self.bucket_name = os.environ.get("GOOGLE_CLOUD_STORAGE_BUCKET")
        if not self.bucket_name:
            raise Exception("Environment variable GOOGLE_CLOUD_STORAGE_BUCKET is not set.")

    def upload_to_gcs(self, file_path: str) -> str:
        """Upload a file to Google Cloud Storage and return its GCS URI."""
        bucket = self.storage_client.bucket(self.bucket_name)
        blob_name = os.path.basename(file_path)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        return f"gs://{self.bucket_name}/{blob_name}"

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from a PDF using Google Cloud Vision."""
        gcs_uri = self.upload_to_gcs(file_path)
        input_config = vision.InputConfig(gcs_source=vision.GcsSource(uri=gcs_uri), mime_type="application/pdf")
        request = vision.AnnotateFileRequest(
            features=[vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)],
            input_config=input_config
        )
        response = self.client.batch_annotate_files(requests=[request])
        if response.responses[0].error.message:
            raise Exception(f"Google Vision API error: {response.responses[0].error.message}")
        text = ""
        for page_response in response.responses[0].responses:
            text += page_response.full_text_annotation.text
        return text

    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from an image or PDF file."""
        if file_path.lower().endswith(".pdf"):
            return self.extract_text_from_pdf(file_path)
        return self.extract_text_from_image(file_path)

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
        """Compare two files (images or PDFs) by extracting and comparing their text."""
        try:
            text1 = self.extract_text_from_file(file1_path)
            text2 = self.extract_text_from_file(file2_path)
        finally:
            # Clean up temporary files in serverless environments
            if os.path.exists(file1_path):
                os.remove(file1_path)
            if os.path.exists(file2_path):
                os.remove(file2_path)

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