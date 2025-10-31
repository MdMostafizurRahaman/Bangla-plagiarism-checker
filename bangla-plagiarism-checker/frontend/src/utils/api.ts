import axios, { InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import toast from 'react-hot-toast';
import {
  ExtractionResult,
  PlagiarismResult,
  CorpusDocument,
  CorpusStats,
  SearchResult,
  BatchJob,
  FileUploadOptions,
  PlagiarismCheckOptions,
  ApiResponse,
  HealthCheckResponse,
  PlagiarismError
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for PDF processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error: AxiosError) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error: AxiosError) => {
    console.error('API Response Error:', error);
    
    // Handle different error types
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      const errorData = data as any;
      
      switch (status) {
        case 400:
          toast.error(errorData?.detail || 'ভুল অনুরোধ');
          break;
        case 404:
          toast.error('API endpoint পাওয়া যায়নি');
          break;
        case 500:
          toast.error(errorData?.detail || 'সার্ভার ত্রুটি');
          break;
        default:
          toast.error(errorData?.detail || 'অজানা ত্রুটি ঘটেছে');
      }
    } else if (error.request) {
      // Network error
      toast.error('নেটওয়ার্ক সংযোগ ত্রুটি। সার্ভার চালু আছে কিনা চেক করুন।');
    } else {
      // Other error
      toast.error('অপ্রত্যাশিত ত্রুটি');
    }
    
    return Promise.reject(error);
  }
);

// API service methods
export const apiService = {
  // Health check
  async healthCheck(): Promise<HealthCheckResponse> {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      throw new Error('API স্বাস্থ্য পরীক্ষা ব্যর্থ');
    }
  },

  // Extract text from PDF
  async extractText(file: File, options: FileUploadOptions = {}): Promise<ExtractionResult> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      // Force use of Gemini AI for better Bangla support
      formData.append('use_gemini', 'true');
      
      if (options.forceOCR !== undefined) {
        formData.append('force_ocr', String(options.forceOCR));
      }
      
      if (options.language) {
        formData.append('language', options.language);
      } else {
        formData.append('language', 'ben+eng'); // Default to Bengali + English
      }

      console.log('🚀 Starting PDF extraction with Gemini AI...');
      
      const response = await api.post('/extract-text', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent: any) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / (progressEvent.total || 1)
          );
          console.log(`Upload progress: ${percentCompleted}%`);
        },
      });

      if (response.data.success) {
        console.log('✅ Text extraction successful:', {
          textLength: response.data.text?.length,
          method: response.data.metadata?.extractionMethod
        });
        toast.success('টেক্সট সফলভাবে নিষ্কাশিত হয়েছে!');
        return response.data;
      } else {
        throw new Error(response.data.error || 'টেক্সট নিষ্কাশন ব্যর্থ');
      }
    } catch (error: any) {
      console.error('❌ Text extraction error:', error);
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('PDF থেকে টেক্সট নিষ্কাশন ব্যর্থ');
    }
  },

  // Check plagiarism
  async checkPlagiarism(text: string, options: PlagiarismCheckOptions = {}): Promise<PlagiarismResult> {
    try {
      const requestData = {
        text,
        threshold: options.threshold || 0.7,
        check_paraphrase: options.checkParaphrase !== false,
        language: options.language || 'bangla',
      };

      const response = await api.post('/check-plagiarism', requestData);
      
      let rawData = response.data;
      
      // Handle response format - backend returns success flag and data at top level
      if (rawData && typeof rawData === 'object' && 'success' in rawData) {
        if (!rawData.success) {
          throw new Error(rawData.message || 'প্ল্যাজিয়ারিজম চেক ব্যর্থ');
        }
        // Data is already at top level, no need to access .result
      }

      // Transform backend response to match frontend types
      const transformedResult: PlagiarismResult = {
        overallScore: (rawData.overall_similarity || 0) * 100, // Convert to percentage
        matches: (rawData.matches || []).map((match: any) => ({
          similarity: match.similarity_score || 0,
          source: match.source_title || 'Unknown Source',
          sourceTitle: match.source_title,
          matchedText: match.matched_text || '',
          originalText: match.source_text || '',
          startIndex: match.start_position || 0,
          endIndex: match.end_position || 0,
          type: match.match_type === 'exact' ? 'exact' : 'paraphrase'
        })),
        analysis: {
          totalMatches: rawData.matches?.length || 0,
          exactMatches: (rawData.matches || []).filter((m: any) => m.match_type === 'exact').length,
          paraphraseMatches: (rawData.matches || []).filter((m: any) => m.match_type !== 'exact').length,
          avgSimilarity: rawData.analysis?.average_similarity || rawData.overall_similarity || 0,
          riskLevel: rawData.analysis?.risk_level || (rawData.overall_similarity > 0.7 ? 'high' : rawData.overall_similarity > 0.3 ? 'medium' : 'low')
        },
        processedText: text,
        wordCount: text.trim().split(/\s+/).length,
        sentenceCount: rawData.analysis?.total_sentences || 1,
        processingTime: rawData.processing_time || 0
      };

      toast.success('প্ল্যাজিয়ারিজম চেক সম্পন্ন!');
      return transformedResult;
    } catch (error: any) {
      console.error('Plagiarism check error:', error);
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('প্ল্যাজিয়ারিজম চেক ব্যর্থ');
    }
  },

  // Add document to corpus
  async addToCorpus(data: {
    title: string;
    content: string;
    source?: string;
    metadata?: any;
  }): Promise<CorpusDocument> {
    try {
      const response = await api.post('/add-to-corpus', {
        title: data.title,
        content: data.content,
        source: data.source || 'manual',
        metadata: data.metadata || {},
      });

      toast.success('ডকুমেন্ট কর্পাসে যোগ করা হয়েছে!');
      return response.data;
    } catch (error: any) {
      console.error('Add to corpus error:', error);
      throw new Error('কর্পাসে যোগ করা ব্যর্থ');
    }
  },

  // Get corpus statistics
  async getCorpusStats(): Promise<CorpusStats> {
    try {
      const response = await api.get('/corpus/stats');
      return response.data;
    } catch (error: any) {
      console.error('Get corpus stats error:', error);
      throw new Error('কর্পাস পরিসংখ্যান পেতে ব্যর্থ');
    }
  },

  // Search corpus
  async searchCorpus(query: string, options: {
    limit?: number;
    threshold?: number;
  } = {}): Promise<SearchResult[]> {
    try {
      const response = await api.post('/corpus/search', {
        query,
        limit: options.limit || 10,
        threshold: options.threshold || 0.5,
      });

      return response.data;
    } catch (error: any) {
      console.error('Search corpus error:', error);
      throw new Error('কর্পাস অনুসন্ধান ব্যর্থ');
    }
  },

  // Batch extract PDFs
  async batchExtract(files: File[]): Promise<BatchJob> {
    try {
      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files', file);
      });

      const response = await api.post('/batch-extract', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      toast.success('ব্যাচ প্রক্রিয়াকরণ শুরু হয়েছে!');
      return response.data;
    } catch (error: any) {
      console.error('Batch extract error:', error);
      throw new Error('ব্যাচ প্রক্রিয়াকরণ ব্যর্থ');
    }
  },

  // Get batch status
  async getBatchStatus(batchId: string): Promise<BatchJob> {
    try {
      const response = await api.get(`/batch-status/${batchId}`);
      return response.data;
    } catch (error: any) {
      console.error('Get batch status error:', error);
      throw new Error('ব্যাচ স্ট্যাটাস পেতে ব্যর্থ');
    }
  },
};

