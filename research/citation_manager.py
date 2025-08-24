"""Citation management system for academic research"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime

class CitationManager:
    """Manage citations and bibliographies in various academic formats"""
    
    def __init__(self):
        self.citations = []
        
    def extract_citations(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract citations from academic text
        
        Args:
            text: Text containing citations
            
        Returns:
            List of extracted citations
        """
        citations = []
        
        # Pattern for in-text citations (Author, Year)
        pattern1 = r'\(([A-Z][a-zA-Z\s&,]+),?\s*(\d{4})\)'
        matches1 = re.findall(pattern1, text)
        
        for match in matches1:
            citations.append({
                "authors": match[0].strip(),
                "year": match[1],
                "type": "in-text"
            })
        
        # Pattern for numbered citations [1], [2], etc.
        pattern2 = r'\[(\d+)\]'
        matches2 = re.findall(pattern2, text)
        
        for match in matches2:
            citations.append({
                "number": match,
                "type": "numbered"
            })
        
        return citations
    
    def format_citation(
        self,
        authors: List[str],
        year: int,
        title: str,
        journal: str = "",
        volume: str = "",
        issue: str = "",
        pages: str = "",
        doi: str = "",
        style: str = "APA 7th"
    ) -> str:
        """
        Format a citation in the specified style
        
        Args:
            authors: List of author names
            year: Publication year
            title: Article/book title
            journal: Journal name
            volume: Volume number
            issue: Issue number
            pages: Page numbers
            doi: Digital Object Identifier
            style: Citation style
            
        Returns:
            Formatted citation
        """
        formatters = {
            "APA 7th": self._format_apa,
            "MLA 9th": self._format_mla,
            "Chicago 17th": self._format_chicago,
            "IEEE": self._format_ieee,
            "Harvard": self._format_harvard
        }
        
        formatter = formatters.get(style, self._format_apa)
        return formatter(authors, year, title, journal, volume, issue, pages, doi)
    
    def _format_apa(
        self,
        authors: List[str],
        year: int,
        title: str,
        journal: str,
        volume: str,
        issue: str,
        pages: str,
        doi: str
    ) -> str:
        """Format citation in APA 7th edition style"""
        # Format authors
        if len(authors) == 1:
            author_str = authors[0]
        elif len(authors) == 2:
            author_str = f"{authors[0]} & {authors[1]}"
        else:
            author_str = f"{authors[0]} et al."
        
        # Build citation
        citation = f"{author_str} ({year}). {title}."
        
        if journal:
            citation += f" {journal}"
            if volume:
                citation += f", {volume}"
                if issue:
                    citation += f"({issue})"
            if pages:
                citation += f", {pages}"
        
        if doi:
            citation += f". https://doi.org/{doi}"
        
        return citation
    
    def _format_mla(
        self,
        authors: List[str],
        year: int,
        title: str,
        journal: str,
        volume: str,
        issue: str,
        pages: str,
        doi: str
    ) -> str:
        """Format citation in MLA 9th edition style"""
        # Format authors
        if len(authors) == 1:
            author_str = authors[0]
        elif len(authors) == 2:
            author_str = f"{authors[0]}, and {authors[1]}"
        else:
            author_str = f"{authors[0]}, et al."
        
        # Build citation
        citation = f'{author_str}. "{title}."'
        
        if journal:
            citation += f" {journal}"
            if volume:
                citation += f", vol. {volume}"
            if issue:
                citation += f", no. {issue}"
            citation += f", {year}"
            if pages:
                citation += f", pp. {pages}"
        
        return citation + "."
    
    def _format_chicago(
        self,
        authors: List[str],
        year: int,
        title: str,
        journal: str,
        volume: str,
        issue: str,
        pages: str,
        doi: str
    ) -> str:
        """Format citation in Chicago 17th edition style"""
        # Format authors
        author_str = ", ".join(authors)
        
        # Build citation
        citation = f'{author_str}. "{title}."'
        
        if journal:
            citation += f" {journal} {volume}"
            if issue:
                citation += f", no. {issue}"
            citation += f" ({year})"
            if pages:
                citation += f": {pages}"
        
        if doi:
            citation += f". https://doi.org/{doi}"
        
        return citation + "."
    
    def _format_ieee(
        self,
        authors: List[str],
        year: int,
        title: str,
        journal: str,
        volume: str,
        issue: str,
        pages: str,
        doi: str
    ) -> str:
        """Format citation in IEEE style"""
        # Format authors with initials
        formatted_authors = []
        for author in authors:
            parts = author.split()
            if len(parts) >= 2:
                initials = ". ".join([p[0] for p in parts[:-1]]) + "."
                formatted_authors.append(f"{initials} {parts[-1]}")
            else:
                formatted_authors.append(author)
        
        if len(formatted_authors) > 3:
            author_str = f"{formatted_authors[0]} et al."
        else:
            author_str = ", ".join(formatted_authors)
        
        # Build citation
        citation = f'{author_str}, "{title},"'
        
        if journal:
            citation += f" {journal}"
            if volume:
                citation += f", vol. {volume}"
            if issue:
                citation += f", no. {issue}"
            if pages:
                citation += f", pp. {pages}"
            citation += f", {year}"
        
        return citation + "."
    
    def _format_harvard(
        self,
        authors: List[str],
        year: int,
        title: str,
        journal: str,
        volume: str,
        issue: str,
        pages: str,
        doi: str
    ) -> str:
        """Format citation in Harvard style"""
        # Format authors
        if len(authors) == 1:
            author_str = authors[0]
        elif len(authors) == 2:
            author_str = f"{authors[0]} and {authors[1]}"
        else:
            author_str = f"{authors[0]} et al."
        
        # Build citation
        citation = f"{author_str} {year}, '{title}'"
        
        if journal:
            citation += f", {journal}"
            if volume:
                citation += f", vol. {volume}"
            if issue:
                citation += f", no. {issue}"
            if pages:
                citation += f", pp. {pages}"
        
        return citation + "."
    
    def generate_bibliography(
        self,
        citations: List[Dict[str, Any]],
        style: str = "APA 7th"
    ) -> str:
        """
        Generate a formatted bibliography
        
        Args:
            citations: List of citation data
            style: Citation style
            
        Returns:
            Formatted bibliography
        """
        bibliography = []
        
        for citation in citations:
            formatted = self.format_citation(
                authors=citation.get("authors", []),
                year=citation.get("year", ""),
                title=citation.get("title", ""),
                journal=citation.get("journal", ""),
                volume=citation.get("volume", ""),
                issue=citation.get("issue", ""),
                pages=citation.get("pages", ""),
                doi=citation.get("doi", ""),
                style=style
            )
            bibliography.append(formatted)
        
        # Sort alphabetically
        bibliography.sort()
        
        return "\n\n".join(bibliography)
    
    def validate_citation(self, citation: Dict[str, Any]) -> bool:
        """
        Validate citation data
        
        Args:
            citation: Citation data to validate
            
        Returns:
            True if citation is valid
        """
        required_fields = ["authors", "year", "title"]
        
        for field in required_fields:
            if field not in citation or not citation[field]:
                return False
        
        # Validate year
        try:
            year = int(citation["year"])
            if year < 1500 or year > datetime.now().year + 1:
                return False
        except:
            return False
        
        return True