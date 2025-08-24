"""File processing module for handling various document formats"""

import io
import base64
from typing import List, Dict, Any, Optional
from pypdf import PdfReader
from PIL import Image
import streamlit as st
from config.settings import Config

class FileProcessor:
    """Process various file formats for analysis"""
    
    @staticmethod
    def process_uploaded_files(uploaded_files) -> List[Dict[str, Any]]:
        """
        Process multiple uploaded files
        
        Args:
            uploaded_files: List of uploaded file objects from Streamlit
            
        Returns:
            List of processed file data
        """
        processed_files = []
        
        for file in uploaded_files:
            if file is not None:
                file_data = FileProcessor.process_single_file(file)
                if file_data:
                    processed_files.append(file_data)
        
        return processed_files
    
    @staticmethod
    def process_single_file(file) -> Optional[Dict[str, Any]]:
        """
        Process a single uploaded file
        
        Args:
            file: Uploaded file object from Streamlit
            
        Returns:
            Processed file data or None if processing fails
        """
        try:
            file_extension = file.name.split('.')[-1].lower()
            
            # Check file size
            file_size_mb = file.size / (1024 * 1024)
            if file_size_mb > Config.MAX_FILE_SIZE_MB:
                st.error(f"File {file.name} exceeds maximum size of {Config.MAX_FILE_SIZE_MB}MB")
                return None
            
            # Process based on file type
            if file_extension == 'pdf':
                content = FileProcessor.extract_pdf_text(file)
            elif file_extension == 'txt':
                content = FileProcessor.extract_text(file)
            elif file_extension in ['jpg', 'jpeg', 'png']:
                content = FileProcessor.process_image(file)
            elif file_extension == 'docx':
                content = FileProcessor.extract_docx_text(file)
            else:
                st.warning(f"Unsupported file type: {file_extension}")
                return None
            
            return {
                "filename": file.name,
                "content": content,
                "type": file_extension,
                "size": file_size_mb
            }
            
        except Exception as e:
            st.error(f"Error processing file {file.name}: {str(e)}")
            return None
    
    @staticmethod
    def extract_pdf_text(file) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PdfReader(file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
            
            return text.strip()
            
        except Exception as e:
            st.error(f"Error extracting PDF text: {str(e)}")
            return ""
    
    @staticmethod
    def extract_text(file) -> str:
        """Extract text from text file"""
        try:
            return file.read().decode('utf-8')
        except UnicodeDecodeError:
            try:
                # Try with different encoding
                file.seek(0)
                return file.read().decode('latin-1')
            except:
                st.error("Unable to decode text file")
                return ""
    
    @staticmethod
    def extract_docx_text(file) -> str:
        """Extract text from DOCX file"""
        try:
            import docx
            doc = docx.Document(file)
            text = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)
            
            return "\n\n".join(text)
            
        except Exception as e:
            st.error(f"Error extracting DOCX text: {str(e)}")
            return ""
    
    @staticmethod
    def process_image(file) -> str:
        """Process image file for GPT-5 multimodal analysis"""
        try:
            # Read image
            image = Image.open(file)
            
            # Convert to base64 for GPT-5
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Return as data URL for GPT-5
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            return ""
    
    @staticmethod
    def chunk_text(text: str, max_chunk_size: int = 3000) -> List[str]:
        """
        Split text into chunks for processing
        
        Args:
            text: Text to chunk
            max_chunk_size: Maximum size of each chunk
            
        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            word_size = len(word) + 1  # +1 for space
            
            if current_size + word_size > max_chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_size = word_size
            else:
                current_chunk.append(word)
                current_size += word_size
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    @staticmethod
    def validate_file(file) -> bool:
        """
        Validate uploaded file
        
        Args:
            file: Uploaded file object
            
        Returns:
            True if file is valid
        """
        if file is None:
            return False
        
        # Check file extension
        file_extension = file.name.split('.')[-1].lower()
        if file_extension not in Config.ALLOWED_FILE_TYPES:
            st.error(f"File type .{file_extension} not allowed. Allowed types: {', '.join(Config.ALLOWED_FILE_TYPES)}")
            return False
        
        # Check file size
        file_size_mb = file.size / (1024 * 1024)
        if file_size_mb > Config.MAX_FILE_SIZE_MB:
            st.error(f"File size {file_size_mb:.2f}MB exceeds maximum of {Config.MAX_FILE_SIZE_MB}MB")
            return False
        
        return True