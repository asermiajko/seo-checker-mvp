#!/bin/bash
# Скрипт для деплоя SEO Checker MVP

echo "=== SEO Checker MVP Deployment ==="
echo ""

# 1. Проверка репозитория
echo "Step 1: Checking GitHub repository..."
if curl -s -f -o /dev/null https://github.com/asermiajko/seo-checker-mvp; then
    echo "✓ Repository exists"
else
    echo "✗ Repository doesn't exist. Creating..."
    gh repo create seo-checker-mvp --public --source=. --remote=origin
fi

# 2. Коммит изменений
echo ""
echo "Step 2: Committing changes..."
git add -A
git commit -m "feat: SEO Checker MVP - complete backend and telegram bot

- FastAPI backend with async PostgreSQL
- SEO checks: robots.txt, sitemap, meta tags, headers
- Telegram bot with deep links
- Rate limiting (5 checks/hour)
- Full test coverage (unit, integration, e2e)
- Railway deployment ready
- Documentation complete"

# 3. Пуш в GitHub
echo ""
echo "Step 3: Pushing to GitHub..."
git push -u origin main

echo ""
echo "✓ Code pushed to GitHub: https://github.com/asermiajko/seo-checker-mvp"
echo ""
echo "Next steps:"
echo "1. Go to https://railway.com/project/b21e4f50-40c2-435f-8bb1-c377355f889f/service/45de6a7c-9716-4efb-9e04-729494d1b027"
echo "2. Settings → Source → Connect Repo"
echo "3. Select 'asermiajko/seo-checker-mvp'"
echo "4. Root Directory: 'backend'"
echo "5. Deploy"
