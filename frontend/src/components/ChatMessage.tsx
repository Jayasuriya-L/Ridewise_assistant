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
  const time = new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <div className={`msg-row ${isUser ? 'user' : 'assistant'}`}>
      <div className={`avatar ${isUser ? 'user' : 'assistant'}`}>
        {isUser ? 'U' : 'AI'}
      </div>
      <div className="bubble-wrap">
        <div className={`bubble ${isUser ? 'user' : 'assistant'}`}>
          {message.content}

          {/* Only for assistant messages: show badges inside bubble */}
          {!isUser && (message.queryType || (message.sources && message.sources.length > 0)) && (
            <div className="msg-meta">
              {message.queryType && (
                <span className="badge badge-type">
                  ⚙ {message.queryType}
                </span>
              )}
              {message.sources?.map((src, i) => (
                <span key={i} className="badge badge-source" title={src}>
                  📄 {src.replace('ridewise.db (', 'DB (').replace('.pdf', '')}
                </span>
              ))}
            </div>
          )}
        </div>
        <span style={{ fontSize: '0.67rem', color: 'var(--text-dim)', paddingLeft: isUser ? 0 : 2, alignSelf: isUser ? 'flex-end' : 'flex-start' }}>
          {time}
        </span>
      </div>
    </div>
  );
};
