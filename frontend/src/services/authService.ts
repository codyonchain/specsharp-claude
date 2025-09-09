import EnvironmentChecker from '../utils/environment';

interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
}

class AuthService {
  private apiUrl: string;

  constructor() {
    this.apiUrl = EnvironmentChecker.getApiUrl();
  }

  /**
   * Initiate login flow - either OAuth or bypass based on environment
   */
  async login(): Promise<void> {
    // Check if we should bypass OAuth
    if (EnvironmentChecker.shouldUseAuthBypass()) {
      console.log('🔓 Using auth bypass (test mode)');
      await this.loginWithBypass();
      return;
    }

    // Use real OAuth
    console.log('🔐 Using Google OAuth');
    await this.loginWithOAuth();
  }

  /**
   * Login using OAuth bypass for testing
   */
  private async loginWithBypass(): Promise<void> {
    try {
      // Call the OAuth endpoint which will detect bypass mode
      const response = await fetch(`${this.apiUrl}/api/v2/oauth/login/google`, {
        method: 'GET',
        credentials: 'include',
      });

      // In bypass mode, we get a redirect with token
      if (response.redirected || response.status === 302 || response.status === 307) {
        // Extract token from redirect URL
        const redirectUrl = response.url || response.headers.get('Location');
        if (redirectUrl && redirectUrl.includes('token=')) {
          const urlParams = new URLSearchParams(redirectUrl.split('?')[1]);
          const token = urlParams.get('token');
          const authType = urlParams.get('auth');
          
          if (token && authType === 'bypass') {
            this.setTestUser(token);
            window.location.href = '/dashboard';
            return;
          }
        }
      }

      // Fallback: Set test user directly
      this.setTestUser();
      window.location.href = '/dashboard';
    } catch (error) {
      console.error('Bypass login error:', error);
      // Still set test user on error in bypass mode
      this.setTestUser();
      window.location.href = '/dashboard';
    }
  }

  /**
   * Login using real Google OAuth
   */
  private async loginWithOAuth(): Promise<void> {
    try {
      // Redirect to backend OAuth endpoint
      window.location.href = `${this.apiUrl}/api/v2/oauth/login/google`;
    } catch (error) {
      console.error('OAuth login error:', error);
      throw new Error('Failed to initiate OAuth login');
    }
  }

  /**
   * Set test user for bypass mode
   */
  private setTestUser(token?: string): void {
    const testUser: User = {
      id: 'test-user-123',
      email: 'test@specsharp.com',
      name: 'Test User'
    };
    
    // Store user data
    localStorage.setItem('user', JSON.stringify(testUser));
    localStorage.setItem('isAuthenticated', 'true');
    
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.setItem('token', 'test-token-bypass-mode');
    }
    
    console.log('✅ Test user logged in (bypass mode)');
  }

  /**
   * Handle OAuth callback
   */
  async handleOAuthCallback(token: string): Promise<void> {
    // Store token
    localStorage.setItem('token', token);
    localStorage.setItem('isAuthenticated', 'true');
    
    // Fetch user info
    try {
      const response = await fetch(`${this.apiUrl}/api/v2/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const user = await response.json();
        localStorage.setItem('user', JSON.stringify(user));
        console.log('✅ User logged in via OAuth');
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error);
    }
  }

  /**
   * Logout user
   */
  logout(): void {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    localStorage.removeItem('isAuthenticated');
    window.location.href = '/';
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return localStorage.getItem('isAuthenticated') === 'true';
  }

  /**
   * Get current user
   */
  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }

  /**
   * Get auth token
   */
  getToken(): string | null {
    return localStorage.getItem('token');
  }

  /**
   * Log current auth configuration
   */
  logAuthConfig(): void {
    console.group('🔐 Auth Configuration');
    console.log('Environment:', EnvironmentChecker.getEnvironment());
    console.log('Testing Mode:', EnvironmentChecker.isTestingMode());
    console.log('Auth Bypass:', EnvironmentChecker.shouldUseAuthBypass());
    console.log('OAuth Configured:', EnvironmentChecker.isOAuthConfigured());
    console.log('API URL:', this.apiUrl);
    console.groupEnd();
  }
}

export default new AuthService();