from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os
from typing import List, Dict, Optional
import asyncio
from datetime import datetime
import uuid

from app.core.enhanced_pdf_extractor import EnhancedBanglaPDFExtractor
from app.core.gemini_pdf_extractor import GeminiPDFExtractor
from app.core.plagiarism_detector import BanglaPlagiarismDetector
from app.core.corpus_manager import CorpusManager
from app.models.schemas import (
    TextExtractionResponse, 
    PlagiarismCheckRequest, 
    PlagiarismCheckResponse,
    CorpusDocument
)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    print("🚀 Starting Bangla Plagiarism Checker API...")
    
    # Initialize plagiarism detector
    await plagiarism_detector.initialize()
    
    # Load corpus
    await corpus_manager.load_corpus()
    
    print("✅ API ready!")
    
    yield
    
    # Cleanup on shutdown
    print("🔄 Shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Bangla Plagiarism Checker API",
    description="Advanced plagiarism detection system for Bangla academic content",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
pdf_extractor = EnhancedBanglaPDFExtractor()
gemini_extractor = GeminiPDFExtractor()
plagiarism_detector = BanglaPlagiarismDetector()
corpus_manager = CorpusManager()

# Create upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Bangla Plagiarism Checker API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "pdf_extractor": "ready",
            "plagiarism_detector": "ready",
            "corpus_manager": "ready"
        }
    }

