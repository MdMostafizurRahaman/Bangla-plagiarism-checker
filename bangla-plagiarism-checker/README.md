# Bangla Plagiarism Checker

A comprehensive plagiarism detection system for Bangla academic content with advanced PDF text extraction capabilities.

## Features

- **Enhanced PDF Text Extraction**: Handles mixed Bangla-English text, preserves line structure, and extracts tables
- **OCR Optimization**: Advanced preprocessing for better Bangla text recognition
- **Plagiarism Detection**: Corpus-based analysis with modern text similarity techniques
- **Web Interface**: Modern React-based frontend with FastAPI backend
- **Bangla Corpus**: Building comprehensive Bangla document collection from DU journals

## Project Structure

```
bangla-plagiarism-checker/
├── frontend/          # Next.js frontend
├── backend/           # FastAPI backend
├── docs/              # Documentation
└── README.md
```

## Technology Stack

- **Frontend**: Next.js (JavaScript), React, TailwindCSS
- **Backend**: FastAPI (Python), PyTorch, Transformers
- **OCR**: Tesseract, OpenCV, pdf2image
- **Database**: PostgreSQL, Redis
- **ML**: Sentence Transformers, NLTK, spaCy

## Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Issues Addressed

1. **Line Skipping**: Advanced line detection and text region analysis
2. **Table Extraction**: Specialized table detection and content extraction
3. **Mixed Language**: Improved Bangla-English text handling
4. **Unicode Issues**: Proper Unicode normalization and encoding

## Academic Use

This system is designed specifically for academic integrity in Bangla-language research and education. It addresses the unique challenges of Bangla text processing and plagiarism detection.

## Contributing

Please read our contributing guidelines and code of conduct before submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.