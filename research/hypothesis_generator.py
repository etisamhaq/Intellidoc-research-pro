"""Hypothesis generation module for research"""

from typing import List, Dict, Any, Optional
from core.gpt5_client import GPT5Client
import logging

logger = logging.getLogger(__name__)

class HypothesisGenerator:
    """Generate research hypotheses using GPT-5"""
    
    def __init__(self, gpt5_client: GPT5Client):
        self.client = gpt5_client
        
    def generate_hypotheses(
        self,
        research_area: str,
        literature_summary: str,
        num_hypotheses: int = 5,
        hypothesis_type: str = "empirical"
    ) -> Dict[str, Any]:
        """
        Generate research hypotheses based on literature
        
        Args:
            research_area: The research domain
            literature_summary: Summary of existing literature
            num_hypotheses: Number of hypotheses to generate
            hypothesis_type: Type of hypotheses (empirical, theoretical, exploratory)
            
        Returns:
            Generated hypotheses with rationale
        """
        return self.client.generate_hypotheses(
            research_area=research_area,
            literature_summary=literature_summary,
            num_hypotheses=num_hypotheses
        )
    
    def refine_hypothesis(
        self,
        hypothesis: str,
        feedback: str
    ) -> Dict[str, Any]:
        """
        Refine a hypothesis based on feedback
        
        Args:
            hypothesis: Original hypothesis
            feedback: Feedback for refinement
            
        Returns:
            Refined hypothesis
        """
        prompt = f"""
        Original Hypothesis: {hypothesis}
        
        Feedback: {feedback}
        
        Please refine the hypothesis based on the feedback, making it more:
        1. Specific and measurable
        2. Testable with clear variables
        3. Grounded in theory
        4. Practically feasible
        
        Provide the refined hypothesis with explanation of changes.
        """
        
        try:
            response = self.client.client.chat.completions.create(
                model=self.client.model,
                messages=[
                    {"role": "system", "content": "You are an expert research methodologist."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )
            
            return {
                "success": True,
                "refined_hypothesis": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Error refining hypothesis: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_null_alternative(
        self,
        research_hypothesis: str
    ) -> Dict[str, Any]:
        """
        Generate null and alternative hypotheses
        
        Args:
            research_hypothesis: The research hypothesis
            
        Returns:
            Null and alternative hypotheses
        """
        prompt = f"""
        Research Hypothesis: {research_hypothesis}
        
        Based on this research hypothesis, generate:
        1. Null hypothesis (H0)
        2. Alternative hypothesis (H1)
        3. Statistical approach for testing
        4. Required sample size estimation
        5. Potential Type I and Type II errors
        """
        
        try:
            response = self.client.client.chat.completions.create(
                model=self.client.model,
                messages=[
                    {"role": "system", "content": "You are an expert in research methodology and statistics."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500
            )
            
            return {
                "success": True,
                "hypotheses": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Error generating null/alternative hypotheses: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def evaluate_hypothesis_quality(
        self,
        hypothesis: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Evaluate the quality of a hypothesis
        
        Args:
            hypothesis: The hypothesis to evaluate
            context: Additional context about the research
            
        Returns:
            Quality evaluation with suggestions
        """
        prompt = f"""
        Evaluate the following research hypothesis:
        
        Hypothesis: {hypothesis}
        {"Context: " + context if context else ""}
        
        Assess the hypothesis on:
        1. Clarity and specificity (1-10)
        2. Testability (1-10)
        3. Theoretical grounding (1-10)
        4. Originality (1-10)
        5. Feasibility (1-10)
        
        Provide:
        - Overall quality score
        - Strengths
        - Weaknesses
        - Suggestions for improvement
        """
        
        try:
            response = self.client.client.chat.completions.create(
                model=self.client.model,
                messages=[
                    {"role": "system", "content": "You are an expert research methodologist and peer reviewer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500
            )
            
            return {
                "success": True,
                "evaluation": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Error evaluating hypothesis: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_research_questions(
        self,
        hypothesis: str,
        num_questions: int = 5
    ) -> Dict[str, Any]:
        """
        Generate research questions from a hypothesis
        
        Args:
            hypothesis: The hypothesis
            num_questions: Number of questions to generate
            
        Returns:
            Research questions
        """
        prompt = f"""
        Based on the following hypothesis, generate {num_questions} specific research questions:
        
        Hypothesis: {hypothesis}
        
        For each question provide:
        1. The research question
        2. Type (descriptive, exploratory, explanatory, evaluative)
        3. Data needed to answer it
        4. Potential methods for investigation
        """
        
        try:
            response = self.client.client.chat.completions.create(
                model=self.client.model,
                messages=[
                    {"role": "system", "content": "You are an expert in research design."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000
            )
            
            return {
                "success": True,
                "questions": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Error generating research questions: {e}")
            return {
                "success": False,
                "error": str(e)
            }