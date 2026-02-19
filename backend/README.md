# SEO Checker Backend API

FastAPI-based backend for SEO health checks.

## Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

## Development

```bash
# Run server
uvicorn app.main:app --reload

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Linting
ruff check app/
mypy app/
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `POST /api/check` - SEO check (coming soon)
