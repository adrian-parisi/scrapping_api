# ZenRows Device Profile API

A REST API for managing device profiles used in web scraping operations, built with FastAPI and SQLAlchemy.

## Quick Start

### Prerequisites

- Python 3.12+
- Poetry
- Docker & Docker Compose
- PostgreSQL (or use Docker Compose for local development)

## Getting Started

### 1. Start the API Server
```bash
make up
```
The API will be available at http://localhost:8080

### 2. Create a User and API Key
```bash
# Copy the environment template
cp .env.example .env

# Create user and API key (uses .env automatically)
poetry run python scripts/create_user.py user@example.com
```
This will output an API key like: `ak_1234567890abcdef...`

### 3. Test the API
```bash
# Test with your API key
curl -H "Authorization: Bearer YOUR_API_KEY" "http://localhost:8080/api/v1/device-profiles?page=1&size=10"

# Or visit the interactive docs
open http://localhost:8080/docs
```

### 4. Create Your First Device Profile
```bash
curl -X POST http://localhost:8080/api/v1/device-profiles \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Chrome Profile",
    "device_type": "desktop",
    "window_width": 1920,
    "window_height": 1080,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "country": "us",
    "custom_headers": [
      {"name": "Authorization", "value": "Bearer secret123", "secret": true}
    ]
  }'
```

### 5. List Templates
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" "http://localhost:8080/api/v1/templates"
```

### 6. Create Profile from Template
```bash
# Use a template ID from step 5 (replace TEMPLATE_ID with actual ID)
curl -X POST http://localhost:8080/api/v1/templates/TEMPLATE_ID/create-profile \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Chrome Profile from Template",
    "country": "us"
  }'
```

## Available Commands

```bash
make help  # Show all available commands
make up    # Start Docker services
make down  # Stop Docker services  
make test  # Run all tests
make clean # Clean up containers and files
```

## API Documentation

Once the application is running, you can access:
- Interactive API docs: http://localhost:8080/docs
- ReDoc documentation: http://localhost:8080/redoc

## Project Structure

```
├── app/                 # Application code
│   ├── auth.py          # API key authentication
│   ├── db.py            # Database configuration
│   ├── main.py          # FastAPI application
│   ├── models/          # SQLAlchemy models
│   ├── repositories/    # Data access layer
│   ├── routers/         # API endpoints
│   ├── schemas/         # Pydantic schemas
│   ├── settings.py      # Configuration
│   └── utils/           # Utility modules
├── scripts/             # Utility scripts
├── tests/               # Test suite
├── Makefile             # Development commands
└── docker-compose.yml   # Docker services
```


## Features

- Device profile CRUD operations
- Template-based profile creation
- API key authentication
- ETag-based concurrency control (prevents race conditions from multiple tabs/API retries)
- Soft delete functionality
- Pagination support
- Multi-tenant data isolation

## Technical Decisions

- **Python 3.12**: My strongest language, quickest way to deliver.
- **PostgreSQL**: Robust and reliable, proven under heavy workloads.
- **FastAPI**: Lightweight micro-framework, minimal dependencies, built-in validation and docs.
- **SQLAlchemy**: Standard ORM in Python, integrates cleanly with Postgres.
- **Pydantic v2**: Great for validation and clear error messages out of the box.
- **API Key Auth**: Simplest choice, matches the exercise requirements.
- **Docker python:3.12-slim-bookworm**: Small, secure base image, fast builds. Considered Alpine for smaller size but chose Debian for better compatibility with Python packages.
- **pytest**: I've used it for years; fixtures make tests easy to write and maintain.

## Architecture Considerations

For this interview exercise, I've kept the architecture intentionally simple with a flat structure. In a production system, you'd likely want domain-driven separation:

- **`accounts/`** - User management, API keys (`models/`, `repositories/`, `schemas/`, `routers/`)
- **`profiles/`** - Device profile management (`models/`, `repositories/`, `schemas/`, `routers/`)
- **`templates/`** - Template management (`models/`, `repositories/`, `schemas/`, `routers/`)

This would provide better organization and domain isolation as the system grows, but for the scope of this assessment, the flat structure keeps things straightforward and maintainable.

## Out of Scope

- Template creation/updates via API (templates are managed through database seeding)
- Automatic owner filtering using base repository pattern (ensures all queries are scoped to the authenticated user)
- Complex template versioning system (version tracking, migration scripts, backward compatibility)
- Advanced security hardening (CORS, rate limiting, security headers)
- Production monitoring, logging, and observability
