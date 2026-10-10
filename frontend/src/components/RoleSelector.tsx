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

const CUSTOMER_PROMPTS = [
  { icon: '📅', text: 'What are my active and completed bookings?' },
  { icon: '💰', text: 'What refund am I eligible for if I cancel 6 hours before pickup?' },
  { icon: '⚡', text: 'What is the penalty for returning an EV with low battery?' },
  { icon: '🛠️', text: 'Do I have any recorded damage reports or deductions?' },
];

const AGENT_PROMPTS = [
  { icon: '🔍', text: 'Show full details for booking B-0001 including payments' },
  { icon: '⚠️', text: 'List all damage reports with CHARGED or DISPUTED status' },
  { icon: '📋', text: 'Compare Cancellation Policy v1 vs v2 key differences' },
  { icon: '📊', text: 'What is the late return fee structure and tier grace periods?' },
];

export const RoleSelector: React.FC<RoleSelectorProps> = ({
  role, onRoleChange, customerId, onCustomerIdChange,
  bookingId, onBookingIdChange, onQuickPrompt,
}) => {
  const prompts = role === 'CUSTOMER' ? CUSTOMER_PROMPTS : AGENT_PROMPTS;

  return (
    <aside className="sidebar">
      {/* Role Toggle */}
      <div className="sidebar-section">
        <div className="sidebar-label">Active Role</div>
        <div className="role-toggle">
          <button
            className={`role-btn ${role === 'CUSTOMER' ? 'active' : ''}`}
            onClick={() => onRoleChange('CUSTOMER')}
          >
            Customer
          </button>
          <button
            className={`role-btn ${role === 'SUPPORT_AGENT' ? 'active' : ''}`}
            onClick={() => onRoleChange('SUPPORT_AGENT')}
          >
            Support Agent
          </button>
        </div>

        {role === 'CUSTOMER' && (
          <div className="field">
            <label className="field-label" htmlFor="cust-id">Customer ID <span style={{color:'var(--danger)'}}>*</span></label>
            <input
              id="cust-id"
              className="input"
              type="text"
              placeholder="e.g. CUST0001"
              value={customerId}
              onChange={(e) => onCustomerIdChange(e.target.value.toUpperCase())}
            />
            <span className="field-hint">Try <strong>CUST0001</strong> (GOLD) or <strong>CUST0002</strong></span>
          </div>
        )}

        <div className="field">
          <label className="field-label" htmlFor="book-id">Booking ID <span style={{color:'var(--text-dim)'}}>· Optional</span></label>
          <input
            id="book-id"
            className="input"
            type="text"
            placeholder="e.g. B-0001"
            value={bookingId}
            onChange={(e) => onBookingIdChange(e.target.value.toUpperCase())}
          />
          <span className="field-hint">Focuses the query on a specific booking</span>
        </div>
      </div>

      {/* Quick Prompts */}
      <div className="sidebar-section">
        <div className="sidebar-label">Quick Prompts</div>
        <div className="prompts-list">
          {prompts.map((p, i) => (
            <button key={i} className="prompt-btn" onClick={() => onQuickPrompt(p.text)}>
              <span className="prompt-icon">{p.icon}</span>
              <span>{p.text}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Info Card */}
      <div className="sidebar-footer">
        <div className="info-card">
          <strong>RideWise Assist</strong> queries live operational data from SQLite and 5 official policy documents — all answers are cited and traceable.
        </div>
      </div>
    </aside>
  );
};
