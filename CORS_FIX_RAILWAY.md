# CORS Fix for Railway Deployment

## The Problem
The frontend at https://specsharp.ai can't make API calls due to CORS preflight failures.

## The Solution

### In Railway Dashboard:

1. **Set Environment Variables:**
   ```
   ENVIRONMENT=production
   FRONTEND_URL=https://specsharp.ai
   CORS_ORIGINS=["https://specsharp.ai", "https://www.specsharp.ai"]
   ```
   
   Or as comma-separated:
   ```
   CORS_ORIGINS=https://specsharp.ai,https://www.specsharp.ai
   ```

2. **Verify Configuration:**
   - Visit: `https://[your-railway-url]/health`
   - Check that `cors_origins` includes your frontend URLs
   - Check that `environment` is "production"

3. **Restart/Redeploy the Backend**
   - Railway should auto-redeploy when env vars change
   - If not, manually trigger a redeploy

## Testing CORS

1. Open browser console on https://specsharp.ai
2. Run:
   ```javascript
   fetch('https://[your-railway-url]/health')
     .then(r => r.json())
     .then(console.log)
     .catch(console.error)
   ```

3. You should see the health check response, not a CORS error

## What Changed

The backend now:
- Reads CORS origins from environment variables
- Logs CORS configuration on startup
- Includes production URLs by default
- Has a /health endpoint that shows current CORS configuration

## Important Notes

- The wildcard `*` in CORS origins doesn't work for credentialed requests
- Each exact origin must be listed
- The backend must be restarted after environment variable changes