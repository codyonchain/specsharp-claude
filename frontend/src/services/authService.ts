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

  async login(): Promise<void> {
    if (EnvironmentChecker.shouldUseAuthBypass()) {
      console.log('🔓 Using auth bypass (test mode)');
      await this.loginWithBypass();
      return;
    }

    console.log('🔐 Using Google OAuth');
    await this.loginWithOAuth();
  }

  private async loginWithBypass(): Promise<void> {
    try {
      const response = await fetch(`${this.apiUrl}/api/v2/oauth/login/google`, {
        method: 'GET',
        credentials: 'include',
      });

      if (response.redirected || response.status === 302 || response.status === 307) {
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

      this.setTestUser();
      window.location.href = '/dashboard';
    } catch (error) {
      console.error('Bypass login error:', error);
      this.setTestUser();
      window.location.href = '/dashboard';
    }
  }

  private async loginWithOAuth(): Promise<void> {
    window.location.href = `${this.apiUrl}/api/v2/oauth/login/google`;
  }

  private setTestUser(token?: string): void {
    const testUser: User = {
      id: 'test-user-123',
      email: 'test@specsharp.com',
      name: 'Test User',
    };

    localStorage.setItem('user', JSON.stringify(testUser));
    localStorage.setItem('isAuthenticated', 'true');
    localStorage.setItem('token', token || 'test-token-bypass-mode');

    console.log('✅ Test user logged in (bypass mode)');
  }

  async handleOAuthCallback(token: string): Promise<void> {
    localStorage.setItem('token', token);
    localStorage.setItem('isAuthenticated', 'true');
    console.log('✅ Token stored from OAuth callback');
    window.location.href = '/dashboard';
  }

  logout(): void {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    localStorage.removeItem('isAuthenticated');
    window.location.href = '/login';
  }

  isAuthenticated(): boolean {
    return localStorage.getItem('isAuthenticated') === 'true';
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }

  getUser(): User | null {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }
}

export default new AuthService();
