# Bangla Plagiarism Checker

## সম্পূর্ণ বাংলা প্ল্যাজিয়ারিজম চেকার প্রজেক্ট

এটি একটি আধুনিক বাংলা প্ল্যাজিয়ারিজম ডিটেকশন সিস্টেম যা Google Gemini AI ব্যবহার করে PDF থেকে টেক্সট নিষ্কাশন এবং Sentence Transformers ব্যবহার করে প্ল্যাজিয়ারিজম চেক করে।

### 🚀 Features (বৈশিষ্ট্য)

#### PDF Text Extraction
- **Gemini AI Integration**: Google Gemini AI ব্যবহার করে উন্নত বাংলা টেক্সট নিষ্কাশন
- **Full PDF Processing**: সম্পূর্ণ PDF প্রক্রিয়াকরণ (সব পেজ)
- **Bangla Content Detection**: বাংলা কনটেন্ট ভ্যালিডেশন
- **Fallback OCR**: Gemini ব্যর্থ হলে OCR ব্যাকআপ

#### Plagiarism Detection
- **Semantic Similarity**: Sentence Transformers মডেল ব্যবহার
- **Configurable Threshold**: কাস্টমাইজযোগ্য সিমিলারিটি থ্রেশহোল্ড
- **Paraphrase Detection**: প্যারাফ্রেজ চেকিং
- **Detailed Analysis**: বিস্তারিত ম্যাচ রিপোর্ট

#### User Interface
- **Clean Modern UI**: Next.js এবং TailwindCSS
- **Drag & Drop Upload**: সহজ ফাইল আপলোড
- **Real-time Results**: তাৎক্ষণিক রেজাল্ট দেখানো
- **Full Text View**: সম্পূর্ণ নিষ্কাশিত টেক্সট দেখা

## 📁 Project Structure

```
bangla-plagiarism-checker/
├── backend/                    # FastAPI Backend
│   ├── main.py                # Main API server
│   ├── requirements.txt       # Python dependencies
│   ├── uploads/              # Temporary file storage
│   └── app/
│       ├── core/
│       │   ├── enhanced_pdf_extractor.py  # OCR-based extraction
│       │   ├── gemini_pdf_extractor.py    # Gemini AI extraction
│       │   ├── plagiarism_detector.py     # Plagiarism detection
│       │   └── corpus_manager.py          # Document corpus
│       └── models/
│           └── schemas.py                 # Pydantic models
├── frontend/                  # Next.js Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.tsx    # File upload component
│   │   │   ├── PlagiarismResults.tsx  # Results display
│   │   │   └── TextInput.tsx     # Text input component
│   │   ├── pages/
│   │   │   └── index.tsx         # Main page
│   │   ├── utils/
│   │   │   └── api.ts            # API utilities
│   │   └── types/
│   │       └── index.ts          # TypeScript types
│   ├── package.json         # Node.js dependencies
│   ├── tailwind.config.js   # TailwindCSS config
│   └── next.config.js       # Next.js configuration
└── README.md                # This file
```

## 🛠️ Installation & Setup

### Prerequisites (প্রয়োজনীয়তা)

1. **Python 3.8+** installed
2. **Node.js 18+** and npm installed
3. **Google Gemini API Key** (for PDF extraction)
4. **Git** for version control

### Step 1: Clone Repository

```bash
git clone https://github.com/MdMostafizurRahaman/Bangla-plagiarism-checker.git
cd bangla-plagiarism-checker
```

### Step 2: Backend Setup

#### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the backend directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

**Get Gemini API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

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

#### Start Frontend Development Server

```bash
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## 🚀 Usage (ব্যবহার)

### PDF Text Extraction & Plagiarism Check

1. Open `http://localhost:3000` in your browser
2. **Upload PDF**: Drag & drop or click to select a PDF file
3. **Extract & Check**: Click the "Extract Text & Check Plagiarism" button
4. **View Results**:
   - Extracted text (first 500 characters shown)
   - Plagiarism score and analysis
   - Matched text segments
   - Similarity percentage

