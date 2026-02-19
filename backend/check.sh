#!/bin/bash
# Quality check script for backend

set -e

echo "🔍 Running code quality checks..."
echo ""

echo "1️⃣ Ruff (linting)..."
.venv/bin/ruff check app/
echo "✅ Ruff passed"
echo ""

echo "2️⃣ MyPy (type checking)..."
.venv/bin/mypy app/
echo "✅ MyPy passed"
echo ""

echo "3️⃣ Ruff (formatting check)..."
.venv/bin/ruff format --check app/
echo "✅ Formatting is correct"
echo ""

echo "✨ All quality checks passed!"
