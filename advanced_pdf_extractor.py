import fitz
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter
import os
import shutil
import cv2
import numpy as np
import google.generativeai as genai
import base64
import io
import time

# Gemini API Key
GEMINI_API_KEY = "AIzaSyA2cqiH1MecukxgSyMtZ9K2zSZG3O3Rkoo"

def setup_gemini():
    """Setup Gemini API"""
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel('gemini-1.5-flash')

def save_text_to_file(text, filename="extracted_text.txt"):
    """Save text to file with UTF-8 encoding"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"💾 Text saved to '{filename}'")

def preprocess_image_for_ocr(image):
    """Enhanced image preprocessing for better OCR results"""
    # Convert PIL Image to numpy array
    img_array = np.array(image)
    
    # Convert to grayscale if needed
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array
    
    # Resize image for better OCR (if too small)
    height, width = gray.shape
    if height < 1000:
        scale_factor = 1000 / height
        new_width = int(width * scale_factor)
        gray = cv2.resize(gray, (new_width, 1000), interpolation=cv2.INTER_CUBIC)
    
    # Noise reduction
    denoised = cv2.fastNlMeansDenoising(gray)
    
    # Apply bilateral filter to preserve edges
    bilateral = cv2.bilateralFilter(denoised, 9, 75, 75)
    
    # Enhanced adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        bilateral, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        11, 2
    )
    
    # Morphological operations to clean up text
    kernel = np.ones((1, 1), np.uint8)
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # Remove small noise
    kernel2 = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel2)
    
    # Convert back to PIL Image
    processed_image = Image.fromarray(cleaned)
    
    # Enhance contrast and sharpness
    enhancer = ImageEnhance.Contrast(processed_image)
    contrast_enhanced = enhancer.enhance(1.3)
    
    sharpness_enhancer = ImageEnhance.Sharpness(contrast_enhanced)
    final_image = sharpness_enhancer.enhance(1.5)
    
    return final_image

def image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

def extract_text_with_gemini(image, model):
    """Extract text from image using Gemini Vision AI"""
    try:
        # Convert image to base64
        img_base64 = image_to_base64(image)
        
        # Create prompt for Gemini
        prompt = """
        আপনি একটি অভিজ্ঞ বাংলা এবং ইংরেজি OCR বিশেষজ্ঞ। এই ইমেজে যে টেক্সট আছে তা সম্পূর্ণ নির্ভুলভাবে এক্সট্র্যাক্ট করুন।

        নিয়মাবলী:
        1. বাংলা টেক্সট সঠিক ইউনিকোড বাংলায় লিখুন
        2. ইংরেজি টেক্সট যেমন আছে তেমন রাখুন
        3. সকল পাংচুয়েশন, নম্বর, বিশেষ চিহ্ন সংরক্ষণ করুন
        4. লাইন ব্রেক এবং ফরম্যাটিং বজায় রাখুন
        5. যদি কোনো টেক্সট অস্পষ্ট হয় তবে [অস্পষ্ট] লিখুন

        শুধুমাত্র এক্সট্র্যাক্ট করা টেক্সট দিন, অন্য কোনো মন্তব্য নয়।
        """
        
        # Send request to Gemini
        response = model.generate_content([prompt, {"mime_type": "image/png", "data": img_base64}])
        
        if response.text:
            return response.text.strip()
        else:
            return ""
            
    except Exception as e:
        print(f"⚠ Gemini extraction failed: {e}")
        return ""

def advanced_ocr_with_multiple_methods(image):
    """Try multiple OCR methods for better results"""
    results = []
    
    # Method 1: Tesseract with Bangla+English
    try:
        config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
        text1 = pytesseract.image_to_string(image, lang='ben+eng', config=config)
        if text1.strip():
            results.append(("Tesseract ben+eng", text1))
    except:
        pass
    
    # Method 2: Tesseract with Bangla only
    try:
        config = r'--oem 3 --psm 6'
        text2 = pytesseract.image_to_string(image, lang='ben', config=config)
        if text2.strip():
            results.append(("Tesseract ben", text2))
    except:
        pass
    
    # Method 3: Tesseract with different PSM
    try:
        config = r'--oem 3 --psm 3 -c preserve_interword_spaces=1'
        text3 = pytesseract.image_to_string(image, lang='ben+eng', config=config)
        if text3.strip():
            results.append(("Tesseract PSM3", text3))
    except:
        pass
    
    # Return the longest/best result
    if results:
        best_result = max(results, key=lambda x: len(x[1]))
        return best_result[1]
    
    return ""

def process_pdf_advanced(pdf_file, use_gemini=True, force_ocr=False):
    """
    Advanced PDF processing with multiple extraction methods
    """
    print(f"📘 Advanced Processing: {pdf_file}")
    
    if not os.path.exists(pdf_file):
        print("❌ PDF file not found!")
        return ""
    
    # Setup Gemini if requested
    model = None
    if use_gemini:
        try:
            model = setup_gemini()
            print("🤖 Gemini AI initialized")
        except Exception as e:
            print(f"⚠ Gemini setup failed: {e}")
            use_gemini = False
    
    def is_valid_bangla_text(text):
        """Check if text contains meaningful Bangla content"""
        if not text or len(text.strip()) < 30:
            return False
        
        # Check for Bangla Unicode characters
        bangla_chars = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars > 0:
            bangla_ratio = bangla_chars / total_chars
            return bangla_ratio > 0.3 or bangla_chars > 20
        
        return False
    
    # Try embedded text extraction first (unless forced OCR)
    if not force_ocr:
        try:
            print("🔍 Trying embedded text extraction...")
            doc = fitz.open(pdf_file)
            embedded_text = ""
            for page_num, page in enumerate(doc, 1):
                page_text = page.get_text("text")
                embedded_text += f"\n--- Page {page_num} ---\n{page_text}"
            doc.close()
            
            if len(embedded_text.strip()) > 100:
                if is_valid_bangla_text(embedded_text):
                    print("✅ Valid Bangla text found in embedded content")
                    return embedded_text
                else:
                    print("⚠ Embedded text found but appears to be corrupted font encoding")
        except Exception as e:
            print(f"⚠ Embedded text extraction failed: {e}")
    
    # Use OCR with image processing
    print("🔄 Using advanced OCR extraction...")
    
    try:
        # Convert PDF to high-quality images
        print("📸 Converting PDF to images (high quality)...")
        images = convert_from_path(pdf_file, dpi=300, fmt='png')
        
        full_text = ""
        
        for i, img in enumerate(images, 1):
            print(f"🔍 Processing page {i}/{len(images)}...")
            
            # Preprocess image
            processed_img = preprocess_image_for_ocr(img)
            
            # Save processed image for debugging (optional)
            # processed_img.save(f"debug_page_{i}.png")
            
            page_text = ""
            
            # Try Gemini AI first (if available)
            if use_gemini and model:
                print(f"  🤖 Using Gemini AI for page {i}...")
                gemini_text = extract_text_with_gemini(processed_img, model)
                if gemini_text and len(gemini_text.strip()) > 50:
                    page_text = gemini_text
                    print(f"  ✅ Gemini extracted {len(gemini_text)} characters")
                else:
                    print(f"  ⚠ Gemini result insufficient, trying OCR...")
            
            # If Gemini failed or not available, use advanced OCR
            if not page_text:
                print(f"  🔤 Using advanced OCR for page {i}...")
                ocr_text = advanced_ocr_with_multiple_methods(processed_img)
                if ocr_text:
                    page_text = ocr_text
                    print(f"  ✅ OCR extracted {len(ocr_text)} characters")
                else:
                    print(f"  ❌ OCR failed for page {i}")
            
            # Add page text to full text
            if page_text:
                full_text += f"\n\n=== Page {i} ===\n{page_text}"
            
            # Small delay to avoid API rate limits
            if use_gemini:
                time.sleep(1)
        
        print("✅ Advanced extraction complete!")
        return full_text
        
    except Exception as e:
        print(f"❌ Advanced extraction failed: {e}")
        return ""

# Test the advanced processor
if __name__ == "__main__":
    print("🚀 Starting advanced PDF text extraction...")
    
    # Process PDF with Gemini AI + Advanced OCR
    pdf_filename = "002.pdf"
    
    print(f"\n📋 Processing: {pdf_filename}")
    text = process_pdf_advanced(
        pdf_filename, 
        use_gemini=True,  # Use Gemini AI
        force_ocr=True   # Skip embedded text, go straight to OCR
    )
    
    if text:
        output_filename = "017_advanced_extracted.txt"
        save_text_to_file(text, output_filename)
        
        # Show summary
        lines = text.split('\n')
        bangla_chars = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
        
        print(f"\n📊 Extraction Summary:")
        print(f"  • Total characters: {len(text):,}")
        print(f"  • Total lines: {len(lines):,}")
        print(f"  • Bangla characters: {bangla_chars:,}")
        print(f"  • Saved to: {output_filename}")
        
        # Show first few lines as preview
        preview_lines = [line.strip() for line in lines[:10] if line.strip()]
        print(f"\n👀 Preview (first few lines):")
        for i, line in enumerate(preview_lines[:5], 1):
            print(f"  {i}. {line[:100]}{'...' if len(line) > 100 else ''}")
    else:
        print("❌ No text could be extracted from the PDF")