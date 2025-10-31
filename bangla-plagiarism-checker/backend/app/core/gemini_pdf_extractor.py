"""
Gemini AI-powered PDF text extraction with advanced Bangla text recognition
Integration wrapper for the plagiarism checker backend
"""

import fitz  # PyMuPDF
import google.generativeai as genai
from PIL import Image
import io
import os
import tempfile
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gemini API Key - Load from environment
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class GeminiPDFExtractor:
    """Gemini AI-powered PDF text extractor for Bangla academic documents"""
    
    def __init__(self):
        self.model = self.setup_gemini()
        self.temp_dir = tempfile.mkdtemp()
    
    def setup_gemini(self):
        """Setup Gemini API"""
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            return genai.GenerativeModel('gemini-2.0-flash')
        except Exception as e:
            logger.error(f"❌ Gemini setup failed: {e}")
            return None
    
    def extract_text_from_page(self, page_image: Image.Image, page_num: int) -> str:
        """Extract text from a single page using Gemini AI"""
        if not self.model:
            return ""
        
        try:
            # Prepare prompt for Bangla text extraction
            prompt = """
            Extract ALL text from this image with high accuracy. This is an academic document that may contain:
            - Bengali/Bangla text (বাংলা টেক্সট)
            - English text
            - Mixed content
            
            Requirements:
            1. Preserve exact text content
            2. Maintain proper line breaks and formatting
            3. Keep Bengali characters in Unicode format
            4. Preserve English text as-is
            5. Include all numbers, citations, and references
            6. Maintain paragraph structure
            
            Output only the extracted text, no additional commentary.
            """
            
            # Generate content using Gemini Vision
            response = self.model.generate_content([prompt, page_image])
            
            if response and response.text:
                return response.text.strip()
            else:
                logger.warning(f"⚠ No text extracted from page {page_num}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Gemini extraction failed for page {page_num}: {e}")
            return ""
    
    def has_embedded_text(self, pdf_path: str) -> bool:
        """Check if PDF has embedded text"""
        try:
            doc = fitz.open(pdf_path)
            has_text = False
            
            for page_num in range(min(3, len(doc))):  # Check first 3 pages
                page = doc[page_num]
                text = page.get_text().strip()
                if len(text) > 100:  # Meaningful text threshold
                    has_text = True
                    break
            
            doc.close()
            return has_text
        except Exception as e:
            logger.error(f"❌ Error checking embedded text: {e}")
            return False
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Main extraction method compatible with backend interface
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            Dict with 'text', 'error', and 'metadata' keys
        """
        try:
            logger.info(f"🚀 Starting Gemini PDF extraction: {pdf_path}")
            
            # Check if file exists
            if not os.path.exists(pdf_path):
                return {
                    'text': '',
                    'error': f'File not found: {pdf_path}',
                    'metadata': {}
                }
            
            # Open PDF
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            # Check for embedded text first
            if self.has_embedded_text(pdf_path):
                logger.info("📄 Trying embedded text extraction first...")
                embedded_text = ""
                for page in doc:
                    embedded_text += page.get_text("text") + "\n"
                
                # Check if embedded text is valid Bengali
                if len(embedded_text.strip()) > 500 and self._is_bangla_content(embedded_text):
                    logger.info("✅ Valid embedded text found")
                    doc.close()
                    return {
                        'text': self.clean_extracted_text(embedded_text),
                        'error': None,
                        'metadata': {
                            'total_pages': total_pages,
                            'total_characters': len(embedded_text),
                            'extraction_method': 'embedded_text',
                            'model': 'built-in'
                        }
                    }
                else:
                    logger.info("⚠ Embedded text not suitable, using Gemini AI...")
            
            logger.info(f"📄 Processing {total_pages} pages with Gemini AI...")
            
            # Process all pages for complete extraction
            max_pages = total_pages  # Process all pages for complete extraction
            extracted_text = []
            
            for page_num in range(max_pages):
                page = doc[page_num]
                
                # Convert page to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  # High resolution
                img_data = pix.tobytes("png")
                page_image = Image.open(io.BytesIO(img_data))
                
                logger.info(f"🔍 Processing page {page_num + 1}/{max_pages}...")
                
                # Extract text using Gemini
                page_text = self.extract_text_from_page(page_image, page_num + 1)
                
                if page_text:
                    extracted_text.append(page_text)
                    logger.info(f"  ✅ Extracted {len(page_text)} characters")
                else:
                    logger.warning(f"  ⚠ No text extracted from page {page_num + 1}")
            
            doc.close()
            
            # If we got nothing from Gemini, try OCR fallback
            if not any(extracted_text):
                logger.info("🔄 Gemini failed, trying PyMuPDF extraction...")
                doc = fitz.open(pdf_path)
                fallback_text = ""
                for page in doc:
                    fallback_text += page.get_text() + "\n"
                doc.close()
                
                if fallback_text.strip():
                    full_text = self.clean_extracted_text(fallback_text)
                else:
                    full_text = "টেক্সট নিষ্কাশন করা যায়নি। দয়া করে আবার চেষ্টা করুন।"
            else:
                # Combine all text
                full_text = "\n\n".join(extracted_text)
                full_text = self.clean_extracted_text(full_text)
            
            # Calculate metadata
            metadata = {
                'total_pages': total_pages,
                'total_characters': len(full_text),
                'extraction_method': 'gemini_ai',
                'model': 'gemini-2.0-flash',
                'pages_processed': max_pages
            }
            
            logger.info(f"✅ Extraction completed: {len(full_text)} characters")
            
            return {
                'text': full_text,
                'error': None,
                'metadata': metadata
            }
            
        except Exception as e:
            error_msg = f"Gemini extraction failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                'text': '',
                'error': error_msg,
                'metadata': {}
            }
    
    def _is_bangla_content(self, text: str) -> bool:
        """Check if text contains significant Bengali content"""
        if not text or len(text.strip()) < 100:
            return False
        
        # Count Bengali characters
        bangla_chars = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars == 0:
            return False
        
        # Accept if >10% Bengali characters or has significant amount
        return (bangla_chars / total_chars) > 0.1 or bangla_chars > 50
    
    def clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        import re
        
        # Split into lines
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines but preserve paragraph breaks
            if not line:
                if cleaned_lines and cleaned_lines[-1] != '':
                    cleaned_lines.append('')
                continue
            
            # Basic cleaning
            line = re.sub(r'\s+', ' ', line)  # Normalize whitespace
            cleaned_lines.append(line)
        
        # Join lines back
        result = '\n'.join(cleaned_lines)
        
        # Fix excessive line breaks
        result = re.sub(r'\n\n\n+', '\n\n', result)
        
        return result.strip()

# Main interface function for backend compatibility
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Main extraction function compatible with existing backend
    
    Args:
        pdf_path (str): Path to PDF file
        
    Returns:
        str: Extracted text content
    """
    extractor = GeminiPDFExtractor()
    result = extractor.extract_text_from_pdf(pdf_path)
    
    if result['error']:
        logger.error(f"Extraction failed: {result['error']}")
        return ""
    
    return result['text']

# Test function
if __name__ == "__main__":
    # Test with 002.pdf
    test_file = "d:/Bangla Plagiarism/002.pdf"
    
    extractor = GeminiPDFExtractor()
    result = extractor.extract_text_from_pdf(test_file)
    
    if result['error']:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Success! Extracted {len(result['text'])} characters")
        print(f"📊 Metadata: {result['metadata']}")
        print(f"\n📝 First 1000 characters:")
        print(result['text'][:1000])