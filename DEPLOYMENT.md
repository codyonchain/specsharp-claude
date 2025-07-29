# SpecSharp Production Deployment Guide

## Pre-Deployment Checklist

### 1. Environment Variables
- [ ] Copy `.env.production.example` files and fill in real values
- [ ] Set strong SECRET_KEY (use: `openssl rand -hex 32`)
- [ ] Update OAuth redirect URLs in Google Console
- [ ] Set production database URL

### 2. Security Checks
- [ ] Run `npm run lint` in frontend
- [ ] Run `black .` and `mypy .` in backend
- [ ] All console.log statements removed
- [ ] API URLs use environment variables
- [ ] Error messages are user-friendly

### 3. Testing
- [ ] Run frontend tests: `npm test`
- [ ] Run backend tests: `pytest`
- [ ] Test with production environment locally
- [ ] Test error scenarios
- [ ] Test authentication flows

## Deployment Steps

### Frontend (Vercel)
```bash
cd frontend
npm run build
vercel --prod
```

### Backend (Railway/Render/AWS)
```bash
cd backend
# Ensure requirements.txt is up to date
pip freeze > requirements.txt

# Deploy with your platform's CLI
# Example for Railway:
railway up
```

### Database Migration
```bash
cd backend
alembic upgrade head
```

## Post-Deployment

1. **Verify Services**
   - [ ] Frontend loads correctly
   - [ ] API health check passes
   - [ ] Authentication works
   - [ ] Can create/view projects

2. **Monitor Logs**
   - Check for any errors in first hour
   - Monitor response times
   - Check for failed requests

3. **Security Headers**
   - Verify CORS is properly configured
   - Check CSP headers
   - Ensure HTTPS is enforced

## Rollback Plan

If issues occur:
1. Revert to previous deployment
2. Check logs for root cause
3. Fix in staging environment
4. Re-deploy when verified

## Support

For deployment issues:
- Check logs first
- Review this guide
- Contact team if needed
