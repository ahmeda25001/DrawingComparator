"""
Error monitoring and debugging script for Drawing Comparator.
This script helps identify where file size limits are being hit and provides debugging information.
"""

import os
import json
from datetime import datetime
from config import Config

class ErrorMonitor:
    """Monitor and log file size related errors."""
    
    def __init__(self, log_file="/tmp/file_size_errors.log"):
        self.log_file = log_file
        
    def log_error(self, error_type, file_info, error_message, additional_info=None):
        """Log file size related errors with detailed information."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "file_info": file_info,
            "error_message": error_message,
            "limits": Config.get_limits_info(),
            "additional_info": additional_info or {}
        }
        
        try:
            # Append to log file
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry, indent=2) + "\n\n")
        except Exception as e:
            print(f"Failed to write to log file: {e}")
    
    def log_file_upload_attempt(self, filename, file_size, success=True, error=None):
        """Log file upload attempts with size information."""
        file_info = {
            "filename": filename,
            "size_bytes": file_size,
            "size_formatted": Config.format_bytes(file_size),
            "success": success
        }
        
        if success:
            self.log_error("FILE_UPLOAD_SUCCESS", file_info, "File upload successful")
        else:
            self.log_error("FILE_UPLOAD_FAILED", file_info, str(error))
    
    def check_limits_against_file(self, file_size):
        """Check which limits a file size violates."""
        violations = []
        
        if file_size > Config.FLASK_MAX_CONTENT_LENGTH:
            violations.append({
                "limit_type": "Flask MAX_CONTENT_LENGTH",
                "limit_value": Config.FLASK_MAX_CONTENT_LENGTH,
                "limit_formatted": Config.format_bytes(Config.FLASK_MAX_CONTENT_LENGTH),
                "exceeded_by": file_size - Config.FLASK_MAX_CONTENT_LENGTH,
                "exceeded_by_formatted": Config.format_bytes(file_size - Config.FLASK_MAX_CONTENT_LENGTH)
            })
        
        if file_size > Config.GOOGLE_VISION_MAX_FILE_SIZE:
            violations.append({
                "limit_type": "Google Vision API",
                "limit_value": Config.GOOGLE_VISION_MAX_FILE_SIZE,
                "limit_formatted": Config.format_bytes(Config.GOOGLE_VISION_MAX_FILE_SIZE),
                "exceeded_by": file_size - Config.GOOGLE_VISION_MAX_FILE_SIZE,
                "exceeded_by_formatted": Config.format_bytes(file_size - Config.GOOGLE_VISION_MAX_FILE_SIZE)
            })
        
        if file_size > Config.VERCEL_HOBBY_REQUEST_LIMIT:
            violations.append({
                "limit_type": "Vercel Hobby Plan",
                "limit_value": Config.VERCEL_HOBBY_REQUEST_LIMIT,
                "limit_formatted": Config.format_bytes(Config.VERCEL_HOBBY_REQUEST_LIMIT),
                "exceeded_by": file_size - Config.VERCEL_HOBBY_REQUEST_LIMIT,
                "exceeded_by_formatted": Config.format_bytes(file_size - Config.VERCEL_HOBBY_REQUEST_LIMIT)
            })
        
        return violations
    
    def generate_error_report(self):
        """Generate a comprehensive error report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "configuration": Config.get_limits_info(),
            "common_issues": [
                {
                    "issue": "413 Request Entity Too Large",
                    "cause": "Flask MAX_CONTENT_LENGTH exceeded",
                    "current_limit": Config.format_bytes(Config.FLASK_MAX_CONTENT_LENGTH),
                    "solution": "Increase app.config['MAX_CONTENT_LENGTH'] or compress files"
                },
                {
                    "issue": "Google Vision API Error",
                    "cause": "File size exceeds 20MB limit",
                    "current_limit": Config.format_bytes(Config.GOOGLE_VISION_MAX_FILE_SIZE),
                    "solution": "Compress images or use smaller files"
                },
                {
                    "issue": "Vercel Function Timeout",
                    "cause": "Large files take too long to process",
                    "current_limit": f"{Config.VERCEL_FUNCTION_TIMEOUT} seconds",
                    "solution": "Upgrade to Pro plan or optimize processing"
                }
            ],
            "file_size_thresholds": {
                "safe_size": Config.format_bytes(15 * 1024 * 1024),  # 15MB
                "warning_size": Config.format_bytes(18 * 1024 * 1024),  # 18MB
                "max_size": Config.format_bytes(Config.GOOGLE_VISION_MAX_FILE_SIZE)
            }
        }
        
        return report
    
    def get_recent_errors(self, hours=24):
        """Get recent errors from the log file."""
        if not os.path.exists(self.log_file):
            return []
        
        recent_errors = []
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        
        try:
            with open(self.log_file, 'r') as f:
                content = f.read()
                # Split by double newline to separate log entries
                entries = content.split('\n\n')
                
                for entry in entries:
                    if entry.strip():
                        try:
                            log_data = json.loads(entry.strip())
                            entry_time = datetime.fromisoformat(log_data['timestamp']).timestamp()
                            
                            if entry_time >= cutoff_time:
                                recent_errors.append(log_data)
                        except (json.JSONDecodeError, KeyError, ValueError):
                            continue
        except Exception as e:
            print(f"Error reading log file: {e}")
        
        return recent_errors

# Convenience function for quick file size checking
def quick_file_check(file_path):
    """Quickly check if a file meets all size requirements."""
    if not os.path.exists(file_path):
        return {"error": "File does not exist"}
    
    file_size = os.path.getsize(file_path)
    monitor = ErrorMonitor()
    violations = monitor.check_limits_against_file(file_size)
    
    return {
        "file_path": file_path,
        "file_size": file_size,
        "file_size_formatted": Config.format_bytes(file_size),
        "violations": violations,
        "is_valid": len(violations) == 0,
        "recommendations": [
            "Compress the image if violations exist",
            "Use JPEG format for photos",
            "Consider resizing large images"
        ] if violations else ["File size is within all limits"]
    }

if __name__ == "__main__":
    # Example usage
    monitor = ErrorMonitor()
    report = monitor.generate_error_report()
    print("File Size Limit Report:")
    print("=" * 50)
    print(json.dumps(report, indent=2))