@app.post("/extract-text", response_model=TextExtractionResponse)
async def extract_text_from_pdf(
    file: UploadFile = File(...),
    force_ocr: bool = False,
    use_gemini: bool = True,
    language: str = "ben+eng"
):
    """Extract text from uploaded PDF file using Gemini AI and OCR"""
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text using Gemini AI first for better Bangla support
        if use_gemini:
            print("🔄 Using Gemini AI for text extraction...")
            result = gemini_extractor.extract_text_from_pdf(file_path)
            
            if result["text"] and len(result["text"].strip()) > 100:
                # Successful Gemini extraction
                normalized_metadata = {
                    "pageCount": result["metadata"].get("total_pages", 0),
                    "extractionMethod": "gemini_ai",
                    "confidence": 0.95,  # High confidence for AI extraction
                    "language": language,
                    "processingTime": 0.0,
                    "tablesFound": 0
                }
                
                return TextExtractionResponse(
                    text=result["text"],
                    metadata=normalized_metadata,
                    file_id=file_id,
                    filename=file.filename,
                    success=True
                )
            else:
                print("⚠ Gemini extraction failed, falling back to OCR...")
        
        # Fallback to traditional OCR extraction
        print("🔄 Using OCR for text extraction...")
        result = pdf_extractor.process_pdf_enhanced(
            file_path, 
            lang=language, 
            force_ocr=True  # Force OCR as fallback
        )
        
        if result["error"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Normalize metadata format
        metadata = result["metadata"]
        normalized_metadata = {
            "pageCount": metadata.get("total_pages", 0),
            "extractionMethod": metadata.get("extraction_method", "ocr"),
            "confidence": metadata.get("confidence_avg", 0.8),
            "language": language,
            "processingTime": metadata.get("processing_time", 0.0),
            "tablesFound": metadata.get("tables_found", 0)
        }
        
        return TextExtractionResponse(
            text=result["text"],
            metadata=normalized_metadata,
            file_id=file_id,
            filename=file.filename,
            success=True
        )
    
    except Exception as e:
        print(f"❌ Text extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")
    
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/check-plagiarism")
async def check_plagiarism(request: PlagiarismCheckRequest):
    """Check text for plagiarism against corpus"""
    
    try:
        # Perform plagiarism check
        result = await plagiarism_detector.check_plagiarism(
            text=request.text,
            threshold=request.threshold,
            check_paraphrase=request.check_paraphrase
        )
        
        # Return simplified response format for frontend
        return {
            "overall_similarity": result["overall_similarity"],
            "plagiarism_score": result["plagiarism_score"], 
            "is_plagiarized": result["is_plagiarized"],
            "matches": result["matches"],
            "analysis": result["analysis"],
            "processing_time": result["processing_time"],
            "success": True
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plagiarism check failed: {str(e)}")

@app.post("/check-file-plagiarism")
async def check_file_plagiarism(file: UploadFile = File(...)):
    """Extract text from PDF and check for plagiarism"""
    
    try:
        # First extract text
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text using Gemini AI for full PDF processing
        extraction_result = gemini_extractor.extract_text_from_pdf(file_path)
        
        if not extraction_result["text"]:
            raise HTTPException(status_code=400, detail="কোনো টেক্সট পাওয়া যায়নি")
        
        # Check plagiarism
        plagiarism_result = await plagiarism_detector.check_plagiarism(
            text=extraction_result["text"],
            threshold=0.7,
            check_paraphrase=True
        )
        
        return {
            "overall_similarity": plagiarism_result["overall_similarity"],
            "plagiarism_score": plagiarism_result["plagiarism_score"],
            "is_plagiarized": plagiarism_result["is_plagiarized"], 
            "matches": plagiarism_result["matches"],
            "analysis": plagiarism_result["analysis"],
            "processing_time": plagiarism_result["processing_time"],
            "extracted_text": extraction_result["text"][:500] + "..." if len(extraction_result["text"]) > 500 else extraction_result["text"],
            "file_info": {
                "filename": file.filename,
                "pages": extraction_result.get("metadata", {}).get("pages", 0)
            },
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File plagiarism check failed: {str(e)}")
    
    finally:
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/add-to-corpus")
async def add_document_to_corpus(
    title: str,
    content: str,
    source: str = "manual",
    metadata: Optional[Dict] = None
):
    """Add a document to the corpus"""
    
    try:
        doc_id = await corpus_manager.add_document(
            title=title,
            content=content,
            source=source,
            metadata=metadata or {}
        )
        
        return {
            "success": True,
            "document_id": doc_id,
            "message": "Document added to corpus successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add document: {str(e)}")

@app.get("/corpus/stats")
async def get_corpus_stats():
    """Get corpus statistics"""
    
    try:
        stats = await corpus_manager.get_stats()
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.post("/corpus/search")
async def search_corpus(
    query: str,
    limit: int = 10,
    threshold: float = 0.5
):
    """Search documents in corpus"""
    
    try:
        results = await corpus_manager.search_documents(
            query=query,
            limit=limit,
            threshold=threshold
        )
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/batch-extract")
async def batch_extract_pdfs(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    """Extract text from multiple PDF files"""
    
    # Validate files
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail=f"File {file.filename} is not a PDF"
            )
    
    # Generate batch ID
    batch_id = str(uuid.uuid4())
    
    # Process files in background
    background_tasks.add_task(
        process_batch_extraction,
        files=files,
        batch_id=batch_id
    )
    
    return {
        "batch_id": batch_id,
        "message": f"Processing {len(files)} files",
        "status": "started"
    }

async def process_batch_extraction(files: List[UploadFile], batch_id: str):
    """Background task for batch PDF processing"""
    
    results = []
    
    for file in files:
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
        
        try:
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Extract text
            result = pdf_extractor.process_pdf_enhanced(file_path)
            
            results.append({
                "filename": file.filename,
                "file_id": file_id,
                "success": not bool(result["error"]),
                "text_length": len(result["text"]),
                "metadata": result["metadata"]
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "file_id": file_id,
                "success": False,
                "error": str(e)
            })
        
        finally:
            # Clean up
            if os.path.exists(file_path):
                os.remove(file_path)
    
    # Store results (in a real app, you'd store this in a database)
    # For now, we'll just log it
    print(f"Batch {batch_id} completed: {len(results)} files processed")

@app.get("/batch-status/{batch_id}")
async def get_batch_status(batch_id: str):
    """Get status of batch processing"""
    
    # In a real app, you'd check the database
    # For now, return a placeholder
    return {
        "batch_id": batch_id,
        "status": "completed",
        "message": "Batch processing completed"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)