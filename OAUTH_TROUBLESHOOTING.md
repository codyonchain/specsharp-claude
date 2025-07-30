# OAuth Troubleshooting Guide - SpecSharp

## Debug Features Added

### 1. Console Logging in Login Component
When you click "Continue with Google", check the browser console for:
```
=== OAuth Debug Information ===
Environment: production
API URL from env: https://api.specsharp.ai
Fallback API URL: http://localhost:8001
Final API URL being used: https://api.specsharp.ai
OAuth endpoint: /api/v1/oauth/login/google
Full OAuth URL: https://api.specsharp.ai/api/v1/oauth/login/google
Window location before redirect: https://specsharp.ai/login
==============================
```

### 2. OAuth Debug Panel (Development Only)
In development mode, a debug panel appears in the bottom right showing:
- Current environment variables
- Last OAuth attempt details
- Expected OAuth flow
- URL parameters

### 3. Session Storage Debug Info
OAuth attempts are stored in sessionStorage. Check it with:
```javascript
JSON.parse(sessionStorage.getItem('oauth_debug'))
```

## Verification Steps

### Step 1: Verify Frontend Environment
1. Open https://specsharp.ai
2. Open browser DevTools Console
3. Run: `console.log(import.meta.env.VITE_API_URL)`
4. Should output: `https://api.specsharp.ai`

### Step 2: Test OAuth Flow
1. Navigate to https://specsharp.ai/login
2. Open Network tab in DevTools
3. Click "Continue with Google"
4. Check console for debug output
5. In Network tab, look for redirect to `api.specsharp.ai/api/v1/oauth/login/google`

### Step 3: Check Backend Redirect
The backend should redirect to Google with these exact parameters:
```
https://accounts.google.com/o/oauth2/v2/auth?
  client_id=1072123305615-n2inm0l8t62lp9n1gjb70hn2otb9b4u5.apps.googleusercontent.com&
  redirect_uri=https://api.specsharp.ai/api/v1/oauth/callback/google&
  response_type=code&
  scope=openid email profile&
  access_type=offline
```

### Step 4: Verify Google Console Settings

**CRITICAL**: The redirect_uri must match EXACTLY in Google Console.

In Google Cloud Console > APIs & Services > Credentials > OAuth 2.0 Client IDs:

**Authorized JavaScript origins** (add all):
```
https://specsharp.ai
https://www.specsharp.ai
https://api.specsharp.ai
http://localhost:3000
```

**Authorized redirect URIs** (add exactly):
```
https://api.specsharp.ai/api/v1/oauth/callback/google
http://localhost:8001/api/v1/oauth/callback/google
```

## Common Issues and Solutions

### Issue: redirect_uri_mismatch

**Cause 1**: Backend is not using the correct redirect_uri
- **Solution**: Backend must use exactly `https://api.specsharp.ai/api/v1/oauth/callback/google`

**Cause 2**: URL encoding issues
- **Solution**: Ensure redirect_uri is properly URL encoded

**Cause 3**: Protocol mismatch (http vs https)
- **Solution**: Always use https in production

**Cause 4**: Trailing slashes
- **Solution**: Remove any trailing slashes from URLs

### Issue: Frontend not getting API URL

**Symptoms**:
- Console shows API URL as undefined
- OAuth redirects to localhost

**Solution**:
1. In Vercel dashboard, set: `VITE_API_URL=https://api.specsharp.ai`
2. Redeploy the application
3. Clear browser cache

### Issue: CORS errors

**Solution**: Backend must allow these origins:
```python
ALLOWED_ORIGINS = [
    "https://specsharp.ai",
    "https://www.specsharp.ai",
    "http://localhost:3000"
]
```

## Backend Requirements

The backend OAuth handler at `/api/v1/oauth/login/google` must:

```python
@router.get("/oauth/login/google")
async def google_login():
    # CRITICAL: Use exact redirect_uri
    redirect_uri = "https://api.specsharp.ai/api/v1/oauth/callback/google"
    
    # For local development
    if os.getenv("ENVIRONMENT") == "development":
        redirect_uri = "http://localhost:8001/api/v1/oauth/callback/google"
    
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        "response_type=code&"
        "scope=openid email profile&"
        "access_type=offline"
    )
    
    return RedirectResponse(google_auth_url)
```

## Testing Checklist

- [ ] Frontend console shows correct API URL
- [ ] Network tab shows redirect to `api.specsharp.ai`
- [ ] No redirect_uri parameter sent from frontend
- [ ] Backend redirects to Google with correct redirect_uri
- [ ] Google Console has exact redirect URIs added
- [ ] CORS is configured correctly
- [ ] After Google auth, redirects back to frontend with token

## Emergency Fixes

If still getting redirect_uri_mismatch:

1. **Double-check Google Console** - Copy/paste these exactly:
   ```
   https://api.specsharp.ai/api/v1/oauth/callback/google
   ```

2. **Check backend logs** - The exact redirect_uri being used

3. **Use curl to test backend**:
   ```bash
   curl -I https://api.specsharp.ai/api/v1/oauth/login/google
   ```
   Check the Location header for the redirect_uri parameter

4. **Clear Google OAuth cache** - Sometimes Google caches old settings