/**
 * AniCare AI — Central Frontend API HTTP Client
 * 
 * Provides unified networking, JWT token injection, timeout handling,
 * and seamless fallback handling for SIH 2026 Hackathon presentation.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';
const TOKEN_KEY = 'anicare_auth_token';

class ApiClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  setToken(token) {
    if (token) {
      localStorage.setItem(TOKEN_KEY, token);
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
  }

  clearToken() {
    localStorage.removeItem(TOKEN_KEY);
  }

  getHeaders(customHeaders = {}, isFormData = false) {
    const headers = { ...customHeaders };
    if (!isFormData) {
      headers['Content-Type'] = 'application/json';
    }
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
    const isFormData = options.body instanceof FormData;

    const config = {
      ...options,
      headers: this.getHeaders(options.headers, isFormData),
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          errorData = { error: response.statusText, status_code: response.status };
        }
        const err = new Error(errorData.error || errorData.detail || `Request failed with status ${response.status}`);
        err.status = response.status;
        err.data = errorData;
        throw err;
      }

      return await response.json();
    } catch (error) {
      // Mark whether this was a connection failure (backend offline)
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        error.isNetworkError = true;
      }
      throw error;
    }
  }

  get(endpoint, params = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        query.append(key, val);
      }
    });
    const queryString = query.toString();
    const fullEndpoint = queryString ? `${endpoint}?${queryString}` : endpoint;
    return this.request(fullEndpoint, { method: 'GET' });
  }

  post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  upload(endpoint, formData) {
    return this.request(endpoint, {
      method: 'POST',
      body: formData,
    });
  }

  async checkHealth() {
    try {
      return await this.get('/health');
    } catch (err) {
      return { status: 'offline', connected: false, error: err.message };
    }
  }
}

export const apiClient = new ApiClient(BASE_URL);
export default apiClient;
