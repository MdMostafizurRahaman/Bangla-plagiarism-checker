// Common interface definitions for the application

export interface PlagiarismMatch {
  similarity: number;
  source: string;
  sourceTitle?: string;
  matchedText: string;
  originalText: string;
  startIndex: number;
  endIndex: number;
  type: 'exact' | 'paraphrase';
}

export interface PlagiarismResult {
  overallScore: number;
  matches: PlagiarismMatch[];
  analysis: {
    totalMatches: number;
    exactMatches: number;
    paraphraseMatches: number;
    avgSimilarity: number;
    riskLevel: 'low' | 'medium' | 'high';
  };
  processedText: string;
  wordCount: number;
  sentenceCount: number;
  processingTime: number;
}

export interface ExtractionResult {
  success: boolean;
  text: string;
  metadata: {
    pageCount: number;
    extractionMethod: 'pdfplumber' | 'ocr' | 'hybrid';
    confidence?: number;
    language?: string;
    processingTime: number;
  };
  error?: string;
}

export interface CorpusDocument {
  id: string;
  title: string;
  content: string;
  source: string;
  metadata?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

export interface CorpusStats {
  totalDocuments: number;
  totalWords: number;
  avgDocumentLength: number;
  languages: string[];
  lastUpdated: string;
}

export interface SearchResult {
  document: CorpusDocument;
  similarity: number;
  matchedSegments: string[];
}

export interface BatchJob {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  totalFiles: number;
  processedFiles: number;
  results: ExtractionResult[];
  createdAt: string;
  completedAt?: string;
  error?: string;
}

export interface FileUploadOptions {
  forceOCR?: boolean;
  language?: 'bangla' | 'english' | 'auto';
}

export interface PlagiarismCheckOptions {
  threshold?: number;
  checkParaphrase?: boolean;
  language?: 'bangla' | 'english';
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface HealthCheckResponse {
  status: 'healthy';
  timestamp: string;
  version: string;
  models: {
    loaded: boolean;
    name: string;
  }[];
}

// Form interfaces
export interface FileUploadState {
  isDragActive: boolean;
  files: File[];
  uploading: boolean;
  progress: number;
  extractionResult: ExtractionResult | null;
  error: string | null;
}

export interface TextInputState {
  text: string;
  wordCount: number;
  characterCount: number;
  analyzing: boolean;
  result: PlagiarismResult | null;
  error: string | null;
}

export interface AnalysisSettings {
  threshold: number;
  checkParaphrase: boolean;
  language: 'bangla' | 'english';
}

// Component Props
export interface FileUploadProps {
  onTextExtracted: (result: ExtractionResult) => void;
  onAnalysisComplete?: (result: PlagiarismResult) => void;
  className?: string;
}

export interface TextInputProps {
  onAnalysisComplete: (result: PlagiarismResult) => void;
  className?: string;
}

export interface PlagiarismResultsProps {
  result: PlagiarismResult;
  originalText: string;
  onReset?: () => void;
  className?: string;
}

// Error types
export interface ApiError {
  status: number;
  message: string;
  detail?: string;
}

export class PlagiarismError extends Error {
  public status: number;
  public detail?: string;

  constructor(message: string, status: number = 500, detail?: string) {
    super(message);
    this.name = 'PlagiarismError';
    this.status = status;
    this.detail = detail;
  }
}