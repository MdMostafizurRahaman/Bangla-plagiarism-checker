#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Bangla Font Converter - Converts only Bangla text from SutonnyMJ to Unicode
Keeps English text unchanged
"""

import re

# Comprehensive SutonnyMJ to Unicode mapping
SUTONNYMJ_TO_UNICODE = {
    # Vowels and consonants
    'K': 'ক', 'L': 'খ', 'M': 'গ', 'N': 'ঘ', 'O': 'ঙ',
    'P': 'চ', 'Q': 'ছ', 'R': 'জ', 'S': 'ঝ', 'T': 'ঞ',
    'U': 'ট', 'V': 'ঠ', 'W': 'ড', 'X': 'ঢ', 'Y': 'ণ',
    'Z': 'ত', '_': 'থ', '`': 'দ', 'a': 'ধ', 'b': 'ন',
    'c': 'প', 'd': 'ফ', 'e': 'ব', 'f': 'ভ', 'g': 'ম',
    'h': 'য', 'i': 'র', 'j': 'ল', 'k': 'শ', 'l': 'ষ',
    'm': 'স', 'n': 'হ', 'o': 'ড়', 'p': 'ঢ়', 'q': 'য়',
    'r': 'ৎ', 's': 'ং', 't': 'ঃ', 'u': 'ঁ',
    
    # Vowel marks and special characters
    'v': 'া', 'w': 'ি', 'x': 'ী', 'y': 'ু', 'z': 'ূ',
    '†': 'ে', '‡': 'ো', 'ˆ': 'ৈ', '©': 'র্', '¨': 'ৗ',
    '¯': '্', '°': 'ং', '±': 'ঃ', '²': 'ঁ', '³': '্র',
    '´': '্য', 'µ': '্ব', '¶': '্ম', '·': '্ন', '¸': '্ল',
    '¹': '্ক', 'º': '্খ', '»': '্গ', '¼': '্ঘ', '½': '্ঙ',
    
    # Compound characters
    'Av': 'আ', 'B': 'ই', 'C': 'ঈ', 'D': 'উ', 'E': 'ঊ',
    'F': 'ঋ', 'G': 'এ', 'H': 'ঐ', 'I': 'ও', 'J': 'ঔ',
    
    # Numbers
    '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪',
    '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯',
    
    # Special SutonnyMJ combinations
    'kv': 'শা', 'wš': 'শি', 'šÍ': 'ন্তি', 'Í': 'ী',
    'w`': 'দি', 'KZ': 'কত', 'vi': 'ার', 'PP': 'চর্চ',
    '©v': 'র্চা', 'cÖ': 'প্র', 'wÖ': 'ত্রি', 'w¶': 'ক্ষি',
    'Z': 'ত', 'Kvk': 'কাশ', '¥x': 'মী', 'Bmy': 'ইসু',
    '¨': 'য', 'my': 'সু', '‡`': 'দে', 'k': 'শ',
    
    # More patterns found in the document
    'MvjZzs': 'গালতুং', 'mvsevw`KZv': 'সাংবাদিকতা',
    'M‡elYv': 'গবেষণা', 'we‡køl': 'বিশ্লেষ', 'Y': 'ণ',
    'msev`': 'সংবাদ', 'cwÎKv': 'পত্রিকা', 'AbjvBb': 'অনলাইন',
    
    # Fix common wrong conversions
    'ঃযরং': 'this', 'ংঃঁফু': 'study', 'ঃযব': 'the',
    'হধঃঁৎব': 'nature', 'ধহফ': 'and', 'ৎবঢ়ৎবংবহঃধঃরড়হ': 'representation',
    'ড়ভ': 'of', 'হবিং': 'news', 'ঢ়ঁনষরংযবফ': 'published',
    'রহ': 'in', 'ঃিড়': 'two', 'ইধহমষধফবংযর': 'Bangladeshi',
    'হবিংঢ়ধঢ়বৎং': 'newspapers', 'যধাব': 'have', 'নববহ': 'been',
}

def is_english_line(line):
    """Check if a line is primarily English"""
    if not line.strip():
        return True
    
    # Check for English keywords
    english_keywords = [
        'Abstract', 'In this study', 'the nature', 'representation',
        'news published', 'newspapers', 'analysed using', 'ideas',
        'peace journalism', 'model given', 'Norwegian', 'social scientist',
        'Johan Galtung', 'coding frames', 'prepared', 'light',
        'framing analysis', 'content analysis', 'method', 'used',
        'Considering', 'overall results', 'research', 'found',
        'Bangladeshi media', 'still dependent', 'traditional style',
        'journalism', 'reporting war', 'conflicts', 'practice',
        'large scale', 'evidence', 'conventional trends',
        'sustaining', 'contributing', 'shaping', 'problem',
        'greater degree', 'However', 'proven', 'vital role',
        'resolving', 'establishing peace', 'ISSN', 'DOI', 'http'
    ]
    
    # Check if line contains primarily ASCII characters
    ascii_chars = sum(1 for c in line if ord(c) < 128)
    total_chars = len(line)
    
    if total_chars > 0 and ascii_chars / total_chars > 0.7:
        return True
    
    # Check for English keywords
    line_lower = line.lower()
    for keyword in english_keywords:
        if keyword.lower() in line_lower:
            return True
    
    return False

def convert_bangla_line(line):
    """Convert a Bangla line from SutonnyMJ to Unicode"""
    if is_english_line(line):
        return line  # Keep English lines unchanged
    
    result = line
    
    # Apply mappings from longest to shortest to avoid conflicts
    sorted_mappings = sorted(SUTONNYMJ_TO_UNICODE.items(), key=lambda x: len(x[0]), reverse=True)
    
    for sutonnymj, unicode_char in sorted_mappings:
        result = result.replace(sutonnymj, unicode_char)
    
    return result

def convert_file(input_file, output_file):
    """Convert entire file while preserving English content"""
    print(f"🔄 Converting {input_file} to proper Unicode...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    converted_lines = []
    for i, line in enumerate(lines):
        original_line = line.rstrip('\n')
        
        if is_english_line(original_line):
            # Keep English lines exactly as they are
            converted_lines.append(original_line)
            if i < 10:  # Show first few conversions
                print(f"Line {i+1} (English): {original_line[:60]}...")
        else:
            # Convert Bangla lines
            converted_line = convert_bangla_line(original_line)
            converted_lines.append(converted_line)
            if i < 10:  # Show first few conversions
                print(f"Line {i+1} (Bangla): {original_line[:30]}... → {converted_line[:30]}...")
    
    # Write converted content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(converted_lines))
    
    print(f"✅ Conversion complete! Saved to {output_file}")
    return len(converted_lines)

if __name__ == "__main__":
    # Convert the extracted text
    total_lines = convert_file('extracted_text_002.txt', 'extracted_text_002_proper.txt')
    print(f"\n📊 Processed {total_lines} lines total")