"""Research gap identification module"""

from typing import List, Dict, Any, Optional
from core.gpt5_client import GPT5Client
import logging

logger = logging.getLogger(__name__)

class ResearchGapFinder:
    """Identify research gaps from literature analysis"""
    
    def __init__(self, gpt5_client: GPT5Client):
        self.client = gpt5_client
        
    def identify_gaps(
        self,
        papers: List[Dict[str, Any]],
        research_area: str,
        gap_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Identify research gaps from analyzed papers
        
        Args:
            papers: List of paper data
            research_area: The research domain
            gap_types: Types of gaps to identify
            
        Returns:
            Identified research gaps
        """
        if gap_types is None:
            gap_types = [
                "Methodological",
                "Theoretical",
                "Empirical",
                "Geographical",
                "Temporal",
                "Population"
            ]
        
        # Prepare paper summaries
        paper_summaries = []
        for paper in papers[:10]:  # Limit to 10 papers for API
            summary = f"Title: {paper.get('title', 'Unknown')}\n"
            summary += f"Content: {paper.get('content', '')[:500]}\n"
            paper_summaries.append(summary)
        
        prompt = f"""
        Research Area: {research_area}
        
        Based on the following papers, identify research gaps in these categories:
        {', '.join(gap_types)}
        
        Papers analyzed:
        {"---".join(paper_summaries)}
        
        For each gap identified, provide:
        1. Gap description
        2. Category
        3. Importance (High/Medium/Low)
        4. Suggested approach to address it
        5. Potential impact if addressed
        """
        
        try:
            request_params = {
                "model": self.client.model,
                "messages": [
                    {"role": "system", "content": "You are an expert in research methodology and literature analysis."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000
            }
            
            # Add reasoning_effort only if supported
            if "aimlapi" in str(self.client.client.base_url).lower():
                request_params["reasoning_effort"] = "high"
            
            response = self.client.client.chat.completions.create(**request_params)
            
            return {
                "success": True,
                "gaps": response.choices[0].message.content,
                "paper_count": len(papers)
            }
            
        except Exception as e:
            logger.error(f"Error identifying research gaps: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def prioritize_gaps(
        self,
        gaps: List[Dict[str, Any]],
        criteria: List[str] = None
    ) -> Dict[str, Any]:
        """
        Prioritize research gaps based on criteria
        
        Args:
            gaps: List of identified gaps
            criteria: Prioritization criteria
            
        Returns:
            Prioritized gaps
        """
        if criteria is None:
            criteria = [
                "Impact potential",
                "Feasibility",
                "Resource requirements",
                "Timeline",
                "Innovation potential"
            ]
        
        gaps_text = "\n".join([f"- {gap}" for gap in gaps])
        
        prompt = f"""
        Research Gaps:
        {gaps_text}
        
        Prioritize these gaps based on:
        {', '.join(criteria)}
        
        Provide:
        1. Ranked list of gaps (highest to lowest priority)
        2. Scoring for each criterion (1-10)
        3. Overall priority score
        4. Justification for ranking
        5. Recommended sequence for addressing gaps
        """
        
        try:
            response = self.client.client.chat.completions.create(
                model=self.client.model,
                messages=[
                    {"role": "system", "content": "You are an expert in research planning and prioritization."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500
            )
            
            return {
                "success": True,
                "prioritized_gaps": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Error prioritizing gaps: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_research_proposal(
        self,
        gap: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Generate a research proposal to address a gap
        
        Args:
            gap: The research gap to address
            context: Additional context
            
        Returns:
            Research proposal outline
        """
        prompt = f"""
        Research Gap: {gap}
        {"Context: " + context if context else ""}
        
        Generate a research proposal outline to address this gap:
        
        1. Title
        2. Research Objectives (3-5 specific objectives)
        3. Research Questions
        4. Theoretical Framework
        5. Methodology
           - Research Design
           - Data Collection Methods
           - Sample/Participants
           - Analysis Approach
        6. Expected Outcomes
        7. Timeline (12-month plan)
        8. Resources Required
        9. Potential Challenges and Mitigation
        10. Significance and Impact
        """
        
        try:
            request_params = {
                "model": self.client.model,
                "messages": [
                    {"role": "system", "content": "You are an expert in research proposal development."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 3000
            }
            
            # Add reasoning_effort only if supported
            if "aimlapi" in str(self.client.client.base_url).lower():
                request_params["reasoning_effort"] = "high"
            
            response = self.client.client.chat.completions.create(**request_params)
            
            return {
                "success": True,
                "proposal": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Error generating research proposal: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_gap_trends(
        self,
        gaps: List[str],
        time_period: str = "5 years"
    ) -> Dict[str, Any]:
        """
        Analyze trends in research gaps over time
        
        Args:
            gaps: List of research gaps
            time_period: Time period for analysis
            
        Returns:
            Trend analysis
        """
        gaps_text = "\n".join([f"- {gap}" for gap in gaps])
        
        prompt = f"""
        Research Gaps Identified:
        {gaps_text}
        
        Time Period: {time_period}
        
        Analyze these gaps to identify:
        1. Emerging themes and patterns
        2. Persistent gaps (unaddressed over time)
        3. Recently addressed gaps
        4. Interdisciplinary opportunities
        5. Technology-enabled research opportunities
        6. Predicted future gaps
        
        Provide insights on how the research landscape is evolving.
        """
        
        try:
            response = self.client.client.chat.completions.create(
                model=self.client.model,
                messages=[
                    {"role": "system", "content": "You are an expert in research trends and forecasting."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500
            )
            
            return {
                "success": True,
                "trends": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Error analyzing gap trends: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def suggest_collaborations(
        self,
        gap: str,
        expertise_needed: List[str] = None
    ) -> Dict[str, Any]:
        """
        Suggest collaborations to address research gaps
        
        Args:
            gap: The research gap
            expertise_needed: Types of expertise required
            
        Returns:
            Collaboration suggestions
        """
        if expertise_needed is None:
            expertise_needed = []
        
        prompt = f"""
        Research Gap: {gap}
        {"Required Expertise: " + ", ".join(expertise_needed) if expertise_needed else ""}
        
        Suggest collaboration strategy:
        1. Key disciplines to involve
        2. Types of institutions (academic, industry, government)
        3. Specific expertise required
        4. Potential collaboration models
        5. Resource sharing opportunities
        6. Expected benefits of collaboration
        7. Potential challenges and solutions
        """
        
        try:
            response = self.client.client.chat.completions.create(
                model=self.client.model,
                messages=[
                    {"role": "system", "content": "You are an expert in research collaboration and interdisciplinary work."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500
            )
            
            return {
                "success": True,
                "collaborations": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Error suggesting collaborations: {e}")
            return {
                "success": False,
                "error": str(e)
            }