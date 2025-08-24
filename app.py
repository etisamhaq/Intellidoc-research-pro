"""
IntelliDoc Research Pro - AI-Powered Document Intelligence & Research Platform
Main Streamlit Application
"""

import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Load environment variables
load_dotenv()

# Import custom modules
from config.settings import Config
from core.gpt5_client import GPT5Client
from modules.file_processor import FileProcessor
from research.literature_review import LiteratureReviewGenerator
from research.citation_manager import CitationManager
from ui.visualizations import ResearchVisualizations

# Page configuration
st.set_page_config(
    page_title=Config.APP_NAME,
    page_icon=Config.PAGE_ICON,
    layout=Config.LAYOUT,
    initial_sidebar_state=Config.INITIAL_SIDEBAR_STATE
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #F8FAFC;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #10B981;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #3B82F6;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'gpt5_client' not in st.session_state:
    api_key = os.getenv('COMET_API_KEY', '')
    if not api_key:
        # Fallback to AI/ML API if available
        api_key = os.getenv('AIMLAPI_KEY', '')

    if api_key:
        st.session_state.gpt5_client = GPT5Client(api_key)
    else:
        st.session_state.gpt5_client = None

if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []

if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}

# Header
st.markdown('<p class="main-header">🔬 IntelliDoc Research Pro</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Document Intelligence Platform with GPT-5-nano</p>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Configuration")

    # API Key input
    api_key_input = st.text_input(
        "Comet API Key",
        type="password",
        value=os.getenv('COMET_API_KEY', '') or os.getenv('AIMLAPI_KEY', ''),
        help="Enter your Comet API key to access GPT-5-nano"
    )

    if api_key_input:
        st.session_state.gpt5_client = GPT5Client(api_key_input)
        if st.session_state.gpt5_client.using_comet:
            st.success(f"✅ Comet API configured (Model: GPT-5-nano)")
        else:
            st.success("✅ AI/ML API configured (Model: GPT-5-nano)")

    st.divider()

    # Research Mode Selection
    research_mode = st.selectbox(
        "🎯 Research Mode",
        ["📚 Literature Review", "🔍 Document Analysis", "📊 Meta-Analysis",
         "💡 Hypothesis Generation", "🔬 Research Synthesis", "📝 Citation Management"]
    )

    st.divider()

    # Analysis Settings
    st.subheader("Analysis Settings")

    analysis_depth = st.select_slider(
        "Analysis Depth",
        options=Config.ANALYSIS_DEPTHS,
        value="Comprehensive"
    )

    reasoning_level = st.select_slider(
        "GPT-5 Reasoning Level",
        options=Config.REASONING_LEVELS,
        value="high",
        help="Higher reasoning levels provide deeper analysis but take longer"
    )

    citation_style = st.selectbox(
        "Citation Style",
        Config.CITATION_STYLES,
        help="Select the citation format for references"
    )

    st.divider()

    # Quick Actions
    st.subheader("Quick Actions")
    if st.button("🔄 Clear All Data", type="secondary"):
        st.session_state.processed_files = []
        st.session_state.analysis_results = {}
        st.rerun()

# Main Content Area
if not st.session_state.gpt5_client:
    st.warning("⚠️ Please enter your Comet API key in the sidebar to continue")
    st.info("Get your API key from [Comet API](https://cometapi.com)")

    st.divider()
    st.subheader("🎯 Key Features")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
        <h3>📚 Literature Review</h3>
        <p>Generate comprehensive literature reviews from multiple research papers</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
        <h3>🔍 Deep Analysis</h3>
        <p>Extract insights using GPT-5's advanced reasoning capabilities</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
        <h3>📊 Visualizations</h3>
        <p>Interactive charts and graphs for research data</p>
        </div>
        """, unsafe_allow_html=True)

else:
    # Main application interface
    if research_mode == "📚 Literature Review":
        st.header("📚 Literature Review Generator")

        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload Papers", "🔍 Generate Review", "📊 Visualizations", "💾 Export"])

        with tab1:
            st.subheader("Upload Research Papers")

            uploaded_files = st.file_uploader(
                "Select PDF files",
                type=['pdf', 'txt', 'docx'],
                accept_multiple_files=True,
                help="Upload research papers for literature review"
            )

            if uploaded_files:
                with st.spinner("Processing files..."):
                    processed = FileProcessor.process_uploaded_files(uploaded_files)
                    st.session_state.processed_files = processed

                st.success(f"✅ Processed {len(processed)} files successfully")

                # Show file info
                for file in processed:
                    st.write(f"📄 **{file['filename']}** ({file['size']:.2f} MB)")

        with tab2:
            st.subheader("Generate Literature Review")

            if st.session_state.processed_files:
                research_question = st.text_area(
                    "Research Question",
                    placeholder="What specific aspect of the research are you investigating?",
                    height=100
                )

                col1, col2 = st.columns(2)
                with col1:
                    include_gaps = st.checkbox("Identify Research Gaps", value=True)
                with col2:
                    include_future = st.checkbox("Suggest Future Research", value=True)

                if st.button("🚀 Generate Literature Review", type="primary"):
                    if research_question:
                        with st.spinner("Generating comprehensive literature review with GPT-5..."):
                            # Create review generator
                            review_gen = LiteratureReviewGenerator(st.session_state.gpt5_client)

                            # Generate review
                            result = review_gen.generate_review(
                                papers=st.session_state.processed_files,
                                research_question=research_question,
                                review_settings={
                                    "depth": analysis_depth,
                                    "include_gaps": include_gaps,
                                    "include_future": include_future
                                }
                            )

                            if result["success"]:
                                st.session_state.analysis_results["literature_review"] = result
                                st.success("✅ Literature review generated successfully!")

                                # Display review
                                st.markdown("### Generated Literature Review")
                                review_text = result.get("full_review", "")
                                if review_text:
                                    st.markdown(review_text)
                                else:
                                    st.warning("The literature review returned empty. Please try again or check your API connection.")

                                # Show metadata
                                st.info(f"📊 Analyzed {result['paper_count']} papers | "
                                       f"Word count: {result['metadata']['total_words']}")
                            else:
                                st.error(f"Error: {result.get('error', 'Unknown error')}")
                    else:
                        st.warning("Please enter a research question")
            else:
                st.info("Please upload research papers in the 'Upload Papers' tab")

        with tab3:
            st.subheader("Research Visualizations")

            if st.session_state.analysis_results.get("literature_review"):
                # Create visualizations
                viz = ResearchVisualizations()

                col1, col2 = st.columns(2)

                with col1:
                    # Theme distribution
                    fig1 = viz.create_theme_distribution({})
                    st.plotly_chart(fig1, use_container_width=True)

                with col2:
                    # Research timeline
                    fig2 = viz.create_research_timeline([])
                    st.plotly_chart(fig2, use_container_width=True)

                # Citation network
                st.subheader("Citation Network")
                fig3 = viz.create_citation_network([])
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("Generate a literature review first to see visualizations")

        with tab4:
            st.subheader("Export Options")

            if st.session_state.analysis_results.get("literature_review"):
                export_format = st.selectbox(
                    "Export Format",
                    ["PDF", "Word Document", "LaTeX", "Markdown", "HTML"]
                )

                if st.button("💾 Export Literature Review"):
                    st.success(f"✅ Literature review exported as {export_format}")
                    st.balloons()
            else:
                st.info("Generate a literature review first to export")

    elif research_mode == "🔍 Document Analysis":
        st.header("🔍 Document Analysis")

        col1, col2 = st.columns([2, 1])

        with col1:
            uploaded_file = st.file_uploader(
                "Upload Document",
                type=['pdf', 'txt', 'docx', 'jpg', 'png']
            )

            if uploaded_file:
                with st.spinner("Processing document..."):
                    processed = FileProcessor.process_single_file(uploaded_file)

                if processed:
                    st.success(f"✅ Document processed: {processed['filename']}")

                    analysis_type = st.selectbox(
                        "Analysis Type",
                        ["comprehensive", "summary", "research", "legal", "medical", "financial"]
                    )

                    if st.button("🔍 Analyze Document", type="primary"):
                        with st.spinner(f"Analyzing with GPT-5 ({reasoning_level} reasoning)..."):
                            result = st.session_state.gpt5_client.analyze_document(
                                content=processed['content'],
                                analysis_type=analysis_type,
                                reasoning_level=reasoning_level
                            )

                            if result["success"]:
                                st.markdown("### Analysis Results")
                                analysis_text = result.get("analysis", "")
                                if analysis_text:
                                    st.markdown(analysis_text)
                                else:
                                    st.warning("The analysis returned empty. Please try again or check your API connection.")
                            else:
                                st.error(f"Error: {result.get('error', 'Unknown error')}")

        with col2:
            st.markdown("""
            ### Analysis Types

            - **Comprehensive**: Full analysis with all aspects
            - **Summary**: Concise summary of key points
            - **Research**: Academic research perspective
            - **Legal**: Legal implications and terms
            - **Medical**: Clinical findings and insights
            - **Financial**: Financial metrics and analysis
            """)

    elif research_mode == "💡 Hypothesis Generation":
        st.header("💡 Research Hypothesis Generator")

        research_area = st.text_input(
            "Research Area",
            placeholder="e.g., Machine Learning in Healthcare"
        )

        literature_summary = st.text_area(
            "Literature Summary",
            placeholder="Provide a summary of existing literature in this area...",
            height=200
        )

        num_hypotheses = st.slider("Number of Hypotheses", 3, 10, 5)

        if st.button("💡 Generate Hypotheses", type="primary"):
            if research_area and literature_summary:
                with st.spinner("Generating research hypotheses with GPT-5..."):
                    result = st.session_state.gpt5_client.generate_hypotheses(
                        research_area=research_area,
                        literature_summary=literature_summary,
                        num_hypotheses=num_hypotheses
                    )

                    if result["success"]:
                        st.markdown("### Generated Research Hypotheses")
                        hypotheses_text = result.get("hypotheses", "")
                        if hypotheses_text:
                            st.markdown(hypotheses_text)
                        else:
                            st.warning("No hypotheses were generated. Please try again or check your API connection.")
                    else:
                        st.error(f"Error: {result.get('error', 'Unknown error')}")
            else:
                st.warning("Please provide both research area and literature summary")

    elif research_mode == "📊 Meta-Analysis":
        st.header("📊 Meta-Analysis Generator")

        st.markdown("""
        Conduct statistical meta-analysis of multiple research studies to identify patterns,
        effect sizes, and overall trends across the literature.
        """)

        col1, col2 = st.columns([2, 1])

        with col1:
            # Upload studies for meta-analysis
            uploaded_files = st.file_uploader(
                "Upload Studies for Meta-Analysis",
                type=['pdf', 'txt', 'docx'],
                accept_multiple_files=True,
                help="Upload research papers/studies for meta-analysis"
            )

            if uploaded_files:
                with st.spinner("Processing uploaded studies..."):
                    for file in uploaded_files:
                        processed = FileProcessor.process_single_file(file)
                        if processed:
                            st.session_state.processed_files.append(processed)

                st.success(f"✅ {len(uploaded_files)} studies processed for meta-analysis")

            if st.session_state.processed_files:
                st.subheader("Meta-Analysis Settings")

                research_question = st.text_input(
                    "Research Question/Hypothesis",
                    placeholder="e.g., Does AI improve diagnostic accuracy in medical imaging?"
                )

                analysis_type = st.selectbox(
                    "Analysis Type",
                    ["Effect Size Analysis", "Systematic Review", "Quantitative Synthesis", "Qualitative Meta-Analysis"]
                )

                statistical_method = st.selectbox(
                    "Statistical Method",
                    ["Random Effects Model", "Fixed Effects Model", "Mixed Effects Model"]
                )

                col_a, col_b = st.columns(2)
                with col_a:
                    include_forest_plot = st.checkbox("Generate Forest Plot Description", value=True)
                with col_b:
                    include_heterogeneity = st.checkbox("Assess Heterogeneity", value=True)

                if st.button("📊 Conduct Meta-Analysis", type="primary"):
                    if research_question:
                        with st.spinner("Conducting meta-analysis with GPT-5..."):
                            # Prepare papers for meta-analysis
                            papers_content = [f"Study {i+1}: {p['content']}" for i, p in enumerate(st.session_state.processed_files)]

                            result = st.session_state.gpt5_client.conduct_meta_analysis(
                                papers=papers_content,
                                research_question=research_question,
                                analysis_type=analysis_type,
                                statistical_method=statistical_method,
                                include_forest_plot=include_forest_plot,
                                include_heterogeneity=include_heterogeneity
                            )

                            if result["success"]:
                                st.session_state.analysis_results["meta_analysis"] = result
                                st.success("✅ Meta-analysis completed successfully!")

                                st.markdown("### Meta-Analysis Results")
                                analysis_text = result.get("analysis", "")
                                if analysis_text:
                                    st.markdown(analysis_text)

                                    # Show analysis metadata
                                    st.info(f"📊 Studies analyzed: {result.get('study_count', 0)} | "
                                           f"Method: {statistical_method} | "
                                           f"Type: {analysis_type}")
                                else:
                                    st.warning("Meta-analysis completed but no content was returned.")
                            else:
                                st.error(f"Error: {result.get('error', 'Unknown error')}")
                    else:
                        st.warning("Please enter a research question")

        with col2:
            st.markdown("""
            ### Meta-Analysis Types

            - **Effect Size Analysis**: Calculate and compare effect sizes across studies
            - **Systematic Review**: Comprehensive analysis of study methodologies and outcomes
            - **Quantitative Synthesis**: Statistical combination of numerical results
            - **Qualitative Meta-Analysis**: Thematic analysis across qualitative studies

            ### Statistical Methods

            - **Random Effects**: Assumes studies estimate different effect sizes
            - **Fixed Effects**: Assumes all studies estimate the same effect size
            - **Mixed Effects**: Combines both approaches
            """)

    elif research_mode == "🔬 Research Synthesis":
        st.header("🔬 Research Synthesis")

        st.markdown("""
        Create comprehensive synthesis matrices and thematic analyses to identify patterns,
        gaps, and relationships across multiple research studies.
        """)

        col1, col2 = st.columns([2, 1])

        with col1:
            # Use existing processed files or upload new ones
            if not st.session_state.processed_files:
                uploaded_files = st.file_uploader(
                    "Upload Research Papers",
                    type=['pdf', 'txt', 'docx'],
                    accept_multiple_files=True,
                    help="Upload papers for research synthesis"
                )

                if uploaded_files:
                    with st.spinner("Processing papers..."):
                        for file in uploaded_files:
                            processed = FileProcessor.process_single_file(file)
                            if processed:
                                st.session_state.processed_files.append(processed)

                    st.success(f"✅ {len(uploaded_files)} papers processed")

            if st.session_state.processed_files:
                st.subheader("Synthesis Configuration")

                synthesis_type = st.selectbox(
                    "Synthesis Type",
                    ["Thematic Analysis", "Synthesis Matrix", "Concept Mapping", "Gap Analysis", "Methodology Comparison"]
                )

                if synthesis_type == "Synthesis Matrix":
                    comparison_categories = st.multiselect(
                        "Comparison Categories",
                        ["Methodology", "Sample Size", "Key Findings", "Limitations", "Theoretical Framework", "Data Collection", "Analysis Methods"],
                        default=["Methodology", "Key Findings", "Limitations"]
                    )
                elif synthesis_type == "Thematic Analysis":
                    num_themes = st.slider("Number of Themes to Identify", 3, 10, 5)

                research_focus = st.text_area(
                    "Research Focus/Question",
                    placeholder="What specific aspect would you like to synthesize across the studies?",
                    height=100
                )

                if st.button("🔬 Generate Research Synthesis", type="primary"):
                    if research_focus:
                        with st.spinner(f"Generating {synthesis_type.lower()}..."):
                            if synthesis_type == "Thematic Analysis":
                                from research.literature_review import LiteratureReviewGenerator
                                review_gen = LiteratureReviewGenerator(st.session_state.gpt5_client)

                                result = review_gen.generate_thematic_analysis(
                                    papers=st.session_state.processed_files,
                                    num_themes=num_themes
                                )

                            elif synthesis_type == "Synthesis Matrix":
                                from research.literature_review import LiteratureReviewGenerator
                                review_gen = LiteratureReviewGenerator(st.session_state.gpt5_client)

                                result = review_gen.create_synthesis_matrix(
                                    papers=st.session_state.processed_files,
                                    categories=comparison_categories
                                )

                            elif synthesis_type == "Gap Analysis":
                                from research.research_gap_finder import ResearchGapFinder
                                gap_finder = ResearchGapFinder(st.session_state.gpt5_client)

                                result = gap_finder.identify_gaps(
                                    papers=st.session_state.processed_files,
                                    research_area=research_focus
                                )

                            else:
                                # For other synthesis types, use general synthesis
                                result = st.session_state.gpt5_client.generate_research_synthesis(
                                    papers=[p['content'] for p in st.session_state.processed_files],
                                    synthesis_type=synthesis_type,
                                    research_focus=research_focus
                                )

                            if result["success"]:
                                st.session_state.analysis_results["research_synthesis"] = result
                                st.success(f"✅ {synthesis_type} completed successfully!")

                                st.markdown(f"### {synthesis_type} Results")

                                # Display results based on synthesis type
                                if synthesis_type == "Thematic Analysis":
                                    content = result.get("themes", "")
                                elif synthesis_type == "Synthesis Matrix":
                                    content = result.get("matrix", "")
                                elif synthesis_type == "Gap Analysis":
                                    content = result.get("gaps", "")
                                else:
                                    content = result.get("synthesis", "")

                                if content:
                                    st.markdown(content)

                                    # Show metadata
                                    papers_count = len(st.session_state.processed_files)
                                    st.info(f"📊 Papers analyzed: {papers_count} | Type: {synthesis_type}")
                                else:
                                    st.warning("Synthesis completed but no content was returned.")
                            else:
                                st.error(f"Error: {result.get('error', 'Unknown error')}")
                    else:
                        st.warning("Please provide a research focus or question")

        with col2:
            st.markdown("""
            ### Synthesis Types

            - **Thematic Analysis**: Identify key themes across studies
            - **Synthesis Matrix**: Compare studies across categories
            - **Concept Mapping**: Visualize relationships between concepts
            - **Gap Analysis**: Identify research gaps and opportunities
            - **Methodology Comparison**: Compare research approaches
            """)

    elif research_mode == "📝 Citation Management":
        st.header("📝 Citation Management")

        st.markdown("""
        Extract, format, and manage citations from research documents. Generate bibliographies
        in various academic formats.
        """)

        col1, col2 = st.columns([2, 1])

        with col1:
            # Citation operation selection
            citation_operation = st.selectbox(
                "Citation Operation",
                ["Extract Citations", "Format Bibliography", "Generate Citations", "Citation Analysis"]
            )

            if citation_operation == "Extract Citations":
                # Text input for citation extraction
                text_input = st.text_area(
                    "Paste Text with Citations",
                    placeholder="Paste your academic text containing citations here...",
                    height=200
                )

                if st.button("🔍 Extract Citations", type="primary"):
                    if text_input:
                        from research.citation_manager import CitationManager
                        citation_manager = CitationManager()

                        with st.spinner("Extracting citations..."):
                            citations = citation_manager.extract_citations(text_input)

                            if citations:
                                st.success(f"✅ Found {len(citations)} citations")

                                st.markdown("### Extracted Citations")
                                for i, citation in enumerate(citations, 1):
                                    if citation.get("type") == "in-text":
                                        st.write(f"{i}. **{citation['authors']}** ({citation['year']})")
                                    elif citation.get("type") == "numbered":
                                        st.write(f"{i}. Reference [{citation['number']}]")

                                # Store citations for further processing
                                st.session_state.extracted_citations = citations
                            else:
                                st.warning("No citations found in the provided text.")
                    else:
                        st.warning("Please provide text to extract citations from")

            elif citation_operation == "Format Bibliography":
                if st.session_state.processed_files:
                    st.markdown("### Generate Bibliography from Uploaded Papers")

                    format_style = st.selectbox(
                        "Citation Format",
                        ["APA 7th", "MLA 9th", "Chicago 17th", "IEEE", "Harvard"]
                    )

                    if st.button("📚 Generate Bibliography", type="primary"):
                        with st.spinner("Generating bibliography..."):
                            result = st.session_state.gpt5_client.generate_bibliography(
                                papers=st.session_state.processed_files,
                                format_style=format_style
                            )

                            if result["success"]:
                                st.markdown("### Generated Bibliography")
                                bibliography = result.get("bibliography", "")
                                if bibliography:
                                    st.markdown(bibliography)
                                    st.info(f"📚 Format: {format_style} | Papers: {len(st.session_state.processed_files)}")
                                else:
                                    st.warning("Bibliography generated but no content returned.")
                            else:
                                st.error(f"Error: {result.get('error', 'Unknown error')}")
                else:
                    st.info("Upload research papers first to generate bibliography")

            elif citation_operation == "Generate Citations":
                st.markdown("### Generate Citation for a Source")

                source_type = st.selectbox(
                    "Source Type",
                    ["Journal Article", "Book", "Conference Paper", "Website", "Thesis/Dissertation"]
                )

                # Dynamic form based on source type
                if source_type == "Journal Article":
                    authors = st.text_input("Authors", placeholder="Smith, J., & Doe, A.")
                    title = st.text_input("Article Title")
                    journal = st.text_input("Journal Name")
                    year = st.text_input("Year", placeholder="2025")
                    volume = st.text_input("Volume (optional)")
                    pages = st.text_input("Pages (optional)", placeholder="123-145")

                    source_info = {
                        "type": source_type,
                        "authors": authors,
                        "title": title,
                        "journal": journal,
                        "year": year,
                        "volume": volume,
                        "pages": pages
                    }

                elif source_type == "Book":
                    authors = st.text_input("Authors", placeholder="Smith, J.")
                    title = st.text_input("Book Title")
                    publisher = st.text_input("Publisher")
                    year = st.text_input("Year", placeholder="2025")
                    edition = st.text_input("Edition (optional)")

                    source_info = {
                        "type": source_type,
                        "authors": authors,
                        "title": title,
                        "publisher": publisher,
                        "year": year,
                        "edition": edition
                    }

                format_style = st.selectbox(
                    "Citation Format",
                    ["APA 7th", "MLA 9th", "Chicago 17th", "IEEE", "Harvard"],
                    key="citation_format"
                )

                if st.button("📝 Generate Citation", type="primary"):
                    if all(source_info[key] for key in ["authors", "title", "year"]):
                        with st.spinner("Generating citation..."):
                            result = st.session_state.gpt5_client.format_citation(
                                source_info=source_info,
                                format_style=format_style
                            )

                            if result["success"]:
                                st.markdown("### Generated Citation")
                                citation = result.get("citation", "")
                                if citation:
                                    st.code(citation)
                                    st.info(f"📝 Format: {format_style}")
                                else:
                                    st.warning("Citation generated but no content returned.")
                            else:
                                st.error(f"Error: {result.get('error', 'Unknown error')}")
                    else:
                        st.warning("Please fill in the required fields (authors, title, year)")

            elif citation_operation == "Citation Analysis":
                if st.session_state.processed_files:
                    if st.button("📊 Analyze Citations", type="primary"):
                        with st.spinner("Analyzing citation patterns..."):
                            papers_content = [p['content'] for p in st.session_state.processed_files]

                            result = st.session_state.gpt5_client.analyze_citations(
                                papers=papers_content
                            )

                            if result["success"]:
                                st.markdown("### Citation Analysis Results")
                                analysis = result.get("analysis", "")
                                if analysis:
                                    st.markdown(analysis)
                                    st.info(f"📊 Papers analyzed: {len(st.session_state.processed_files)}")
                                else:
                                    st.warning("Citation analysis completed but no content returned.")
                            else:
                                st.error(f"Error: {result.get('error', 'Unknown error')}")
                else:
                    st.info("Upload research papers first to analyze citations")

        with col2:
            st.markdown("""
            ### Citation Operations

            - **Extract Citations**: Find citations in academic text
            - **Format Bibliography**: Generate formatted reference lists
            - **Generate Citations**: Create proper citations for sources
            - **Citation Analysis**: Analyze citation patterns and networks

            ### Supported Formats

            - **APA 7th**: American Psychological Association
            - **MLA 9th**: Modern Language Association
            - **Chicago 17th**: Chicago Manual of Style
            - **IEEE**: Institute of Electrical and Electronics Engineers
            - **Harvard**: Harvard referencing system
            """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748B; padding: 2rem;">
    <p>🚀 Powered by GPT-5-nano via Comet API | Built for Researchers & Academics</p>
    <p>© 2025 IntelliDoc Research Pro | Version 1.0.0</p>
</div>
""", unsafe_allow_html=True)