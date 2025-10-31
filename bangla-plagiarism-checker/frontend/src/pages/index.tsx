import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import FileUpload from '../components/FileUpload';
import TextInput from '../components/TextInput';
import PlagiarismResults from '../components/PlagiarismResults';
import { apiService } from '../utils/api';
import { FileCheck } from 'lucide-react';

const HomePage: React.FC = () => {
  const [extractedText, setExtractedText] = useState<string>('');
  const [plagiarismResults, setPlagiarismResults] = useState<any>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const [activeTab, setActiveTab] = useState<'upload' | 'text'>('upload');
  const [showFullText, setShowFullText] = useState(false);

  const handleFileUpload = async (file: File) => {
    setIsExtracting(true);
    try {
      const result = await apiService.extractText(file);
      setExtractedText(result.text);
      setPlagiarismResults(null);
    } catch (error: any) {
      console.error('Text extraction failed:', error);
    } finally {
      setIsExtracting(false);
    }
  };

  const handleTextSubmit = async (text: string, settings: any) => {
    setIsChecking(true);
    try {
      const result = await apiService.checkPlagiarism(text, settings);
      setPlagiarismResults(result);
    } catch (error: any) {
      console.error('Plagiarism check failed:', error);
    } finally {
      setIsChecking(false);
    }
  };

  const handleClearText = () => {
    setExtractedText('');
    setPlagiarismResults(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-center" />

      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900 text-center">
            বাংলা প্ল্যাজিয়ারিজম চেকার
          </h1>
          <p className="text-gray-600 text-center mt-2">
            বাংলা টেক্সটের মৌলিকত্ব যাচাই করুন
          </p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Step Indicator */}
        <div className="flex items-center justify-center mb-8">
          <div className="flex items-center space-x-4">
            <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
              !extractedText ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
            }`}>
              <span className="text-sm font-medium">১. টেক্সট আপলোড</span>
            </div>
            <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
              extractedText && !plagiarismResults ? 'bg-blue-100 text-blue-800' : 
              plagiarismResults ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
            }`}>
              <span className="text-sm font-medium">২. প্ল্যাজিয়ারিজম চেক</span>
            </div>
            <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
              plagiarismResults ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
            }`}>
              <span className="text-sm font-medium">৩. ফলাফল</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Input */}
          <div className="lg:col-span-2 space-y-6">
            {/* Tab Navigation */}
            <div className="bg-white rounded-lg shadow-sm p-2">
              <div className="flex">
                <button
                  onClick={() => setActiveTab('upload')}
                  className={`flex-1 py-3 px-4 text-center rounded-md transition-colors ${
                    activeTab === 'upload'
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <span className="text-sm font-medium">PDF আপলোড</span>
                </button>
                <button
                  onClick={() => setActiveTab('text')}
                  className={`flex-1 py-3 px-4 text-center rounded-md transition-colors ${
                    activeTab === 'text'
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <span className="text-sm font-medium">টেক্সট ইনপুট</span>
                </button>
              </div>
            </div>

            {/* Content */}
            {activeTab === 'upload' && (
              <FileUpload
                onFileUpload={handleFileUpload}
                onTextExtracted={(data) => setExtractedText(data.text)}
                isProcessing={isExtracting}
              />
            )}
            
            {activeTab === 'text' && (
              <TextInput
                onTextSubmit={handleTextSubmit}
                isProcessing={isChecking}
                extractedText={extractedText}
              />
            )}

            {/* Extracted Text */}
            {extractedText && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">নিষ্কাশিত টেক্সট</h3>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setShowFullText(!showFullText)}
                      className="px-3 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded text-sm"
                    >
                      {showFullText ? 'সংক্ষিপ্ত দেখুন' : 'পুরো টেক্সট দেখুন'}
                    </button>
                    <button
                      onClick={async () => {
                        setIsChecking(true);
                        try {
                          const result = await apiService.checkPlagiarism(extractedText);
                          setPlagiarismResults(result);
                        } catch (error: any) {
                          console.error('Plagiarism check failed:', error);
                          alert('প্ল্যাজিয়ারিজম চেক ব্যর্থ হয়েছে: ' + (error.message || 'অজানা ত্রুটি'));
                        } finally {
                          setIsChecking(false);
                        }
                      }}
                      disabled={isChecking}
                      className="px-3 py-1 bg-green-100 hover:bg-green-200 text-green-700 rounded text-sm disabled:opacity-50"
                    >
                      {isChecking ? 'চেক করা হচ্ছে...' : 'প্ল্যাজিয়ারিজম চেক'}
                    </button>
                    <button
                      onClick={() => navigator.clipboard.writeText(extractedText)}
                      className="px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded text-sm"
                    >
                      কপি করুন
                    </button>
                    <button
                      onClick={handleClearText}
                      className="px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded text-sm"
                    >
                      পরিষ্কার করুন
                    </button>
                  </div>
                </div>
                <div className={`${showFullText ? 'max-h-96' : 'max-h-60'} overflow-y-auto border rounded p-4 bg-gray-50`}>
                  <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                    {showFullText ? extractedText : extractedText.substring(0, 1000) + (extractedText.length > 1000 ? '...' : '')}
                  </p>
                </div>
                <div className="mt-4 text-sm text-gray-600">
                  <strong>টেক্সট দৈর্ঘ্য:</strong> {extractedText.length} অক্ষর
                  {!showFullText && extractedText.length > 1000 && (
                    <span className="ml-2 text-blue-600">
                      (পুরো টেক্সট দেখতে "পুরো টেক্সট দেখুন" বাটনে ক্লিক করুন)
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-1 space-y-6">
            {!plagiarismResults ? (
              <div className="bg-white rounded-lg shadow-sm p-6 text-center">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <FileCheck className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  ফলাফলের অপেক্ষায়
                </h3>
                <p className="text-gray-600 text-sm">
                  প্ল্যাজিয়ারিজম চেক করার জন্য টেক্সট আপলোড করুন
                </p>
              </div>
            ) : (
              <PlagiarismResults
                results={plagiarismResults}
                originalText={extractedText}
              />
            )}

            {/* Help */}
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <h4 className="font-semibold text-blue-900 mb-3">সাহায্য</h4>
              <div className="space-y-2 text-sm text-blue-800">
                <p>• PDF ফাইল আপলোড করুন অথবা সরাসরি টেক্সট লিখুন</p>
                <p>• AI সিস্টেম আপনার টেক্সট বিশ্লেষণ করবে</p>
                <p>• বিস্তারিত প্ল্যাজিয়ারিজম রিপোর্ট পাবেন</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <div className="text-center">
            <h3 className="font-semibold text-gray-900 mb-2">বাংলা প্ল্যাজিয়ারিজম চেকার</h3>
            <p className="text-gray-600 text-sm">
              AI প্রযুক্তি ব্যবহার করে বাংলা লেখার মৌলিকত্ব যাচাই করার সেবা
            </p>
            <p className="text-gray-500 text-xs mt-4">
              © ২০২৪ বাংলা প্ল্যাজিয়ারিজম চেকার। সর্বস্বত্ব সংরক্ষিত।
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;