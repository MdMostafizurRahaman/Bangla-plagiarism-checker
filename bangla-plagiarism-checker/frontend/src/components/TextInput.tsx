import React, { useState, useEffect } from 'react';
import { Search, Type, X } from 'lucide-react';

interface TextInputProps {
  onTextSubmit: (text: string, settings: any) => void;
  isProcessing: boolean;
  extractedText?: string;
}

const TextInput: React.FC<TextInputProps> = ({ 
  onTextSubmit, 
  isProcessing, 
  extractedText 
}) => {
  const [text, setText] = useState('');

  useEffect(() => {
    if (extractedText) {
      setText(extractedText);
    }
  }, [extractedText]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim()) {
      onTextSubmit(text.trim(), {
        threshold: 0.7,
        checkParaphrase: true
      });
    }
  };

  const wordCount = text.trim().split(/\s+/).filter(word => word.length > 0).length;

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="flex items-center space-x-2 mb-4">
        <Type className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-900">টেক্সট ইনপুট</h3>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="এখানে আপনার বাংলা টেক্সট লিখুন বা পেস্ট করুন..."
            className="w-full h-64 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-800"
            required
          />
        </div>
        
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            <span className="font-medium">{wordCount}</span> শব্দ | 
            <span className="ml-1 font-medium">{text.length}</span> অক্ষর
          </div>
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={() => setText('')}
              className="flex items-center space-x-1 px-4 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              disabled={!text.trim()}
            >
              <X className="w-4 h-4" />
              <span>ক্লিয়ার</span>
            </button>
            <button
              type="submit"
              disabled={isProcessing || !text.trim()}
              className="flex items-center space-x-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors"
            >
              <Search className="w-4 h-4" />
              <span>
                {isProcessing ? 'চেক করা হচ্ছে...' : 'প্ল্যাজিয়ারিজম চেক করুন'}
              </span>
            </button>
          </div>
        </div>
      </form>

      {/* Instructions */}
      <div className="mt-4 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-2">টিপস:</h4>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• কমপক্ষে ১০০ শব্দের টেক্সট লিখুন</li>
          <li>• বাংলা এবং ইংরেজি উভয় ভাষায় লেখা যাবে</li>
          <li>• দীর্ঘ টেক্সটের জন্য PDF আপলোড ব্যবহার করুন</li>
        </ul>
      </div>
    </div>
  );
};

export default TextInput;