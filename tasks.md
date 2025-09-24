# ZenRows Device Profile API - Task List

## Phase 1: Project Setup & Configuration

### 1.1 Project Structure Setup
- [x] Create `app/` directory structure
  - [x] `app/main.py` - FastAPI application entry point
  - [x] `app/settings.py` - Configuration management
  - [x] `app/db.py` - Database connection and session management
  - [x] `app/auth.py` - API key authentication
  - [x] `app/core/` directory with:
    - [x] `errors.py` - Error handling and problem+json responses
    - [x] `pagination.py` - Pagination utilities
    - [x] `headers.py` - Header validation utilities
  - [x] `app/models/` directory with:
    - [x] `device_profile.py` - Device profile SQLAlchemy model
    - [x] `template.py` - Template SQLAlchemy model
    - [x] `api_key.py` - API key SQLAlchemy model
    - [x] `user.py` - User SQLAlchemy model
  - [x] `app/schemas/` directory with:
    - [x] `device_profile.py` - Pydantic schemas for device profiles
    - [x] `template.py` - Pydantic schemas for templates
  - [x] `app/repositories/` directory with:
    - [x] `device_profile.py` - Device profile repository
    - [x] `template.py` - Template repository
    - [ ] `user.py` - User repository
  - [x] `app/routers/` directory with:
    - [x] `device_profiles.py` - Device profile API endpoints
    - [x] `templates.py` - Template API endpoints
  - [x] `scripts/` directory with:
    - [x] `create_user.py` - Command-line script for user creation
  - [x] `app/middleware/` directory with:
    - [x] `request_id.py` - Request ID middleware for correlation tracking
    - [x] `request_size.py` - Request size limiting middleware

### 1.2 Configuration Setup
- [x] Create `app/settings.py` with environment variable loading
  - [x] `DATABASE_URL` - Database connection string (SQLite for tests, PostgreSQL for production)
  - [x] `API_KEY_PEPPER` - Secret for API key hashing
  - [x] `DEFAULT_PAGE_SIZE` - Default pagination size (25)
  - [x] `MAX_PAGE_SIZE` - Maximum pagination size (100)
  - [x] `MAX_REQUEST_SIZE` - Maximum request body size (1MB)
  - [x] Case-insensitive environment variable loading
- [x] Create `.env.example` with all required environment variables
- [x] Update `pyproject.toml` with required dependencies

### 1.3 Database Setup
- [ ] Initialize Alembic: `alembic init alembic`
- [ ] Configure `alembic/env.py` to use SQLAlchemy metadata from `app.db`
- [ ] Create initial migration for database schema
- [ ] Create seed migration for templates and test API key

## Phase 2: Database Models & Migrations

### 2.1 Device Profile Model
- [x] Create `app/models/device_profile.py`
  - [x] `id` (UUID PK)
  - [x] `owner_id` (UUID, NOT NULL)
  - [x] `name` (TEXT, NOT NULL)
  - [x] `device_type` (ENUM: desktop|mobile, NOT NULL)
  - [x] `window_width` (INT, 100..10000)
  - [x] `window_height` (INT, 100..10000)
  - [x] `user_agent` (TEXT, NOT NULL)
  - [x] `country` (CHAR(2), nullable)
  - [x] `custom_headers` (JSON, default [])
  - [x] `extras` (JSON, default {})
  - [x] `version` (INT, default 1)
  - [x] `created_at`, `updated_at` (timestamptz)
  - [x] `deleted_at` (timestamptz NULL)

### 2.2 Template Model
- [x] Create `app/models/template.py`
  - [x] `id` (UUID PK)
  - [x] `name` (TEXT UNIQUE)
  - [x] `description` (TEXT NULL)
  - [x] `data` (JSON NOT NULL)
  - [x] `version` (TEXT NULL)
  - [x] `created_at`, `updated_at` (timestamptz)

