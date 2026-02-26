type SessionUser = {
  id: string;
  email: string;
};

type AuthCallbackResult =
  | { ok: true; accessToken: string }
  | { ok: false; error: string };

const ACCESS_TOKEN_KEY = 'specsharp_access_token';
const EXPIRES_AT_KEY = 'specsharp_token_expires_at';
const USER_KEY = 'specsharp_user';

const LEGACY_TOKEN_KEY = 'token';
const LEGACY_AUTH_KEY = 'isAuthenticated';

const hasSessionStorage = (): boolean =>
  typeof window !== 'undefined' && typeof window.sessionStorage !== 'undefined';

const hasLocalStorage = (): boolean =>
  typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';

const storageGet = (key: string): string | null => {
  if (!hasSessionStorage()) return null;
  return window.sessionStorage.getItem(key);
};

const storageSet = (key: string, value: string): void => {
  if (!hasSessionStorage()) return;
  window.sessionStorage.setItem(key, value);
};

const storageRemove = (key: string): void => {
  if (!hasSessionStorage()) return;
  window.sessionStorage.removeItem(key);
};

const clearLegacyLocalAuthStorage = (): void => {
  if (!hasLocalStorage()) return;
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem(EXPIRES_AT_KEY);
  window.localStorage.removeItem(USER_KEY);
  window.localStorage.removeItem(LEGACY_TOKEN_KEY);
  window.localStorage.removeItem(LEGACY_AUTH_KEY);
};

const migrateLegacyLocalStorageSession = (): void => {
  if (!hasSessionStorage() || !hasLocalStorage()) return;
  if (window.sessionStorage.getItem(ACCESS_TOKEN_KEY)) {
    return;
  }

  const legacyToken =
    window.localStorage.getItem(ACCESS_TOKEN_KEY) ||
    window.localStorage.getItem(LEGACY_TOKEN_KEY);
  if (!legacyToken) {
    return;
  }

  window.sessionStorage.setItem(ACCESS_TOKEN_KEY, legacyToken);
  const legacyExpiry = window.localStorage.getItem(EXPIRES_AT_KEY);
  if (legacyExpiry) {
    window.sessionStorage.setItem(EXPIRES_AT_KEY, legacyExpiry);
  }
  const legacyUser = window.localStorage.getItem(USER_KEY);
  if (legacyUser) {
    window.sessionStorage.setItem(USER_KEY, legacyUser);
  }

  clearLegacyLocalAuthStorage();
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
  expires_in?: number;
  user?: SessionUser;
}) => {
  const payload = parseJwtPayload(session.access_token);
  const exp = typeof payload?.exp === 'number'
    ? payload.exp
    : nowEpoch() + (session.expires_in || 3600);

  storageSet(ACCESS_TOKEN_KEY, session.access_token);
  storageSet(EXPIRES_AT_KEY, String(exp));

  if (session.user) {
    storageSet(USER_KEY, JSON.stringify(session.user));
  }

  clearLegacyLocalAuthStorage();
};

export const clearAuthSession = () => {
  migrateLegacyLocalStorageSession();
  storageRemove(ACCESS_TOKEN_KEY);
  storageRemove(EXPIRES_AT_KEY);
  storageRemove(USER_KEY);
  storageRemove(LEGACY_TOKEN_KEY);
  storageRemove(LEGACY_AUTH_KEY);
  clearLegacyLocalAuthStorage();
};

const readSession = () => {
  migrateLegacyLocalStorageSession();
  return {
    accessToken: storageGet(ACCESS_TOKEN_KEY),
    expiresAt: Number(storageGet(EXPIRES_AT_KEY) || '0'),
  };
};

export const isAuthenticatedSession = (): boolean => {
  const { accessToken, expiresAt } = readSession();
  if (!accessToken) return false;
  return expiresAt > nowEpoch() + 30;
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
  const expiresIn = Number(params.get('expires_in') || '3600');

  if (!accessToken) {
    return { ok: false, error: 'No access token found in callback URL' };
  }

  persistSession({
    access_token: accessToken,
    expires_in: expiresIn,
  });
  await fetchSupabaseUser(accessToken).catch(() => null);
  return { ok: true, accessToken };
};

export const getValidAccessToken = async (): Promise<string | null> => {
  const { accessToken, expiresAt } = readSession();

  if (!accessToken) return null;
  if (expiresAt <= nowEpoch() + 30) {
    clearAuthSession();
    return null;
  }
  return accessToken;
};

export const setAccessTokenSession = (
  accessToken: string,
  options?: { expiresInSeconds?: number; user?: SessionUser }
): void => {
  persistSession({
    access_token: accessToken,
    expires_in: options?.expiresInSeconds,
    user: options?.user,
  });
};
