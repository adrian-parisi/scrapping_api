# ZenRows Device Profile API

A REST API for managing device profiles used in web scraping operations, built with FastAPI and SQLAlchemy.

## Development Setup

### Prerequisites

- Python 3.12+
- Poetry

### Installation

1. Install dependencies:
```bash
poetry install
```

2. Set up environment variables:
```bash
# Create .env file with required variables
# See app/settings.py for required configuration
```

## Testing

### Using SQLite (Default)

The tests use an in-memory SQLite database for fast and reliable testing.

1. Run tests:
```bash
poetry run pytest -v
```

### Test Database Details

- **Database**: SQLite (in-memory for tests)
- **No external dependencies required**
- **Fast test execution**

## API Documentation

Once the application is running, you can access:
- Interactive API docs: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

## Project Structure

```
app/
├── auth.py              # API key authentication
├── core/
│   └── errors.py        # Error handling
├── db.py                # Database configuration
├── main.py              # FastAPI application
├── models/              # SQLAlchemy models
├── repositories/        # Data access layer
├── routers/             # API endpoints
├── schemas/             # Pydantic schemas
└── settings.py          # Configuration
```

## Features

- Device profile CRUD operations
- Template-based profile creation
- API key authentication
- ETag-based concurrency control
- Soft delete functionality
- Pagination support
- Multi-tenant data isolation
