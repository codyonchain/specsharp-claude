import authService from '../authService';

describe('authService.logout', () => {
  const originalLocation = window.location;

  beforeEach(() => {
    sessionStorage.clear();
    localStorage.clear();
  });

  afterEach(() => {
    Object.defineProperty(window, 'location', {
      configurable: true,
      value: originalLocation,
    });
  });

  it('clears V2 auth/session artifacts and fallback caches, then hard-redirects to /login', () => {
    sessionStorage.setItem('specsharp_access_token', 'token');
    sessionStorage.setItem('specsharp_token_expires_at', '123456');
    sessionStorage.setItem('specsharp_user', JSON.stringify({ id: 'user_1', email: 'user@example.com' }));
    sessionStorage.setItem('specsharp_projects', '[{"id":"proj_1"}]');
    sessionStorage.setItem('specsharp_scenarios', '{"proj_1":[{"id":"scenario_1"}]}');
    localStorage.setItem('token', 'legacy-token');
    localStorage.setItem('isAuthenticated', 'true');
    localStorage.setItem('specsharp_projects', '[{"id":"proj_2"}]');
    localStorage.setItem('specsharp_scenarios', '{"proj_2":[{"id":"scenario_2"}]}');
    localStorage.setItem('unrelated_key', 'keep-me');

    const assign = vi.fn();
    Object.defineProperty(window, 'location', {
      configurable: true,
      value: {
        ...originalLocation,
        assign,
      },
    });

    authService.logout();

    expect(sessionStorage.getItem('specsharp_access_token')).toBeNull();
    expect(sessionStorage.getItem('specsharp_token_expires_at')).toBeNull();
    expect(sessionStorage.getItem('specsharp_user')).toBeNull();
    expect(sessionStorage.getItem('specsharp_projects')).toBeNull();
    expect(sessionStorage.getItem('specsharp_scenarios')).toBeNull();
    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('isAuthenticated')).toBeNull();
    expect(localStorage.getItem('specsharp_projects')).toBeNull();
    expect(localStorage.getItem('specsharp_scenarios')).toBeNull();
    expect(localStorage.getItem('unrelated_key')).toBe('keep-me');
    expect(assign).toHaveBeenCalledWith('/login');
  });
});
