#!/usr/bin/env python3
"""
Test script for Bangla Plagiarism Checker with 002.pdf
"""

import requests
import os
import json
import time

def test_pdf_extraction():
    """Test PDF extraction with 002.pdf file"""
    
    # Configuration
    API_BASE = "http://localhost:8000"
    PDF_FILE = "002.pdf"
    
    print("🚀 Testing Bangla Plagiarism Checker with 002.pdf")
    print("=" * 60)
    
    # Step 1: Check API health
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print("✅ API Health Check:")
            print(f"   Status: {health['status']}")
            print(f"   Services: {health['services']}")
        else:
            print("❌ API health check failed")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False
    
    # Step 2: Check PDF file
    if not os.path.exists(PDF_FILE):
        print(f"❌ PDF file not found: {PDF_FILE}")
        print(f"Current directory: {os.getcwd()}")
        return False
    
    file_size = os.path.getsize(PDF_FILE)
    print(f"\n📄 PDF File Information:")
    print(f"   File: {PDF_FILE}")
    print(f"   Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    # Step 3: Extract text from PDF
    print(f"\n🔄 Extracting text from {PDF_FILE}...")
    
    try:
        with open(PDF_FILE, 'rb') as f:
            files = {'file': (PDF_FILE, f, 'application/pdf')}
            data = {
                'force_ocr': 'true',  # Force OCR for better Bangla extraction
                'language': 'bangla'
            }
            
            start_time = time.time()
            response = requests.post(
                f"{API_BASE}/extract-text", 
                files=files, 
                data=data, 
                timeout=180  # 3 minutes timeout
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                
                print("✅ Text extraction successful!")
                print(f"\n📊 Extraction Results:")
                print(f"   Success: {result['success']}")
                print(f"   Pages: {result['metadata']['pageCount']}")
                print(f"   Method: {result['metadata']['extractionMethod']}")
                print(f"   Processing time: {result['metadata']['processingTime']:.2f}s")
                print(f"   Request time: {end_time - start_time:.2f}s")
                
                extracted_text = result['text']
                print(f"   Text length: {len(extracted_text):,} characters")
                
                # Analyze text quality
                lines = extracted_text.split('\n')
                non_empty_lines = [line for line in lines if line.strip()]
                
                print(f"\n📝 Text Analysis:")
                print(f"   Total lines: {len(lines):,}")
                print(f"   Non-empty lines: {len(non_empty_lines):,}")
                print(f"   Empty lines: {len(lines) - len(non_empty_lines):,}")
                
                # Character analysis
                bangla_chars = sum(1 for char in extracted_text if '\u0980' <= char <= '\u09FF')
                english_chars = sum(1 for char in extracted_text if char.isalpha() and char.isascii())
                digits = sum(1 for char in extracted_text if char.isdigit())
                
                print(f"   Bangla characters: {bangla_chars:,}")
                print(f"   English characters: {english_chars:,}")
                print(f"   Digits: {digits:,}")
                
                # Show sample text
                print(f"\n📖 Sample Text (first 800 characters):")
                print("─" * 60)
                print(extracted_text[:800])
                print("─" * 60)
                
                # Test line preservation
                print(f"\n🔍 Line Preservation Test:")
                sample_lines = lines[:10]
                for i, line in enumerate(sample_lines, 1):
                    if line.strip():
                        print(f"   Line {i}: {line[:50]}{'...' if len(line) > 50 else ''}")
                
                # Save extracted text for further analysis
                with open('extracted_text_002.txt', 'w', encoding='utf-8') as f:
                    f.write(extracted_text)
                print(f"\n💾 Extracted text saved to: extracted_text_002.txt")
                
                return extracted_text
                
            else:
                print(f"❌ Text extraction failed: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return None
                
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - PDF processing took too long")
        return None
    except Exception as e:
        print(f"❌ Text extraction error: {e}")
        return None

def test_plagiarism_check(text):
    """Test plagiarism checking with extracted text"""
    
    if not text or len(text.strip()) < 100:
        print("⚠️ Text too short for plagiarism check")
        return
    
    API_BASE = "http://localhost:8000"
    
    print(f"\n🔍 Testing Plagiarism Detection...")
    
    # Take first 1000 characters for testing
    sample_text = text[:1000].strip()
    
    try:
        data = {
            'text': sample_text,
            'threshold': 0.7,
            'check_paraphrase': True,
            'language': 'bangla'
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/check-plagiarism", json=data, timeout=60)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Plagiarism check completed!")
            print(f"   Processing time: {end_time - start_time:.2f}s")
            print(f"   Overall score: {result['overallScore']:.2f}")
            print(f"   Risk level: {result['analysis']['riskLevel']}")
            print(f"   Total matches: {result['analysis']['totalMatches']}")
            print(f"   Word count: {result['wordCount']}")
            
        else:
            print(f"❌ Plagiarism check failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Plagiarism check error: {e}")

if __name__ == "__main__":
    # Change to the correct directory
    os.chdir(r"d:\Bangla Plagiarism")
    
    # Test PDF extraction
    extracted_text = test_pdf_extraction()
    
    # Test plagiarism detection if extraction was successful
    if extracted_text:
        test_plagiarism_check(extracted_text)
    
    print(f"\n🎉 Testing completed!")
    print(f"📱 You can also test via web interface at: http://localhost:3000")