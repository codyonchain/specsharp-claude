# SpecSharp Production Deployment Checklist

## ✅ Database Setup (Supabase)
- [x] Production database configured: `postgresql://postgres:****@db.iniumggvzvtlmganesxv.supabase.co:5432/postgres`
- [ ] Run database migrations: `cd backend && alembic upgrade head`
- [ ] Verify database connection: `cd backend && python -c "from app.db.database import engine; print('Connected!' if engine else 'Failed')"`

## 🔐 Security Configuration
- [x] Generated secure SECRET_KEY
- [x] Generated secure SESSION_SECRET_KEY
- [ ] Update Google OAuth credentials:
  - [ ] Add production redirect URIs in Google Console
  - [ ] Get production GOOGLE_CLIENT_SECRET
- [ ] Update FRONTEND_URL with actual domain
- [ ] Configure CORS origins in `backend/app/core/config.py`

## 🚀 Backend Deployment
- [ ] Install production dependencies: `pip install -r requirements.txt`
- [ ] Set environment: `export ENVIRONMENT=production`
- [ ] Use production env file: `cp .env.production .env`
- [ ] Test with production settings locally
- [ ] Deploy to hosting platform (Railway/Render/AWS)

## 🎨 Frontend Deployment
- [ ] Update API URL in `frontend/.env.production`:
  ```
  NEXT_PUBLIC_API_URL=https://api.specsharp.com
  NEXT_PUBLIC_ENVIRONMENT=production
  ```
- [ ] Build production bundle: `npm run build`
- [ ] Test production build: `npm run preview`
- [ ] Deploy to Vercel/Netlify

## 📋 Final Checks
- [ ] SSL certificates configured
- [ ] Domain DNS configured
- [ ] Health check endpoint working
- [ ] Authentication flow tested
- [ ] Project creation/viewing tested
- [ ] Error logging configured
- [ ] Monitoring setup (optional)

## 🔧 Production Commands

### Backend (Railway example):
```bash
# Deploy
railway up

# View logs
railway logs

# Run migrations
railway run alembic upgrade head
```

### Frontend (Vercel example):
```bash
# Deploy
vercel --prod

# Preview
vercel
```

## ⚠️ Important Notes
1. **Never commit .env.production to git!**
2. Update OAuth redirect URIs for production domain
3. Consider using managed Redis (Redis Cloud, Upstash)
4. Set up database backups in Supabase
5. Enable Row Level Security (RLS) in Supabase if needed