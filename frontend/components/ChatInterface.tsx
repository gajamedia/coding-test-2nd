import React, { useState } from 'react';
import { v4 as uuidv4 } from 'uuid';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  sources?: any[];
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: uuidv4(),
      type: 'user',
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: input,
          // history: chatHistory,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get a response from server.');
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: uuidv4(),
        type: 'assistant',
        content: data.answer,
        sources: data.sources || [],
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      setError(err.message || 'Unexpected error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="chat-interface max-w-2xl mx-auto bg-white p-4 shadow-md rounded-md">
      <div className="messages h-80 overflow-y-auto mb-4 border rounded p-2 bg-gray-50">
        {messages.map((msg) => (
          <div key={msg.id} className={`mb-2 text-sm ${msg.type === 'user' ? 'text-right' : 'text-left'}`}>
            <div className={`inline-block p-2 rounded-lg ${msg.type === 'user' ? 'bg-blue-100' : 'bg-gray-200'}`}>
              <p>{msg.content}</p>
              {msg.type === 'assistant' && (msg.sources?.length ?? 0 ) > 0 && (
                <div className="mt-1 text-xs text-gray-600">
                  <strong>Sources:</strong>
                  <ul className="list-disc ml-4">
                    {(msg.sources ?? []).map((src, idx) => (
                      <li key={idx}>{src}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && <p className="text-gray-500">Loading...</p>}
        {error && <p className="text-red-500">Error: {error}</p>}
      </div>

      <div className="input-area flex gap-2">
        <input
          type="text"
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyPress}
          placeholder="Ask a question..."
          className="flex-1 px-3 py-2 border rounded-md"
        />
        <button
          onClick={handleSendMessage}
          className="bg-blue-600 text-white px-4 py-2 rounded-md disabled:opacity-50"
          disabled={isLoading}
        >
          Send
        </button>
      </div>
    </div>
  );
}