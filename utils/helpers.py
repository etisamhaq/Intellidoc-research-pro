"""Helper utilities for the application"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import re
import string
import random

class Helpers:
    """General helper utilities"""
    
    @staticmethod
    def generate_id(prefix: str = "doc") -> str:
        """
        Generate unique ID
        
        Args:
            prefix: Prefix for the ID
            
        Returns:
            Unique ID string
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"{prefix}_{timestamp}_{random_str}"
    
    @staticmethod
    def calculate_reading_time(text: str, wpm: int = 250) -> int:
        """
        Calculate estimated reading time in minutes
        
        Args:
            text: Text content
            wpm: Words per minute (default 250)
            
        Returns:
            Reading time in minutes
        """
        words = len(text.split())
        minutes = words / wpm
        return max(1, round(minutes))
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """
        Truncate text to specified length
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add when truncated
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def extract_keywords(text: str, num_keywords: int = 10) -> List[str]:
        """
        Extract keywords from text
        
        Args:
            text: Source text
            num_keywords: Number of keywords to extract
            
        Returns:
            List of keywords
        """
        # Remove punctuation and convert to lowercase
        text_clean = text.lower()
        for char in string.punctuation:
            text_clean = text_clean.replace(char, ' ')
        
        # Split into words
        words = text_clean.split()
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                     'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                     'could', 'should', 'may', 'might', 'must', 'can', 'could', 'this',
                     'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
        
        # Count word frequency
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_keywords[:num_keywords]]
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean text for processing
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove control characters
        text = ''.join(char for char in text if char.isprintable() or char.isspace())
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text.strip()
    
    @staticmethod
    def calculate_hash(content: str) -> str:
        """
        Calculate SHA256 hash of content
        
        Args:
            content: Content to hash
            
        Returns:
            Hash string
        """
        return hashlib.sha256(content.encode()).hexdigest()
    
    @staticmethod
    def parse_authors(authors_str: str) -> List[str]:
        """
        Parse author string into list
        
        Args:
            authors_str: String containing authors
            
        Returns:
            List of author names
        """
        # Handle different formats
        if ';' in authors_str:
            authors = authors_str.split(';')
        elif ',' in authors_str and '&' in authors_str:
            # Format: "Smith, J., Jones, K., & Williams, R."
            authors = re.split(r',\s*&\s*|,\s*', authors_str)
        elif ',' in authors_str:
            authors = authors_str.split(',')
        elif ' and ' in authors_str:
            authors = authors_str.split(' and ')
        else:
            authors = [authors_str]
        
        # Clean up each author
        return [author.strip() for author in authors if author.strip()]
    
    @staticmethod
    def format_date(date_obj: datetime, format: str = "long") -> str:
        """
        Format date for display
        
        Args:
            date_obj: DateTime object
            format: Format type (short, long, iso)
            
        Returns:
            Formatted date string
        """
        formats = {
            "short": "%m/%d/%Y",
            "long": "%B %d, %Y",
            "iso": "%Y-%m-%d",
            "full": "%A, %B %d, %Y at %I:%M %p"
        }
        
        return date_obj.strftime(formats.get(format, formats["long"]))
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimate token count for GPT models
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    @staticmethod
    def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
        """
        Split list into chunks
        
        Args:
            lst: List to chunk
            chunk_size: Size of each chunk
            
        Returns:
            List of chunks
        """
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
    
    @staticmethod
    def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge multiple dictionaries
        
        Args:
            *dicts: Dictionaries to merge
            
        Returns:
            Merged dictionary
        """
        result = {}
        for d in dicts:
            result.update(d)
        return result
    
    @staticmethod
    def create_progress_message(current: int, total: int, prefix: str = "Progress") -> str:
        """
        Create progress message
        
        Args:
            current: Current item
            total: Total items
            prefix: Message prefix
            
        Returns:
            Progress message
        """
        percentage = (current / total) * 100 if total > 0 else 0
        return f"{prefix}: {current}/{total} ({percentage:.1f}%)"
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """
        Extract URLs from text
        
        Args:
            text: Text containing URLs
            
        Returns:
            List of URLs
        """
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)
    
    @staticmethod
    def calculate_similarity_score(text1: str, text2: str) -> float:
        """
        Calculate simple similarity score between texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        # Simple word overlap calculation
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    @staticmethod
    def format_number(num: float, decimals: int = 2) -> str:
        """
        Format number with thousand separators
        
        Args:
            num: Number to format
            decimals: Decimal places
            
        Returns:
            Formatted number string
        """
        if num >= 1_000_000:
            return f"{num/1_000_000:.{decimals}f}M"
        elif num >= 1_000:
            return f"{num/1_000:.{decimals}f}K"
        else:
            return f"{num:.{decimals}f}"