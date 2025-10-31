#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced SutonnyMJ to Unicode Converter
Based on actual SutonnyMJ font mapping analysis
"""

import re

def convert_sutonnymj_to_unicode(text):
    """
    Convert SutonnyMJ encoded text to proper Unicode Bangla
    """
    
    # Skip if line is English
    if is_english_text(text):
        return text
    
    # Apply SutonnyMJ to Unicode conversion
    result = text
    
    # Step 1: Handle compound characters first
    compound_mappings = {
        # Common SutonnyMJ patterns observed in the text
        'kvwšÍ': 'শান্তি',
        'mvsevw`KZv': 'সাংবাদিকতা',
        'PP©v': 'চর্চা',
        'cwi‡cÖw¶Z': 'পরিপ্রেক্ষিত',
        'Kvk¥xi': 'কাশমীর',
        'Bmy¨': 'ইস্যু',
        '†ivev‡qZ': 'রোবায়েত',
        '†di‡`Šm': 'ফেরদৌস',
        'Zb¥q': 'তন্ময়',
        'mvnv': 'সাহা',
        'Rq': 'জয়',
        'gyL¨kã': 'মুখ্যশব্দ',
        'MYgva¨g': 'গণমাধ্যম',
        'hy×gyLxbZv': 'যুদ্ধমুখিনতা',
        'Aa¨vcK': 'অধ্যাপক',
        'MY‡hvMv‡hvM': 'গণযোগাযোগ',
        'wefvM': 'বিভাগ',
        'XvKv': 'ঢাকা',
        'wek^we`¨vjq': 'বিশ্ববিদ্যালয়',
        'cÖfvlK': 'প্রভাষক',
        'KwgDwb‡Kkb': 'কমিউনিকেশন',
        'A¨vÛ': 'অ্যান্ড',
        'gvwëwgwWqv': 'মাল্টিমিডিয়া',
        'Rvb©vwjRg': 'জার্নালিজম',
        'Bmjvgx': 'ইসলামী',
        'Kzwóqv': 'কুষ্টিয়া',
        'cwÎKv': 'পত্রিকা',
        'msL¨v': 'সংখ্যা',
        'hy³': 'যুক্ত',
        '†m‡Þ¤^i': 'সেপ্টেম্বর',
        'f~wgKv': 'ভূমিকা',
        'fviZxq': 'ভারতীয়',
        'Dcgnv‡`k': 'উপমহাদেশ',
        '¸iæZ¡c~Y©': 'গুরুত্বপূর্ণ',
        'AÂj': 'অঞ্চল',
        'fviZ': 'ভারত',
        'cvwK¯Ívb': 'পাকিস্তান',
        'Pxb': 'চীন',
        'wZb': 'তিন',
        '†`k': 'দেশ',
        'gv‡S': 'মাঝে',
        'we¯Í…Z': 'বিস্তৃত',
        'wefvR': 'বিভাগ',
        'ci': 'পর',
        '†_‡K': 'থেকে',
        'GB': 'এই',
        'wewfbœ': 'বিভিন্ন',
        'ivR‰bwZK': 'রাজনৈতিক',
        'ag©xq': 'ধর্মীয়',
        'BZ¨vw`': 'ইত্যাদি',
        'Bmy¨‡Z': 'ইস্যুতে',
        'Av‡jvPbvq': 'আলোচনায়',
        'G‡m‡Q': 'এসেছে',
        'me©‡kl': 'সর্বশেষ',
        'wbqwš¿Z': 'নিয়ন্ত্রিত',
        'Kvk¥x‡i': 'কাশমীরে',
        'we‡kl': 'বিশেষ',
        'gh©v`v': 'মর্যাদা',
        'wejyß': 'বিলুপ্ত',
        'K‡i': 'করে',
        'wel‡q': 'বিষয়ে',
        'evsjv‡`k': 'বাংলাদেশ',
        'mivmwi': 'সরাসরি',
        'hy³': 'যুক্ত',
        'bv': 'না',
        '_vK‡jI': 'থাকলেও',
        'f~': 'ভূ',
        'ivR‰bwZK': 'রাজনৈতিক',
        'Kvi‡Y': 'কারণে',
        'Bmy¨wU': 'ইস্যুটি',
        'AZ¨šÍ': 'অত্যন্ত',
        '¸iæZ¡c~Y©': 'গুরুত্বপূর্ণ',
        'cvkvcvwk': 'পাশাপাশি',
        'emevmKvix': 'বাসবাসকারী',
        'Rb‡Mvôx': 'জনগোষ্ঠী',
        'AwaKvsk': 'অধিকাংশ',
        'gvbyl': 'মানুষ',
        'gymwjg': 'মুসলিম',
        'nIqvq': 'হওয়ায়',
        'G‡`k': 'এদেশ',
        'gvby‡li': 'মানুষের',
        'm‡½': 'সাথে',
        'GK': 'এক',
        'ai‡bi': 'ধরনের',
        'gb¯ÍvwË¡K': 'মনস্তাত্ত্বিক',
        'ˆbK‡U¨i': 'নৈকট্যের',
        'welqwU': 'বিষয়টি',
        'we‡eP¨': 'বিবেচ্য',
        'wejyß': 'বিলুপ্ত',
        'Kivi': 'করার',
        'm„ó': 'সৃষ্ট',
        'eZ©gvb': 'বর্তমান',
        'Bmy¨wU': 'ইস্যুটি',
        'ZvB': 'তাই',
        'evsjv‡`wk': 'বাংলাদেশি',
        'cvVK‡`i': 'পাঠকদের',
        'Kv‡Q': 'কাছে',
        'A‡bK': 'অনেক',
        '†`‡ki': 'দেশের',
        'cÖvq': 'প্রায়',
        'me': 'সব',
        'msev`cÎ': 'সংবাদপত্র',
        'G': 'এ',
        'wel‡q': 'বিষয়ে',
        'wbqwgZ': 'নিয়মিত',
        'cÖwZ‡e`b': 'প্রতিবেদন',
        'cÖKvk': 'প্রকাশ',
        'K‡i‡Q': 'করেছে',
        'AbjvBb': 'অনলাইন',
        'MYgva¨gMy‡jv‡Z': 'গণমাধ্যমগুলোতে',
        'I': 'ও',
        'wbqwgZ': 'নিয়মিত',
        'G': 'এ',
        'Bmy¨‡Z': 'ইস্যুতে',
        'msev`': 'সংবাদ',
        'cÖKvwkZ': 'প্রকাশিত',
        'n‡q‡Q': 'হয়েছে',
        'cvVKmsL¨vi': 'পাঠকসংখ্যার',
        'we‡ePbvq': 'বিবেচনায়',
        'wewWwbDR24': 'বিডিনিউজ24',
        'Kg': 'কম',
        'I': 'ও',
        'cÖ_g': 'প্রথম',
        'Av‡jv': 'আলো',
        'AbjvBb': 'অনলাইন',
        '†`‡ki': 'দেশের',
        'AbjvBb': 'অনলাইন',
        'MYgva¨gMy‡jvi': 'গণমাধ্যমগুলোর',
        'g‡a¨': 'মধ্যে',
        'Ab¨Zg': 'অন্যতম',
        '¸iæZ¡c~Y©': 'গুরুত্বপূর্ণ',
        'eZ©gvb': 'বর্তমান',
        'M‡elYvwU': 'গবেষণাটি',
        'cwiPvjbvi': 'পরিচালনার',
        'gva¨‡g': 'মাধ্যমে',
        'kvwšÍ': 'শান্তি',
        'mvsevw`KZv': 'সাংবাদিকতা',
        'g‡W‡ji': 'মডেলের',
        'Av‡jv‡K': 'আলোকে',
        'wewWwbDR24': 'বিডিনিউজ24',
        'Kg': 'কম',
        'I': 'ও',
        'cÖ_g': 'প্রথম',
        'Av‡jv': 'আলো',
        'AbjvB‡b': 'অনলাইনে',
        'Kvk¥xi': 'কাশমীর',
        'Bmy¨‡Z': 'ইস্যুতে',
        'cÖKvwkZ': 'প্রকাশিত',
        'msev`My‡jvi': 'সংবাদগুলোর',
        'cwi‡ekbv': 'পরিবেশনা',
        'I': 'ও',
        'cÖK…wZ': 'প্রকৃতি',
        '†`Lv': 'দেখা',
        'n‡q‡Q': 'হয়েছে'
    }
    
    # Apply compound mappings first
    for sutonnymj, unicode_bangla in compound_mappings.items():
        result = result.replace(sutonnymj, unicode_bangla)
    
    # Step 2: Handle remaining individual characters
    char_mappings = {
        # Basic consonants
        'K': 'ক', 'L': 'খ', 'M': 'গ', 'N': 'ঘ', 'O': 'ঙ',
        'P': 'চ', 'Q': 'ছ', 'R': 'জ', 'S': 'ঝ', 'T': 'ঞ',
        'U': 'ট', 'V': 'ঠ', 'W': 'ড', 'X': 'ঢ', 'Y': 'ণ',
        'Z': 'ত', '_': 'থ', '`': 'দ', 'a': 'ধ', 'b': 'ন',
        'c': 'প', 'd': 'ফ', 'e': 'ব', 'f': 'ভ', 'g': 'ম',
        'h': 'য', 'i': 'র', 'j': 'ল', 'k': 'শ', 'l': 'ষ',
        'm': 'স', 'n': 'হ', 'o': 'ড়', 'p': 'ঢ়', 'q': 'য়',
        'r': 'ৎ', 's': 'ং', 't': 'ঃ', 'u': 'ঁ',
        
        # Vowel marks
        'v': 'া', 'w': 'ি', 'x': 'ী', 'y': 'ু', 'z': 'ূ',
        '†': 'ে', '‡': 'ো', 'ˆ': 'ৈ', '©': 'র্', '¨': 'ৗ',
        '¯': '্', '°': 'ং', '±': 'ঃ', '²': 'ঁ',
        
        # Special characters
        '¥': 'য', 'Í': 'ী', 'š': 'ন', 'Ö': 'প্র', '¶': 'প',
        
        # Numbers
        '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪',
        '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'
    }
    
    # Apply character mappings
    for sutonnymj_char, unicode_char in char_mappings.items():
        result = result.replace(sutonnymj_char, unicode_char)
    
    return result

def is_english_text(text):
    """Check if text is primarily English"""
    text = text.strip()
    if not text:
        return True
    
    # English indicators
    english_words = [
        'abstract', 'in this study', 'the nature', 'representation',
        'news published', 'newspapers', 'analysed using', 'ideas',
        'peace journalism', 'model given', 'norwegian', 'social scientist',
        'johan galtung', 'coding frames', 'prepared', 'light',
        'framing analysis', 'content analysis', 'method', 'used',
        'considering', 'overall results', 'research', 'found',
        'bangladeshi media', 'still dependent', 'traditional style',
        'journalism', 'reporting war', 'conflicts', 'practice',
        'large scale', 'evidence', 'conventional trends',
        'sustaining', 'contributing', 'shaping', 'problem',
        'greater degree', 'however', 'proven', 'vital role',
        'resolving', 'establishing peace', 'issn', 'doi', 'http',
        'ministry of law', 'buchanan', 'mustafa', 'ottosen',
        'lee', 'maslog', 'khan', 'sheuli', 'galtung', 'lynch',
        'mcgoldrick', 'pan', 'kosicki', 'goffman', 'creswell',
        'facebook', 'alexa', 'transcend', 'harper', 'row',
        'sage publications', 'universidad', 'new york',
        'gloucestershire', 'hawthorn press', 'doi', 'retrieved'
    ]
    
    text_lower = text.lower()
    
    # Check for English keywords
    for word in english_words:
        if word in text_lower:
            return True
    
    # Check ASCII ratio
    ascii_count = sum(1 for c in text if ord(c) < 128)
    total_chars = len(text)
    
    if total_chars > 0 and ascii_count / total_chars > 0.8:
        return True
    
    return False

def convert_file_smart(input_file, output_file):
    """Convert file intelligently preserving English content"""
    print(f"🎯 Smart conversion: {input_file} → {output_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    converted_lines = []
    for i, line in enumerate(lines):
        original = line.rstrip('\n')
        
        if is_english_text(original):
            converted_lines.append(original)
            if i < 15:
                print(f"Line {i+1} [EN]: {original[:60]}...")
        else:
            converted = convert_sutonnymj_to_unicode(original)
            converted_lines.append(converted)
            if i < 15:
                print(f"Line {i+1} [BN]: {original[:30]} → {converted[:40]}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(converted_lines))
    
    print(f"✅ Smart conversion completed! {len(converted_lines)} lines processed")

if __name__ == "__main__":
    convert_file_smart('extracted_text_002.txt', 'extracted_text_002_final.txt')