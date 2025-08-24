"""Visualization components for research data"""

import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud
import pandas as pd
import networkx as nx
from typing import List, Dict, Any
import streamlit as st

class ResearchVisualizations:
    """Create various research-related visualizations"""
    
    @staticmethod
    def create_research_timeline(papers: List[Dict[str, Any]]) -> go.Figure:
        """
        Create an interactive timeline of research papers
        
        Args:
            papers: List of paper data with years
            
        Returns:
            Plotly figure
        """
        # Extract years and titles
        timeline_data = []
        for paper in papers:
            if "year" in paper and "title" in paper:
                timeline_data.append({
                    "year": paper["year"],
                    "title": paper["title"],
                    "authors": paper.get("authors", "Unknown")
                })
        
        if not timeline_data:
            # Create dummy data for demo
            timeline_data = [
                {"year": 2020, "title": "Paper 1", "authors": "Author A"},
                {"year": 2021, "title": "Paper 2", "authors": "Author B"},
                {"year": 2022, "title": "Paper 3", "authors": "Author C"},
                {"year": 2023, "title": "Paper 4", "authors": "Author D"},
            ]
        
        df = pd.DataFrame(timeline_data)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['year'],
            y=list(range(len(df))),
            mode='markers+text',
            marker=dict(size=15, color='blue'),
            text=df['title'],
            textposition="top center",
            hovertemplate='<b>%{text}</b><br>Year: %{x}<br>Authors: %{customdata}<extra></extra>',
            customdata=df['authors']
        ))
        
        fig.update_layout(
            title="Research Timeline",
            xaxis_title="Year",
            yaxis_title="",
            showlegend=False,
            height=400,
            yaxis=dict(showticklabels=False, showgrid=False),
            hovermode='closest'
        )
        
        return fig
    
    @staticmethod
    def create_theme_distribution(themes: Dict[str, int]) -> go.Figure:
        """
        Create a pie chart of research themes
        
        Args:
            themes: Dictionary of theme names and counts
            
        Returns:
            Plotly figure
        """
        if not themes:
            # Demo data
            themes = {
                "Machine Learning": 25,
                "Natural Language Processing": 20,
                "Computer Vision": 15,
                "Data Analysis": 20,
                "Deep Learning": 20
            }
        
        fig = go.Figure(data=[go.Pie(
            labels=list(themes.keys()),
            values=list(themes.values()),
            hole=0.3,
            marker=dict(colors=px.colors.qualitative.Set3)
        )])
        
        fig.update_layout(
            title="Research Theme Distribution",
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_citation_network(citations: List[Dict[str, Any]]) -> go.Figure:
        """
        Create a citation network graph
        
        Args:
            citations: List of citation relationships
            
        Returns:
            Plotly figure
        """
        # Create a simple demo network if no data
        if not citations:
            G = nx.karate_club_graph()
        else:
            G = nx.Graph()
            for citation in citations:
                if "source" in citation and "target" in citation:
                    G.add_edge(citation["source"], citation["target"])
        
        # Get positions for nodes
        pos = nx.spring_layout(G)
        
        # Create edge trace
        edge_trace = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace.append(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=0.5, color='gray'),
                hoverinfo='none'
            ))
        
        # Create node trace
        node_trace = go.Scatter(
            x=[pos[node][0] for node in G.nodes()],
            y=[pos[node][1] for node in G.nodes()],
            mode='markers+text',
            text=[str(node) for node in G.nodes()],
            textposition="top center",
            marker=dict(
                size=10,
                color=[G.degree(node) for node in G.nodes()],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Connections")
            ),
            hovertemplate='Node: %{text}<br>Connections: %{marker.color}<extra></extra>'
        )
        
        # Create figure
        fig = go.Figure(data=edge_trace + [node_trace])
        
        fig.update_layout(
            title="Citation Network",
            showlegend=False,
            height=500,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            hovermode='closest'
        )
        
        return fig
    
    @staticmethod
    def create_methodology_comparison(methodologies: Dict[str, List[str]]) -> go.Figure:
        """
        Create a comparison chart of research methodologies
        
        Args:
            methodologies: Dictionary of methodology types and papers using them
            
        Returns:
            Plotly figure
        """
        if not methodologies:
            # Demo data
            methodologies = {
                "Quantitative": ["Paper 1", "Paper 2", "Paper 5"],
                "Qualitative": ["Paper 3", "Paper 4"],
                "Mixed Methods": ["Paper 6", "Paper 7", "Paper 8"],
                "Experimental": ["Paper 9", "Paper 10"],
                "Survey": ["Paper 11", "Paper 12", "Paper 13"]
            }
        
        data = []
        for method, papers in methodologies.items():
            data.append({
                "Methodology": method,
                "Count": len(papers),
                "Papers": ", ".join(papers[:3]) + ("..." if len(papers) > 3 else "")
            })
        
        df = pd.DataFrame(data)
        
        fig = go.Figure(data=[go.Bar(
            x=df['Methodology'],
            y=df['Count'],
            text=df['Count'],
            textposition='auto',
            marker_color='lightblue',
            hovertemplate='<b>%{x}</b><br>Papers: %{customdata}<br>Count: %{y}<extra></extra>',
            customdata=df['Papers']
        )])
        
        fig.update_layout(
            title="Research Methodology Distribution",
            xaxis_title="Methodology",
            yaxis_title="Number of Papers",
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_word_cloud(text: str) -> Any:
        """
        Create a word cloud from text
        
        Args:
            text: Text to create word cloud from
            
        Returns:
            WordCloud object
        """
        if not text:
            text = "research analysis literature review methodology qualitative quantitative data science machine learning artificial intelligence"
        
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            colormap='viridis',
            max_words=100
        ).generate(text)
        
        return wordcloud
    
    @staticmethod
    def create_statistics_summary(stats: Dict[str, Any]) -> go.Figure:
        """
        Create a summary visualization of research statistics
        
        Args:
            stats: Dictionary of statistics
            
        Returns:
            Plotly figure
        """
        if not stats:
            # Demo statistics
            stats = {
                "Total Papers": 25,
                "Average Citations": 45,
                "Publication Years": "2018-2023",
                "Total Authors": 67,
                "Research Methods": 5
            }
        
        # Create a table visualization
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Metric', 'Value'],
                fill_color='paleturquoise',
                align='left',
                font=dict(size=14)
            ),
            cells=dict(
                values=[list(stats.keys()), list(stats.values())],
                fill_color='lavender',
                align='left',
                font=dict(size=12),
                height=30
            )
        )])
        
        fig.update_layout(
            title="Research Statistics Summary",
            height=300
        )
        
        return fig
    
    @staticmethod
    def create_gap_analysis_chart(gaps: List[Dict[str, Any]]) -> go.Figure:
        """
        Create a visualization of research gaps
        
        Args:
            gaps: List of research gaps with importance scores
            
        Returns:
            Plotly figure
        """
        if not gaps:
            # Demo data
            gaps = [
                {"gap": "Limited longitudinal studies", "importance": 8},
                {"gap": "Lack of cross-cultural validation", "importance": 7},
                {"gap": "Insufficient sample sizes", "importance": 6},
                {"gap": "Need for mixed methods", "importance": 9},
                {"gap": "Theory development needed", "importance": 8}
            ]
        
        df = pd.DataFrame(gaps)
        
        fig = go.Figure(data=[go.Bar(
            y=df['gap'],
            x=df['importance'],
            orientation='h',
            marker=dict(
                color=df['importance'],
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="Importance")
            ),
            text=df['importance'],
            textposition='outside'
        )])
        
        fig.update_layout(
            title="Research Gap Analysis",
            xaxis_title="Importance Score",
            yaxis_title="Research Gaps",
            height=400,
            margin=dict(l=200)
        )
        
        return fig