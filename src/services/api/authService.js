import apiClient from './client';
import { CURRENT_USER } from '../../data/mockData';

export const authService = {
  /**
   * Authenticates user against backend or simulates mock login.
   */
  async login(email, password) {
    try {
      const response = await apiClient.post('/auth/login', { email, password });
      if (response.access_token) {
        apiClient.setToken(response.access_token);
      }
      return response;
    } catch (error) {
      if (error.isNetworkError) {
        console.warn('Backend unavailable, using simulated demo session for:', email);
        return {
          access_token: 'mock-session-jwt-token',
          token_type: 'bearer',
          user: CURRENT_USER,
          isDemoFallback: true,
        };
      }
      throw error;
    }
  },

  /**
   * Registers a new account.
   */
  async register(userData) {
    const response = await apiClient.post('/auth/register', userData);
    if (response.access_token) {
      apiClient.setToken(response.access_token);
    }
    return response;
  },

  /**
   * Fetches currently logged-in user profile.
   */
  async getCurrentUser() {
    try {
      return await apiClient.get('/auth/me');
    } catch (error) {
      console.warn('Unable to fetch live profile, returning local context:', error.message);
      return CURRENT_USER;
    }
  },

  /**
   * Signs out current user session.
   */
  logout() {
    apiClient.clearToken();
  },

  /**
   * Checks if session token is stored.
   */
  isAuthenticated() {
    return Boolean(apiClient.getToken());
  },
};

export default authService;
