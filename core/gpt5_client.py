"""GPT-5 Comet API Client Integration"""

from openai import OpenAI
import json
from typing import Dict, List, Optional, Any
from config.settings import Config
import streamlit as st
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPT5Client:
    """Client for interacting with GPT-5 via Comet API"""

    def __init__(self, api_key: str = None):
        """Initialize GPT-5 client with Comet API"""
        self.api_key = api_key or Config.COMET_API_KEY
        self.using_comet = False

        if not self.api_key:
            # Fallback to AI/ML API if available
            self.api_key = Config.AIMLAPI_KEY
            base_url = Config.AIMLAPI_BASE_URL
            logger.warning("Using AI/ML API as fallback")
        else:
            base_url = Config.COMET_BASE_URL
            self.using_comet = True
            logger.info("Using Comet API")

        try:
            self.client = OpenAI(
                base_url=base_url,
                api_key=self.api_key
            )
        except Exception as e:
            logger.error(f"Failed to initialize API client: {e}")
            raise

        # Use GPT-5-nano model (available on both APIs)
        self.model = Config.GPT5_MODEL  # This is gpt-5-nano from .env
        logger.info(f"Using model: {self.model} on {'Comet' if self.using_comet else 'AI/ML'} API")

        self.retry_attempts = 3
        self.retry_delay = 1

    def analyze_document(
        self,
        content: str,
        analysis_type: str = "comprehensive",
        reasoning_level: str = "high",
        max_tokens: int = 6000  # Increased significantly to accommodate reasoning tokens
    ) -> Dict[str, Any]:
        """
        Analyze a document using GPT-5

        Args:
            content: Document content to analyze
            analysis_type: Type of analysis to perform
            reasoning_level: GPT-5 reasoning effort level
            max_tokens: Maximum tokens in response

        Returns:
            Analysis results
        """
        # Input validation
        if not content or len(content.strip()) == 0:
            return {
                "success": False,
                "error": "No content provided for analysis"
            }

        # Try API call with retries
        for attempt in range(self.retry_attempts):
            try:
                system_prompt = self._get_system_prompt(analysis_type)

                # Build request parameters - Use higher token allocation for GPT-5-nano reasoning
                request_params = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Analyze the following document:\n\n{content}"}
                    ],
                    "max_tokens": max(max_tokens, 4000),  # Ensure minimum 4000 tokens for reasoning + response
                    "temperature": 0.7
                }

                # Add reasoning_effort only if supported (AI/ML API)
                if not self.using_comet and "aimlapi" in str(self.client.base_url).lower():
                    request_params["reasoning_effort"] = reasoning_level

                logger.info(f"Making API request to: {self.client.base_url}")
                logger.info(f"Using model: {self.model}")
                logger.debug(f"Request params: {request_params}")

                response = self.client.chat.completions.create(**request_params)

                # Debug logging
                logger.debug(f"Response object: {response}")
                if response and response.choices:
                    logger.debug(f"Number of choices: {len(response.choices)}")
                    if len(response.choices) > 0:
                        logger.debug(f"First choice: {response.choices[0]}")
                        logger.debug(f"Message: {response.choices[0].message}")
                        logger.debug(f"Content: {repr(response.choices[0].message.content)}")

                # Check if response has content
                if response and response.choices and len(response.choices) > 0:
                    content = response.choices[0].message.content
                    if content is None or content == "":
                        logger.warning(f"Empty response content from API: {repr(content)}")
                        logger.warning(f"Full response: {response}")
                        content = "The API returned an empty response. This might be due to content filtering or model limitations. Please try with different content or a shorter text."
                else:
                    logger.error("Invalid response structure from API")
                    logger.error(f"Full response: {response}")
                    content = "Error: Invalid response from API. Please try again."

                usage_info = None
                if hasattr(response, 'usage'):
                    try:
                        if hasattr(response.usage, 'dict'):
                            usage_info = response.usage.dict()
                        else:
                            usage_info = {
                                'prompt_tokens': getattr(response.usage, 'prompt_tokens', 0),
                                'completion_tokens': getattr(response.usage, 'completion_tokens', 0),
                                'total_tokens': getattr(response.usage, 'total_tokens', 0)
                            }
                    except Exception as e:
                        logger.warning(f"Could not extract usage info: {e}")

                return {
                    "success": True,
                    "analysis": content,
                    "usage": usage_info,
                    "model_used": self.model,
                    "api_used": "Comet" if self.using_comet else "AI/ML"
                }

            except Exception as e:
                logger.error(f"API call attempt {attempt + 1} failed: {e}")
                logger.error(f"Exception type: {type(e)}")
                logger.error(f"Exception details: {str(e)}")

                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    return {
                        "success": False,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "message": f"API call failed after {self.retry_attempts} attempts. Please check your API key, internet connection, and try again.",
                        "model_used": self.model,
                        "api_used": "Comet" if self.using_comet else "AI/ML"
                    }

    def generate_literature_review(
        self,
        papers: List[str],
        research_question: str,
        review_depth: str = "Comprehensive",
        include_gaps: bool = True,
        include_future: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive literature review from multiple papers

        Args:
            papers: List of paper contents
            research_question: The research question to focus on
            review_depth: Depth of analysis
            include_gaps: Whether to identify research gaps
            include_future: Whether to suggest future research

        Returns:
            Literature review results
        """
        # Input validation
        if not papers or len(papers) == 0:
            return {
                "success": False,
                "error": "No papers provided for literature review"
            }

        if not research_question or len(research_question.strip()) == 0:
            return {
                "success": False,
                "error": "No research question provided"
            }

        try:
            # Combine papers for analysis - limit content to avoid token limits
            combined_content = "\n\n---NEW PAPER---\n\n".join([
                paper[:3000] for paper in papers[:10] if paper and len(paper.strip()) > 0
            ])

            if not combined_content:
                return {
                    "success": False,
                    "error": "No valid paper content found"
                }

            prompt = f"""
            Generate a comprehensive literature review based on the following papers.

            Research Question: {research_question}
            Analysis Depth: {review_depth}

            Please provide:
            1. Executive Summary
            2. Key Themes and Findings
            3. Methodological Approaches
            4. Theoretical Frameworks
            {"5. Research Gaps" if include_gaps else ""}
            {"6. Future Research Directions" if include_future else ""}
            7. Conclusion

            Papers to analyze:
            {combined_content}
            """

            # Build request parameters - Allocate sufficient tokens for reasoning + response
            request_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert academic researcher specializing in systematic literature reviews. Provide comprehensive, well-structured reviews with clear sections and evidence-based insights."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 6000,  # Higher allocation for comprehensive literature reviews
                "temperature": 0.7
            }

            # Add reasoning_effort only if supported
            if not self.using_comet and "aimlapi" in str(self.client.base_url).lower():
                request_params["reasoning_effort"] = "high"

            logger.info(f"Generating literature review using {self.model}")
            logger.info(f"Papers count: {len(papers)}, Research question: {research_question[:100]}...")

            response = self.client.chat.completions.create(**request_params)

            # Check if response has content
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if not content or content.strip() == "":
                    logger.warning("Empty literature review response from API")
                    logger.warning(f"Full response: {response}")
                    content = f"Literature review generation completed but returned empty content. This may be due to content filtering or API limitations. Please try with shorter papers or a different research question. Papers analyzed: {len(papers)}"
            else:
                logger.error("Invalid response structure for literature review")
                logger.error(f"Full response: {response}")
                content = "Error: Unable to generate literature review due to invalid API response. Please try again."

            return {
                "success": True,
                "review": content,
                "paper_count": len(papers),
                "model_used": self.model,
                "api_used": "Comet" if self.using_comet else "AI/ML"
            }

        except Exception as e:
            logger.error(f"Literature review generation failed: {e}")
            logger.error(f"Exception type: {type(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "message": f"Failed to generate literature review: {str(e)}"
            }

    def compare_documents(
        self,
        documents: List[str],
        comparison_aspects: List[str] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple documents

        Args:
            documents: List of document contents
            comparison_aspects: Specific aspects to compare

        Returns:
            Comparison results
        """
        if comparison_aspects is None:
            comparison_aspects = [
                "Main arguments",
                "Methodology",
                "Key findings",
                "Limitations",
                "Conclusions"
            ]

        try:
            prompt = f"""
            Compare the following {len(documents)} documents across these aspects:
            {', '.join(comparison_aspects)}

            Provide a detailed comparison table and analysis.

            Documents:
            {"---DOCUMENT SEPARATOR---".join(documents)}
            """

            request_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert document analyst."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 4000  # Increased for reasoning + response
            }

            if "aimlapi" in str(self.client.base_url).lower():
                request_params["reasoning_effort"] = "high"

            response = self.client.chat.completions.create(**request_params)

            # Check response content
            content = ""
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content or "No comparison results returned."

            return {
                "success": True,
                "comparison": content
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def answer_research_question(
        self,
        question: str,
        context: str,
        provide_citations: bool = True
    ) -> Dict[str, Any]:
        """
        Answer a research question based on provided context

        Args:
            question: The research question
            context: Document context to base answer on
            provide_citations: Whether to include citations

        Returns:
            Answer with optional citations
        """
        try:
            prompt = f"""
            Based on the following context, answer this research question:

            Question: {question}

            {"Please provide specific citations from the text to support your answer." if provide_citations else ""}

            Context:
            {context}
            """

            request_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a research assistant. Provide accurate, evidence-based answers."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000  # Increased for reasoning + response
            }

            if "aimlapi" in str(self.client.base_url).lower():
                request_params["reasoning_effort"] = "medium"

            response = self.client.chat.completions.create(**request_params)

            # Check response content
            content = ""
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content or "No answer generated."

            return {
                "success": True,
                "answer": content
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def generate_hypotheses(
        self,
        research_area: str,
        literature_summary: str,
        num_hypotheses: int = 5
    ) -> Dict[str, Any]:
        """
        Generate research hypotheses based on literature

        Args:
            research_area: The research domain
            literature_summary: Summary of existing literature
            num_hypotheses: Number of hypotheses to generate

        Returns:
            Generated hypotheses with rationale
        """
        # Input validation
        if not research_area or len(research_area.strip()) == 0:
            return {
                "success": False,
                "error": "No research area provided"
            }

        if not literature_summary or len(literature_summary.strip()) == 0:
            return {
                "success": False,
                "error": "No literature summary provided"
            }

        try:
            prompt = f"""
            Based on the following research area and literature summary, generate {num_hypotheses} testable research hypotheses.

            Research Area: {research_area}

            Literature Summary:
            {literature_summary}

            For each hypothesis, provide:
            1. The hypothesis statement
            2. Rationale based on the literature
            3. Suggested methodology for testing
            4. Expected outcomes

            Please ensure each hypothesis is clearly numbered and well-structured.
            """

            request_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert research methodologist specializing in hypothesis generation. Generate clear, testable hypotheses with detailed rationale and methodology."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 4000,  # Increased significantly for reasoning + response
                "temperature": 0.7
            }

            # Add reasoning_effort only if supported
            if not self.using_comet and "aimlapi" in str(self.client.base_url).lower():
                request_params["reasoning_effort"] = "high"

            logger.info(f"Generating {num_hypotheses} hypotheses for research area: {research_area[:100]}...")
            response = self.client.chat.completions.create(**request_params)

            # Check response content with detailed logging
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if not content or content.strip() == "":
                    logger.warning("Empty hypothesis generation response from API")
                    logger.warning(f"Full response: {response}")
                    content = f"Hypothesis generation completed but returned empty content. This may be due to content filtering or API limitations. Please try with a different research area or more detailed literature summary. Research area: {research_area}"
            else:
                logger.error("Invalid response structure for hypothesis generation")
                logger.error(f"Full response: {response}")
                content = "Error: Unable to generate hypotheses due to invalid API response. Please try again."

            return {
                "success": True,
                "hypotheses": content,
                "research_area": research_area,
                "num_requested": num_hypotheses,
                "model_used": self.model,
                "api_used": "Comet" if self.using_comet else "AI/ML"
            }

        except Exception as e:
            logger.error(f"Hypothesis generation failed: {e}")
            logger.error(f"Exception type: {type(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "message": f"Failed to generate hypotheses: {str(e)}"
            }

    def conduct_meta_analysis(
        self,
        papers: List[str],
        research_question: str,
        analysis_type: str = "Effect Size Analysis",
        statistical_method: str = "Random Effects Model",
        include_forest_plot: bool = True,
        include_heterogeneity: bool = True
    ) -> Dict[str, Any]:
        """
        Conduct meta-analysis of multiple research studies

        Args:
            papers: List of paper contents
            research_question: Research question/hypothesis
            analysis_type: Type of meta-analysis
            statistical_method: Statistical method to use
            include_forest_plot: Whether to describe forest plot
            include_heterogeneity: Whether to assess heterogeneity

        Returns:
            Meta-analysis results
        """
        # Input validation
        if not papers or len(papers) < 2:
            return {
                "success": False,
                "error": "At least 2 studies required for meta-analysis"
            }

        if not research_question or len(research_question.strip()) == 0:
            return {
                "success": False,
                "error": "No research question provided"
            }

        try:
            # Prepare studies for analysis - limit content to avoid token limits
            studies_content = "\n\n---STUDY SEPARATOR---\n\n".join([
                study[:2000] for study in papers[:15] if study and len(study.strip()) > 0
            ])

            prompt = f"""
            Conduct a comprehensive meta-analysis based on the following research question and studies.

            Research Question: {research_question}
            Analysis Type: {analysis_type}
            Statistical Method: {statistical_method}

            Please provide:
            1. Executive Summary
            2. Study Characteristics (sample sizes, methodologies, populations)
            3. Effect Size Analysis (if applicable)
            4. Statistical Results and Confidence Intervals
            {"5. Forest Plot Description and Interpretation" if include_forest_plot else ""}
            {"6. Heterogeneity Assessment (I² statistic, Q-test)" if include_heterogeneity else ""}
            7. Publication Bias Assessment
            8. Clinical/Practical Significance
            9. Limitations and Recommendations
            10. Conclusion

            Studies to analyze:
            {studies_content}

            Please ensure statistical rigor and provide specific numerical estimates where possible.
            """

            request_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert biostatistician and meta-analysis researcher. Provide rigorous statistical analysis with appropriate caveats about data limitations. Focus on effect sizes, confidence intervals, and heterogeneity assessment."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 8000,  # Increased significantly for complex meta-analysis
                "temperature": 0.7
            }

            # Add reasoning_effort only if supported
            if not self.using_comet and "aimlapi" in str(self.client.base_url).lower():
                request_params["reasoning_effort"] = "high"

            logger.info(f"Conducting meta-analysis of {len(papers)} studies for: {research_question[:100]}...")
            response = self.client.chat.completions.create(**request_params)

            # Check response content
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if not content or content.strip() == "":
                    logger.warning("Empty meta-analysis response from API")
                    logger.warning(f"Full response: {response}")
                    content = f"Meta-analysis completed but returned empty content. This may be due to content filtering or API limitations. Please try with fewer studies or a different research question. Studies analyzed: {len(papers)}"
            else:
                logger.error("Invalid response structure for meta-analysis")
                logger.error(f"Full response: {response}")
                content = "Error: Unable to conduct meta-analysis due to invalid API response. Please try again."

            return {
                "success": True,
                "analysis": content,
                "study_count": len(papers),
                "analysis_type": analysis_type,
                "statistical_method": statistical_method,
                "model_used": self.model,
                "api_used": "Comet" if self.using_comet else "AI/ML"
            }

        except Exception as e:
            logger.error(f"Meta-analysis failed: {e}")
            logger.error(f"Exception type: {type(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "message": f"Failed to conduct meta-analysis: {str(e)}"
            }

    def generate_research_synthesis(
        self,
        papers: List[str],
        synthesis_type: str = "Concept Mapping",
        research_focus: str = ""
    ) -> Dict[str, Any]:
        """
        Generate research synthesis across multiple papers

        Args:
            papers: List of paper contents
            synthesis_type: Type of synthesis to perform
            research_focus: Focus area for synthesis

        Returns:
            Research synthesis results
        """
        # Input validation
        if not papers or len(papers) == 0:
            return {
                "success": False,
                "error": "No papers provided for synthesis"
            }

        try:
            # Prepare papers for synthesis
            papers_content = "\n\n---PAPER SEPARATOR---\n\n".join([
                paper[:2500] for paper in papers[:10] if paper and len(paper.strip()) > 0
            ])

            if synthesis_type == "Concept Mapping":
                task_description = "Create a comprehensive concept map showing relationships between key concepts, theories, and findings across the papers."
            elif synthesis_type == "Methodology Comparison":
                task_description = "Compare and contrast the methodological approaches, highlighting strengths, weaknesses, and innovations."
            else:
                task_description = f"Perform {synthesis_type.lower()} to identify patterns and relationships across the studies."

            prompt = f"""
            Perform {synthesis_type} across the following research papers.

            Research Focus: {research_focus}

            Task: {task_description}

            Please provide:
            1. Overview of papers and scope
            2. Key concepts and themes identified
            3. Relationships and patterns between studies
            4. Methodological insights (if applicable)
            5. Theoretical contributions and frameworks
            6. Convergent and divergent findings
            7. Synthesis conclusions and implications
            8. Recommendations for future research

            Papers to synthesize:
            {papers_content}
            """

            request_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert research synthesist. Create comprehensive syntheses that reveal patterns, relationships, and insights across multiple studies. Focus on theoretical connections and methodological innovations."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 7000,  # Increased for comprehensive synthesis
                "temperature": 0.7
            }

            # Add reasoning_effort only if supported
            if not self.using_comet and "aimlapi" in str(self.client.base_url).lower():
                request_params["reasoning_effort"] = "high"

            logger.info(f"Generating {synthesis_type} for {len(papers)} papers...")
            response = self.client.chat.completions.create(**request_params)

            # Check response content
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if not content or content.strip() == "":
                    logger.warning("Empty research synthesis response from API")
                    logger.warning(f"Full response: {response}")
                    content = f"Research synthesis completed but returned empty content. This may be due to content filtering or API limitations. Please try with fewer papers or adjust the research focus. Papers analyzed: {len(papers)}"
            else:
                logger.error("Invalid response structure for research synthesis")
                logger.error(f"Full response: {response}")
                content = "Error: Unable to generate research synthesis due to invalid API response. Please try again."

            return {
                "success": True,
                "synthesis": content,
                "paper_count": len(papers),
                "synthesis_type": synthesis_type,
                "model_used": self.model,
                "api_used": "Comet" if self.using_comet else "AI/ML"
            }

        except Exception as e:
            logger.error(f"Research synthesis failed: {e}")
            logger.error(f"Exception type: {type(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "message": f"Failed to generate research synthesis: {str(e)}"
            }

    def generate_bibliography(
        self,
        papers: List[Dict[str, Any]],
        format_style: str = "APA 7th"
    ) -> Dict[str, Any]:
        """
        Generate formatted bibliography from papers

        Args:
            papers: List of paper data with metadata
            format_style: Citation format style

        Returns:
            Formatted bibliography
        """
        # Input validation
        if not papers or len(papers) == 0:
            return {
                "success": False,
                "error": "No papers provided for bibliography"
            }

        try:
            # Extract paper information for bibliography
            paper_info = []
            for i, paper in enumerate(papers):
                info = f"Paper {i+1}:\n"
                info += f"Filename: {paper.get('filename', 'Unknown')}\n"
                info += f"Content excerpt: {paper.get('content', '')[:500]}...\n"
                paper_info.append(info)

            papers_text = "\n\n".join(paper_info)

            prompt = f"""
            Generate a properly formatted bibliography in {format_style} format for the following research papers.

            For each paper, extract or infer the following information where possible:
            - Author(s)
            - Title
            - Publication year
            - Journal/Publisher
            - Volume/Issue (if applicable)
            - Page numbers (if applicable)
            - DOI or URL (if available)

            Format each entry according to {format_style} guidelines. If information is missing,
            indicate this clearly and provide the best possible citation with available information.

            Papers to cite:
            {papers_text}

            Please provide:
            1. Complete bibliography in {format_style} format
            2. Notes about any missing information
            3. Formatting guidelines used
            """

            request_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": f"You are an expert academic librarian specializing in {format_style} citation format. Generate accurate, properly formatted bibliographies following official style guidelines."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 6000,  # Increased for comprehensive bibliographies
                "temperature": 0.3  # Lower temperature for more consistent formatting
            }

            # Add reasoning_effort only if supported
            if not self.using_comet and "aimlapi" in str(self.client.base_url).lower():
                request_params["reasoning_effort"] = "medium"

            logger.info(f"Generating {format_style} bibliography for {len(papers)} papers...")
            response = self.client.chat.completions.create(**request_params)

            # Check response content
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if not content or content.strip() == "":
                    logger.warning("Empty bibliography response from API")
                    logger.warning(f"Full response: {response}")
                    content = f"Bibliography generation completed but returned empty content. This may be due to insufficient paper metadata. Papers processed: {len(papers)}"
            else:
                logger.error("Invalid response structure for bibliography")
                logger.error(f"Full response: {response}")
                content = "Error: Unable to generate bibliography due to invalid API response. Please try again."

            return {
                "success": True,
                "bibliography": content,
                "paper_count": len(papers),
                "format_style": format_style,
                "model_used": self.model,
                "api_used": "Comet" if self.using_comet else "AI/ML"
            }

        except Exception as e:
            logger.error(f"Bibliography generation failed: {e}")
            logger.error(f"Exception type: {type(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "message": f"Failed to generate bibliography: {str(e)}"
            }

    def format_citation(
        self,
        source_info: Dict[str, Any],
        format_style: str = "APA 7th"
    ) -> Dict[str, Any]:
        """
        Format a single citation in the specified style

        Args:
            source_info: Dictionary with source information
            format_style: Citation format style

        Returns:
            Formatted citation
        """
        try:
            # Build source description
            source_desc = f"Source Type: {source_info.get('type', 'Unknown')}\n"
            for key, value in source_info.items():
                if value and key != 'type':
                    source_desc += f"{key.title()}: {value}\n"

            prompt = f"""
            Generate a properly formatted citation in {format_style} format for the following source:

            {source_desc}

            Please provide:
            1. The complete citation in {format_style} format
            2. Brief explanation of formatting choices

            Follow official {format_style} guidelines precisely.
            """

            request_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": f"You are an expert in {format_style} citation format. Generate precise, properly formatted citations following official guidelines."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,  # Increased for detailed citation formatting
                "temperature": 0.2  # Very low temperature for consistent formatting
            }

            # Add reasoning_effort only if supported
            if not self.using_comet and "aimlapi" in str(self.client.base_url).lower():
                request_params["reasoning_effort"] = "medium"

            logger.info(f"Formatting {format_style} citation for {source_info.get('type', 'unknown')} source...")
            response = self.client.chat.completions.create(**request_params)

            # Check response content
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if not content or content.strip() == "":
                    logger.warning("Empty citation formatting response from API")
                    logger.warning(f"Full response: {response}")
                    content = f"Citation formatting completed but returned empty content. Please check the source information provided."
            else:
                logger.error("Invalid response structure for citation formatting")
                logger.error(f"Full response: {response}")
                content = "Error: Unable to format citation due to invalid API response. Please try again."

            return {
                "success": True,
                "citation": content,
                "format_style": format_style,
                "source_type": source_info.get('type', 'Unknown'),
                "model_used": self.model,
                "api_used": "Comet" if self.using_comet else "AI/ML"
            }

        except Exception as e:
            logger.error(f"Citation formatting failed: {e}")
            logger.error(f"Exception type: {type(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "message": f"Failed to format citation: {str(e)}"
            }

    def analyze_citations(
        self,
        papers: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze citation patterns across multiple papers

        Args:
            papers: List of paper contents

        Returns:
            Citation analysis results
        """
        # Input validation
        if not papers or len(papers) == 0:
            return {
                "success": False,
                "error": "No papers provided for citation analysis"
            }

        try:
            # Prepare papers for analysis
            papers_content = "\n\n---PAPER SEPARATOR---\n\n".join([
                paper[:2000] for paper in papers[:10] if paper and len(paper.strip()) > 0
            ])

            prompt = f"""
            Analyze citation patterns and networks across the following research papers.

            Please provide:
            1. Citation frequency analysis
            2. Most cited authors and works
            3. Citation recency patterns (temporal analysis)
            4. Interdisciplinary citation patterns
            5. Self-citation analysis
            6. Citation network insights
            7. Geographic distribution of citations (if evident)
            8. Journal/publication venue analysis
            9. Gaps in citation coverage
            10. Recommendations for additional references

            Papers to analyze:
            {papers_content}

            Focus on patterns, trends, and insights that could inform future research.
            """

            request_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert bibliometrician and citation analyst. Provide comprehensive analysis of citation patterns, networks, and trends. Focus on actionable insights for researchers."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 6000,  # Increased for comprehensive citation analysis
                "temperature": 0.7
            }

            # Add reasoning_effort only if supported
            if not self.using_comet and "aimlapi" in str(self.client.base_url).lower():
                request_params["reasoning_effort"] = "high"

            logger.info(f"Analyzing citation patterns across {len(papers)} papers...")
            response = self.client.chat.completions.create(**request_params)

            # Check response content
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if not content or content.strip() == "":
                    logger.warning("Empty citation analysis response from API")
                    logger.warning(f"Full response: {response}")
                    content = f"Citation analysis completed but returned empty content. This may be due to limited citation information in the provided papers. Papers analyzed: {len(papers)}"
            else:
                logger.error("Invalid response structure for citation analysis")
                logger.error(f"Full response: {response}")
                content = "Error: Unable to analyze citations due to invalid API response. Please try again."

            return {
                "success": True,
                "analysis": content,
                "paper_count": len(papers),
                "model_used": self.model,
                "api_used": "Comet" if self.using_comet else "AI/ML"
            }

        except Exception as e:
            logger.error(f"Citation analysis failed: {e}")
            logger.error(f"Exception type: {type(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "message": f"Failed to analyze citations: {str(e)}"
            }

    def _get_system_prompt(self, analysis_type: str) -> str:
        """Get appropriate system prompt based on analysis type"""
        prompts = {
            "comprehensive": "You are an expert document analyst. Provide comprehensive analysis including summary, key points, insights, and recommendations.",
            "summary": "You are an expert at summarizing documents. Provide clear, concise summaries.",
            "research": "You are an academic researcher. Analyze documents from a research perspective.",
            "legal": "You are a legal document analyst. Focus on legal implications and key terms.",
            "medical": "You are a medical document analyst. Focus on clinical findings and medical insights.",
            "financial": "You are a financial analyst. Focus on financial metrics and implications."
        }
        return prompts.get(analysis_type, prompts["comprehensive"])

    @st.cache_data(ttl=3600)
    def cached_analysis(_self, content: str, analysis_type: str) -> Dict[str, Any]:
        """Cached version of document analysis for better performance"""
        return _self.analyze_document(content, analysis_type)