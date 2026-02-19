#!/bin/bash
set -x
cd /Users/aleksejsermazko/Documents/Cursor/work/git/projects/seo-checker-tool
echo "=== Current directory ==="
pwd
echo ""
echo "=== Git status ==="
git status
echo ""
echo "=== Adding files ==="
git add -A
echo ""
echo "=== Creating commit ==="
git commit -m "feat: SEO Checker MVP - complete backend and telegram bot"
echo ""
echo "=== Pushing to GitHub ==="
git push -u origin main 2>&1
echo ""
echo "=== Done ==="