### 2.3 User Model
- [x] Create `app/models/user.py`
  - [x] `id` (UUID PK)
  - [x] `email` (VARCHAR(255) UNIQUE NOT NULL)
  - [x] `is_active` (BOOLEAN, default TRUE)
  - [x] `created_at`, `updated_at` (timestamptz)

### 2.4 API Key Model
- [x] Create `app/models/api_key.py`
  - [x] `id` (UUID PK)
  - [x] `owner_id` (UUID NOT NULL, FK to users)
  - [x] `key_hash` (TEXT UNIQUE NOT NULL)
  - [x] `created_at`, `updated_at` (timestamptz)

### 2.5 Database Indexes
- [x] Create unique partial index: `(owner_id, lower(name)) WHERE deleted_at IS NULL`
- [ ] Create performance index: `(owner_id, updated_at DESC)`
- [x] Create unique index on users.email

### 2.6 Alembic Migrations
- [ ] Generate initial migration: `alembic revision --autogenerate -m "Initial migration"`
- [ ] Create seed migration with templates:
  - [ ] "Chrome on Windows desktop"
  - [ ] "iOS 17 on iPhone Pro"
  - [ ] Test user and API key for local development
- [ ] Apply migrations: `alembic upgrade head`

## Phase 3: Authentication & Authorization

### 3.1 API Key Authentication
- [x] Create `app/auth.py` with API key validation
  - [x] Hash API key with pepper using SHA-256
  - [x] Lookup API key in database
  - [x] Return owner_id on successful authentication
  - [x] Handle missing/invalid keys (401 Unauthorized)

### 3.2 Owner Scoping
- [x] Ensure all repository queries filter by owner_id
- [x] Never fetch by ID without owner scoping
- [x] Return 404 (not 403) for other users' resources

## Phase 4: Validation & Business Logic

### 4.1 Country Validation
- [ ] Create ISO-3166-1 country code validation
- [ ] Ensure country codes are lowercase
- [ ] Validate against in-memory set of valid codes

### 4.2 Window Size Validation
- [ ] Validate window_width/height: 100-10000
- [ ] Optional: tighter ranges by device type
- [ ] Cross-field validation: mobile with ultra-wide viewport → reject

### 4.3 Custom Headers Validation
- [ ] Validate custom_headers as array of {name, value}
- [ ] Deny hop-by-hop/controlled names:
  - [ ] host, content-length, connection, transfer-encoding, keep-alive, upgrade, trailer
- [ ] Preserve order and duplicates in headers array

### 4.4 Schema Conversion
- [ ] Implement camelCase ↔ snake_case conversion
- [ ] Request/Response: device, viewport.width, viewport.height, userAgent, country, headers, extras
- [ ] DB columns: snake_case

## Phase 5: Repository Layer

### 5.1 Device Profile Repository
- [ ] Create `app/repositories/device_profile.py`
  - [ ] `create(owner_id, profile_data)` - Create new profile
  - [ ] `get_by_id(owner_id, profile_id)` - Get profile by ID
  - [ ] `list(owner_id, limit, offset)` - List profiles with pagination
  - [ ] `update(owner_id, profile_id, data, version)` - Update profile with version check
  - [ ] `soft_delete(owner_id, profile_id)` - Soft delete profile
  - [ ] `check_name_exists(owner_id, name)` - Check for duplicate names

### 5.2 Template Repository
- [ ] Create `app/repositories/template.py`
  - [ ] `list()` - List all templates
  - [ ] `get_by_id(template_id)` - Get template by ID
  - [ ] `create_profile_from_template(owner_id, template_id, overrides)` - Clone template

### 5.3 User Repository
- [ ] Create `app/repositories/user.py`
  - [ ] `create(email, name)` - Create new user
  - [ ] `get_by_email(email)` - Get user by email
  - [ ] `get_by_id(user_id)` - Get user by ID
  - [ ] `create_api_key(user_id)` - Generate API key for user
  - [ ] `get_api_keys(user_id)` - List user's API keys

