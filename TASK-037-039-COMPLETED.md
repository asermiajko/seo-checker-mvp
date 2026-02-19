# TASK-037 & TASK-039: Railway Backend Setup & Migrations — COMPLETED ✅

**Date**: 2026-02-19  
**Tasks**: TASK-037 (Railway Backend Setup) + TASK-039 (Database Migrations)  
**Status**: COMPLETE (Preparation Phase)  
**Duration**: ~1 hour

---

## ✅ What Was Completed

### TASK-037: Railway Backend Setup

**Files Created**:
1. ✅ `backend/Procfile` — Web process configuration for Railway
2. ✅ `backend/railway.json` — Railway build/deploy settings (NIXPACKS)
3. ✅ `backend/.env.example` — Environment variables template
4. ✅ `backend/RAILWAY_DEPLOYMENT.md` — Quick deployment instructions
5. ✅ `backend/README_DEPLOYMENT.md` — Comprehensive deployment guide

**Configuration**:
- Web process: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Build system: NIXPACKS (auto-detects Python)
- Restart policy: ON_FAILURE (max 10 retries)
- Dependencies: All listed in `requirements.txt`

### TASK-039: Database Migrations

**Files Created/Updated**:
1. ✅ `backend/alembic.ini` — Alembic configuration
2. ✅ `backend/migrations/env.py` — Migration environment (configured for Railway)
3. ✅ `backend/migrations/versions/4cffd1d19e60_initial_schema.py` — Initial DB schema migration
4. ✅ `backend/requirements.txt` — Added `alembic==1.16.5`

**Migration Details**:
- **Tables Created**:
  - `check_requests` — User SEO check requests
  - `check_results` — SEO check results with reports
- **Foreign Keys**: `check_results.check_request_id` → `check_requests.id` (CASCADE)
- **Indexes**: `id`, `telegram_id`
- **JSON Columns**: `report_data`, `detailed_checks`

**Alembic Configuration**:
- Reads `DATABASE_URL` from environment (Railway auto-provides)
- Imports `Base` metadata from `app.database`
- Supports both online/offline migrations

---

## 📁 Project Structure (Updated)

```
backend/
├── Procfile                   ⭐ NEW — Railway web process
├── railway.json               ⭐ NEW — Railway config
├── .env.example               ⭐ NEW — Env vars template
├── alembic.ini                ⭐ NEW — Alembic config
├── RAILWAY_DEPLOYMENT.md      ⭐ NEW — Quick deploy guide
├── README_DEPLOYMENT.md       ⭐ NEW — Full deploy guide
├── migrations/                ⭐ NEW — Alembic migrations
│   ├── env.py                 ⭐ Configured for Railway
│   ├── versions/
│   │   └── 4cffd1d19e60_initial_schema.py  ⭐ Initial migration
├── app/
│   ├── checks/
│   ├── routes/
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── main.py
├── tests/
└── requirements.txt           ⭐ Updated (added alembic)
```

---

## 🚀 Deployment Instructions (For Next Session)

### Option 1: Railway CLI (Recommended)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli
railway login

# 2. Initialize project
cd backend/
railway init

# 3. Add PostgreSQL
railway add  # Select "PostgreSQL"

# 4. Set environment variables
railway variables set ENVIRONMENT=production

# 5. Deploy
railway up

# 6. Run migrations
railway run python -m alembic upgrade head

# 7. Test
railway domain
curl https://your-backend.railway.app/api/health
```

### Option 2: Railway Dashboard (Manual)

1. Go to https://railway.app/new
2. Create new project from GitHub repo
3. Add PostgreSQL service
4. Set environment variables in Settings
5. Deploy automatically on git push
6. Run migrations via Railway console

---

## 📊 Migration Schema

### Table: `check_requests`
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | Primary Key, Index |
| telegram_id | BigInteger | Not Null, Index |
| username | String(255) | Nullable |
| site_url | String(500) | Not Null |
| status | String(50) | Default: 'pending' |
| created_at | TIMESTAMP | Default: now() |
| updated_at | TIMESTAMP | Default: now(), on update: now() |

### Table: `check_results`
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | Primary Key, Index |
| check_request_id | Integer | Foreign Key → check_requests.id (CASCADE) |
| score | DECIMAL(3,1) | Not Null |
| problems_critical | Integer | Default: 0 |
| problems_important | Integer | Default: 0 |
| checks_ok | Integer | Default: 0 |
| report_data | JSON | Not Null |
| detailed_checks | JSON | Not Null |
| processing_time_sec | Integer | Nullable |
| created_at | TIMESTAMP | Default: now() |

---

## 🧪 Testing Locally (Optional)

### Test Migration with Local PostgreSQL

```bash
# Set up local PostgreSQL (if available)
createdb seo_checker_test

# Set DATABASE_URL
export DATABASE_URL="postgresql+asyncpg://localhost/seo_checker_test"

# Run migration
cd backend/
source .venv/bin/activate
python -m alembic upgrade head

# Verify tables
psql seo_checker_test -c "\dt"
```

---

## ⚠️ Important Notes

### Railway Deployment
- **Railway CLI required**: Install with `npm install -g @railway/cli`
- **DATABASE_URL**: Auto-provided by PostgreSQL addon (no manual config needed)
- **PORT**: Auto-provided by Railway (don't hardcode)
- **Migrations**: Must run manually after first deployment

### Alembic Migrations
- **Environment**: Reads `DATABASE_URL` from env (see `migrations/env.py`)
- **Async Driver**: Uses `asyncpg` for PostgreSQL
- **Auto-generate**: Not used due to async engine complexity
- **Manual Migrations**: Created based on `app/models.py`

### Security
- ✅ No secrets in git (.env.example only)
- ✅ DATABASE_URL from Railway addon
- ✅ HTTPS by default on Railway domains

---

## 📝 What's Ready

**Deployment Files**: ✅ Complete  
**Database Migrations**: ✅ Complete  
**Documentation**: ✅ Complete  
**Dependencies**: ✅ Updated  
**Configuration**: ✅ Complete

**Status**: READY FOR RAILWAY DEPLOYMENT 🚀

---

## 🎯 Next Steps

### Immediate (Requires User Action)
1. **Install Railway CLI**: `npm install -g @railway/cli`
2. **Login to Railway**: `railway login`
3. **Deploy Backend**: Follow `README_DEPLOYMENT.md`

### After Backend Deployment
- **TASK-038**: Deploy Telegram bot to Railway
- **TASK-040**: Integration testing (bot → API → DB)

---

**Tasks Completed**: TASK-037 ✅ + TASK-039 ✅  
**Time Spent**: ~1 hour  
**Files Created**: 7 new files + 1 updated  
**Status**: READY FOR DEPLOYMENT 🚀

---

**Date**: 2026-02-19  
**Author**: Claude (Cursor Agent)  
**Module**: 7 - Deployment (in progress)
