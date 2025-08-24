"""Literature review generation module"""

from typing import List, Dict, Any, Optional
from core.gpt5_client import GPT5Client
import streamlit as st

class LiteratureReviewGenerator:
    """Generate comprehensive literature reviews using GPT-5"""

    def __init__(self, gpt5_client: GPT5Client):
        self.client = gpt5_client

    def generate_review(
        self,
        papers: List[Dict[str, Any]],
        research_question: str,
        review_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive literature review

        Args:
            papers: List of paper data (content, metadata)
            research_question: The research question to focus on
            review_settings: Settings for the review generation

        Returns:
            Generated literature review with sections
        """
        # Extract paper contents
        paper_contents = [p.get("content", "") for p in papers if p.get("content")]

        if not paper_contents:
            return {
                "success": False,
                "error": "No valid papers provided for review"
            }

        # Generate the review
        result = self.client.generate_literature_review(
            papers=paper_contents,
            research_question=research_question,
            review_depth=review_settings.get("depth", "Comprehensive"),
            include_gaps=review_settings.get("include_gaps", True),
            include_future=review_settings.get("include_future", True)
        )

        if result["success"]:
            # Parse the review into sections
            review_text = result.get("review", "")

            # Handle empty review
            if not review_text:
                review_text = "The literature review is being generated. Please try again if no content appears."

            sections = self._parse_review_sections(review_text)

            return {
                "success": True,
                "full_review": review_text,
                "sections": sections,
                "paper_count": len(papers),
                "metadata": {
                    "research_question": research_question,
                    "review_depth": review_settings.get("depth", "Comprehensive"),
                    "total_words": len(review_text.split()) if review_text else 0
                }
            }
        else:
            return result

    def _parse_review_sections(self, review_text: str) -> Dict[str, str]:
        """
        Parse literature review into sections

        Args:
            review_text: Full review text

        Returns:
            Dictionary of review sections
        """
        sections = {
            "executive_summary": "",
            "key_themes": "",
            "methodologies": "",
            "theoretical_frameworks": "",
            "research_gaps": "",
            "future_directions": "",
            "conclusion": ""
        }

        # Simple section parsing (can be improved with more sophisticated parsing)
        current_section = None
        lines = review_text.split('\n')

        section_markers = {
            "executive summary": "executive_summary",
            "key themes": "key_themes",
            "methodolog": "methodologies",
            "theoretical framework": "theoretical_frameworks",
            "research gap": "research_gaps",
            "future": "future_directions",
            "conclusion": "conclusion"
        }

        for line in lines:
            line_lower = line.lower()

            # Check if this line marks a new section
            for marker, section_key in section_markers.items():
                if marker in line_lower and any(c in line for c in ['#', ':', '1.', '2.', '3.', '4.', '5.', '6.', '7.']):
                    current_section = section_key
                    break

            # Add content to current section
            if current_section:
                sections[current_section] += line + "\n"

        return sections

    def generate_thematic_analysis(
        self,
        papers: List[Dict[str, Any]],
        num_themes: int = 5
    ) -> Dict[str, Any]:
        """
        Generate thematic analysis of papers

        Args:
            papers: List of paper data
            num_themes: Number of themes to identify

        Returns:
            Thematic analysis results
        """
        paper_contents = [p.get("content", "")[:2000] for p in papers if p.get("content")]

        prompt = f"""
        Perform a thematic analysis of the following {len(papers)} research papers.
        Identify and describe the {num_themes} most prominent themes.

        For each theme provide:
        1. Theme name
        2. Description
        3. Which papers discuss this theme
        4. Key insights related to this theme

        Papers:
        {"---PAPER SEPARATOR---".join(paper_contents)}
        """

        try:
            request_params = {
                "model": self.client.model,
                "messages": [
                    {"role": "system", "content": "You are an expert in qualitative research and thematic analysis."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 3000  # Increased for reasoning + response
            }

            # Add reasoning_effort only if supported
            if "aimlapi" in str(self.client.client.base_url).lower():
                request_params["reasoning_effort"] = "high"

            response = self.client.client.chat.completions.create(**request_params)

            return {
                "success": True,
                "themes": response.choices[0].message.content
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def identify_research_gaps(
        self,
        papers: List[Dict[str, Any]],
        research_area: str
    ) -> Dict[str, Any]:
        """
        Identify research gaps from literature

        Args:
            papers: List of paper data
            research_area: The research domain

        Returns:
            Identified research gaps
        """
        paper_contents = [p.get("content", "")[:2000] for p in papers if p.get("content")]

        prompt = f"""
        Based on the following {len(papers)} papers in {research_area}, identify research gaps.

        Provide:
        1. Major unexplored areas
        2. Methodological gaps
        3. Theoretical gaps
        4. Practical application gaps
        5. Recommendations for future research

        Papers:
        {"---PAPER SEPARATOR---".join(paper_contents)}
        """

        try:
            request_params = {
                "model": self.client.model,
                "messages": [
                    {"role": "system", "content": "You are an expert research methodologist specializing in identifying research opportunities."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2500  # Increased for reasoning + response
            }

            # Add reasoning_effort only if supported
            if "aimlapi" in str(self.client.client.base_url).lower():
                request_params["reasoning_effort"] = "high"

            response = self.client.client.chat.completions.create(**request_params)

            return {
                "success": True,
                "gaps": response.choices[0].message.content
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def create_synthesis_matrix(
        self,
        papers: List[Dict[str, Any]],
        categories: List[str]
    ) -> Dict[str, Any]:
        """
        Create a synthesis matrix comparing papers across categories

        Args:
            papers: List of paper data
            categories: Categories to compare

        Returns:
            Synthesis matrix
        """
        paper_titles = [p.get("filename", f"Paper {i+1}") for i, p in enumerate(papers)]
        paper_contents = [p.get("content", "")[:1500] for p in papers if p.get("content")]

        prompt = f"""
        Create a synthesis matrix comparing these {len(papers)} papers across the following categories:
        {', '.join(categories)}

        Format as a table with papers as rows and categories as columns.
        Be concise but comprehensive.

        Papers:
        {chr(10).join([f"{i+1}. {title}" for i, title in enumerate(paper_titles)])}

        Paper contents:
        {"---PAPER SEPARATOR---".join(paper_contents)}
        """

        try:
            request_params = {
                "model": self.client.model,
                "messages": [
                    {"role": "system", "content": "You are an expert at creating research synthesis matrices."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 3000  # Increased for reasoning + response
            }

            # Add reasoning_effort only if supported
            if "aimlapi" in str(self.client.client.base_url).lower():
                request_params["reasoning_effort"] = "medium"

            response = self.client.client.chat.completions.create(**request_params)

            return {
                "success": True,
                "matrix": response.choices[0].message.content,
                "papers": paper_titles,
                "categories": categories
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }