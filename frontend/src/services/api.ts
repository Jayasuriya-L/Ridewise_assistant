export interface ChatMessageData {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequestPayload {
  message: string;
  role: 'CUSTOMER' | 'SUPPORT_AGENT';
  customer_id?: string;
  booking_id?: string;
  conversation_history?: ChatMessageData[];
}

export interface ChatResponsePayload {
  answer: string;
  role: string;
  query_type: string;
  sources: string[];
  data_context?: Record<string, any>;
}

export interface HealthResponsePayload {
  status: string;
  database_connected: boolean;
  policy_docs_indexed: number;
  llm_configured: boolean;
  timestamp: string;
}

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';

export async function checkHealth(): Promise<HealthResponsePayload> {
  const response = await fetch(`${BACKEND_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed with status: ${response.status}`);
  }
  return response.json();
}

export async function sendChatMessage(payload: ChatRequestPayload): Promise<ChatResponsePayload> {
  const response = await fetch(`${BACKEND_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    const detail = errorBody?.detail || `Server returned error status ${response.status}`;
    throw new Error(detail);
  }

  return response.json();
}
