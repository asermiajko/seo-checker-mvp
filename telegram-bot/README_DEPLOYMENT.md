# SEO Checker Telegram Bot — Deployment Guide

## ✅ Pre-Deployment Checklist

All deployment files are ready:

- ✅ `Procfile` — Railway worker process configuration
- ✅ `railway.json` — Railway build/deploy settings  
- ✅ `requirements.txt` — Python dependencies
- ✅ `.env.example` — Environment variables template

---

## 🚀 Deployment to Railway

### Prerequisites
1. Railway CLI installed: `npm install -g @railway/cli`
2. Railway account: https://railway.app
3. **Backend API already deployed** (get API URL)
4. **Telegram Bot Token** from @BotFather

---

## 🤖 Step 1: Get Telegram Bot Token

### Option A: Create New Bot
```
1. Open Telegram, find @BotFather
2. Send: /newbot
3. Follow instructions:
   - Bot name: "SEO Checker Bot"
   - Bot username: "your_seo_checker_bot" (must end with 'bot')
4. Copy token: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

### Option B: Use Existing Bot
```
1. Talk to @BotFather
2. Send: /mybots
3. Select your bot
4. Select "API Token"
5. Copy token
```

---

## 🚀 Step 2: Deploy Bot to Railway

### Initialize Railway Project

```bash
cd telegram-bot/
railway init
# Name: "seo-checker-bot"
```

### Set Environment Variables

```bash
# Set bot token
railway variables set TELEGRAM_TOKEN=YOUR_TOKEN_HERE

# Set backend API URL (from backend deployment)
railway variables set API_URL=https://your-backend.railway.app
```

**Important**: Replace with your actual values!

### Deploy

```bash
railway up
```

This will:
1. Install dependencies from `requirements.txt`
2. Start bot with `python bot.py`
3. Bot begins polling Telegram for updates

---

## 🧪 Testing Deployed Bot

### 1. Check Bot is Running

```bash
railway logs
```

Look for: "Bot started successfully" or similar message.

### 2. Test Bot on Telegram

Open Telegram and find your bot:

**Test /start command:**
```
/start
```
Expected: Welcome message with instructions

**Test /help command:**
```
/help
```
Expected: Help message with features list

**Test SEO check (via web form link from bot):**
1. Bot provides web form link
2. Submit URL in web form
3. Receive deep link in Telegram
4. Click deep link
5. Bot checks site and returns report

### 3. Test Rate Limiting

Send 6 check requests quickly:
- First 5 should succeed
- 6th should return rate limit error

---

## 🔧 Configuration Details

### Environment Variables

**Required:**
- `TELEGRAM_TOKEN` — Bot token from @BotFather
- `API_URL` — Backend API URL (Railway deployment)

**Auto-provided by Railway:**
- None (bot doesn't need PORT)

### Process Type

- **Worker process** (not web) — bot uses Telegram polling, not HTTP server
- No port binding needed
- Long-running process that polls Telegram API

---

## 🛠 Troubleshooting

### Issue: Bot Not Responding

**Check logs:**
```bash
railway logs
```

**Common causes:**
- Invalid TELEGRAM_TOKEN
- Backend API URL incorrect or unreachable
- Bot token already used by another instance

**Fix:**
```bash
# Verify environment variables
railway variables

# Update if needed
railway variables set TELEGRAM_TOKEN=correct_token
railway variables set API_URL=https://correct-backend-url.railway.app

# Restart bot
railway restart
```

### Issue: Bot Can't Connect to Backend

**Test backend manually:**
```bash
curl https://your-backend.railway.app/api/health
```

**If backend down:**
- Check backend Railway logs
- Verify backend DATABASE_URL is set
- Restart backend: `cd backend/ && railway restart`

**If backend up but bot still fails:**
- Check API_URL in bot environment variables
- Ensure URL includes `https://` and no trailing slash
- Check Railway logs for connection errors

### Issue: Multiple Bot Instances

**Symptom**: Bot responds twice to each message

**Cause**: Bot running locally AND on Railway

**Fix**:
```bash
# Stop local bot (if running)
# Check Railway logs to confirm only one instance
railway logs
```

---

## 📊 Monitoring

### View Bot Logs

```bash
railway logs

# Follow logs in real-time
railway logs --follow
```

### Check Bot Status

Railway dashboard → Deployments:
- Deployment status (success/failed)
- CPU usage
- Memory usage
- Restart count

---

## 🔄 Updating Bot

### Deploy New Changes

```bash
# Make changes to code
git add .
git commit -m "Update bot"

# Push and deploy
cd telegram-bot/
railway up
```

Railway automatically redeploys.

### Update Environment Variables

```bash
# Update API URL (if backend URL changed)
railway variables set API_URL=https://new-backend-url.railway.app

# Restart bot
railway restart
```

---

## 🔗 Connecting Bot to Backend

### Backend API URL Format

```
https://seo-checker-backend.railway.app
```

**Important:**
- Must start with `https://`
- No trailing slash
- Should match backend Railway domain

### Testing Connection

```bash
# From bot logs, find API request
railway logs | grep "API request"

# Or test manually
curl https://your-backend.railway.app/api/health
```

---

## ✅ Deployment Checklist

Before deploying bot:
- [x] Backend deployed and working
- [x] Backend API URL known
- [x] Telegram bot token obtained from @BotFather
- [x] Railway CLI installed and logged in
- [x] Bot deployment files created (Procfile, railway.json)
- [x] Environment variables ready (TELEGRAM_TOKEN, API_URL)

To deploy:
- [ ] `railway init` in telegram-bot/
- [ ] Set environment variables
- [ ] `railway up`
- [ ] Test bot on Telegram

---

## 📋 Alternative: Local Testing

### Test Bot Locally (Before Deployment)

```bash
cd telegram-bot/
source .venv/bin/activate

# Set environment variables
export TELEGRAM_TOKEN="your_token_from_botfather"
export API_URL="http://localhost:8000"

# Run bot
python bot.py
```

**Note**: Backend must be running locally on port 8000.

---

## 🎯 Next Steps After Bot Deployment

### TASK-040: Integration Testing
1. Test complete flow: Telegram → Bot → API → Database
2. Verify rate limiting in production
3. Test error handling (invalid URLs, timeouts)
4. Performance testing (response times)

### Module 8: Documentation & Polish
1. Write comprehensive README
2. API documentation
3. User guide for bot
4. Final polish and testing

---

## ✅ Status

**TASK-038: Railway Bot Deployment** — Files Ready

Created:
- ✅ `Procfile` (worker process)
- ✅ `railway.json` (deploy config)
- ✅ `.env.example` (env vars template)
- ✅ `README_DEPLOYMENT.md` (this file)

**Next**: Deploy using Railway CLI or continue with documentation.

---

**Last Updated**: 2026-02-19  
**Project**: SEO Checker MVP  
**Module**: 7 - Deployment
