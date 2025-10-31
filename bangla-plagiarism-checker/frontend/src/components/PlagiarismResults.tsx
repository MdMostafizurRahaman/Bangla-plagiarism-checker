import React from 'react';
import { PlagiarismResult } from '../types';
import { AlertTriangle, Shield, CheckCircle } from 'lucide-react';

interface PlagiarismResultsProps {
  results: PlagiarismResult;
  originalText: string;
}

const PlagiarismResults: React.FC<PlagiarismResultsProps> = ({ results, originalText }) => {
  if (!results) {
    return (
      <div className='text-center py-12'>
        <p className='text-gray-500'>
          প্ল্যাজিয়ারিজম চেক করার জন্য টেক্সট আপলোড করুন
        </p>
      </div>
    );
  }

  const getMatchTypeColor = (matchType: 'exact' | 'paraphrase') => {
    switch(matchType) {
      case 'exact': return 'bg-red-100 text-red-800 border-red-300';
      case 'paraphrase': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getMatchTypeLabel = (matchType: 'exact' | 'paraphrase') => {
    switch(matchType) {
      case 'exact': return 'হুবহু মিল';
      case 'paraphrase': return 'প্যারাফ্রেজ';
      default: return 'সাদৃশ্য';
    }
  };

  const getRiskLevelIcon = (riskLevel: string) => {
    switch(riskLevel) {
      case 'high': return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'medium': return <Shield className="w-5 h-5 text-yellow-500" />;
      case 'low': return <CheckCircle className="w-5 h-5 text-green-500" />;
      default: return <Shield className="w-5 h-5 text-gray-500" />;
    }
  };

  const getRiskLevelText = (riskLevel: string) => {
    switch(riskLevel) {
      case 'high': return 'উচ্চ ঝুঁকি';
      case 'medium': return 'মাঝারি ঝুঁকি';
      case 'low': return 'কম ঝুঁকি';
      default: return 'অজানা';
    }
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch(riskLevel) {
      case 'high': return 'bg-red-50 border-red-200 text-red-800';
      case 'medium': return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'low': return 'bg-green-50 border-green-200 text-green-800';
      default: return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  return (
    <div className='space-y-6'>
      {/* Overall Score */}
      <div className='bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6'>
        <h3 className='text-lg font-semibold text-gray-800 mb-4 flex items-center'>
          {getRiskLevelIcon(results.analysis.riskLevel)}
          <span className="ml-2">প্ল্যাজিয়ারিজম স্কোর</span>
        </h3>
        <div className='text-center'>
          <div className='text-4xl font-bold text-blue-600 mb-2'>
            {results.overallScore.toFixed(1)}%
          </div>
          <p className='text-gray-600'>সমতার হার</p>
          <div className={`mt-4 inline-flex items-center px-3 py-1 rounded-full border ${getRiskLevelColor(results.analysis.riskLevel)}`}>
            {getRiskLevelIcon(results.analysis.riskLevel)}
            <span className="ml-1 text-sm font-medium">{getRiskLevelText(results.analysis.riskLevel)}</span>
          </div>
        </div>
      </div>

      {/* Analysis Summary */}
      <div className='bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6'>
        <h4 className='text-lg font-semibold text-gray-800 mb-4'>বিশ্লেষণ সারসংক্ষেপ</h4>
        <div className='grid grid-cols-2 gap-4 text-sm'>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className='text-gray-600'>মোট ম্যাচ:</span>
              <span className='font-medium'>{results.analysis.totalMatches}</span>
            </div>
            <div className="flex justify-between">
              <span className='text-gray-600'>হুবহু মিল:</span>
              <span className='font-medium text-red-600'>{results.analysis.exactMatches}</span>
            </div>
            <div className="flex justify-between">
              <span className='text-gray-600'>প্যারাফ্রেজ:</span>
              <span className='font-medium text-yellow-600'>{results.analysis.paraphraseMatches}</span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className='text-gray-600'>মোট শব্দ:</span>
              <span className='font-medium'>{results.wordCount}</span>
            </div>
            <div className="flex justify-between">
              <span className='text-gray-600'>বাক্য সংখ্যা:</span>
              <span className='font-medium'>{results.sentenceCount}</span>
            </div>
            <div className="flex justify-between">
              <span className='text-gray-600'>প্রক্রিয়াকরণ সময়:</span>
              <span className='font-medium'>{results.processingTime.toFixed(2)}s</span>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Matches */}
      {results.matches && results.matches.length > 0 && (
        <div className='bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6'>
          <h4 className='text-lg font-semibold text-gray-800 mb-4'>বিস্তারিত ম্যাচ</h4>
          <div className='space-y-4'>
            {results.matches.slice(0, 5).map((match, index) => (
              <div key={index} className='border border-gray-200 rounded-lg p-4 bg-gray-50'>
                <div className='flex justify-between items-center mb-3'>
                  <span className='font-medium text-gray-800'>ম্যাচ {index + 1}</span>
                  <div className='flex items-center space-x-2'>
                    <span className={`px-2 py-1 rounded text-xs font-medium border ${getMatchTypeColor(match.type)}`}>
                      {getMatchTypeLabel(match.type)}
                    </span>
                    <span className='font-bold text-blue-600'>
                      {(match.similarity * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div>
                    <p className='text-xs text-gray-500 mb-1'>আপনার টেক্সট:</p>
                    <p className='text-sm text-gray-800 bg-white p-3 rounded border'>
                      {match.matchedText.substring(0, 200)}
                      {match.matchedText.length > 200 && '...'}
                    </p>
                  </div>
                  
                  <div>
                    <p className='text-xs text-gray-500 mb-1'>সোর্স: {match.source}</p>
                    <p className='text-sm text-gray-600 bg-blue-50 p-3 rounded border border-blue-200'>
                      {match.originalText.substring(0, 200)}
                      {match.originalText.length > 200 && '...'}
                    </p>
                  </div>
                </div>
              </div>
            ))}
            
            {results.matches.length > 5 && (
              <div className="text-center text-gray-500 text-sm">
                আরও {results.matches.length - 5}টি ম্যাচ পাওয়া গেছে
              </div>
            )}
          </div>
        </div>
      )}

      {/* No matches */}
      {(!results.matches || results.matches.length === 0) && (
        <div className='bg-green-50 border border-green-200 rounded-2xl p-6 text-center'>
          <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
          <h4 className='text-lg font-semibold text-green-800 mb-2'>কোন প্ল্যাজিয়ারিজম পাওয়া যায়নি!</h4>
          <p className='text-green-600'>আপনার টেক্সট মূল বলে মনে হচ্ছে।</p>
        </div>
      )}
    </div>
  );
};

export default PlagiarismResults;