### Manual Text Check

1. Click "Check Text Manually" button
2. Enter or paste text in the textarea
3. Adjust settings if needed:
   - Similarity threshold (default: 0.7)
   - Check paraphrase (default: enabled)
4. Click "Check Plagiarism" to analyze

## 🔧 Configuration

### Backend Configuration

Key settings in `backend/main.py`:

```python
# File upload settings
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = ['.pdf']

# Plagiarism settings
DEFAULT_THRESHOLD = 0.7
DEFAULT_CHECK_PARAPHRASE = True
```

### Frontend Configuration

The frontend automatically connects to `http://localhost:8000`. For production deployment, update the API URL in `frontend/src/utils/api.ts`.

## 📝 API Endpoints

### Core Endpoints
- `GET /` - API information
- `GET /health` - Health check

### Text Extraction
- `POST /extract-text` - Extract text from PDF using Gemini AI
- `POST /batch-extract` - Process multiple PDFs (background task)

### Plagiarism Detection
- `POST /check-plagiarism` - Check text for plagiarism
- `POST /check-file-plagiarism` - Extract from PDF and check plagiarism

### Corpus Management
- `POST /add-to-corpus` - Add document to corpus
- `GET /corpus/stats` - Get corpus statistics
- `POST /corpus/search` - Search corpus documents

## 🐛 Troubleshooting

### Common Issues

#### 1. Gemini API Key Issues
```bash
# Check if key is set
cd backend
python -c "import os; print('GEMINI_API_KEY' in os.environ)"
```

#### 2. Model Download Failed
```bash
# Manual download with specific model
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
print('Model downloaded!')
"
```

#### 3. Port Already in Use
```bash
# Kill process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port
uvicorn main:app --port 8001
```

#### 4. Frontend Connection Issues
- Ensure backend is running on port 8000
- Check CORS settings in `main.py`
- Verify API URL in `frontend/src/utils/api.ts`

## 📊 Performance Tips

1. **PDF Size**: Keep PDFs under 50MB for best performance
2. **Text Length**: Gemini processes full PDFs but results may be truncated for very long documents
3. **Similarity Threshold**: Lower values (0.5-0.7) for academic papers, higher (0.8+) for strict checking
4. **Corpus Size**: Keep corpus manageable for faster searches

## 🛡️ Security Notes

1. File uploads limited to PDF files only
2. File size limits enforced (50MB max)
3. Input validation on all endpoints
4. CORS configured for frontend domain
5. API keys stored securely in environment variables

## 📚 Dependencies

### Backend (Python)
- **FastAPI** - Web framework
- **PyMuPDF** - PDF processing
- **google-generativeai** - Gemini AI integration
- **sentence-transformers** - ML similarity detection
- **python-multipart** - File upload handling
- **uvicorn** - ASGI server

### Frontend (Node.js)
- **Next.js** - React framework
- **React** - UI library
- **axios** - HTTP client
- **react-dropzone** - File upload component
- **lucide-react** - Icons
- **tailwindcss** - CSS framework

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is for educational and research purposes. Please use responsibly for academic integrity checking.

---

## Quick Start Commands

```bash
# Backend Setup
cd backend
pip install -r requirements.txt
# Add GEMINI_API_KEY to .env file
uvicorn main:app --reload

# Frontend Setup (new terminal)
cd frontend
npm install
npm run dev

# Access Application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 🎯 Key Features Summary

✅ **Full PDF Processing** - Processes all pages with Gemini AI
✅ **Bangla Language Support** - Optimized for Bengali text extraction
✅ **Real-time Plagiarism Check** - Instant results with detailed analysis
✅ **Clean Modern UI** - Simple, emoji-free interface
✅ **Configurable Settings** - Adjustable similarity thresholds
✅ **Corpus Management** - Add and search reference documents
✅ **API Documentation** - Auto-generated FastAPI docs

**সবকিছু প্রস্তুত! এখন আপনি সম্পূর্ণ বাংলা প্ল্যাজিয়ারিজম চেকার ব্যবহার করতে পারেন।** 🎉