### 5.4 User Management Script
- [x] Create `scripts/create_user.py`
  - [x] Command-line interface: `python scripts/create_user.py <email>`
  - [x] Create user if not exists
  - [x] Generate and return API key
  - [x] Handle duplicate email errors
  - [x] Print API key to stdout for easy copying

## Phase 6: Pydantic Schemas

### 6.1 Device Profile Schemas
- [ ] Create `app/schemas/device_profile.py`
  - [ ] `DeviceProfileCreate` - For POST requests
  - [ ] `DeviceProfileUpdate` - For PATCH requests
  - [ ] `DeviceProfileResponse` - For GET responses
  - [ ] `DeviceProfileList` - For paginated list responses

### 6.2 Template Schemas
- [ ] Create `app/schemas/template.py`
  - [ ] `TemplateResponse` - For template responses
  - [ ] `TemplateList` - For template list responses
  - [ ] `CreateProfileFromTemplate` - For template clone requests


## Phase 7: API Endpoints

### 7.1 Device Profile Endpoints
- [x] Create `app/routers/device_profiles.py`
  - [x] `GET /api/v1/device-profiles` - List profiles with pagination
  - [x] `POST /api/v1/device-profiles` - Create profile
  - [x] `GET /api/v1/device-profiles/{id}` - Get profile with ETag
  - [x] `PATCH /api/v1/device-profiles/{id}` - Update profile with If-Match
  - [x] `DELETE /api/v1/device-profiles/{id}` - Soft delete profile

### 7.2 Template Endpoints
- [x] Create `app/routers/templates.py`
  - [x] `GET /api/v1/templates` - List templates
  - [x] `GET /api/v1/templates/{id}` - Get template
  - [x] `POST /api/v1/templates/{id}/create-profile` - Create profile from template

### 7.3 User Management Script (Technical Interview Only)
- [ ] Create `scripts/create_user.py` - Command-line script for user creation
  - [ ] Accept email as command-line argument
  - [ ] Create user with email and generated name
  - [ ] Generate API key for the user
  - [ ] Return API key as command output
  - [ ] **WARNING**: This script is for technical interview purposes only
  - [ ] **WARNING**: No authentication required - NOT suitable for production


## Phase 8: Error Handling & Response Format

### 8.1 Problem+JSON Responses
- [ ] Create `app/core/errors.py`
  - [ ] Standardized error response format
  - [ ] Fields: type, title, status, detail, instance
  - [ ] Validation error details
  - [ ] Include request URI in instance field

### 8.2 HTTP Status Codes
- [ ] 201 Created with Location header on create
- [ ] 200 OK on fetch/update
- [ ] 204 No Content on delete
- [ ] 400 Bad Request
- [ ] 401 Unauthorized
- [ ] 403 Forbidden
- [ ] 404 Not Found
- [ ] 409 Conflict (duplicate name)
- [ ] 422 Unprocessable Entity (validation errors)
- [ ] 428 Precondition Required (missing If-Match)
- [ ] 412 Precondition Failed (ETag mismatch)

## Phase 9: Pagination & Headers

### 9.1 Pagination Implementation
- [ ] Create `app/core/pagination.py`
  - [ ] Query params: limit, offset
  - [ ] Clamp: 1..MAX_PAGE_SIZE; offset >= 0
  - [ ] Link header with rel="next"/rel="prev"

### 9.2 ETag/If-Match Support
- [ ] Implement ETag generation from version
- [ ] Validate If-Match header on updates
- [ ] Return current ETag on 412 Precondition Failed
- [ ] Bump version atomically with updates

### 9.3 Request ID Middleware
- [ ] Create `app/middleware/request_id.py`
  - [ ] Generate unique request ID for each request
  - [ ] Add X-Request-ID header to responses
  - [ ] Include request ID in error responses

