import os
import json
import sqlite3
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import asyncio
import logging

from app.models.schemas import CorpusDocument, CorpusStats, SearchResult

logger = logging.getLogger(__name__)

class CorpusManager:
    """Manages the Bangla corpus for plagiarism detection"""
    
    def __init__(self, db_path: str = "bangla_corpus.db"):
        self.db_path = db_path
        self.documents = {}
        self.initialized = False
        self._setup_database()
    
    def _setup_database(self):
        """Setup SQLite database for corpus storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    word_count INTEGER,
                    language TEXT DEFAULT 'bangla'
                )
            ''')
            
            # Create index for faster searches
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_source ON documents(source)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_language ON documents(language)
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Database setup completed")
            
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            raise e
    
    async def load_corpus(self):
        """Load existing corpus from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM documents')
            rows = cursor.fetchall()
            
            for row in rows:
                doc_id, title, content, source, created_at, metadata_json, word_count, language = row
                
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                self.documents[doc_id] = CorpusDocument(
                    id=doc_id,
                    title=title,
                    content=content,
                    source=source,
                    created_at=datetime.fromisoformat(created_at),
                    metadata=metadata,
                    word_count=word_count,
                    language=language
                )
            
            conn.close()
            self.initialized = True
            logger.info(f"✅ Loaded {len(self.documents)} documents from corpus")
            
        except Exception as e:
            logger.error(f"❌ Failed to load corpus: {e}")
            # Initialize with empty corpus if loading fails
            self.initialized = True
    
    async def add_document(self, title: str, content: str, source: str = "manual", 
                          metadata: Dict = None) -> str:
        """Add a new document to the corpus"""
        
        doc_id = str(uuid.uuid4())
        word_count = len(content.split())
        created_at = datetime.now()
        metadata = metadata or {}
        
        try:
            # Add to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO documents (id, title, content, source, created_at, metadata, word_count, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc_id, title, content, source, 
                created_at.isoformat(), json.dumps(metadata), 
                word_count, 'bangla'
            ))
            
            conn.commit()
            conn.close()
            
            # Add to memory
            self.documents[doc_id] = CorpusDocument(
                id=doc_id,
                title=title,
                content=content,
                source=source,
                created_at=created_at,
                metadata=metadata,
                word_count=word_count,
                language='bangla'
            )
            
            logger.info(f"✅ Added document '{title}' to corpus (ID: {doc_id})")
            return doc_id
            
        except Exception as e:
            logger.error(f"❌ Failed to add document to corpus: {e}")
            raise e
    
    async def get_document(self, doc_id: str) -> Optional[CorpusDocument]:
        """Get a document by ID"""
        return self.documents.get(doc_id)
    
    async def search_documents(self, query: str, limit: int = 10, 
                              threshold: float = 0.5) -> List[SearchResult]:
        """Search documents in corpus (simple text-based search for now)"""
        results = []
        query_lower = query.lower()
        
        for doc in self.documents.values():
            content_lower = doc.content.lower()
            
            # Simple text matching (in production, use semantic search)
            if query_lower in content_lower:
                # Calculate rough similarity based on query coverage
                similarity = min(len(query_lower) / len(content_lower), 1.0)
                
                if similarity >= threshold:
                    # Find matched text snippet
                    start_idx = content_lower.find(query_lower)
                    end_idx = min(start_idx + len(query) + 100, len(doc.content))
                    matched_text = doc.content[max(0, start_idx - 50):end_idx]
                    
                    result = SearchResult(
                        document_id=doc.id,
                        title=doc.title,
                        similarity_score=similarity,
                        matched_text=matched_text,
                        source=doc.source,
                        metadata=doc.metadata
                    )
                    results.append(result)
        
        # Sort by similarity and limit results
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:limit]
    
    async def get_stats(self) -> CorpusStats:
        """Get corpus statistics"""
        total_documents = len(self.documents)
        total_words = sum(doc.word_count for doc in self.documents.values())
        
        # Approximate sentence count (assuming 15 words per sentence)
        total_sentences = total_words // 15
        
        # Count by sources
        sources = {}
        languages = {}
        
        for doc in self.documents.values():
            sources[doc.source] = sources.get(doc.source, 0) + 1
            languages[doc.language] = languages.get(doc.language, 0) + 1
        
        last_updated = max(
            (doc.created_at for doc in self.documents.values()),
            default=datetime.now()
        )
        
        return CorpusStats(
            total_documents=total_documents,
            total_words=total_words,
            total_sentences=total_sentences,
            sources=sources,
            languages=languages,
            last_updated=last_updated
        )
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document from corpus"""
        try:
            # Remove from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
            deleted = cursor.rowcount > 0
            
            conn.commit()
            conn.close()
            
            # Remove from memory
            if doc_id in self.documents:
                del self.documents[doc_id]
                logger.info(f"✅ Deleted document {doc_id} from corpus")
                return True
            
            return deleted
            
        except Exception as e:
            logger.error(f"❌ Failed to delete document: {e}")
            return False
    
    async def bulk_import_from_directory(self, directory_path: str, 
                                        source: str = "bulk_import") -> Dict[str, Any]:
        """Import multiple text files from a directory"""
        imported = 0
        failed = 0
        errors = []
        
        if not os.path.exists(directory_path):
            return {"error": f"Directory {directory_path} does not exist"}
        
        for filename in os.listdir(directory_path):
            if filename.lower().endswith('.txt'):
                file_path = os.path.join(directory_path, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    title = os.path.splitext(filename)[0]
                    
                    await self.add_document(
                        title=title,
                        content=content,
                        source=source,
                        metadata={"imported_from": filename}
                    )
                    
                    imported += 1
                    
                except Exception as e:
                    failed += 1
                    errors.append(f"{filename}: {str(e)}")
                    logger.warning(f"Failed to import {filename}: {e}")
        
        return {
            "imported": imported,
            "failed": failed,
            "errors": errors
        }
    
    def get_all_documents(self) -> List[CorpusDocument]:
        """Get all documents in corpus"""
        return list(self.documents.values())
    
    async def export_corpus(self, export_path: str) -> bool:
        """Export corpus to JSON file"""
        try:
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "total_documents": len(self.documents),
                "documents": []
            }
            
            for doc in self.documents.values():
                export_data["documents"].append({
                    "id": doc.id,
                    "title": doc.title,
                    "content": doc.content,
                    "source": doc.source,
                    "created_at": doc.created_at.isoformat(),
                    "metadata": doc.metadata,
                    "word_count": doc.word_count,
                    "language": doc.language
                })
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Exported corpus to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to export corpus: {e}")
            return False