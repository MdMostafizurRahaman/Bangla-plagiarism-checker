import fitz
import google.generativeai as genai
import base64
import io
from PIL import Image
import time
import os

# Gemini API Key
GEMINI_API_KEY = "AIzaSyA2cqiH1MecukxgSyMtZ9K2zSZG3O3Rkoo"

def setup_gemini():
    """Setup Gemini API"""
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        return genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        print(f"❌ Gemini setup failed: {e}")
        return None

def save_text_to_file(text, filename="extracted_text.txt"):
    """Save text to file with UTF-8 encoding"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"💾 Text saved to '{filename}'")

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
        
        # Create detailed prompt for Gemini
        prompt = """
        আপনি একটি বিশেষজ্ঞ OCR সিস্টেম। এই ইমেজে যে টেক্সট আছে তা সম্পূর্ণ নির্ভুলভাবে এক্সট্র্যাক্ট করুন।

        গুরুত্বপূর্ণ নির্দেশনা:
        1. বাংলা টেক্সট অবশ্যই সঠিক ইউনিকোড বাংলায় লিখুন (যেমন: ক, খ, গ, ঘ)
        2. ইংরেজি টেক্সট যেমন আছে ঠিক তেমন রাখুন
        3. সকল নম্বর, বিরাম চিহ্ন, বিশেষ চিহ্ন সংরক্ষণ করুন
        4. লাইন ব্রেক এবং প্যারাগ্রাফ স্ট্রাকচার বজায় রাখুন
        5. শিরোনাম, উপশিরোনাম, তালিকা - সবকিছুর ফরম্যাট রক্ষা করুন
        6. যদি কোনো টেক্সট পড়তে সমস্যা হয় তবে [অস্পষ্ট] লিখুন
        7. SutonnyMJ বা অন্য কোনো legacy ফন্ট থাকলে সেটি ইউনিকোড বাংলায় কনভার্ট করুন

        উদাহরণ:
        - ভুল: kvwšÍ mvsevw`KZv
        - সঠিক: শান্তি সাংবাদিকতা

        শুধুমাত্র এক্সট্র্যাক্ট করা টেক্সট দিন, কোনো ব্যাখ্যা বা মন্তব্য নয়।
        """
        
        # Send request to Gemini
        response = model.generate_content([
            prompt, 
            {"mime_type": "image/png", "data": img_base64}
        ])
        
        if response.text:
            return response.text.strip()
        else:
            print("⚠ Gemini returned empty response")
            return ""
            
    except Exception as e:
        print(f"⚠ Gemini extraction error: {e}")
        return ""

def extract_text_with_pymupdf_and_gemini(pdf_file, use_gemini=True):
    """
    Extract text using PyMuPDF for images and Gemini for OCR
    """
    print(f"📘 Processing: {pdf_file}")
    
    if not os.path.exists(pdf_file):
        print("❌ PDF file not found!")
        return ""
    
    # Setup Gemini
    model = None
    if use_gemini:
        model = setup_gemini()
        if model:
            print("🤖 Gemini AI initialized successfully")
        else:
            print("❌ Gemini AI failed to initialize")
            return ""
    
    def is_valid_bangla_text(text):
        """Check if text contains meaningful Bangla content"""
        if not text or len(text.strip()) < 30:
            return False
        
        # Count Bangla Unicode characters
        bangla_chars = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars > 0:
            bangla_ratio = bangla_chars / total_chars
            return bangla_ratio > 0.2 or bangla_chars > 15
        
        return False
    
    try:
        # First try embedded text extraction
        print("🔍 Checking embedded text...")
        doc = fitz.open(pdf_file)
        embedded_text = ""
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            page_text = page.get_text("text")
            if page_text.strip():
                embedded_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        
        # Check if embedded text is good quality Bangla
        if len(embedded_text.strip()) > 100 and is_valid_bangla_text(embedded_text):
            print("✅ Found valid Bangla in embedded text")
            doc.close()
            return embedded_text
        elif len(embedded_text.strip()) > 100:
            print("⚠ Embedded text found but appears to be legacy font encoding")
        else:
            print("⚠ No meaningful embedded text found")
        
        # Use Gemini OCR on page images
        if use_gemini and model:
            print("🔄 Using Gemini AI for OCR extraction...")
            full_text = ""
            
            for page_num in range(doc.page_count):
                print(f"🔍 Processing page {page_num + 1}/{doc.page_count}...")
                
                # Get page as image
                page = doc[page_num]
                
                # Render page to image with high resolution
                mat = fitz.Matrix(3.0, 3.0)  # 3x zoom for better quality
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                
                # Extract text using Gemini
                print(f"  🤖 Gemini analyzing page {page_num + 1}...")
                page_text = extract_text_with_gemini(image, model)
                
                if page_text:
                    full_text += f"\n\n=== Page {page_num + 1} ===\n{page_text}"
                    print(f"  ✅ Extracted {len(page_text)} characters")
                else:
                    print(f"  ⚠ No text extracted from page {page_num + 1}")
                
                # Rate limiting
                time.sleep(2)
            
            doc.close()
            return full_text
        
        else:
            print("❌ Gemini not available for OCR")
            doc.close()
            return embedded_text  # Return embedded text as fallback
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return ""

def main():
    """Main function to test the extractor"""
    print("🚀 Starting Gemini-powered PDF text extraction...")
    
    # Test with available PDF
    pdf_files = ["002.pdf", "017.pdf"]
    
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            print(f"\n📋 Processing: {pdf_file}")
            
            # Extract text
            text = extract_text_with_pymupdf_and_gemini(pdf_file, use_gemini=True)
            
            if text and len(text.strip()) > 100:
                # Save result
                output_filename = f"{pdf_file.replace('.pdf', '')}_gemini_extracted.txt"
                save_text_to_file(text, output_filename)
                
                # Show summary
                lines = text.split('\n')
                bangla_chars = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
                english_chars = sum(1 for c in text if c.isascii() and c.isalpha())
                
                print(f"\n📊 Extraction Summary:")
                print(f"  • Total characters: {len(text):,}")
                print(f"  • Total lines: {len(lines):,}")
                print(f"  • Bangla characters: {bangla_chars:,}")
                print(f"  • English characters: {english_chars:,}")
                print(f"  • Saved to: {output_filename}")
                
                # Show preview
                preview_lines = [line.strip() for line in lines if line.strip()][:8]
                print(f"\n👀 Preview:")
                for i, line in enumerate(preview_lines, 1):
                    display_line = line[:80] + "..." if len(line) > 80 else line
                    print(f"  {i}. {display_line}")
                
                break  # Success, stop trying other files
            else:
                print(f"❌ Failed to extract meaningful text from {pdf_file}")
    
    else:
        print("❌ No suitable PDF files found!")

if __name__ == "__main__":
    main()