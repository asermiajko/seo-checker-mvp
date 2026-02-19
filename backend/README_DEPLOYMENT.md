# SEO Checker Backend — Deployment Guide

## ✅ Pre-Deployment Checklist

All deployment files are ready:

- ✅ `Procfile` — Railway process configuration
- ✅ `railway.json` — Railway build/deploy settings  
- ✅ `requirements.txt` — Python dependencies (inc. alembic)
- ✅ `.env.example` — Environment variables template
- ✅ `migrations/` — Alembic database migrations
- ✅ `alembic.ini` — Alembic configuration

---

## 🚀 Deployment to Railway

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
railway login
```

### Step 2: Create Railway Project

```bash
cd backend/
railway init
# Name: "seo-checker-backend"
```

### Step 3: Add PostgreSQL

```bash
railway add
# Select: "PostgreSQL"
```

This will automatically set `DATABASE_URL` environment variable.

### Step 4: Set Environment Variables

```bash
railway variables set ENVIRONMENT=production
```

Railway automatically provides:
- `DATABASE_URL` (from PostgreSQL addon)
- `PORT` (for web process)

### Step 5: Deploy

```bash
railway up
```

This will:
1. Install dependencies from `requirements.txt`
2. Start uvicorn on `$PORT`
3. Make the API available

### Step 6: Run Database Migrations

```bash
# Run migrations on Railway
railway run python -m alembic upgrade head
```

Or use Railway console:
```bash
railway shell
python -m alembic upgrade head
exit
```

### Step 7: Get Deployment URL

```bash
railway domain
```

Or check in Railway dashboard: Settings → Domains

---

## 🧪 Testing Deployed API

### Health Check

```bash
curl https://your-backend.railway.app/api/health
```

Expected response:
```json
{
  "status": "ok",
  "database": "connected"
}
```

### SEO Check

```bash
curl -X POST https://your-backend.railway.app/api/check \
  -H "Content-Type: application/json" \
  -d '{
    "site_url": "https://httpbin.org",
    "telegram_id": 123456789
  }'
```

Expected: 200 OK with full SEO report.

### Rate Limiting Test

```bash
# Make 6 requests quickly
for i in {1..6}; do
  curl -X POST https://your-backend.railway.app/api/check \
    -H "Content-Type: application/json" \
    -d "{\"site_url\": \"https://httpbin.org\", \"telegram_id\": 999000001}"
  echo "\n---Request $i done---\n"
done
```

Expected: First 5 succeed (200), 6th returns 429 (rate limit).

---

## 📋 Environment Variables

### Required (Auto-provided by Railway)
- `DATABASE_URL` — PostgreSQL connection string (from addon)
- `PORT` — HTTP port for uvicorn (Railway sets this)

### Optional
- `ENVIRONMENT` — Set to "production" (default: "development")

---

## 🛠 Troubleshooting

### Issue: Database Connection Failed

**Check DATABASE_URL:**
```bash
railway variables
# Look for DATABASE_URL
```

**Test connection:**
```bash
railway run python -c "from app.database import engine; print('OK')"
```

### Issue: Migration Failed

**Check migration status:**
```bash
railway run python -m alembic current
```

**Rollback if needed:**
```bash
railway run python -m alembic downgrade -1
```

**Re-apply:**
```bash
railway run python -m alembic upgrade head
```

### Issue: Port Binding Error

- Ensure `Procfile` uses `--port $PORT`
- Railway sets `PORT` automatically, don't hardcode it

### Issue: Dependencies Not Installing

**Check requirements.txt:**
```bash
cat requirements.txt
```

**Manually install on Railway:**
```bash
railway run pip install -r requirements.txt
```

---

## 📊 Monitoring

### View Logs

```bash
railway logs
```

Or check Railway dashboard → Deployments → Logs

### Check Resource Usage

Railway dashboard → Metrics:
- CPU usage
- Memory usage
- Network traffic

---

## 🔄 Updating Deployment

### Deploy New Changes

```bash
git add .
git commit -m "Update backend"
railway up
```

Railway will automatically redeploy.

### Run New Migrations

After adding new models:
```bash
# Locally: create migration
python -m alembic revision --autogenerate -m "Add new table"

# Push to Railway
git add migrations/
git commit -m "Add migration"
railway up

# Run migration on Railway
railway run python -m alembic upgrade head
```

---

## ✅ Deployment Status

**TASK-037: Railway Backend Setup** — READY

Files created:
- ✅ `Procfile`
- ✅ `railway.json`
- ✅ `.env.example`
- ✅ `migrations/versions/4cffd1d19e60_initial_schema.py`
- ✅ `RAILWAY_DEPLOYMENT.md` (instructions)
- ✅ `README_DEPLOYMENT.md` (this file)

Next: Deploy using Railway CLI or Railway dashboard.

---

**Last Updated**: 2026-02-19  
**Project**: SEO Checker MVP  
**Module**: 7 - Deployment
