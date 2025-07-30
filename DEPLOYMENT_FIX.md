# Deployment Fix Instructions

## The Issue
The frontend (deployed on Vercel) cannot connect to the backend API because:
1. The frontend is trying to reach `https://api.specsharp.ai` which doesn't exist
2. Your backend is deployed on Railway with a different URL

## How to Fix

### 1. Update Vercel Environment Variables
In your Vercel dashboard for the frontend:
1. Go to Settings → Environment Variables
2. Add/Update: `VITE_API_URL` = `[YOUR RAILWAY BACKEND URL]`
   - Example: `https://specsharp-backend.railway.app`
   - This should be the URL where your Railway backend is accessible

### 2. Update Railway Environment Variables (if needed)
In your Railway dashboard for the backend:
1. Ensure these environment variables are set:
   - `ENVIRONMENT` = `production`
   - `FRONTEND_URL` = `https://specsharp.ai`
   - `CORS_ORIGINS` = `["https://specsharp.ai", "https://www.specsharp.ai", "https://specsharp.vercel.app"]`

### 3. Verify Backend is Running
1. Visit your Railway backend URL directly (e.g., `https://your-backend.railway.app/docs`)
2. You should see the FastAPI documentation page
3. If not, check Railway logs for errors

### 4. Redeploy
1. After updating environment variables, redeploy both services:
   - Vercel: Will auto-redeploy when env vars are updated
   - Railway: May need manual redeploy

## Quick Test
Once deployed, test the API connection:
1. Open browser console on https://specsharp.ai
2. Run: `fetch('[YOUR_RAILWAY_URL]/api/v1/health').then(r => r.json()).then(console.log)`
3. You should see a response, not a CORS error

## Note
The backend code has been updated to include proper CORS origins for production.