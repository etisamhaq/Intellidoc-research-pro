"""Input validation utilities"""

import re
from typing import Any, List, Optional, Dict
import os
from config.settings import Config

class Validators:
    """Validation utilities for input data"""
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        Validate API key format
        
        Args:
            api_key: The API key to validate
            
        Returns:
            True if valid
        """
        if not api_key:
            return False
        
        # Check if it's the placeholder
        if api_key == "your_api_key_here_replace_this":
            return False
        
        # Basic validation - should be alphanumeric with possible dashes/underscores
        pattern = r'^[a-zA-Z0-9_-]{20,}$'
        return bool(re.match(pattern, api_key))
    
    @staticmethod
    def validate_file_type(filename: str) -> bool:
        """
        Validate file type against allowed types
        
        Args:
            filename: Name of the file
            
        Returns:
            True if file type is allowed
        """
        if not filename:
            return False
        
        extension = filename.split('.')[-1].lower()
        return extension in Config.ALLOWED_FILE_TYPES
    
    @staticmethod
    def validate_file_size(file_size_bytes: int) -> bool:
        """
        Validate file size against maximum allowed
        
        Args:
            file_size_bytes: File size in bytes
            
        Returns:
            True if file size is within limit
        """
        max_size_bytes = Config.MAX_FILE_SIZE_MB * 1024 * 1024
        return 0 < file_size_bytes <= max_size_bytes
    
    @staticmethod
    def validate_research_question(question: str) -> Dict[str, Any]:
        """
        Validate research question
        
        Args:
            question: The research question
            
        Returns:
            Validation result with feedback
        """
        result = {
            "valid": True,
            "issues": [],
            "suggestions": []
        }
        
        if not question:
            result["valid"] = False
            result["issues"].append("Research question is empty")
            return result
        
        # Check minimum length
        if len(question) < 10:
            result["valid"] = False
            result["issues"].append("Research question is too short")
            result["suggestions"].append("Provide a more detailed research question")
        
        # Check maximum length
        if len(question) > 1000:
            result["issues"].append("Research question is very long")
            result["suggestions"].append("Consider breaking into multiple sub-questions")
        
        # Check if it's actually a question
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'does', 'do', 'is', 'are', 'can', 'could', 'would', 'should']
        if not any(word in question.lower() for word in question_words) and '?' not in question:
            result["suggestions"].append("Consider phrasing as a clear question")
        
        return result
    
    @staticmethod
    def validate_citation_style(style: str) -> bool:
        """
        Validate citation style
        
        Args:
            style: Citation style name
            
        Returns:
            True if valid style
        """
        return style in Config.CITATION_STYLES
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address format
        
        Args:
            email: Email address
            
        Returns:
            True if valid email format
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_year(year: Any) -> bool:
        """
        Validate publication year
        
        Args:
            year: Year value
            
        Returns:
            True if valid year
        """
        try:
            year_int = int(year)
            return 1900 <= year_int <= 2030
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_doi(doi: str) -> bool:
        """
        Validate DOI format
        
        Args:
            doi: Digital Object Identifier
            
        Returns:
            True if valid DOI format
        """
        # DOI pattern: 10.xxxx/xxxxx
        pattern = r'^10\.\d{4,}\/[-._;()\/:a-zA-Z0-9]+$'
        return bool(re.match(pattern, doi))
    
    @staticmethod
    def validate_hypothesis(hypothesis: str) -> Dict[str, Any]:
        """
        Validate research hypothesis
        
        Args:
            hypothesis: The hypothesis text
            
        Returns:
            Validation result
        """
        result = {
            "valid": True,
            "issues": [],
            "suggestions": []
        }
        
        if not hypothesis:
            result["valid"] = False
            result["issues"].append("Hypothesis is empty")
            return result
        
        # Check length
        if len(hypothesis) < 20:
            result["valid"] = False
            result["issues"].append("Hypothesis is too short")
        
        # Check for testable components
        testable_keywords = ['will', 'should', 'increase', 'decrease', 'affect', 'influence', 'correlate', 'predict', 'cause', 'lead to', 'result in']
        if not any(keyword in hypothesis.lower() for keyword in testable_keywords):
            result["suggestions"].append("Ensure hypothesis is testable with clear predictions")
        
        # Check for variables
        if 'and' not in hypothesis.lower() and 'between' not in hypothesis.lower():
            result["suggestions"].append("Consider clearly stating the variables being tested")
        
        return result
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename for safe file operations
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove path traversal attempts
        filename = os.path.basename(filename)
        
        # Replace problematic characters
        invalid_chars = '<>:"|?*\\/\r\n'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        name, ext = os.path.splitext(filename)
        if len(name) > 100:
            name = name[:100]
        
        return name + ext
    
    @staticmethod
    def validate_export_format(format: str) -> bool:
        """
        Validate export format
        
        Args:
            format: Export format
            
        Returns:
            True if valid format
        """
        valid_formats = ['pdf', 'docx', 'latex', 'markdown', 'json', 'csv', 'xlsx']
        return format.lower() in valid_formats
    
    @staticmethod
    def validate_analysis_depth(depth: str) -> bool:
        """
        Validate analysis depth setting
        
        Args:
            depth: Analysis depth
            
        Returns:
            True if valid depth
        """
        return depth in Config.ANALYSIS_DEPTHS
    
    @staticmethod
    def validate_reasoning_level(level: str) -> bool:
        """
        Validate GPT-5 reasoning level
        
        Args:
            level: Reasoning level
            
        Returns:
            True if valid level
        """
        return level in Config.REASONING_LEVELS