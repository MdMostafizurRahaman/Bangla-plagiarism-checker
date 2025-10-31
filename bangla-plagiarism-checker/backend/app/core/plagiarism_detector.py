import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple, Any
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import asyncio
import time
from datetime import datetime
import logging

from app.models.schemas import PlagiarismMatch, PlagiarismAnalysis

logger = logging.getLogger(__name__)

class BanglaPlagiarismDetector:
    """Advanced plagiarism detection for Bangla text"""
    
    def __init__(self):
        self.model = None
        self.corpus_embeddings = {}
        self.corpus_documents = {}
        self.initialized = False
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
    
    async def initialize(self):
        """Initialize the plagiarism detector"""
        logger.info("🔄 Initializing Bangla Plagiarism Detector...")
        
        try:
            # Load multilingual sentence transformer model
            # This model works well with Bangla text
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            
            self.initialized = True
            logger.info("✅ Plagiarism detector initialized!")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize plagiarism detector: {e}")
            raise e
    
    def preprocess_bangla_text(self, text: str) -> str:
        """Preprocess Bangla text for better analysis"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page markers
        text = re.sub(r'--- Page \d+ ---', '', text)
        
        # Remove table markers
        text = re.sub(r'=== Table \d+ ===', '', text)
        
        # Fix common punctuation issues
        text = re.sub(r'([।!?])\s*([।!?])', r'\1', text)
        
        # Ensure proper sentence ending
        text = re.sub(r'([^।!?])\s*$', r'\1।', text)
        
        return text.strip()
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences, handling Bangla punctuation"""
        # Preprocess text
        text = self.preprocess_bangla_text(text)
        
        # Split by Bangla sentence terminators
        sentences = re.split(r'[।!?]+', text)
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Minimum sentence length
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        if not self.model:
            return 0.0
        
        try:
            embeddings = self.model.encode([text1, text2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(similarity)
        except Exception as e:
            logger.warning(f"Error calculating similarity: {e}")
            return 0.0
    
    def find_exact_matches(self, text: str, corpus_text: str, min_length: int = 50) -> List[Tuple[str, int, int]]:
        """Find exact text matches"""
        matches = []
        words_text = text.split()
        words_corpus = corpus_text.split()
        
        # Sliding window approach
        for i in range(len(words_text) - min_length // 5):  # Approximate word count
            for j in range(len(words_corpus) - min_length // 5):
                # Check for exact match starting positions
                match_length = 0
                while (i + match_length < len(words_text) and 
                       j + match_length < len(words_corpus) and
                       words_text[i + match_length].lower() == words_corpus[j + match_length].lower()):
                    match_length += 1
                
                # If match is long enough
                if match_length >= min_length // 5:
                    matched_text = ' '.join(words_text[i:i + match_length])
                    if len(matched_text) >= min_length:
                        matches.append((matched_text, i, i + match_length))
        
        return matches
    
    def detect_paraphrasing(self, sentences: List[str], corpus_sentences: List[str], 
                          threshold: float = 0.8) -> List[PlagiarismMatch]:
        """Detect paraphrased content using semantic similarity"""
        matches = []
        
        if not self.model:
            return matches
        
        try:
            # Encode all sentences
            query_embeddings = self.model.encode(sentences)
            corpus_embeddings = self.model.encode(corpus_sentences)
            
            # Calculate similarities
            similarities = cosine_similarity(query_embeddings, corpus_embeddings)
            
            for i, sentence in enumerate(sentences):
                for j, corpus_sentence in enumerate(corpus_sentences):
                    similarity = similarities[i][j]
                    
                    if similarity >= threshold and len(sentence) > 20:
                        match = PlagiarismMatch(
                            source_title="Corpus Document",
                            source_id=f"corpus_{j}",
                            similarity_score=float(similarity),
                            matched_text=sentence,
                            source_text=corpus_sentence,
                            start_position=i * 100,  # Approximate position
                            end_position=(i + 1) * 100,
                            match_type="paraphrase" if similarity < 0.95 else "similar"
                        )
                        matches.append(match)
        
        except Exception as e:
            logger.warning(f"Error in paraphrase detection: {e}")
        
        return matches
    
    async def check_plagiarism(self, text: str, threshold: float = 0.7, 
                              check_paraphrase: bool = True) -> Dict[str, Any]:
        """Check text for plagiarism"""
        start_time = time.time()
        
        if not self.initialized:
            raise RuntimeError("Plagiarism detector not initialized")
        
        # Preprocess text
        cleaned_text = self.preprocess_bangla_text(text)
        sentences = self.split_into_sentences(cleaned_text)
        
        # Initialize results
        all_matches = []
        total_similarity = 0.0
        flagged_sentences = 0
        
        # Mock corpus for demonstration
        # In a real implementation, this would come from your corpus manager
        mock_corpus = [
            "বাংলা ভাষার অনেক গুরুত্বপূর্ণ সাহিত্য রয়েছে যা আমাদের সংস্কৃতির অংশ।",
            "শিক্ষা ব্যবস্থার উন্নতির জন্য আমাদের নতুন পদ্ধতি অবলম্বন করতে হবে।",
            "প্রযুক্তির উন্নতির সাথে সাথে আমাদের জীবনযাত্রার মানও উন্নত হচ্ছে।",
            "গবেষণার ক্ষেত্রে নতুন নতুন আবিষ্কার আমাদের জ্ঞানের পরিধি বৃদ্ধি করছে।"
        ]
        
        # Check each sentence
        for i, sentence in enumerate(sentences):
            best_similarity = 0.0
            best_match = None
            
            # Check against corpus
            for j, corpus_text in enumerate(mock_corpus):
                similarity = self.calculate_semantic_similarity(sentence, corpus_text)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    
                    if similarity >= threshold:
                        best_match = PlagiarismMatch(
                            source_title=f"Document {j + 1}",
                            source_id=f"doc_{j}",
                            similarity_score=similarity,
                            matched_text=sentence,
                            source_text=corpus_text,
                            start_position=i * 100,
                            end_position=(i + 1) * 100,
                            match_type="similar" if similarity >= 0.9 else "paraphrase"
                        )
            
            if best_match:
                all_matches.append(best_match)
                flagged_sentences += 1
            
            total_similarity += best_similarity
        
        # Calculate overall metrics
        avg_similarity = total_similarity / len(sentences) if sentences else 0.0
        plagiarism_score = (flagged_sentences / len(sentences)) * 100 if sentences else 0.0
        is_plagiarized = plagiarism_score > 30  # 30% threshold
        
        # Determine risk level
        if plagiarism_score < 15:
            risk_level = "low"
        elif plagiarism_score < 50:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        # Create analysis
        analysis = PlagiarismAnalysis(
            total_sentences=len(sentences),
            flagged_sentences=flagged_sentences,
            unique_sources=len(set(match.source_id for match in all_matches)),
            longest_match_length=max((len(match.matched_text) for match in all_matches), default=0),
            average_similarity=avg_similarity,
            risk_level=risk_level
        )
        
        processing_time = time.time() - start_time
        
        return {
            "overall_similarity": avg_similarity,
            "plagiarism_score": plagiarism_score,
            "is_plagiarized": is_plagiarized,
            "matches": all_matches,
            "analysis": analysis,
            "processing_time": processing_time
        }
    
    def add_to_corpus(self, document_id: str, text: str, metadata: Dict = None):
        """Add document to corpus for comparison"""
        if not self.model:
            return
        
        # Preprocess and encode text
        cleaned_text = self.preprocess_bangla_text(text)
        sentences = self.split_into_sentences(cleaned_text)
        
        try:
            embeddings = self.model.encode(sentences)
            self.corpus_embeddings[document_id] = embeddings
            self.corpus_documents[document_id] = {
                "text": cleaned_text,
                "sentences": sentences,
                "metadata": metadata or {}
            }
        except Exception as e:
            logger.error(f"Failed to add document to corpus: {e}")
    
    def update_corpus(self, corpus_data: Dict[str, str]):
        """Update corpus with multiple documents"""
        for doc_id, text in corpus_data.items():
            self.add_to_corpus(doc_id, text)