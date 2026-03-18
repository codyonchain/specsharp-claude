import { setAccessTokenSession } from '../session';

describe('session persistence', () => {
  beforeEach(() => {
    sessionStorage.clear();
    localStorage.clear();
  });

  it('clears authenticated project and scenario caches when establishing a new session', () => {
    sessionStorage.setItem('specsharp_projects', '[{"id":"session_proj"}]');
    sessionStorage.setItem('specsharp_scenarios', '{"session_proj":[{"id":"scenario_1"}]}');
    localStorage.setItem('specsharp_projects', '[{"id":"local_proj"}]');
    localStorage.setItem('specsharp_scenarios', '{"local_proj":[{"id":"scenario_2"}]}');
    localStorage.setItem('unrelated_key', 'keep-me');

    setAccessTokenSession('opaque-token', {
      expiresInSeconds: 3600,
      user: { id: 'user_1', email: 'user@example.com' },
    });

    expect(sessionStorage.getItem('specsharp_access_token')).toBe('opaque-token');
    expect(sessionStorage.getItem('specsharp_projects')).toBeNull();
    expect(sessionStorage.getItem('specsharp_scenarios')).toBeNull();
    expect(localStorage.getItem('specsharp_projects')).toBeNull();
    expect(localStorage.getItem('specsharp_scenarios')).toBeNull();
    expect(localStorage.getItem('unrelated_key')).toBe('keep-me');
  });
});
