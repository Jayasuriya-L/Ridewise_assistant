import React, { useState, useEffect } from 'react';
import { RoleSelector } from './components/RoleSelector';
import { ChatWindow } from './components/ChatWindow';
import { MessageItem } from './components/ChatMessage';
import { sendChatMessage, checkHealth, HealthResponsePayload } from './services/api';

export const App: React.FC = () => {
  const [role, setRole] = useState<'CUSTOMER' | 'SUPPORT_AGENT'>('CUSTOMER');
  const [customerId, setCustomerId] = useState('CUST0001');
  const [bookingId, setBookingId] = useState('');
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [health, setHealth] = useState<HealthResponsePayload | null>(null);

  useEffect(() => {
    checkHealth().then(setHealth).catch(() => setHealth(null));
  }, []);

  const handleNewConversation = () => {
    setMessages([]);
    setErrorMessage(null);
    setInputText('');
  };

  const sendMessage = async (textToSend?: string) => {
    const text = (textToSend || inputText).trim();
    if (!text || isLoading) return;

    if (role === 'CUSTOMER' && !customerId.trim()) {
      setErrorMessage('Please enter a valid Customer ID before asking questions.');
      return;
    }

    const userMsg: MessageItem = {
      id: `u-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setErrorMessage(null);
    setIsLoading(true);

    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      const res = await sendChatMessage({
        message: text,
        role,
        customer_id: role === 'CUSTOMER' ? customerId.trim() : undefined,
        booking_id: bookingId.trim() || undefined,
        conversation_history: history,
      });

      setMessages((prev) => [...prev, {
        id: `a-${Date.now()}`,
        role: 'assistant',
        content: res.answer,
        queryType: res.query_type,
        sources: res.sources,
        timestamp: new Date().toISOString(),
      }]);
    } catch (err: any) {
      setErrorMessage(err.message || 'Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-shell">
      {/* Header */}
      <header className="app-header">
        <div className="brand">
          <div className="brand-icon">
            <svg viewBox="0 0 24 24">
              <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/>
            </svg>
          </div>
          <div>
            <div className="brand-name">RideWise Assist</div>
            <div className="brand-tag">AI Rental & Policy Intelligence Concierge</div>
          </div>
        </div>

        <div className="header-right">
          {health && (
            <div className="status-pill">
              <span className="status-dot" />
              {health.database_connected ? `Connected · ${health.policy_docs_indexed} Docs Indexed` : 'Disconnected'}
            </div>
          )}
          <button className="btn-new-chat" onClick={handleNewConversation}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            New Chat
          </button>
        </div>
      </header>

      {/* Body */}
      <div className="workspace">
        <RoleSelector
          role={role}
          onRoleChange={(r) => { setRole(r); handleNewConversation(); }}
          customerId={customerId}
          onCustomerIdChange={setCustomerId}
          bookingId={bookingId}
          onBookingIdChange={setBookingId}
          onQuickPrompt={(p) => sendMessage(p)}
        />
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          errorMessage={errorMessage}
          onClearError={() => setErrorMessage(null)}
          inputText={inputText}
          onInputChange={setInputText}
          onSendMessage={() => sendMessage()}
          onChipClick={(t) => sendMessage(t)}
        />
      </div>
    </div>
  );
};

export default App;
