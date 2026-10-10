import React from 'react';

interface RoleSelectorProps {
  role: 'CUSTOMER' | 'SUPPORT_AGENT';
  onRoleChange: (role: 'CUSTOMER' | 'SUPPORT_AGENT') => void;
  customerId: string;
  onCustomerIdChange: (id: string) => void;
  bookingId: string;
  onBookingIdChange: (id: string) => void;
  onQuickPrompt: (prompt: string) => void;
}

export const RoleSelector: React.FC<RoleSelectorProps> = ({
  role,
  onRoleChange,
  customerId,
  onCustomerIdChange,
  bookingId,
  onBookingIdChange,
  onQuickPrompt,
}) => {
  return (
    <aside className="control-panel">
      <div>
        <h3 className="panel-title">Active Role</h3>
        <div className="role-switcher" style={{ marginTop: '0.5rem' }}>
          <button
            type="button"
            className={`role-btn ${role === 'CUSTOMER' ? 'active' : ''}`}
            onClick={() => onRoleChange('CUSTOMER')}
          >
            Customer
          </button>
          <button
            type="button"
            className={`role-btn ${role === 'SUPPORT_AGENT' ? 'active' : ''}`}
            onClick={() => onRoleChange('SUPPORT_AGENT')}
          >
            Support Agent
          </button>
        </div>
      </div>

      {role === 'CUSTOMER' && (
        <div className="input-group">
          <label className="input-label" htmlFor="customer-id-input">
            Customer ID (Required)
          </label>
          <input
            id="customer-id-input"
            className="text-input"
            type="text"
            placeholder="e.g. CUST0001"
            value={customerId}
            onChange={(e) => onCustomerIdChange(e.target.value.toUpperCase())}
          />
          <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
            Try <strong>CUST0001</strong> (Gold), <strong>CUST0002</strong>
          </span>
        </div>
      )}

      <div className="input-group">
        <label className="input-label" htmlFor="booking-id-input">
          Booking ID Context (Optional)
        </label>
        <input
          id="booking-id-input"
          className="text-input"
          type="text"
          placeholder="e.g. B-0001"
          value={bookingId}
          onChange={(e) => onBookingIdChange(e.target.value.toUpperCase())}
        />
        <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
          Directs query to a specific reservation
        </span>
      </div>

      <div className="quick-prompts-section">
        <h3 className="panel-title">Quick Test Prompts</h3>
        {role === 'CUSTOMER' ? (
          <>
            <button
              className="quick-prompt-btn"
              onClick={() => onQuickPrompt("What are my active and completed bookings?")}
            >
              📅 View my bookings
            </button>
            <button
              className="quick-prompt-btn"
              onClick={() => onQuickPrompt("What is the cancellation refund policy if I cancel 6 hours before pickup?")}
            >
              📄 Refund policy (6 hrs before)
            </button>
            <button
              className="quick-prompt-btn"
              onClick={() => onQuickPrompt("What is the penalty for returning an EV scooter with low battery?")}
            >
              ⚡ EV low battery penalty rules
            </button>
            <button
              className="quick-prompt-btn"
              onClick={() => onQuickPrompt("Do I have any recorded damage reports or deductions?")}
            >
              🛠️ Check my damage reports
            </button>
          </>
        ) : (
          <>
            <button
              className="quick-prompt-btn"
              onClick={() => onQuickPrompt("Show details for booking B-0001 including vehicle and payment status")}
            >
              🔍 Inspect Booking B-0001
            </button>
            <button
              className="quick-prompt-btn"
              onClick={() => onQuickPrompt("List all damage reports with status CHARGED or DISPUTED")}
            >
              ⚠️ Review open damage claims
            </button>
            <button
              className="quick-prompt-btn"
              onClick={() => onQuickPrompt("Explain the difference between Cancellation Policy v1 and v2")}
            >
              ⚖️ Compare Policy v1 vs v2
            </button>
          </>
        )}
      </div>
    </aside>
  );
};
