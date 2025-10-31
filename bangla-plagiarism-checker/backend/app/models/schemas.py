from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class TextExtractionResponse(BaseModel):
    """Response model for text extraction"""
    text: str
    metadata: Dict[str, Any]
    file_id: str
    filename: str
    success: bool
    error: Optional[str] = None

class PlagiarismMatch(BaseModel):
    """Plagiarism match information"""
    source_title: str
    source_id: str
    similarity_score: float
    matched_text: str
    source_text: str
    start_position: int
    end_position: int
    match_type: str  # 'exact', 'paraphrase', 'similar'

class PlagiarismAnalysis(BaseModel):
    """Detailed plagiarism analysis"""
    total_sentences: int
    flagged_sentences: int
    unique_sources: int
    longest_match_length: int
    average_similarity: float
    risk_level: str  # 'low', 'medium', 'high'

class PlagiarismCheckRequest(BaseModel):
    """Request model for plagiarism check"""
    text: str
    threshold: float = 0.7
    check_paraphrase: bool = True
    language: str = "bangla"

class PlagiarismCheckResponse(BaseModel):
    """Response model for plagiarism check"""
    overall_similarity: float
    plagiarism_score: float
    is_plagiarized: bool
    matches: List[PlagiarismMatch]
    analysis: PlagiarismAnalysis
    processing_time: float

class CorpusDocument(BaseModel):
    """Corpus document model"""
    id: str
    title: str
    content: str
    source: str
    created_at: datetime
    metadata: Dict[str, Any]
    word_count: int
    language: str

class CorpusStats(BaseModel):
    """Corpus statistics"""
    total_documents: int
    total_words: int
    total_sentences: int
    sources: Dict[str, int]
    languages: Dict[str, int]
    last_updated: datetime

class BatchProcessingResult(BaseModel):
    """Batch processing result"""
    batch_id: str
    total_files: int
    successful: int
    failed: int
    results: List[Dict[str, Any]]
    processing_time: float

class SearchResult(BaseModel):
    """Search result model"""
    document_id: str
    title: str
    similarity_score: float
    matched_text: str
    source: str
    metadata: Dict[str, Any]