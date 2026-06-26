import React from 'react';
import ReactMarkdown from 'react-markdown';
import { useState } from 'react';

interface MessageBubbleProps {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ role, content, sources }) => {
  const [copiedSource, setCopiedSource] = useState<string | null>(null);

  const handleSourceCopy = (source: string) => {
    navigator.clipboard.writeText(source).then(() => {
      setCopiedSource(source);
      setTimeout(() => setCopiedSource(null), 2000);
    });
  };

  return (
    <div className={`flex ${role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-lg p-4 rounded-lg shadow-md ${
          role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-900'
        }`}
      >
        <ReactMarkdown className="prose">{content}</ReactMarkdown>
        {role === 'assistant' && sources && sources.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {sources.map((source, index) => (
              <button
                key={index}
                onClick={() => handleSourceCopy(source)}
                className="text-xs bg-gray-300 text-gray-700 px-2 py-1 rounded hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                {copiedSource === source ? 'Copied!' : `Source ${index + 1}`}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;