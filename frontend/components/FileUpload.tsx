import React, { useState, useRef } from 'react';

interface FileUploadProps {
  onUploadComplete?: (result: any) => void;
  onUploadError?: (error: string) => void;
}

export default function FileUpload({ onUploadComplete, onUploadError }: FileUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    if (selectedFile.type !== 'application/pdf') {
      onUploadError?.('Only PDF files are allowed.');
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) { // 10 MB limit
      onUploadError?.('File size exceeds 10MB limit.');
      return;
    }

    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setIsUploading(true);
      setUploadProgress(0);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed.');

      const result = await response.json();
      onUploadComplete?.(result);
      setFile(null);
    } catch (error: any) {
      onUploadError?.(error.message || 'Upload error.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileSelect({ target: { files: [droppedFile] } } as any);
    }
  };

  return (
    <div className="file-upload">
      <div 
        className="upload-area border p-4 mb-4 text-center cursor-pointer"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        {file ? <p>{file.name}</p> : <p>Drag & drop a PDF here or click to select</p>}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
      />

      <button 
        onClick={handleUpload}
        disabled={!file || isUploading}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        {isUploading ? 'Uploading...' : 'Upload PDF'}
      </button>

      {isUploading && (
        <div className="progress-bar bg-gray-200 h-2 mt-2 rounded">
          <div
            className="bg-green-500 h-full rounded"
            style={{ width: `${uploadProgress}%`, transition: 'width 0.3s' }}
          />
        </div>
      )}
    </div>
  );
}
