import fitz
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import os
import shutil
import cv2
import numpy as np
import re
import pandas as pd
from typing import List, Dict, Tuple, Optional
import logging
from dataclasses import dataclass
import unicodedata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TextRegion:
    """Represents a text region with its content and properties"""
    text: str
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    confidence: float
    is_table: bool = False
    line_number: int = 0

@dataclass
class TableCell:
    """Represents a table cell"""
    text: str
    row: int
    col: int
    bbox: Tuple[int, int, int, int]

class EnhancedBanglaPDFExtractor:
    """Enhanced PDF text extractor specifically designed for Bangla academic documents"""
    
    def __init__(self):
        self.temp_dir = 'temp_extraction'
        self.dpi = 400  # High DPI for better quality
        
        # Tesseract configuration for better Bangla recognition
        self.tesseract_config = {
            'basic': r'--oem 3 --psm 6 -c preserve_interword_spaces=1',
            'table': r'--oem 3 --psm 6 -c preserve_interword_spaces=1 -c textord_tabfind_find_tables=1',
            'line_detection': r'--oem 3 --psm 13 -c preserve_interword_spaces=1'
        }
    
    def normalize_bangla_text(self, text: str) -> str:
        """Normalize Bangla Unicode text"""
        if not text:
            return ""
        
        # Unicode normalization
        text = unicodedata.normalize('NFC', text)
        
        # Common Bangla text corrections
        replacements = {
            'ি': 'ি',  # Fix common vowel sign issues
            'ী': 'ী',
            'ু': 'ু',
            'ূ': 'ূ',
            'ে': 'ে',
            'ো': 'ো',
        }
        
        for wrong, correct in replacements.items():
            text = text.replace(wrong, correct)
        
        return text
    
    def is_valid_bangla_text(self, text: str, min_chars: int = 10) -> bool:
        """Check if text contains valid Bangla content"""
        if not text or len(text.strip()) < min_chars:
            return False
        
        # Count Bangla characters (standard Unicode range)
        bangla_chars = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
        
        # Count extended Latin characters (often used in legacy Bangla fonts)
        extended_latin = sum(1 for c in text if 0x00C0 <= ord(c) <= 0x024F)
        
        # Count characters with diacritical marks (common in legacy Bangla)
        diacritical = sum(1 for c in text if 0x0100 <= ord(c) <= 0x017F)
        
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars == 0:
            return False
        
        # Consider it valid Bangla if:
        # 1. Standard Bangla Unicode characters
        # 2. Has extended Latin (legacy font encoding)
        # 3. Mixed content with some Bangla-like patterns
        bangla_ratio = bangla_chars / total_chars
        legacy_ratio = (extended_latin + diacritical) / total_chars
        
        # Accept if has standard Bangla chars OR legacy encoding patterns OR meaningful text
        is_standard_bangla = bangla_ratio > 0.3 or bangla_chars > 20
        is_legacy_bangla = legacy_ratio > 0.01 and total_chars > 30  # More permissive
        has_meaningful_content = len(text.strip()) > 100 and total_chars > 50  # Has substantial content
        
        return is_standard_bangla or is_legacy_bangla or has_meaningful_content
    
    def preprocess_image_advanced(self, image: Image.Image) -> Image.Image:
        """Advanced image preprocessing for better OCR results"""
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Noise reduction with bilateral filter
        bilateral = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            bilateral, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            15, 3
        )
        
        # Morphological operations to connect broken characters
        kernel_close = np.ones((1, 2), np.uint8)
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel_close)
        
        # Remove small noise
        kernel_open = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel_open)
        
        # Convert back to PIL Image
        processed_image = Image.fromarray(cleaned)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(processed_image)
        sharpened = enhancer.enhance(1.3)
        
        return sharpened
    
    def detect_text_regions(self, image: Image.Image) -> List[TextRegion]:
        """Detect and classify text regions including tables"""
        img_array = np.array(image)
        
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Detect lines and rectangles for table detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Detect horizontal and vertical lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        
        horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
        
        # Combine lines to detect table regions
        table_mask = cv2.add(horizontal_lines, vertical_lines)
        
        # Find contours for text regions
        contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        text_regions = []
        
        # Get text regions using Tesseract
        try:
            # Get bounding boxes for all text
            data = pytesseract.image_to_data(image, lang='ben+eng', 
                                           config=self.tesseract_config['line_detection'],
                                           output_type=pytesseract.Output.DICT)
            
            for i, text in enumerate(data['text']):
                if text.strip():
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    conf = data['conf'][i]
                    
                    if conf > 30:  # Only consider confident detections
                        bbox = (x, y, x + w, y + h)
                        
                        # Check if this region intersects with table lines
                        is_table = self._intersects_with_table(bbox, table_mask)
                        
                        region = TextRegion(
                            text=text.strip(),
                            bbox=bbox,
                            confidence=conf,
                            is_table=is_table
                        )
                        text_regions.append(region)
        
        except Exception as e:
            logger.warning(f"Error in text region detection: {e}")
        
        return text_regions
    
    def _intersects_with_table(self, bbox: Tuple[int, int, int, int], table_mask: np.ndarray) -> bool:
        """Check if a bounding box intersects with table lines"""
        x1, y1, x2, y2 = bbox
        roi = table_mask[y1:y2, x1:x2]
        return np.any(roi > 0)
    
    def extract_table_content(self, image: Image.Image, table_regions: List[TextRegion]) -> str:
        """Extract structured table content"""
        if not table_regions:
            return ""
        
        # Group table regions by proximity
        tables = self._group_table_regions(table_regions)
        
        table_text = ""
        for i, table in enumerate(tables):
            table_text += f"\n=== Table {i+1} ===\n"
            
            # Sort cells by position (top to bottom, left to right)
            sorted_cells = sorted(table, key=lambda x: (x.bbox[1], x.bbox[0]))
            
            # Convert to structured format
            table_data = self._organize_table_cells(sorted_cells)
            table_text += table_data + "\n"
        
        return table_text
    
    def _group_table_regions(self, regions: List[TextRegion]) -> List[List[TextRegion]]:
        """Group table regions that belong to the same table"""
        tables = []
        used = set()
        
        for i, region in enumerate(regions):
            if i in used or not region.is_table:
                continue
            
            table_group = [region]
            used.add(i)
            
            # Find nearby table regions
            for j, other in enumerate(regions):
                if j in used or not other.is_table:
                    continue
                
                if self._are_regions_close(region, other):
                    table_group.append(other)
                    used.add(j)
            
            if len(table_group) > 1:  # Only consider groups with multiple cells
                tables.append(table_group)
        
        return tables
    
    def _are_regions_close(self, region1: TextRegion, region2: TextRegion, 
                          threshold: int = 100) -> bool:
        """Check if two regions are close enough to be in the same table"""
        x1, y1, x2, y2 = region1.bbox
        x3, y3, x4, y4 = region2.bbox
        
        # Calculate center points
        center1 = ((x1 + x2) // 2, (y1 + y2) // 2)
        center2 = ((x3 + x4) // 2, (y3 + y4) // 2)
        
        # Calculate distance
        distance = np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
        
        return distance < threshold
    
    def _organize_table_cells(self, cells: List[TextRegion]) -> str:
        """Organize table cells into a readable format"""
        if not cells:
            return ""
        
        # Simple approach: organize by rows based on Y coordinates
        rows = {}
        
        for cell in cells:
            y_center = (cell.bbox[1] + cell.bbox[3]) // 2
            
            # Find the closest row (within 20 pixels)
            best_row = None
            min_diff = 20
            
            for row_y in rows.keys():
                diff = abs(y_center - row_y)
                if diff < min_diff:
                    min_diff = diff
                    best_row = row_y
            
            if best_row is None:
                best_row = y_center
                rows[best_row] = []
            
            rows[best_row].append(cell)
        
        # Sort rows by Y coordinate and cells within rows by X coordinate
        table_text = ""
        for row_y in sorted(rows.keys()):
            row_cells = sorted(rows[row_y], key=lambda x: x.bbox[0])
            row_text = " | ".join(cell.text for cell in row_cells)
            table_text += row_text + "\n"
        
        return table_text
    
    def extract_text_with_structure(self, image: Image.Image) -> Tuple[str, List[TextRegion]]:
        """Extract text while preserving document structure"""
        # Preprocess image
        processed_img = self.preprocess_image_advanced(image)
        
        # Detect text regions
        text_regions = self.detect_text_regions(processed_img)
        
        # Separate table and regular text regions
        table_regions = [r for r in text_regions if r.is_table]
        text_regions_only = [r for r in text_regions if not r.is_table]
        
        # Extract regular text with line preservation
        regular_text = self._extract_structured_text(processed_img, text_regions_only)
        
        # Extract table content
        table_text = self.extract_table_content(processed_img, table_regions)
        
        # Combine texts
        full_text = regular_text
        if table_text:
            full_text += "\n\n" + table_text
        
        return full_text, text_regions
    
    def _extract_structured_text(self, image: Image.Image, regions: List[TextRegion]) -> str:
        """Extract text while preserving line structure"""
        try:
            # Use line-by-line extraction with PSM 4 (single column)
            config = r'--oem 3 --psm 4 -c preserve_interword_spaces=1'
            text = pytesseract.image_to_string(image, lang='ben+eng', config=config)
            
            # Clean and normalize the text
            lines = text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if line:  # Skip empty lines
                    # Normalize Bangla text
                    line = self.normalize_bangla_text(line)
                    
                    # Fix common OCR errors for Bangla
                    line = self._fix_bangla_ocr_errors(line)
                    
                    cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)
        
        except Exception as e:
            logger.error(f"Error in structured text extraction: {e}")
            return ""
    
    def _fix_bangla_ocr_errors(self, text: str) -> str:
        """Fix common OCR errors in Bangla text"""
        # Common OCR misrecognitions for Bangla
        corrections = {
            'ঢ': 'ধ',  # Common confusions
            'ও': 'ে',
            'া': 'ি',
            '০': 'ও',
            '১': 'ল',
            '৩': 'য',
        }
        
        # Apply corrections carefully (only if it makes sense contextually)
        for wrong, correct in corrections.items():
            # Add context-aware corrections here
            pass
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Fix line breaks within sentences
        text = re.sub(r'(\S)\n(\S)', r'\1 \2', text)
        
        return text.strip()
    
    def process_pdf_enhanced(self, pdf_path: str, lang: str = 'ben+eng', 
                           force_ocr: bool = False) -> Dict:
        """Enhanced PDF processing with improved text extraction"""
        logger.info(f"📘 Processing PDF: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            return {"error": "PDF file not found", "text": "", "metadata": {}}
        
        try:
            # Create temp directory
            if not os.path.exists(self.temp_dir):
                os.makedirs(self.temp_dir)
            
            metadata = {
                "total_pages": 0,
                "extraction_method": "",
                "tables_found": 0,
                "confidence_avg": 0.0,
                "processing_time": 0
            }
            
            # Try embedded text extraction first
            embedded_text = ""
            if not force_ocr:
                embedded_text = self._extract_embedded_text(pdf_path)
                if self.is_valid_bangla_text(embedded_text, min_chars=100):
                    logger.info("✅ Valid embedded text found")
                    metadata["extraction_method"] = "embedded"
                    return {
                        "text": self.normalize_bangla_text(embedded_text),
                        "metadata": metadata,
                        "error": None
                    }
                else:
                    logger.info("⚠ Embedded text not suitable, using OCR")
            
            # Use OCR extraction
            logger.info("🔄 Using enhanced OCR extraction...")
            metadata["extraction_method"] = "ocr"
            
            # Convert PDF to images
            try:
                # Try pdf2image first (requires poppler)
                images = convert_from_path(pdf_path, dpi=self.dpi)
                logger.info(f"✅ Using pdf2image for {len(images)} pages")
            except Exception as e:
                logger.warning(f"⚠️ pdf2image failed: {e}")
                logger.info("🔄 Falling back to PyMuPDF for image conversion...")
                
                # Try Gemini AI as fallback
                try:
                    from .gemini_pdf_extractor import GeminiPDFExtractor
                    logger.info("🤖 Trying Gemini AI extraction as fallback...")
                    gemini_extractor = GeminiPDFExtractor()
                    gemini_result = gemini_extractor.extract_text_from_pdf(pdf_path)
                    
                    if not gemini_result['error'] and len(gemini_result['text']) > 100:
                        logger.info("✅ Gemini AI extraction successful!")
                        metadata["extraction_method"] = "gemini_ai"
                        metadata.update(gemini_result['metadata'])
                        return {
                            "text": gemini_result['text'],
                            "metadata": metadata,
                            "error": None
                        }
                    else:
                        logger.warning("⚠ Gemini AI extraction failed, continuing with PyMuPDF...")
                except Exception as gemini_error:
                    logger.warning(f"⚠ Gemini AI fallback failed: {gemini_error}")
                    logger.info("🔄 Continuing with PyMuPDF...")
                
                
                # Fallback to PyMuPDF
                doc = fitz.open(pdf_path)
                images = []
                
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    
                    # Render page to pixmap with high DPI
                    mat = fitz.Matrix(self.dpi/72, self.dpi/72)
                    pix = page.get_pixmap(matrix=mat)
                    
                    # Convert to PIL Image
                    img_data = pix.tobytes("png")
                    from io import BytesIO
                    image = Image.open(BytesIO(img_data))
                    images.append(image)
                
                doc.close()
                logger.info(f"✅ Using PyMuPDF fallback for {len(images)} pages")
            
            metadata["total_pages"] = len(images)
            
            full_text = ""
            all_regions = []
            total_confidence = 0
            confidence_count = 0
            tables_found = 0
            
            for i, img in enumerate(images, 1):
                logger.info(f"Processing page {i}/{len(images)}...")
                
                # Extract text with structure
                page_text, regions = self.extract_text_with_structure(img)
                
                if page_text.strip():
                    full_text += f"\n--- Page {i} ---\n{page_text}\n"
                
                # Update metadata
                table_regions = [r for r in regions if r.is_table]
                tables_found += len(table_regions)
                
                for region in regions:
                    total_confidence += region.confidence
                    confidence_count += 1
                
                all_regions.extend(regions)
            
            # Calculate average confidence
            if confidence_count > 0:
                metadata["confidence_avg"] = total_confidence / confidence_count
            
            metadata["tables_found"] = tables_found
            
            # Final text processing
            final_text = self.post_process_text(full_text)
            
            logger.info("✅ Enhanced OCR extraction complete!")
            
            return {
                "text": final_text,
                "metadata": metadata,
                "error": None,
                "regions": len(all_regions)
            }
        
        except Exception as e:
            logger.error(f"❌ Enhanced extraction failed: {e}")
            return {
                "error": str(e),
                "text": "",
                "metadata": metadata
            }
        
        finally:
            # Cleanup
            if os.path.exists(self.temp_dir):
                try:
                    shutil.rmtree(self.temp_dir)
                except:
                    pass
    
    def _extract_embedded_text(self, pdf_path: str) -> str:
        """Extract embedded text from PDF"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text("text") + "\n"
            doc.close()
            return text
        except Exception as e:
            logger.warning(f"Embedded text extraction failed: {e}")
            return ""
    
    def post_process_text(self, text: str) -> str:
        """Final text processing and cleanup"""
        if not text:
            return ""
        
        # Split into lines for processing
        lines = text.split('\n')
        processed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip page markers but keep section markers
            if line.startswith('--- Page ') and line.endswith(' ---'):
                processed_lines.append(line)
                continue
            
            # Normalize Bangla text
            line = self.normalize_bangla_text(line)
            
            # Remove excessive whitespace
            line = re.sub(r'\s+', ' ', line)
            
            # Add line if it has meaningful content
            if len(line.strip()) > 2:
                processed_lines.append(line)
        
        # Join lines back
        result = '\n'.join(processed_lines)
        
        # Fix paragraph breaks
        result = re.sub(r'\n\n\n+', '\n\n', result)
        
        return result.strip()
    
    def save_extracted_text(self, text: str, filename: str = "extracted_text.txt") -> str:
        """Save extracted text to file"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(text)
            logger.info(f"💾 Text saved to '{filename}'")
            return filename
        except Exception as e:
            logger.error(f"Failed to save text: {e}")
            return ""

# Example usage and testing
if __name__ == "__main__":
    extractor = EnhancedBanglaPDFExtractor()
    
    # Test with your PDF
    pdf_file = "017.pdf"  # Replace with your PDF path
    
    result = extractor.process_pdf_enhanced(pdf_file, lang='ben+eng')
    
    if result["error"]:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Extraction successful!")
        print(f"📊 Metadata: {result['metadata']}")
        print(f"📄 Text length: {len(result['text'])} characters")
        
        # Save to file
        extractor.save_extracted_text(result["text"], "enhanced_extraction.txt")
        
        # Show first 500 characters
        print(f"\n📝 First 500 characters:")
        print(result["text"][:500])

# Main interface function for backend compatibility
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Main extraction function compatible with existing backend
    
    Args:
        pdf_path (str): Path to PDF file
        
    Returns:
        str: Extracted text content
    """
    extractor = EnhancedBanglaPDFExtractor()
    result = extractor.process_pdf_enhanced(pdf_path, lang='ben+eng')
    
    if result['error']:
        logger.error(f"Enhanced extraction failed: {result['error']}")
        # Try Gemini as final fallback
        try:
            from .gemini_pdf_extractor import extract_text_from_pdf as gemini_extract
            logger.info("🤖 Trying Gemini AI as final fallback...")
            gemini_text = gemini_extract(pdf_path)
            if gemini_text and len(gemini_text) > 100:
                logger.info("✅ Gemini AI final fallback successful!")
                return gemini_text
        except Exception as e:
            logger.warning(f"⚠ Gemini final fallback failed: {e}")
        
        return ""
    
    return result['text']