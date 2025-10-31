# Bangla Plagiarism Checker - Complete Setup Guide

## সম্পূর্ণ বাংলা প্ল্যাজিয়ারিজম চেকার প্রজেক্ট

এটি একটি সম্পূর্ণ বাংলা প্ল্যাজিয়ারিজম ডিটেকশন সিস্টেম যা PDF থেকে টেক্সট নিষ্কাশন এবং প্ল্যাজিয়ারিজম চেক করতে পারে।

### 🚀 Features (বৈশিষ্ট্য)

#### PDF Text Extraction
- **উন্নত OCR**: OpenCV এবং Tesseract ব্যবহার করে
- **টেবিল ডিটেকশন**: PDF থেকে টেবিল টেক্সট নিষ্কাশন
- **Line Preservation**: লাইন গ্যাপ সমস্যা সমাধান
- **Mixed Language**: বাংলা-ইংরেজি মিশ্রিত টেক্সট হ্যান্ডলিং
- **Unicode Normalization**: বাংলা টেক্সটের জন্য সঠিক এনকোডিং

#### Plagiarism Detection
- **Semantic Similarity**: Sentence Transformers মডেল ব্যবহার
- **Exact Matching**: সঠিক টেক্সট ম্যাচিং
- **Paraphrase Detection**: প্যারাফ্রেজ চেক
- **Corpus Management**: ডকুমেন্ট কর্পাস ব্যবস্থাপনা

#### User Interface
- **Modern UI**: Next.js এবং TailwindCSS
- **Drag & Drop**: ফাইল আপলোড
- **Real-time Analysis**: লাইভ প্ল্যাজিয়ারিজম চেক
- **Results Visualization**: হাইলাইটেড রেজাল্ট

## 📁 Project Structure

```
bangla-plagiarism-checker/
├── backend/                    # FastAPI Backend
│   ├── main.py                # Main API server
│   ├── enhanced_pdf_extractor.py  # Advanced PDF processing
│   ├── plagiarism_detector.py # Plagiarism detection engine
│   ├── corpus_manager.py      # Document corpus management
│   ├── requirements.txt       # Python dependencies
│   └── uploads/              # File upload directory
├── frontend/                  # Next.js Frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/           # Next.js pages
│   │   ├── utils/           # API utilities
│   │   └── types/           # TypeScript definitions
│   ├── package.json         # Node.js dependencies
│   ├── tailwind.config.js   # TailwindCSS config
│   └── next.config.js       # Next.js configuration
└── README.md                # This file
```

## 🛠️ Installation & Setup

### Prerequisites (প্রয়োজনীয়তা)

1. **Python 3.8+** installed
2. **Node.js 18+** and npm installed
3. **Tesseract OCR** for text extraction
4. **Git** for version control

### Step 1: Clone Repository

```bash
cd "d:\Bangla Plagiarism"
# Already in project directory
```

### Step 2: Backend Setup

#### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Install Tesseract OCR

**Windows:**
```bash
# Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR
```

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr tesseract-ocr-ben

# macOS
brew install tesseract tesseract-lang
```

#### Download ML Models

```bash
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print('Model downloaded successfully!')
"
```

#### Start Backend Server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

### Step 3: Frontend Setup

#### Install Node.js Dependencies

```bash
cd ../frontend
npm install
```

#### Environment Configuration

```bash
# Copy environment file
cp .env.example .env.local

# Edit .env.local if needed (default values should work)
```

#### Start Frontend Development Server

```bash
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## 🚀 Usage (ব্যবহার)

### 1. PDF Text Extraction

1. Open `http://localhost:3000`
2. **File Upload** ট্যাবে যান
3. PDF ফাইল drag & drop করুন অথবা ক্লিক করে সিলেক্ট করুন
4. **Extract Text** বাটনে ক্লিক করুন
5. নিষ্কাশিত টেক্সট দেখুন

### 2. Text Analysis

1. **Text Input** ট্যাবে যান
2. টেক্সট টাইপ করুন অথবা পেস্ট করুন
3. সেটিংস কনফিগার করুন:
   - **Similarity Threshold**: 0.7 (default)
   - **Check Paraphrase**: ✅
   - **Language**: Bangla
