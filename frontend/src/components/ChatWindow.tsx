import React, { useRef, useEffect } from 'react';
import { ChatMessage, MessageItem } from './ChatMessage';

interface ChatWindowProps {
  messages: MessageItem[];
  isLoading: boolean;
  errorMessage: string | null;
  onClearError: () => void;
  inputText: string;
  onInputChange: (val: string) => void;
  onSendMessage: () => void;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  isLoading,
  errorMessage,
  onClearError,
  inputText,
  onInputChange,
  onSendMessage,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSendMessage();
    }
  };

  return (
    <main className="chat-main">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-chat-state">
            <div className="empty-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
            </div>
            <div>
              <h2 style={{ fontSize: '1.15rem', color: '#fff', marginBottom: '0.4rem' }}>
                How can RideWise Assist help you today?
              </h2>
              <p style={{ fontSize: '0.85rem', maxWidth: '420px', margin: '0 auto', color: 'var(--text-muted)' }}>
                Ask about your bookings, vehicle specifications, cancellation & refund rules, late return penalties, or EV battery guidelines.
              </p>
            </div>
          </div>
        ) : (
          messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)
        )}

        {isLoading && (
          <div className="message-row assistant">
            <div className="avatar assistant">RW</div>
            <div className="bubble assistant" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Consulting policies and database</span>
              <div className="loader-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {errorMessage && (
        <div className="error-banner">
          <span>⚠️ {errorMessage}</span>
          <button
            type="button"
            onClick={onClearError}
            style={{ background: 'transparent', border: 'none', color: 'inherit', cursor: 'pointer', fontWeight: 'bold' }}
          >
            ✕
          </button>
        </div>
      )}

      <div className="chat-input-bar">
        <input
          id="chat-user-input"
          type="text"
          className="chat-input"
          placeholder="Type your question here (e.g. Can I cancel my reservation and get a refund?)..."
          value={inputText}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
        <button
          id="send-message-btn"
          type="button"
          className="btn-send"
          onClick={onSendMessage}
          disabled={isLoading || !inputText.trim()}
        >
          <span>Send</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>
    </main>
  );
};