// Utility functions
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const validateFile = (file: File): { valid: boolean; error?: string } => {
  // Check file type
  if (!file.type.includes('pdf') && !file.name.toLowerCase().endsWith('.pdf')) {
    return { valid: false, error: 'শুধুমাত্র PDF ফাইল সমর্থিত' };
  }

  // Check file size (50MB limit)
  const maxSize = 50 * 1024 * 1024;
  if (file.size > maxSize) {
    return { valid: false, error: 'ফাইল সাইজ ৫০MB এর বেশি হতে পারে না' };
  }

  return { valid: true };
};

export const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Text processing utilities
export const preprocessBanglaText = (text: string): string => {
  // Remove extra whitespace
  text = text.replace(/\s+/g, ' ');
  
  // Fix common Unicode issues
  text = text.replace(/\u200C/g, ''); // Remove zero-width non-joiner
  text = text.replace(/\u200D/g, ''); // Remove zero-width joiner
  
  // Normalize Unicode
  text = text.normalize('NFC');
  
  return text.trim();
};

export const extractSentences = (text: string): string[] => {
  // Split by Bangla sentence terminators
  const sentences = text.split(/[।!?]+/).filter(s => s.trim().length > 0);
  return sentences.map(s => s.trim());
};

export const calculateReadingTime = (text: string): number => {
  // Average reading speed: 200 words per minute for Bangla
  const words = text.trim().split(/\s+/).length;
  return Math.ceil(words / 200);
};

export default api;