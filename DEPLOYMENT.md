# SpecSharp Deployment Guide

## Current Production URLs

- **Frontend**: https://specsharp.ai (and https://www.specsharp.ai)
- **Backend API**: https://api.specsharp.ai

## OAuth Configuration

### Google OAuth Credentials
- **Client ID**: 1072123305615-n2inm0l8t62lp9n1gjb70hn2otb9b4u5.apps.googleusercontent.com
- **Client Secret**: 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

### Required Redirect URIs in Google Console
1. http://localhost:3000 (frontend local)
2. http://localhost:8001/api/v1/oauth/callback/google (backend local)
3. https://api.specsharp.ai/api/v1/oauth/callback/google (backend prod)
4. https://specsharp.ai (frontend prod)
5. https://www.specsharp.ai (frontend prod with www)

## Frontend Deployment (Vercel)

### Environment Variables
Set these in Vercel dashboard:
```
VITE_API_URL=https://api.specsharp.ai
VITE_GOOGLE_CLIENT_ID=1072123305615-n2inm0l8t62lp9n1gjb70hn2otb9b4u5.apps.googleusercontent.com
VITE_ENVIRONMENT=production
```

### Build Settings
- Framework Preset: Vite
- Build Command: `npm run build:prod`
- Output Directory: `dist`
- Root Directory: `frontend`

### Deployment Steps
1. Push changes to GitHub
2. Vercel will auto-deploy from main branch
3. Verify environment variables are set in Vercel dashboard
4. Test OAuth login flow

## Backend Deployment (Railway)

### Environment Variables
Ensure these are set in your backend deployment:
```
GOOGLE_CLIENT_ID=1072123305615-n2inm0l8t62lp9n1gjb70hn2otb9b4u5.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
FRONTEND_URL=https://specsharp.ai
DATABASE_URL=<your-database-url>
SECRET_KEY=<your-secret-key>
```

### CORS Configuration
Backend should allow origins:
- http://localhost:3000
- https://specsharp.ai
- https://www.specsharp.ai

## Testing Production

1. **OAuth Flow**:
   - Visit https://specsharp.ai
   - Click "Login" in the navigation bar
   - Click "Continue with Google"
   - Should redirect to Google, then back to app authenticated

2. **API Connection**:
   - Check browser console for any API errors
   - Verify requests go to https://api.specsharp.ai

## Troubleshooting

### OAuth Issues
- Verify redirect URIs match exactly in Google Console
- Check backend logs for OAuth errors
- Ensure CORS allows frontend domain

### API Connection Issues
- Check if backend is running
- Verify VITE_API_URL in Vercel environment variables
- Check browser console for CORS errors

## Local Development

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

## Recent Fixes Applied

1. **Environment Variables**: Migrated from NEXT_PUBLIC_* to VITE_* format
2. **TypeScript**: Re-enabled strict mode and fixed all type errors
3. **Logger**: Updated to use import.meta.env for Vite compatibility
4. **Missing Modules**: Created useLocalStorage hook and CommonSizes constants
5. **Production Build**: Configured for minified production deployment
