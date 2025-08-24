"""Integration tests for IntelliDoc Research Pro"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.gpt5_client import GPT5Client
from modules.file_processor import FileProcessor
from research.citation_manager import CitationManager
from research.literature_review import LiteratureReviewGenerator
from research.hypothesis_generator import HypothesisGenerator
from research.research_gap_finder import ResearchGapFinder
from utils.validators import Validators
from utils.helpers import Helpers

class TestGPT5Client(unittest.TestCase):
    """Test GPT-5 client functionality"""
    
    def setUp(self):
        """Set up test client"""
        self.client = GPT5Client()
    
    def test_client_initialization(self):
        """Test client initialization"""
        self.assertIsNotNone(self.client)
        self.assertIsNotNone(self.client.model)
    
    def test_analyze_document(self):
        """Test document analysis"""
        content = "This is a test document for analysis."
        result = self.client.analyze_document(content, "summary")
        
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        
        if result["success"]:
            self.assertIn("analysis", result)

class TestFileProcessor(unittest.TestCase):
    """Test file processing functionality"""
    
    def test_chunk_text(self):
        """Test text chunking"""
        text = " ".join(["word"] * 1000)
        chunks = FileProcessor.chunk_text(text, max_chunk_size=100)
        
        self.assertIsInstance(chunks, list)
        self.assertTrue(len(chunks) > 1)
        
        for chunk in chunks:
            self.assertTrue(len(chunk) <= 100)

class TestCitationManager(unittest.TestCase):
    """Test citation management"""
    
    def setUp(self):
        self.manager = CitationManager()
    
    def test_format_citation_apa(self):
        """Test APA citation formatting"""
        citation = self.manager.format_citation(
            authors=["Smith, J.", "Jones, K."],
            year=2023,
            title="Test Article",
            journal="Test Journal",
            volume="10",
            issue="2",
            pages="100-110",
            style="APA 7th"
        )
        
        self.assertIsInstance(citation, str)
        self.assertIn("Smith", citation)
        self.assertIn("2023", citation)
    
    def test_extract_citations(self):
        """Test citation extraction"""
        text = "According to Smith (2023), this is important. Jones et al. (2022) disagree."
        citations = self.manager.extract_citations(text)
        
        self.assertIsInstance(citations, list)
        self.assertTrue(len(citations) >= 2)
    
    def test_validate_citation(self):
        """Test citation validation"""
        valid_citation = {
            "authors": ["Smith, J."],
            "year": "2023",
            "title": "Test Article"
        }
        
        invalid_citation = {
            "authors": [],
            "year": "invalid",
            "title": ""
        }
        
        self.assertTrue(self.manager.validate_citation(valid_citation))
        self.assertFalse(self.manager.validate_citation(invalid_citation))

class TestValidators(unittest.TestCase):
    """Test validation utilities"""
    
    def test_validate_api_key(self):
        """Test API key validation"""
        valid_key = "a" * 32
        invalid_key = "short"
        placeholder = "your_api_key_here_replace_this"
        
        self.assertTrue(Validators.validate_api_key(valid_key))
        self.assertFalse(Validators.validate_api_key(invalid_key))
        self.assertFalse(Validators.validate_api_key(placeholder))
    
    def test_validate_file_type(self):
        """Test file type validation"""
        self.assertTrue(Validators.validate_file_type("document.pdf"))
        self.assertTrue(Validators.validate_file_type("image.jpg"))
        self.assertFalse(Validators.validate_file_type("script.exe"))
    
    def test_validate_research_question(self):
        """Test research question validation"""
        good_question = "How does climate change affect agricultural productivity?"
        bad_question = "Climate"
        
        good_result = Validators.validate_research_question(good_question)
        bad_result = Validators.validate_research_question(bad_question)
        
        self.assertTrue(good_result["valid"])
        self.assertFalse(bad_result["valid"])
    
    def test_validate_email(self):
        """Test email validation"""
        self.assertTrue(Validators.validate_email("user@example.com"))
        self.assertFalse(Validators.validate_email("invalid-email"))
    
    def test_validate_year(self):
        """Test year validation"""
        self.assertTrue(Validators.validate_year(2023))
        self.assertTrue(Validators.validate_year("2023"))
        self.assertFalse(Validators.validate_year(1800))
        self.assertFalse(Validators.validate_year("invalid"))

class TestHelpers(unittest.TestCase):
    """Test helper utilities"""
    
    def test_generate_id(self):
        """Test ID generation"""
        id1 = Helpers.generate_id("test")
        id2 = Helpers.generate_id("test")
        
        self.assertTrue(id1.startswith("test_"))
        self.assertNotEqual(id1, id2)
    
    def test_calculate_reading_time(self):
        """Test reading time calculation"""
        text = " ".join(["word"] * 250)  # 250 words
        time = Helpers.calculate_reading_time(text)
        
        self.assertEqual(time, 1)
    
    def test_truncate_text(self):
        """Test text truncation"""
        text = "This is a long text that needs to be truncated"
        truncated = Helpers.truncate_text(text, max_length=20)
        
        self.assertTrue(len(truncated) <= 20)
        self.assertTrue(truncated.endswith("..."))
    
    def test_extract_keywords(self):
        """Test keyword extraction"""
        text = "Machine learning is important. Machine learning algorithms are powerful."
        keywords = Helpers.extract_keywords(text, num_keywords=3)
        
        self.assertIsInstance(keywords, list)
        self.assertIn("machine", keywords)
        self.assertIn("learning", keywords)
    
    def test_format_file_size(self):
        """Test file size formatting"""
        self.assertEqual(Helpers.format_file_size(1024), "1.00 KB")
        self.assertEqual(Helpers.format_file_size(1024 * 1024), "1.00 MB")
    
    def test_parse_authors(self):
        """Test author parsing"""
        authors1 = "Smith, J.; Jones, K.; Williams, R."
        parsed1 = Helpers.parse_authors(authors1)
        self.assertEqual(len(parsed1), 3)
        
        authors2 = "Smith, J., Jones, K., & Williams, R."
        parsed2 = Helpers.parse_authors(authors2)
        self.assertEqual(len(parsed2), 3)
    
    def test_calculate_similarity(self):
        """Test similarity calculation"""
        text1 = "machine learning is important"
        text2 = "machine learning is very important"
        text3 = "completely different text here"
        
        score1 = Helpers.calculate_similarity_score(text1, text2)
        score2 = Helpers.calculate_similarity_score(text1, text3)
        
        self.assertTrue(score1 > score2)
        self.assertTrue(0 <= score1 <= 1)
        self.assertTrue(0 <= score2 <= 1)

class TestResearchModules(unittest.TestCase):
    """Test research-specific modules"""
    
    def setUp(self):
        self.client = GPT5Client()
        self.lit_review = LiteratureReviewGenerator(self.client)
        self.hypothesis_gen = HypothesisGenerator(self.client)
        self.gap_finder = ResearchGapFinder(self.client)
    
    def test_literature_review_initialization(self):
        """Test literature review generator initialization"""
        self.assertIsNotNone(self.lit_review)
        self.assertIsNotNone(self.lit_review.client)
    
    def test_hypothesis_generator_initialization(self):
        """Test hypothesis generator initialization"""
        self.assertIsNotNone(self.hypothesis_gen)
        self.assertIsNotNone(self.hypothesis_gen.client)
    
    def test_gap_finder_initialization(self):
        """Test research gap finder initialization"""
        self.assertIsNotNone(self.gap_finder)
        self.assertIsNotNone(self.gap_finder.client)

def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], exit=False, verbosity=2)

if __name__ == "__main__":
    run_tests()