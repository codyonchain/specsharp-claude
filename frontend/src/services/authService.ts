import {
  clearAuthSession,
  getStoredUser,
  getValidAccessToken,
  isAuthenticatedSession,
  startGoogleSignIn,
} from '../v2/auth/session';

interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
}

class AuthService {
  async login(): Promise<void> {
    startGoogleSignIn();
  }

  logout(): void {
    clearAuthSession();
    window.location.href = '/login';
  }

  isAuthenticated(): boolean {
    return isAuthenticatedSession();
  }

  async getToken(): Promise<string | null> {
    return getValidAccessToken();
  }

  getUser(): User | null {
    const user = getStoredUser();
    if (!user) return null;
    return {
      id: user.id,
      email: user.email,
      name: user.email,
    };
  }
}

export default new AuthService();
