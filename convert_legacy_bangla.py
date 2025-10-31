#!/usr/bin/env python3
"""
Legacy Bangla Font to Unicode Converter
এই স্ক্রিপ্ট legacy Bangla fonts (যেমন SutonnyMJ) থেকে standard Unicode Bangla তে convert করে
"""

import re

# Legacy font to Unicode mapping (common SutonnyMJ mappings)
LEGACY_TO_UNICODE = {
    # Vowels and basic characters
    'A': 'অ', 'Av': 'আ', 'B': 'ই', 'C': 'উ', 'D': 'ঊ', 'E': 'এ', 'F': 'ঐ', 
    'G': 'ও', 'H': 'ঔ', 'I': 'ৃ', 'J': 'ৗ', 'K': 'ক', 'L': 'খ', 'M': 'গ',
    'N': 'ঘ', 'O': 'ঙ', 'P': 'চ', 'Q': 'ছ', 'R': 'জ', 'S': 'ঝ', 'T': 'ঞ',
    'U': 'ট', 'V': 'ঠ', 'W': 'ড', 'X': 'ঢ', 'Y': 'ণ', 'Z': 'ত', '_': 'থ',
    '`': 'দ', 'a': 'ধ', 'b': 'ন', 'c': 'প', 'd': 'ফ', 'e': 'ব', 'f': 'ভ',
    'g': 'ম', 'h': 'য', 'i': 'র', 'j': 'ল', 'k': 'শ', 'l': 'ষ', 'm': 'স',
    'n': 'হ', 'o': 'ড়', 'p': 'ঢ়', 'q': 'য়', 'r': 'ৎ', 's': 'ং', 't': 'ঃ',
    'u': 'ঁ', 'v': 'া', 'w': 'ি', 'x': 'ী', 'y': 'ু', 'z': 'ূ',
    
    # Common combinations
    'Av': 'আ', 'Bw': 'ই', 'Kv': 'কা', 'Kb': 'কন', 'Ki': 'কর', 'Kw': 'কি',
    'Ky': 'কু', 'K‡': 'কে', 'Ko': 'কো', 'K©': 'কর্', 'Kz': 'কু', 'Kx': 'কী',
    'gb': 'মন', 'gv': 'মা', 'gi': 'মর', 'gy': 'মু', 'g‡': 'মে', 'go': 'মো',
    'bv': 'না', 'wb': 'ন', 'wU': 'তি', 'wZ': 'তি', 'wK': 'কি', 'wQ': 'ছি',
    'wM': 'গি', 'wj': 'লি', 'wn': 'হি', 'we': 'বি', 'wk': 'শি', 'wr': 'রি',
    'ev': 'বা', 'eb': 'বন', 'ei': 'বর', 'ey': 'বু', 'e‡': 'বে', 'eo': 'বো',
    'Rv': 'জা', 'Rb': 'জন', 'Ri': 'জর', 'Ry': 'জু', 'R‡': 'জে', 'Ro': 'জো',
    'Zv': 'তা', 'Zb': 'তন', 'Zi': 'তর', 'Zy': 'তু', 'Z‡': 'তে', 'Zo': 'তো',
    'Pv': 'চা', 'Pb': 'চন', 'Pi': 'চর', 'Py': 'চু', 'P‡': 'চে', 'Po': 'চো',
    'nv': 'হা', 'nb': 'হন', 'ni': 'হর', 'ny': 'হু', 'n‡': 'হে', 'no': 'হো',
    'mv': 'সা', 'mb': 'সন', 'mi': 'সর', 'my': 'সু', 'm‡': 'সে', 'mo': 'সো',
    'jv': 'লা', 'jb': 'লন', 'ji': 'লর', 'jy': 'লু', 'j‡': 'লে', 'jo': 'লো',
    'dv': 'ফা', 'db': 'ফন', 'di': 'ফর', 'dy': 'ফু', 'd‡': 'ফে', 'do': 'ফো',
    
    # Special characters and conjuncts
    '©': 'র্', '¯': 'স্', '²': 'ত্', '³': 'ন্', '¶': 'ব্', 'Í': 'তি', 'š': 'ন্ত',
    '‡': 'ে', "'": 'ু', '"': 'ূ', '"': 'ৃ', '–': 'া', '—': 'ি', '•': 'ী',
    
    # Numbers
    '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪', 
    '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯',
    
    # Punctuation
    '|': '।', 'ó': 'র্', '„': 'ক্ষ', '…': 'জ্ঞ'
}

def convert_legacy_to_unicode(text):
    """Convert legacy Bangla font text to Unicode Bangla"""
    
    # Sort by length (longer patterns first) to avoid partial replacements
    sorted_mappings = sorted(LEGACY_TO_UNICODE.items(), key=lambda x: len(x[0]), reverse=True)
    
    # Apply conversions
    converted_text = text
    for legacy, unicode_char in sorted_mappings:
        converted_text = converted_text.replace(legacy, unicode_char)
    
    return converted_text

def analyze_text_sample(text, max_lines=20):
    """Analyze and show conversion results"""
    lines = text.split('\n')
    
    print("🔍 Legacy Font to Unicode Conversion Analysis")
    print("=" * 60)
    
    for i, line in enumerate(lines[:max_lines], 1):
        if line.strip():
            original = line.strip()
            converted = convert_legacy_to_unicode(original)
            
            print(f"\nLine {i}:")
            print(f"Original:  {original}")
            print(f"Converted: {converted}")
            
            if original != converted:
                print("✅ Conversion applied")
            else:
                print("⚪ No conversion needed")

def convert_full_text(input_file, output_file=None):
    """Convert entire text file"""
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f"📄 Reading {input_file}...")
        print(f"Original text length: {len(text):,} characters")
        
        # Convert text
        converted_text = convert_legacy_to_unicode(text)
        print(f"Converted text length: {len(converted_text):,} characters")
        
        # Save converted text
        if not output_file:
            output_file = input_file.replace('.txt', '_unicode.txt')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(converted_text)
        
        print(f"💾 Saved converted text to: {output_file}")
        
        # Show sample
        print(f"\n📖 Sample conversion:")
        analyze_text_sample(text, max_lines=5)
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    import os
    
    # Test with sample text
    sample_text = """kvwšÍ mvsevw`KZvi PP©v: cwi‡cÖw¶Z Kvk¥xi Bmy¨
†ivev‡qZ †di‡`Šm*
Zb¥q mvnv Rq**
gyL¨kã: kvwšÍ mvsevw`KZv, Kvk¥xi, MYgva¨g, hy×gyLxbZv
1. f~wgKv
Kvk¥xi fviZxq Dcgnv‡`‡ki GKwU ¸iæZ¡c~Y© AÂj"""
    
    print("🧪 Testing conversion with sample text:")
    analyze_text_sample(sample_text)
    
    # Convert the extracted PDF text
    pdf_file = "extracted_text_002.txt"
    if os.path.exists(pdf_file):
        print(f"\n🔄 Converting {pdf_file}...")
        converted_file = convert_full_text(pdf_file)
        
        if converted_file:
            print(f"\n✅ Conversion completed!")
            print(f"📁 Files:")
            print(f"   Original: {pdf_file}")
            print(f"   Converted: {converted_file}")
    else:
        print(f"❌ File not found: {pdf_file}")