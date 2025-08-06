// Cookie debugging utility
export function debugCookies() {
  console.log('[COOKIE DEBUG] All cookies:', document.cookie);
  console.log('[COOKIE DEBUG] Cookie string length:', document.cookie.length);
  
  // Check if we can see any cookies at all
  if (document.cookie.length === 0) {
    console.log('[COOKIE DEBUG] ⚠️ NO COOKIES FOUND!');
    
    // Check if this is a cross-origin issue
    console.log('[COOKIE DEBUG] Current origin:', window.location.origin);
    console.log('[COOKIE DEBUG] API URL:', import.meta.env.VITE_API_URL);
    
    if (window.location.origin !== import.meta.env.VITE_API_URL) {
      console.log('[COOKIE DEBUG] ⚠️ CROSS-ORIGIN DETECTED - Cookies might not be accessible!');
    }
  }
  
  // Try to parse cookies
  const cookies = document.cookie.split(';').reduce((acc, cookie) => {
    const [key, value] = cookie.trim().split('=');
    if (key) acc[key] = value;
    return acc;
  }, {} as Record<string, string>);
  
  console.log('[COOKIE DEBUG] Parsed cookies:', cookies);
  console.log('[COOKIE DEBUG] Has access_token:', 'access_token' in cookies);
}

// Auto-run on import
debugCookies();