# Railway Deployment Instructions

## Prerequisites
1. Railway CLI installed: `npm install -g @railway/cli`
2. Railway account: https://railway.app
3. PostgreSQL ready on Railway

## Deployment Steps

### 1. Install Railway CLI
```bash
npm install -g @railway/cli
railway login
```

### 2. Initialize Railway Project
```bash
cd backend/
railway init
# Select "Create a new project"
# Name it "seo-checker-backend"
```

### 3. Add PostgreSQL
```bash
railway add
# Select "PostgreSQL"
```

### 4. Set Environment Variables
```bash
# Railway auto-provides DATABASE_URL from PostgreSQL addon
# Add these manually:
railway variables set ENVIRONMENT=production
```

### 5. Deploy Backend
```bash
railway up
```

### 6. Run Database Migrations
```bash
# Option 1: Run migrations on Railway
railway run alembic upgrade head

# Option 2: Use Railway console
railway shell
alembic upgrade head
```

### 7. Get Deployment URL
```bash
railway domain
# Or check Railway dashboard
```

### 8. Test Deployed API
```bash
# Health check
curl https://your-backend.railway.app/api/health

# SEO check
curl -X POST https://your-backend.railway.app/api/check \
  -H "Content-Type: application/json" \
  -d '{"site_url": "https://httpbin.org", "telegram_id": 123456789}'
```

---

## Environment Variables Required

- `DATABASE_URL` — Auto-provided by Railway PostgreSQL addon
- `ENVIRONMENT` — Set to "production"
- `PORT` — Auto-provided by Railway

---

## Files Created for Deployment

- ✅ `Procfile` — Railway process configuration
- ✅ `railway.json` — Railway build/deploy settings
- ✅ `requirements.txt` — Python dependencies (already exists)

---

## Troubleshooting

### Database Connection Issues
```bash
# Check DATABASE_URL
railway variables

# Test connection
railway run python -c "from app.database import engine; print('OK')"
```

### Port Binding Issues
- Ensure `--port $PORT` in Procfile
- Railway automatically sets PORT environment variable

### Migration Failures
```bash
# Check current migration status
railway run alembic current

# Rollback if needed
railway run alembic downgrade -1

# Re-apply
railway run alembic upgrade head
```

---

## Next Steps After TASK-037

1. **TASK-038**: Deploy Telegram bot to Railway
2. **TASK-039**: Set up Alembic migrations
3. **TASK-040**: Integration testing (bot → API → DB)

---

**Status**: Ready for deployment 🚀
