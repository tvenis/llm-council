/**
 * API client for the LLM Council backend.
 */

// Use environment variable if set, otherwise use current origin (for production)
// or localhost for development
const API_BASE = import.meta.env.VITE_API_BASE || 
  (import.meta.env.PROD ? '' : 'http://localhost:8001');

// Helper function to get headers with shared secret
function getHeaders(sharedSecret) {
  const headers = {
    'Content-Type': 'application/json',
  };
  if (sharedSecret) {
    headers['X-Shared-Secret'] = sharedSecret;
  }
  return headers;
}

export const api = {
  /**
   * List all conversations.
   * @param {string} sharedSecret - Optional shared secret for authentication
   */
  async listConversations(sharedSecret = null) {
    const response = await fetch(`${API_BASE}/api/conversations`, {
      headers: getHeaders(sharedSecret),
    });
    if (!response.ok) {
      throw new Error('Failed to list conversations');
    }
    return response.json();
  },

  /**
   * Create a new conversation.
   * @param {string} sharedSecret - Optional shared secret for authentication
   */
  async createConversation(sharedSecret = null) {
    const response = await fetch(`${API_BASE}/api/conversations`, {
      method: 'POST',
      headers: getHeaders(sharedSecret),
      body: JSON.stringify({}),
    });
    if (!response.ok) {
      throw new Error('Failed to create conversation');
    }
    return response.json();
  },

  /**
   * Get a specific conversation.
   * @param {string} conversationId - The conversation ID
   * @param {string} sharedSecret - Optional shared secret for authentication
   */
  async getConversation(conversationId, sharedSecret = null) {
    const response = await fetch(
      `${API_BASE}/api/conversations/${conversationId}`,
      {
        headers: getHeaders(sharedSecret),
      }
    );
    if (!response.ok) {
      throw new Error('Failed to get conversation');
    }
    return response.json();
  },

  /**
   * Send a message in a conversation.
   * @param {string} conversationId - The conversation ID
   * @param {string} content - The message content
   * @param {string} sharedSecret - Optional shared secret for authentication
   */
  async sendMessage(conversationId, content, sharedSecret = null) {
    const response = await fetch(
      `${API_BASE}/api/conversations/${conversationId}/message`,
      {
        method: 'POST',
        headers: getHeaders(sharedSecret),
        body: JSON.stringify({ content }),
      }
    );
    if (!response.ok) {
      throw new Error('Failed to send message');
    }
    return response.json();
  },

  /**
   * Send a message and receive streaming updates.
   * @param {string} conversationId - The conversation ID
   * @param {string} content - The message content
   * @param {function} onEvent - Callback function for each event: (eventType, data) => void
   * @param {string} sharedSecret - Optional shared secret for authentication
   * @returns {Promise<void>}
   */
  async sendMessageStream(conversationId, content, onEvent, sharedSecret = null) {
    const response = await fetch(
      `${API_BASE}/api/conversations/${conversationId}/message/stream`,
      {
        method: 'POST',
        headers: getHeaders(sharedSecret),
        body: JSON.stringify({ content }),
      }
    );

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          try {
            const event = JSON.parse(data);
            onEvent(event.type, event);
          } catch (e) {
            console.error('Failed to parse SSE event:', e);
          }
        }
      }
    }
  },
};
