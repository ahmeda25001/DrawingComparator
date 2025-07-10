"""
File size handling utilities for the Drawing Comparator project.
This module provides functions to validate file sizes and handle large files appropriately.
"""

import os
from flask import jsonify
from PIL import Image
import io

class FileSizeHandler:
    """Handles file size validation and optimization for the Drawing Comparator."""
    
    # File size limits (in bytes)
    FLASK_LIMIT = 16 * 1024 * 1024  # 16MB - Current Flask limit
    RECOMMENDED_FLASK_LIMIT = 50 * 1024 * 1024  # 50MB - Recommended increase
    VERCEL_HOBBY_LIMIT = 4.5 * 1024 * 1024  # 4.5MB - Vercel Hobby plan limit
    VERCEL_PRO_LIMIT = 100 * 1024 * 1024  # 100MB - Vercel Pro plan limit
    GOOGLE_VISION_LIMIT = 20 * 1024 * 1024  # 20MB - Google Vision API limit
    
    @staticmethod
    def get_file_size(file_obj):
        """Get the size of a file object in bytes."""
        file_obj.seek(0, 2)  # Seek to end
        size = file_obj.tell()
        file_obj.seek(0)  # Reset to beginning
        return size
    
    @staticmethod
    def format_file_size(size_bytes):
        """Convert bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    @classmethod
    def validate_file_size(cls, file_obj, filename):
        """
        Validate file size against various limits and return appropriate error messages.
        
        Returns:
            tuple: (is_valid: bool, error_message: str, file_size: int)
        """
        file_size = cls.get_file_size(file_obj)
        formatted_size = cls.format_file_size(file_size)
        
        # Check against Google Vision API limit (most restrictive for processing)
        if file_size > cls.GOOGLE_VISION_LIMIT:
            return False, (
                f"File '{filename}' ({formatted_size}) exceeds Google Vision API limit "
                f"({cls.format_file_size(cls.GOOGLE_VISION_LIMIT)}). "
                f"Please compress or resize your file."
            ), file_size
        
        # Check against current Flask limit
        if file_size > cls.FLASK_LIMIT:
            return False, (
                f"File '{filename}' ({formatted_size}) exceeds upload limit "
                f"({cls.format_file_size(cls.FLASK_LIMIT)}). "
                f"Please use a smaller file."
            ), file_size
        
        return True, "", file_size
    
    @staticmethod
    def compress_image(file_obj, max_size_mb=15, quality=85):
        """
        Compress an image file to reduce its size.
        
        Args:
            file_obj: File object to compress
            max_size_mb: Target maximum size in MB
            quality: JPEG quality (1-100)
        
        Returns:
            io.BytesIO: Compressed image file object
        """
        try:
            # Open image with PIL
            image = Image.open(file_obj)
            
            # Convert to RGB if necessary (for JPEG)
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Calculate compression ratio needed
            original_size = FileSizeHandler.get_file_size(file_obj)
            target_size = max_size_mb * 1024 * 1024
            
            if original_size <= target_size:
                file_obj.seek(0)
                return file_obj
            
            # Try different quality settings
            for q in range(quality, 20, -10):
                output = io.BytesIO()
                image.save(output, format='JPEG', quality=q, optimize=True)
                
                if output.tell() <= target_size:
                    output.seek(0)
                    return output
            
            # If still too large, resize the image
            width, height = image.size
            scale_factor = (target_size / original_size) ** 0.5
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            output = io.BytesIO()
            resized_image.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)
            return output
            
        except Exception as e:
            # If compression fails, return original file
            file_obj.seek(0)
            return file_obj
    
    @classmethod
    def get_size_recommendations(cls):
        """Get recommendations for file size limits."""
        return {
            "current_flask_limit": cls.format_file_size(cls.FLASK_LIMIT),
            "recommended_flask_limit": cls.format_file_size(cls.RECOMMENDED_FLASK_LIMIT),
            "google_vision_limit": cls.format_file_size(cls.GOOGLE_VISION_LIMIT),
            "vercel_hobby_limit": cls.format_file_size(cls.VERCEL_HOBBY_LIMIT),
            "vercel_pro_limit": cls.format_file_size(cls.VERCEL_PRO_LIMIT),
            "recommendations": [
                "Increase Flask MAX_CONTENT_LENGTH to 50MB for better user experience",
                "Consider upgrading to Vercel Pro for 100MB request limit",
                "Implement client-side image compression for files over 15MB",
                "Add progress indicators for large file uploads",
                "Consider chunked upload for very large files"
            ]
        }
