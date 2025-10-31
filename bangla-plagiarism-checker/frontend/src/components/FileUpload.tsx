import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import toast from 'react-hot-toast';

interface FileUploadProps {
  onFileUpload: (file: File) => void;
  onTextExtracted: (data: { text: string; metadata?: any }) => void;
  isProcessing: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileUpload,
  onTextExtracted,
  isProcessing
}) => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [extractionStatus, setExtractionStatus] = useState<'idle' | 'uploading' | 'extracting' | 'success' | 'error'>('idle');
  const [extractionProgress, setExtractionProgress] = useState<string>('');

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      // Validate file
      if (file.type !== 'application/pdf') {
        toast.error('শুধুমাত্র PDF ফাইল আপলোড করুন');
        return;
      }
      if (file.size > 50 * 1024 * 1024) { // 50MB limit
        toast.error('ফাইল সাইজ ৫০ MB এর কম হতে হবে');
        return;
      }

      setUploadedFile(file);
      setExtractionStatus('uploading');
      setExtractionProgress('ফাইল আপলোড হচ্ছে...');

      try {
        // Call the upload function
        await onFileUpload(file);
        setExtractionStatus('success');
        setExtractionProgress('টেক্সট সফলভাবে নিষ্কাশন হয়েছে');
        toast.success('PDF থেকে টেক্সট সফলভাবে নিষ্কাশন হয়েছে');
      } catch (error: any) {
        console.error('File upload failed:', error);
        setExtractionStatus('error');
        setExtractionProgress('নিষ্কাশনে সমস্যা হয়েছে');
        toast.error('টেক্সট নিষ্কাশনে সমস্যা হয়েছে');
      }
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: false,
    disabled: isProcessing || extractionStatus === 'uploading' || extractionStatus === 'extracting'
  });

  const removeFile = () => {
    setUploadedFile(null);
    setExtractionStatus('idle');
    setExtractionProgress('');
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-4">
      {!uploadedFile ? (
        <div className="space-y-4">
          {/* File Input Button */}
          <div className="flex justify-center">
            <label className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg cursor-pointer transition-colors duration-200">
              <Upload className="w-5 h-5 mr-2" />
              PDF ফাইল নির্বাচন করুন
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    onDrop([file]);
                  }
                }}
                className="hidden"
                disabled={isProcessing}
              />
            </label>
          </div>

          {/* Drag and Drop Area */}
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-200 ${
              isDragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
            } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <input {...getInputProps()} />
            <div className="space-y-4">
              <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto">
                <FileText className="w-6 h-6 text-gray-600" />
              </div>
              <div>
                <p className="text-base font-medium text-gray-900 mb-1">
                  {isDragActive ? 'ফাইল ছেড়ে দিন' : 'অথবা এখানে ড্র্যাগ করে আনুন'}
                </p>
                <p className="text-sm text-gray-600">
                  সর্বোচ্চ ফাইল সাইজ: ৫০ MB
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <FileText className="w-6 h-6 text-red-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-1">{uploadedFile.name}</h3>
                <p className="text-sm text-gray-600">
                  আকার: {formatFileSize(uploadedFile.size)}
                </p>
              </div>
            </div>
            {!isProcessing && extractionStatus !== 'uploading' && extractionStatus !== 'extracting' && (
              <button
                onClick={removeFile}
                className="p-2 text-gray-400 hover:text-red-500 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>

          {/* Extraction Status */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">অবস্থা:</span>
              <div className="flex items-center space-x-2">
                {extractionStatus === 'uploading' || extractionStatus === 'extracting' || isProcessing ? (
                  <>
                    <Loader className="w-4 h-4 text-blue-500 animate-spin" />
                    <span className="text-sm text-blue-600">প্রক্রিয়াকরণ হচ্ছে...</span>
                  </>
                ) : extractionStatus === 'success' ? (
                  <>
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span className="text-sm text-green-600">সম্পন্ন</span>
                  </>
                ) : extractionStatus === 'error' ? (
                  <>
                    <AlertCircle className="w-4 h-4 text-red-500" />
                    <span className="text-sm text-red-600">সমস্যা</span>
                  </>
                ) : (
                  <span className="text-sm text-gray-500">অপেক্ষায়</span>
                )}
              </div>
            </div>

            {extractionProgress && (
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-sm text-gray-700">{extractionProgress}</p>
              </div>
            )}

            {(isProcessing || extractionStatus === 'uploading' || extractionStatus === 'extracting') && (
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full animate-pulse w-2/3"></div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
        <h4 className="font-medium text-blue-900 mb-2">নির্দেশনা:</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• উন্নত AI প্রযুক্তি ব্যবহার করে বাংলা টেক্সট নিষ্কাশন</li>
          <li>• সকল ধরণের বাংলা ফন্ট সাপোর্ট</li>
          <li>• স্ক্যান করা ডকুমেন্ট থেকেও টেক্সট পড়তে পারে</li>
          <li>• ইংরেজি ও বাংলা মিশ্র টেক্সট সাপোর্ট</li>
        </ul>
      </div>
    </div>
  );
};

export default FileUpload;
