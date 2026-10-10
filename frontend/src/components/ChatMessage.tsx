import React from 'react';

export interface MessageItem {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  queryType?: string;
  sources?: string[];
  timestamp: string;
}

interface ChatMessageProps {
  message: MessageItem;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
      <div className={`avatar ${isUser ? 'user' : 'assistant'}`}>
        {isUser ? 'U' : 'RW'}
      </div>
      <div className={`bubble ${isUser ? 'user' : 'assistant'}`}>
        <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>

        {!isUser && (message.queryType || (message.sources && message.sources.length > 0)) && (
          <div className="meta-badges">
            {message.queryType && (
              <span className="badge badge-query">
                Category: {message.queryType}
              </span>
            )}
            {message.sources && message.sources.map((src, index) => (
              <span key={index} className="badge badge-source" title={`Source: ${src}`}>
                📌 {src}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
