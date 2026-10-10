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
  onChipClick: (text: string) => void;
}

const STARTER_CHIPS = [
  'View my bookings',
  'Cancellation refund rules',
  'Late return penalty',
  'EV battery fee',
];

export const ChatWindow: React.FC<ChatWindowProps> = ({
  messages, isLoading, errorMessage, onClearError,
  inputText, onInputChange, onSendMessage, onChipClick,
}) => {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); onSendMessage(); }
  };

  return (
    <div className="chat-area">
      <div className="messages-scroll">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon-wrap">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
            </div>
            <div className="empty-title">How can RideWise Assist help you?</div>
            <div className="empty-subtitle">
              Ask about bookings, payment history, cancellation & refund policies, late return penalties, or EV charging guidelines.
            </div>
            <div className="empty-chips">
              {STARTER_CHIPS.map((c, i) => (
                <button key={i} className="chip" onClick={() => onChipClick(c)}>{c}</button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)
        )}

        {isLoading && (
          <div className="typing-wrap">
            <div className="avatar assistant">AI</div>
            <div className="typing-bubble">
              <div className="typing-dot" />
              <div className="typing-dot" />
              <div className="typing-dot" />
            </div>
          </div>
        )}

        <div ref={endRef} />
      </div>

      {errorMessage && (
        <div className="error-banner">
          <span>⚠ {errorMessage}</span>
          <button className="error-close" onClick={onClearError}>✕</button>
        </div>
      )}

      <div className="input-bar">
        <input
          id="chat-user-input"
          className="chat-input"
          type="text"
          placeholder="Ask about your bookings, policies, fees…"
          value={inputText}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
        <button
          id="send-message-btn"
          className="btn-send"
          onClick={onSendMessage}
          disabled={isLoading || !inputText.trim()}
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
          Send
        </button>
      </div>
    </div>
  );
};
