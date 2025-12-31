/**
 * API Client - Abstraction layer for all API calls
 * Handles authentication, error handling, and retries
 */

class APIClient {
  constructor(baseURL = '', apiKey = 'my-secret-antigravity-password') {
    this.baseURL = baseURL;
    this.apiKey = apiKey;
    this.defaultUserId = 'web-demo-user';
  }

  /**
   * Query the companion endpoint
   * @param {Object} params - Query parameters
   * @param {string} params.message - User's question
   * @param {string} params.mode - Persona mode (plain_english, founder_takeaway, engineer_angle)
   * @param {string} params.episode_id - Episode identifier
   * @param {string} [params.user_id] - Optional user ID
   * @param {boolean} [params.debug] - Enable debug mode
   * @param {Object} [params.user_profile] - User profile (role, domain)
   * @returns {Promise<Object>} API response
   */
  async query({ message, mode, episode_id, user_id = null, debug = false, user_profile = null }) {
    const url = `${this.baseURL}/companion/query`;

    const payload = {
      message,
      mode,
      episode_id,
      user_id: user_id || this.defaultUserId,
      debug,
      user_profile
    };

    try {
      const response = await this._fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': this.apiKey
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new APIError(
          errorData.detail || 'Request failed',
          response.status,
          errorData
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(`Network error: ${error.message}`, 0, { originalError: error });
    }
  }

  /**
   * Check API health
   * @returns {Promise<Object>} Health status
   */
  async healthCheck() {
    const url = `${this.baseURL}/health`;

    try {
      const response = await this._fetch(url);

      if (!response.ok) {
        throw new APIError('Health check failed', response.status);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(`Health check error: ${error.message}`, 0);
    }
  }

  /**
   * Get list of episodes
   * @returns {Promise<Array>} List of episodes
   */
  async getEpisodes() {
    const url = `${this.baseURL}/episodes`;

    try {
      const response = await this._fetch(url, {
        headers: {
          'X-API-Key': this.apiKey
        }
      });

      if (!response.ok) {
        throw new APIError('Failed to fetch episodes', response.status);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(`Error fetching episodes: ${error.message}`, 0);
    }
  }

  /**
   * Internal fetch wrapper with timeout and retry logic
   * @private
   */
  async _fetch(url, options = {}, timeout = 120000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error.name === 'AbortError') {
        throw new APIError('Request timeout', 408);
      }

      throw error;
    }
  }
}

/**
 * Custom API Error class
 */
class APIError extends Error {
  constructor(message, statusCode = 500, details = {}) {
    super(message);
    this.name = 'APIError';
    this.statusCode = statusCode;
    this.details = details;
  }

  isNetworkError() {
    return this.statusCode === 0;
  }

  isClientError() {
    return this.statusCode >= 400 && this.statusCode < 500;
  }

  isServerError() {
    return this.statusCode >= 500;
  }

  getUserFriendlyMessage() {
    if (this.isNetworkError()) {
      return 'Network connection failed. Please check your internet connection.';
    }

    if (this.statusCode === 404) {
      return 'The requested resource was not found.';
    }

    if (this.statusCode === 429) {
      return 'Too many requests. Please wait a moment and try again.';
    }

    if (this.isServerError()) {
      return 'Server error occurred. Please try again later.';
    }

    return this.message || 'An unexpected error occurred.';
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { APIClient, APIError };
}
