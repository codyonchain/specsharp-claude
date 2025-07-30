# OAuth Debug Guide for SpecSharp

## Current Issue
OAuth login is failing with `redirect_uri_mismatch` error when clicking "Sign in with Google" from https://specsharp.ai

## OAuth Flow
1. User clicks "Login" → navigates to `/login` page
2. User clicks "Continue with Google" → redirects to backend OAuth endpoint
3. Backend endpoint: `https://api.specsharp.ai/api/v1/oauth/login/google`
4. Backend should redirect to Google with correct parameters
5. Google redirects back to: `https://api.specsharp.ai/api/v1/oauth/callback/google`
6. Backend processes callback and redirects to frontend with token

## Required Google Console Configuration

### Authorized JavaScript Origins
Add ALL of these:
- https://specsharp.ai
- https://www.specsharp.ai
- http://localhost:3000
- https://api.specsharp.ai

### Authorized Redirect URIs
Add EXACTLY these (case-sensitive):
- https://api.specsharp.ai/api/v1/oauth/callback/google
- http://localhost:8001/api/v1/oauth/callback/google

## Backend Requirements

The backend OAuth implementation must:

1. **Construct the correct redirect_uri**:
   ```python
   redirect_uri = "https://api.specsharp.ai/api/v1/oauth/callback/google"
   ```

2. **Environment variables needed**:
   ```
   GOOGLE_CLIENT_ID=1072123305615-n2inm0l8t62lp9n1gjb70hn2otb9b4u5.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=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
   FRONTEND_URL=https://specsharp.ai
   ```

3. **CORS configuration must allow**:
   - https://specsharp.ai
   - https://www.specsharp.ai

## Frontend Configuration

1. **Environment Variables (in Vercel)**:
   ```
   VITE_API_URL=https://api.specsharp.ai
   VITE_GOOGLE_CLIENT_ID=1072123305615-n2inm0l8t62lp9n1gjb70hn2otb9b4u5.apps.googleusercontent.com
   VITE_ENVIRONMENT=production
   ```

2. **Login Component** (already correct):
   - Uses `import.meta.env.VITE_API_URL` for API URL
   - Redirects to `/api/v1/oauth/login/google`

## Debugging Steps

1. **Check Browser Network Tab**:
   - Click "Continue with Google"
   - Look at the redirect URL in network tab
   - Check the `redirect_uri` parameter in the Google OAuth URL
   - It should be exactly: `https://api.specsharp.ai/api/v1/oauth/callback/google`

2. **Common Issues**:
   - Wrong protocol (http vs https)
   - Trailing slashes
   - Wrong domain (using old Railway URL)
   - Case sensitivity
   - URL encoding issues

3. **Backend OAuth Endpoint Check**:
   The backend's `/api/v1/oauth/login/google` endpoint should construct the Google OAuth URL like:
   ```
   https://accounts.google.com/o/oauth2/v2/auth?
   client_id=1072123305615-n2inm0l8t62lp9n1gjb70hn2otb9b4u5.apps.googleusercontent.com&
   redirect_uri=https://api.specsharp.ai/api/v1/oauth/callback/google&
   response_type=code&
   scope=openid email profile&
   access_type=offline
   ```

## Quick Fix Checklist

- [ ] Update Vercel environment variable: `VITE_API_URL=https://api.specsharp.ai`
- [ ] Ensure backend uses correct redirect_uri: `https://api.specsharp.ai/api/v1/oauth/callback/google`
- [ ] Add all URLs to Google Console exactly as shown above
- [ ] Backend CORS allows `https://specsharp.ai` and `https://www.specsharp.ai`
- [ ] Backend environment has correct `FRONTEND_URL=https://specsharp.ai`

## Testing

After making changes:
1. Clear browser cache/cookies
2. Visit https://specsharp.ai
3. Click "Login" in navigation
4. Click "Continue with Google"
5. Should see Google login page
6. After login, should redirect back to SpecSharp authenticated