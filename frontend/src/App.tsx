import React, { useState, useEffect } from 'react';
import { RoleSelector } from './components/RoleSelector';
import { ChatWindow } from './components/ChatWindow';
import { MessageItem } from './components/ChatMessage';
import { sendChatMessage, checkHealth, HealthResponsePayload } from './services/api';

export const App: React.FC = () => {
  const [role, setRole] = useState<'CUSTOMER' | 'SUPPORT_AGENT'>('CUSTOMER');
  const [customerId, setCustomerId] = useState<string>('CUST0001');
  const [bookingId, setBookingId] = useState<string>('');
  const [inputText, setInputText] = useState<string>('');
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [healthStatus, setHealthStatus] = useState<HealthResponsePayload | null>(null);

  useEffect(() => {
    // Initial health check
    checkHealth()
      .then((data) => setHealthStatus(data))
      .catch(() => setHealthStatus(null));
  }, []);

  const handleNewConversation = () => {
    setMessages([]);
    setErrorMessage(null);
  };

  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend || inputText).trim();
    if (!text || isLoading) return;

    if (role === 'CUSTOMER' && !customerId.trim()) {
      setErrorMessage('Please enter a valid Customer ID before submitting questions.');
      return;
    }

    const userMessage: MessageItem = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setErrorMessage(null);
    setIsLoading(true);

    try {
      const historyPayload = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const response = await sendChatMessage({
        message: text,
        role: role,
        customer_id: role === 'CUSTOMER' ? customerId.trim() : undefined,
        booking_id: bookingId.trim() ? bookingId.trim() : undefined,
        conversation_history: historyPayload,
      });

      const assistantMessage: MessageItem = {
        id: `assist-${Date.now()}`,
        role: 'assistant',
        content: response.answer,
        queryType: response.query_type,
        sources: response.sources,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      setErrorMessage(err.message || 'An error occurred while communicating with RideWise Assist.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickPrompt = (prompt: string) => {
    setInputText(prompt);
    handleSendMessage(prompt);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="brand-section">
          <div className="brand-logo">
            <svg viewBox="0 0 24 24">
              <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z" />
            </svg>
          </div>
          <div>
            <h1 className="brand-title">RideWise Assist</h1>
            <p className="brand-subtitle">AI Rental Support & Policy Intelligence Concierge</p>
          </div>
        </div>

        <div className="header-actions">
          {healthStatus && (
            <div className="status-indicator">
              <span className="status-dot"></span>
              <span>Backend Connected ({healthStatus.policy_docs_indexed} Docs)</span>
            </div>
          )}
          <button
            type="button"
            className="btn-secondary"
            onClick={handleNewConversation}
            title="Start a new chat session"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M12 5v14M5 12h14" />
            </svg>
            <span>New Chat</span>
          </button>
        </div>
      </header>

      <div className="chat-workspace">
        <RoleSelector
          role={role}
          onRoleChange={setRole}
          customerId={customerId}
          onCustomerIdChange={setCustomerId}
          bookingId={bookingId}
          onBookingIdChange={setBookingId}
          onQuickPrompt={handleQuickPrompt}
        />

        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          errorMessage={errorMessage}
          onClearError={() => setErrorMessage(null)}
          inputText={inputText}
          onInputChange={setInputText}
          onSendMessage={() => handleSendMessage()}
        />
      </div>
    </div>
  );
};

export default App;
