"""
Configuration file for Drawing Comparator file size limits and settings.
Centralize all limits to make them easily adjustable.
"""

class Config:
    """Configuration class for file size limits and application settings."""
    
    # Flask Configuration
    FLASK_MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB - Increased from 16MB
    
    # Vercel Platform Limits
    VERCEL_HOBBY_REQUEST_LIMIT = 4.5 * 1024 * 1024  # 4.5MB
    VERCEL_PRO_REQUEST_LIMIT = 100 * 1024 * 1024    # 100MB
    VERCEL_FUNCTION_TIMEOUT = 60  # seconds (Pro plan)
    
    # Google Cloud Vision API Limits
    GOOGLE_VISION_MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
    GOOGLE_VISION_MAX_PDF_PAGES = 2000
    
    # File Upload Settings
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    UPLOAD_FOLDER = '/tmp'  # Vercel compatibility
    
    # Image Compression Settings
    DEFAULT_COMPRESSION_QUALITY = 85
    TARGET_COMPRESSED_SIZE_MB = 15
    
    # AI Comparison Settings
    USE_AI_COMPARISON = True  # Enable/disable AI comparison
    OPENAI_MODEL = "gpt-4o"  # or "gpt-3.5-turbo" for faster/cheaper analysis
    AI_FALLBACK_MODEL = "gpt-3.5-turbo"  # Fallback if primary model fails
    AI_TEMPERATURE = 0.1  # Low temperature for consistent analysis
    AI_MAX_TOKENS = 2000  # Maximum tokens for AI response
    AI_TIMEOUT = 30  # Timeout in seconds for AI requests
    
    # Error Messages
    ERROR_MESSAGES = {
        'file_too_large': "File size ({file_size}) exceeds the maximum limit ({limit}). Please use a smaller file or compress your image.",
        'google_vision_limit': "File size ({file_size}) exceeds Google Vision API limit ({limit}). Please compress or resize your file.",
        'invalid_file_type': "Invalid file type. Only PNG, JPG, JPEG, and PDF files are allowed.",
        'no_files': "Both files are required for comparison.",
        'processing_error': "An error occurred while processing your files: {error}",
        'vercel_limit': "File size exceeds Vercel platform limit. Consider upgrading to Pro plan or using smaller files."
    }
    
    @classmethod
    def get_effective_limit(cls):
        """
        Get the most restrictive file size limit that applies.
        Returns the smallest limit that would cause an error.
        """
        limits = [
            cls.FLASK_MAX_CONTENT_LENGTH,
            cls.GOOGLE_VISION_MAX_FILE_SIZE,
            # Note: Vercel limit depends on plan type
        ]
        return min(limits)
    
    @classmethod
    def format_bytes(cls, bytes_value):
        """Convert bytes to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} TB"
    
    @classmethod
    def get_limits_info(cls):
        """Get a dictionary with all relevant limits for display."""
        return {
            "flask_limit": cls.format_bytes(cls.FLASK_MAX_CONTENT_LENGTH),
            "google_vision_limit": cls.format_bytes(cls.GOOGLE_VISION_MAX_FILE_SIZE),
            "effective_limit": cls.format_bytes(cls.get_effective_limit()),
            "vercel_hobby_limit": cls.format_bytes(cls.VERCEL_HOBBY_REQUEST_LIMIT),
            "vercel_pro_limit": cls.format_bytes(cls.VERCEL_PRO_REQUEST_LIMIT),
            "allowed_extensions": list(cls.ALLOWED_EXTENSIONS),
            "ai_comparison_enabled": cls.USE_AI_COMPARISON,
            "ai_model": cls.OPENAI_MODEL,
            "recommendations": [
                f"Keep files under {cls.format_bytes(cls.GOOGLE_VISION_MAX_FILE_SIZE)} for best results",
                "Use JPEG format for photos to reduce file size",
                "Compress images before uploading if they're too large",
                "Consider upgrading to Vercel Pro for larger file support",
                "Set OPENAI_API_KEY for intelligent semantic comparison"
            ]
        }
