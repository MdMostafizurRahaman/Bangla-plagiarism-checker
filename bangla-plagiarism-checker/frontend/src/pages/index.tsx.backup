import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import FileUpload from '../components/FileUpload';
import TextInput from '../components/TextInput';
import PlagiarismResults from '../components/PlagiarismResults';
import { apiService } from '../utils/api';
import { BookOpen, Shield, Zap, FileCheck, Upload, Type, ArrowRight, CheckCircle, AlertCircle } from 'lucide-react';

const HomePage: React.FC = () => {
  const [extractedText, setExtractedText] = useState<string>('');
  const [plagiarismResults, setPlagiarismResults] = useState<any>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const [activeTab, setActiveTab] = useState<'upload' | 'text'>('upload');

  const handleFileUpload = async (file: File) => {
    setIsExtracting(true);
    try {
      const result = await apiService.extractText(file);
      setExtractedText(result.text);
      setPlagiarismResults(null); // Clear previous results
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Toaster
        position="top-center"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
            borderRadius: '12px',
          },
        }}
      />

      {/* Hero Header */}
      <header className="bg-white/90 backdrop-blur-sm border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-4 mb-4">
              <div className="w-14 h-14 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
                <FileCheck className="w-7 h-7 text-white" />
              </div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                বাংলা প্ল্যাজিয়ারিজম চেকার
              </h1>
            </div>
            <p className="text-gray-600 text-lg mb-6">
              AI-চালিত বাংলা টেক্সট বিশ্লেষণ সিস্টেম
            </p>
            
            <div className="flex items-center justify-center space-x-8">
              <div className="flex items-center bg-green-50 px-4 py-2 rounded-full">
                <Shield className="w-5 h-5 mr-2 text-green-500" />
                <span className="text-green-700 font-medium">নিরাপদ</span>
              </div>
              <div className="flex items-center bg-blue-50 px-4 py-2 rounded-full">
                <Zap className="w-5 h-5 mr-2 text-blue-500" />
                <span className="text-blue-700 font-medium">দ্রুত</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* Left Column - Input Section */}
          <div className="xl:col-span-2 space-y-6">
            {/* Step Indicator */}
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">প্রক্রিয়া</h2>
                <div className="flex items-center space-x-2">
                  {!extractedText && !plagiarismResults && (
                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                      ধাপ ১: টেক্সট আপলোড করুন
                    </span>
                  )}
                  {extractedText && !plagiarismResults && (
                    <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium">
                      ধাপ ২: প্ল্যাজিয়ারিজম চেক করুন
                    </span>
                  )}
                  {plagiarismResults && (
                    <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                      ধাপ ৩: ফলাফল দেখুন
                    </span>
                  )}
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    extractedText || activeTab ? 'bg-green-500' : 'bg-blue-500'
                  }`}>
                    <Upload className="w-5 h-5 text-white" />
                  </div>
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    plagiarismResults ? 'bg-green-500' : extractedText ? 'bg-blue-500' : 'bg-gray-300'
                  }`}>
                    <CheckCircle className="w-5 h-5 text-white" />
                  </div>
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    plagiarismResults ? 'bg-green-500' : 'bg-gray-300'
                  }`}>
                    <AlertCircle className="w-5 h-5 text-white" />
                  </div>
                </div>
                <ArrowRight className="w-6 h-6 text-gray-400" />
              </div>
            </div>

            {/* Tab Navigation */}
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-2">
              <div className="flex">
                <button
                  onClick={() => setActiveTab('upload')}
                  className={`flex-1 py-4 px-6 text-center rounded-xl transition-all duration-200 ${
                    activeTab === 'upload'
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Upload className="w-5 h-5 mx-auto mb-2" />
                  <span className="font-semibold">PDF আপলোড</span>
                </button>
                <button
                  onClick={() => setActiveTab('text')}
                  className={`flex-1 py-4 px-6 text-center rounded-xl transition-all duration-200 ${
                    activeTab === 'text'
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Type className="w-5 h-5 mx-auto mb-2" />
                  <span className="font-semibold">টেক্সট ইনপুট</span>
                </button>
              </div>
            </div>

            {/* Content Area */}
            <div className="space-y-6">
              {activeTab === 'upload' && (
                <FileUpload
                  onFileUpload={handleFileUpload}
                  onTextExtracted={setExtractedText}
                  isProcessing={isExtracting}
                />
              )}
              
              {activeTab === 'text' && (
                <TextInput
                  onTextSubmit={handleTextSubmit}
                  isProcessing={isChecking}
                  extractedText={extractedText}
                  onClearText={handleClearText}
                />
              )}
            </div>

            {/* Extracted Text Display */}
            {extractedText && (
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">নিষ্কাশিত টেক্সট</h3>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => navigator.clipboard.writeText(extractedText)}
                      className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors duration-200 text-sm"
                    >
                      কপি করুন
                    </button>
                    <button
                      onClick={handleClearText}
                      className="px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg transition-colors duration-200 text-sm"
                    >
                      পরিষ্কার করুন
                    </button>
                  </div>
                </div>
                <div className="max-h-60 overflow-y-auto custom-scrollbar">
                  <p className="text-gray-800 bangla-text leading-relaxed">
                    {extractedText.substring(0, 500)}...
                  </p>
                </div>
                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                  <p className="text-blue-800 text-sm">
                    <strong>টেক্সট দৈর্ঘ্য:</strong> {extractedText.length} অক্ষর
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Results Section */}
          <div className="xl:col-span-1 space-y-6">
            {!plagiarismResults ? (
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6 text-center">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  ফলাফলের অপেক্ষায়
                </h3>
                <p className="text-gray-600 text-sm">
                  প্ল্যাজিয়ারিজম চেক করার জন্য টেক্সট আপলোড করুন এবং বিশ্লেষণ শুরু করুন
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                <PlagiarismResults
                  results={plagiarismResults}
                  originalText={extractedText}
                />
              </div>
            )}

            {/* Help Section */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-6 border border-blue-200">
              <h4 className="font-semibold text-gray-900 mb-3">সাহায্য</h4>
              <div className="space-y-3 text-sm text-gray-600">
                <div className="flex items-start space-x-2">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2"></div>
                  <p>PDF ফাইল আপলোড করুন অথবা সরাসরি টেক্সট লিখুন</p>
                </div>
                <div className="flex items-start space-x-2">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2"></div>
                  <p>AI সিস্টেম আপনার টেক্সট বিশ্লেষণ করবে</p>
                </div>
                <div className="flex items-start space-x-2">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2"></div>
                  <p>বিস্তারিত প্ল্যাজিয়ারিজম রিপোর্ট পাবেন</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
                )}
              </div>
            )}

            {/* Text Input Tab */}
            {activeTab === 'text' && (
              <TextInput
                onTextSubmit={handleTextSubmit}
                isProcessing={isChecking}
                extractedText={extractedText}
              />
            )}
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 bg-white/80 backdrop-blur-sm border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="text-center">
            <p className="text-gray-600 text-sm">
              বাংলা প্ল্যাজিয়ারিজম চেকার - একাডেমিক সততার জন্য
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;