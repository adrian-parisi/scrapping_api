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
  - [x] `app/schemas/` directory with:
    - [x] `device_profile.py` - Pydantic schemas for device profiles
    - [x] `template.py` - Pydantic schemas for templates
  - [x] `app/repositories/` directory with:
    - [x] `device_profile.py` - Device profile repository
    - [x] `template.py` - Template repository
  - [x] `app/routers/` directory with:
    - [x] `device_profiles.py` - Device profile API endpoints
    - [x] `templates.py` - Template API endpoints
  - [x] `app/middleware/` directory with:
    - [x] `request_id.py` - Request ID middleware for correlation tracking
    - [x] `request_size.py` - Request size limiting middleware

### 1.2 Configuration Setup
- [ ] Create `app/settings.py` with environment variable loading
  - [ ] `DATABASE_URL` - PostgreSQL connection string
  - [ ] `API_KEY_PEPPER` - Secret for API key hashing
  - [ ] `DEFAULT_PAGE_SIZE` - Default pagination size (25)
  - [ ] `MAX_PAGE_SIZE` - Maximum pagination size (100)
  - [ ] `MAX_REQUEST_SIZE` - Maximum request body size (1MB)
  - [ ] Case-insensitive environment variable loading
- [ ] Create `.env.example` with all required environment variables
- [ ] Update `pyproject.toml` with required dependencies

### 1.3 Database Setup
- [ ] Initialize Alembic: `alembic init alembic`
- [ ] Configure `alembic/env.py` to use SQLAlchemy metadata from `app.db`
- [ ] Create initial migration for database schema
- [ ] Create seed migration for templates and test API key

## Phase 2: Database Models & Migrations

### 2.1 Device Profile Model
- [ ] Create `app/models/device_profile.py`
  - [ ] `id` (UUID PK)
  - [ ] `owner_id` (UUID, NOT NULL)
  - [ ] `name` (TEXT, NOT NULL)
  - [ ] `device_type` (ENUM: desktop|mobile, NOT NULL)
  - [ ] `window_width` (INT, 100..10000)
  - [ ] `window_height` (INT, 100..10000)
  - [ ] `user_agent` (TEXT, NOT NULL)
  - [ ] `country` (CHAR(2), nullable)
  - [ ] `custom_headers` (JSONB, default [])
  - [ ] `extras` (JSONB, default {})
  - [ ] `version` (INT, default 1)
  - [ ] `created_at`, `updated_at` (timestamptz)
  - [ ] `deleted_at` (timestamptz NULL)

### 2.2 Template Model
- [ ] Create `app/models/template.py`
  - [ ] `id` (UUID PK)
  - [ ] `name` (TEXT UNIQUE)
  - [ ] `description` (TEXT NULL)
  - [ ] `data` (JSONB NOT NULL)
  - [ ] `version` (TEXT NULL)
  - [ ] `created_at`, `updated_at` (timestamptz)

### 2.3 API Key Model
- [ ] Create `app/models/api_key.py`
  - [ ] `id` (UUID PK)
  - [ ] `owner_id` (UUID NOT NULL)
  - [ ] `key_hash` (TEXT UNIQUE NOT NULL)
  - [ ] `created_at`, `last_used_at`

### 2.4 Database Indexes
- [ ] Create unique partial index: `(owner_id, lower(name)) WHERE deleted_at IS NULL`
- [ ] Create performance index: `(owner_id, updated_at DESC)`

### 2.5 Alembic Migrations
- [ ] Generate initial migration: `alembic revision --autogenerate -m "Initial migration"`
- [ ] Create seed migration with templates:
  - [ ] "Chrome on Windows desktop"
  - [ ] "iOS 17 on iPhone Pro"
  - [ ] Test API key for local development
- [ ] Apply migrations: `alembic upgrade head`

## Phase 3: Authentication & Authorization

### 3.1 API Key Authentication
- [ ] Create `app/auth.py` with API key validation
  - [ ] Hash API key with pepper using SHA-256
  - [ ] Lookup API key in database
  - [ ] Return owner_id on successful authentication
  - [ ] Handle missing/invalid keys (401 Unauthorized)

### 3.2 Owner Scoping
- [ ] Ensure all repository queries filter by owner_id
- [ ] Never fetch by ID without owner scoping
- [ ] Return 404 (not 403) for other users' resources

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
- [ ] Create `app/routers/device_profiles.py`
  - [ ] `GET /api/v1/device-profiles` - List profiles with pagination
  - [ ] `POST /api/v1/device-profiles` - Create profile
  - [ ] `GET /api/v1/device-profiles/{id}` - Get profile with ETag
  - [ ] `PATCH /api/v1/device-profiles/{id}` - Update profile with If-Match
  - [ ] `DELETE /api/v1/device-profiles/{id}` - Soft delete profile

### 7.2 Template Endpoints
- [ ] Create `app/routers/templates.py`
  - [ ] `GET /api/v1/templates` - List templates
  - [ ] `GET /api/v1/templates/{id}` - Get template
  - [ ] `POST /api/v1/templates/{id}/create-profile` - Create profile from template

### 7.3 Health Check Endpoint
- [ ] Create `app/routers/health.py`
  - [ ] `GET /health` - Health check endpoint
  - [ ] Return 200 OK with service status
  - [ ] Include database connectivity check

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
