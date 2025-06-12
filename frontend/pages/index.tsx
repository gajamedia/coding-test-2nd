import React from 'react';
import Head from 'next/head';
import FileUpload from '@/components/FileUpload';
import ChatInterface from '../components/ChatInterface';

export default function Home() {
  return (
    <div>
      <Head>
        <title>RAG-based Financial Q&A System</title>
        <meta name="description" content="AI-powered Q&A system for financial documents" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen p-6 bg-gray-100">
        <h1 className="text-2xl font-bold mb-4">RAG-based Financial Statement Q&A System</h1>

        <div className="mb-6">
          <p className="text-gray-700">Welcome to the RAG-based Q&A System!</p>
          <p className="text-gray-700">Upload a financial statement PDF and start asking questions.</p>
        </div>

       {/* ✅ File Upload */}
        <FileUpload
          onUploadComplete={(res) => {
            console.log('Upload success:', res);
            // Optional: trigger something if needed
          }}
          onUploadError={(err) => {
            console.error('Upload failed:', err);
          }}
        />

        {/* Chat Interface Component */}
        <ChatInterface />
      </main>
    </div>
  );
}