4. **Analyze Text** বাটনে ক্লিক করুন

### 3. Results Analysis

- **Overall Score**: সামগ্রিক প্ল্যাজিয়ারিজম স্কোর
- **Matched Text**: হাইলাইটেড ম্যাচ
- **Source Information**: সোর্স ডকুমেন্ট তথ্য
- **Risk Level**: ঝুঁকির মাত্রা (Low/Medium/High)

## 🔧 Configuration

### Backend Configuration

`backend/main.py` এ কনফিগারেশন পরিবর্তন করুন:

```python
# File upload settings
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = ['.pdf']

# OCR settings
OCR_LANGUAGE = 'ben+eng'  # Bangla + English

# Plagiarism settings
DEFAULT_THRESHOLD = 0.7
DEFAULT_CHECK_PARAPHRASE = True
```

### Frontend Configuration

`.env.local` ফাইল এডিট করুন:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAX_FILE_SIZE=52428800
NEXT_PUBLIC_DEFAULT_LANGUAGE=bangla
```

## 📝 API Endpoints

### Text Extraction
- `POST /extract-text` - PDF থেকে টেক্সট নিষ্কাশন
- `POST /batch-extract` - একাধিক PDF প্রক্রিয়াকরণ

### Plagiarism Check
- `POST /check-plagiarism` - প্ল্যাজিয়ারিজম চেক
- `GET /health` - API স্বাস্থ্য পরীক্ষা

### Corpus Management
- `POST /add-to-corpus` - কর্পাসে ডকুমেন্ট যোগ
- `GET /corpus/stats` - কর্পাস পরিসংখ্যান
- `POST /corpus/search` - কর্পাস অনুসন্ধান

## 🐛 Troubleshooting

### Common Issues

#### 1. Tesseract Not Found
```bash
# Windows: Add to PATH
set PATH=%PATH%;C:\Program Files\Tesseract-OCR

# Linux: Install package
sudo apt install tesseract-ocr tesseract-ocr-ben
```

#### 2. Model Download Failed
```bash
# Manual download
python -c "
import nltk
nltk.download('punkt')
nltk.download('stopwords')
"
```

#### 3. PDF Processing Slow
- Large PDFs: সাইজ 50MB এর নিচে রাখুন
- OCR Settings: `force_ocr=False` সেট করুন যদি টেক্সট স্তর আছে

#### 4. Port Already in Use
```bash
# Backend port change
uvicorn main:app --port 8001

# Frontend port change
npm run dev -- -p 3001
```

## 📊 Performance Tips

1. **PDF Optimization**: PDF ফাইল 50MB এর নিচে রাখুন
2. **OCR Settings**: শুধুমাত্র প্রয়োজনে OCR ব্যবহার করুন
3. **Batch Processing**: একাধিক ফাইলের জন্য batch API ব্যবহার করুন
4. **Corpus Size**: কর্পাস সাইজ 10,000 ডকুমেন্টের নিচে রাখুন

## 🛡️ Security Notes

1. File uploads শুধুমাত্র PDF এ সীমাবদ্ধ
2. File size limits প্রয়োগ করা
3. Input validation সব API endpoints এ
4. CORS properly configured

## 📚 Dependencies

### Backend (Python)
- FastAPI - Web framework
- OpenCV - Image processing
- Tesseract - OCR engine
- Sentence Transformers - ML models
- SQLite - Database

### Frontend (Node.js)
- Next.js - React framework
- TailwindCSS - Styling
- Axios - HTTP client
- React Dropzone - File uploads
- Lucide React - Icons

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is for educational purposes. Use responsibly for academic integrity checking.

---

## Quick Start Commands

```bash
# Start Backend
cd backend && uvicorn main:app --reload

# Start Frontend (new terminal)
cd frontend && npm run dev

# Access Application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**সবকিছু প্রস্তুত! এখন আপনি সম্পূর্ণ বাংলা প্ল্যাজিয়ারিজম চেকার ব্যবহার করতে পারেন।** 🎉