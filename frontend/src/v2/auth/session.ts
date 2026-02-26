type SessionUser = {
  id: string;
  email: string;
};

type AuthCallbackResult =
  | { ok: true; accessToken: string }
  | { ok: false; error: string };

const ACCESS_TOKEN_KEY = 'specsharp_access_token';
const REFRESH_TOKEN_KEY = 'specsharp_refresh_token';
const EXPIRES_AT_KEY = 'specsharp_token_expires_at';
const USER_KEY = 'specsharp_user';

const LEGACY_TOKEN_KEY = 'token';
const LEGACY_AUTH_KEY = 'isAuthenticated';

const hasLocalStorage = (): boolean =>
  typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';

const storageGet = (key: string): string | null => {
  if (!hasLocalStorage()) return null;
  return window.localStorage.getItem(key);
};

const storageSet = (key: string, value: string): void => {
  if (!hasLocalStorage()) return;
  window.localStorage.setItem(key, value);
};

const storageRemove = (key: string): void => {
  if (!hasLocalStorage()) return;
  window.localStorage.removeItem(key);
};

const getSupabaseUrl = (): string =>
  (import.meta.env.VITE_SUPABASE_URL || '').replace(/\/+$/, '');

const getSupabaseAnonKey = (): string => import.meta.env.VITE_SUPABASE_ANON_KEY || '';

const nowEpoch = (): number => Math.floor(Date.now() / 1000);

const parseJwtPayload = (token: string): Record<string, any> | null => {
  try {
    const [, payload] = token.split('.');
    if (!payload) return null;
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const normalized = decodeURIComponent(
      atob(base64)
        .split('')
        .map((char) => `%${`00${char.charCodeAt(0).toString(16)}`.slice(-2)}`)
        .join('')
    );
    return JSON.parse(normalized);
  } catch {
    return null;
  }
};

const persistSession = (session: {
  access_token: string;
  refresh_token?: string;
  expires_in?: number;
  user?: SessionUser;
}) => {
  const payload = parseJwtPayload(session.access_token);
  const exp = typeof payload?.exp === 'number'
    ? payload.exp
    : nowEpoch() + (session.expires_in || 3600);

  storageSet(ACCESS_TOKEN_KEY, session.access_token);
  storageSet(LEGACY_TOKEN_KEY, session.access_token);
  storageSet(LEGACY_AUTH_KEY, 'true');
  storageSet(EXPIRES_AT_KEY, String(exp));

  if (session.refresh_token) {
    storageSet(REFRESH_TOKEN_KEY, session.refresh_token);
  }
  if (session.user) {
    storageSet(USER_KEY, JSON.stringify(session.user));
  }
};

export const clearAuthSession = () => {
  storageRemove(ACCESS_TOKEN_KEY);
  storageRemove(REFRESH_TOKEN_KEY);
  storageRemove(EXPIRES_AT_KEY);
  storageRemove(USER_KEY);
  storageRemove(LEGACY_TOKEN_KEY);
  storageRemove(LEGACY_AUTH_KEY);
};

const readSession = () => ({
  accessToken: storageGet(ACCESS_TOKEN_KEY) || storageGet(LEGACY_TOKEN_KEY),
  refreshToken: storageGet(REFRESH_TOKEN_KEY),
  expiresAt: Number(storageGet(EXPIRES_AT_KEY) || '0'),
});

export const isAuthenticatedSession = (): boolean => {
  const { accessToken, expiresAt, refreshToken } = readSession();
  if (!accessToken) return false;
  if (expiresAt > nowEpoch() + 30) return true;
  return Boolean(refreshToken);
};

export const getStoredUser = (): SessionUser | null => {
  const raw = storageGet(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as SessionUser;
  } catch {
    return null;
  }
};

const fetchSupabaseUser = async (accessToken: string): Promise<SessionUser | null> => {
  const supabaseUrl = getSupabaseUrl();
  const anonKey = getSupabaseAnonKey();
  if (!supabaseUrl || !anonKey) return null;

  const response = await fetch(`${supabaseUrl}/auth/v1/user`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${accessToken}`,
      apikey: anonKey,
    },
  });
  if (!response.ok) return null;

  const data = await response.json();
  if (!data?.id || !data?.email) return null;

  const user = { id: data.id as string, email: data.email as string };
  storageSet(USER_KEY, JSON.stringify(user));
  return user;
};

export const startGoogleSignIn = () => {
  if (typeof window === 'undefined') {
    throw new Error('Google sign-in requires a browser context');
  }
  const supabaseUrl = getSupabaseUrl();
  if (!supabaseUrl) {
    throw new Error('Supabase URL is not configured');
  }
  const redirectTo = `${window.location.origin}/auth/callback`;
  const authUrl = `${supabaseUrl}/auth/v1/authorize?provider=google&redirect_to=${encodeURIComponent(redirectTo)}`;
  window.location.assign(authUrl);
};

export const handleAuthCallback = async (): Promise<AuthCallbackResult> => {
  if (typeof window === 'undefined') {
    return { ok: false, error: 'Auth callback requires a browser context' };
  }
  const hash = window.location.hash.startsWith('#')
    ? window.location.hash.slice(1)
    : window.location.hash;
  const params = new URLSearchParams(hash);

  const error = params.get('error_description') || params.get('error');
  if (error) {
    return { ok: false, error };
  }

  const accessToken = params.get('access_token');
  const refreshToken = params.get('refresh_token');
  const expiresIn = Number(params.get('expires_in') || '3600');

  if (!accessToken) {
    return { ok: false, error: 'No access token found in callback URL' };
  }

  persistSession({
    access_token: accessToken,
    refresh_token: refreshToken || undefined,
    expires_in: expiresIn,
  });
  await fetchSupabaseUser(accessToken).catch(() => null);
  return { ok: true, accessToken };
};

export const getValidAccessToken = async (): Promise<string | null> => {
  const supabaseUrl = getSupabaseUrl();
  const anonKey = getSupabaseAnonKey();
  const { accessToken, refreshToken, expiresAt } = readSession();

  if (!accessToken) return null;

  if (expiresAt > nowEpoch() + 30) {
    return accessToken;
  }

  if (!refreshToken || !supabaseUrl || !anonKey) {
    clearAuthSession();
    return null;
  }

  try {
    const response = await fetch(`${supabaseUrl}/auth/v1/token?grant_type=refresh_token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        apikey: anonKey,
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!response.ok) {
      clearAuthSession();
      return null;
    }

    const data = await response.json();
    if (!data?.access_token) {
      clearAuthSession();
      return null;
    }

    persistSession({
      access_token: data.access_token,
      refresh_token: data.refresh_token || refreshToken,
      expires_in: data.expires_in,
    });
    await fetchSupabaseUser(data.access_token).catch(() => null);
    return data.access_token as string;
  } catch {
    clearAuthSession();
    return null;
  }
};