### 9.4 Request Size Limiting
- [ ] Create `app/middleware/request_size.py`
  - [ ] Limit request body size to MAX_REQUEST_SIZE
  - [ ] Return 413 Payload Too Large for oversized requests
  - [ ] Add X-Request-Size-Limit header to responses

## Phase 10: Testing

### 10.1 Authentication Tests
- [ ] Missing API key → 401
- [ ] Invalid API key → 401
- [ ] Owner isolation: other user's profile → 404

### 10.2 Profile Tests
- [ ] Create, fetch, list (pagination)
- [ ] Duplicate name → 409
- [ ] Soft delete excludes from list
- [ ] Re-create with same name succeeds
- [ ] ETag present on GET
- [ ] PATCH without If-Match → 428
- [ ] Wrong ETag → 412
- [ ] Correct ETag → updates + new ETag
- [ ] Header deny-list enforced (422)
- [ ] Country and viewport validation (422)

### 10.3 Template Tests
- [ ] List and get return seeded items
- [ ] Create from template yields new profile
- [ ] Optional overrides applied
- [ ] Location header set on create endpoints

## Phase 11: Docker & Deployment

### 11.1 Docker Configuration
- [ ] Create `Dockerfile`
  - [ ] Base: python:3.12-slim
  - [ ] Install app + runtime deps only
  - [ ] EXPOSE 8080
  - [ ] Entrypoint: uvicorn app.main:app --host 0.0.0.0 --port 8080

### 11.2 Docker Compose (Optional)
- [ ] Create `docker-compose.yml` for local development
- [ ] Include PostgreSQL service
- [ ] Include Redis service (if needed)

## Phase 12: Documentation & Demo

### 12.1 API Documentation
- [ ] Update README.md with API usage examples
- [ ] Document all endpoints with request/response examples
- [ ] Include authentication setup instructions

### 12.2 Demo Script Preparation
- [ ] Prepare demo script for interview presentation
- [ ] Test all demo scenarios
- [ ] Ensure smooth flow from auth to CRUD operations

## Phase 13: Final Review & Polish

### 13.1 Code Review
- [ ] Review all code for consistency
- [ ] Ensure proper error handling
- [ ] Verify all requirements are met

### 13.2 Performance Testing
- [ ] Test pagination with large datasets
- [ ] Verify database query performance
- [ ] Test concurrent updates with ETag

### 13.3 Security Review
- [ ] Verify API key hashing
- [ ] Check owner scoping
- [ ] Validate input sanitization

## TODO Items (Future Enhancements)

### High Priority
- [ ] Implement profile versioning cleanup job
  - Clean up old profile versions after X days of inactivity
  - Consider active scraping sessions before cleanup
  - Add configuration for cleanup intervals

### Medium Priority
- [ ] Add template version management
  - Handle template updates (e.g., new Chrome versions)
  - Template deprecation strategy
  - Migration scripts for template updates

### Low Priority
- [ ] Add health check endpoint
  - `GET /health` - Health check endpoint
  - Return 200 OK with service status
  - Include database connectivity check
- [ ] Add HATEOAS support
  - Include `_links` object in all responses
  - Add self-links for all resources
  - Add related resource links where applicable
- [ ] Add CORS support
  - Configure CORS middleware for web clients
  - Add appropriate CORS headers
- [ ] Add rate limiting
  - Implement rate limiting middleware
  - Add X-RateLimit-* headers
  - Configure rate limits per API key
- [ ] Add profile version history API
  - `GET /device-profiles/{id}/versions` - List all versions
  - `GET /device-profiles/{id}/versions/{version}` - Get specific version
- [ ] Add profile usage analytics
  - Track which profiles are most used
  - Monitor profile performance
- [ ] Add profile validation
  - Validate device configurations against real devices
  - Test profile effectiveness

## Notes
- Each task should be completed and tested before moving to the next
- Use git commits for each completed task
- Test each endpoint manually before marking as complete
- Follow the layered-lite approach: keep it simple but correct
