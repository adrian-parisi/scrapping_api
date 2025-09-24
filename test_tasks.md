# Test Tasks for ZenRows Device Profile API

## Phase 1: Core Functionality Tests

### 1.1 Device Profile CRUD
- [ ] `test_create_device_profile_success()` - Create profile with valid data
- [ ] `test_get_device_profile_success()` - Retrieve existing profile
- [ ] `test_get_device_profile_not_found()` - Handle non-existent profile
- [ ] `test_update_device_profile_success()` - Update existing profile
- [ ] `test_delete_device_profile_success()` - Soft delete profile
- [ ] `test_list_device_profiles_pagination()` - Paginated listing

### 1.2 Template Operations
- [ ] `test_list_templates()` - List all templates
- [ ] `test_get_template()` - Get specific template
- [ ] `test_create_profile_from_template()` - Create profile from template

### 1.3 User & Authentication
- [ ] `test_create_user_script()` - User creation via script
- [ ] `test_api_key_authentication_success()` - Valid API key
- [ ] `test_api_key_authentication_failure()` - Invalid API key

## Phase 2: Multi-Tenant Security Tests

### 2.1 Data Isolation
- [ ] `test_user_cannot_access_other_users_profiles()` - Profile isolation
- [ ] `test_user_cannot_update_other_users_profiles()` - Update isolation
- [ ] `test_user_cannot_delete_other_users_profiles()` - Delete isolation
- [ ] `test_soft_deleted_profiles_not_visible()` - Soft delete isolation

### 2.2 API Key Security
- [ ] `test_api_key_pepper_hashing()` - Key hashing verification
- [ ] `test_api_key_owner_validation()` - Owner association

## Phase 3: Concurrency & Versioning Tests

### 3.1 Optimistic Concurrency Control
- [ ] `test_concurrent_updates_version_mismatch()` - Version conflict detection
- [ ] `test_etag_if_match_validation()` - ETag header validation
- [ ] `test_version_increment_on_update()` - Version increment

### 3.2 Template Versioning
- [ ] `test_template_update_does_not_affect_existing_profiles()` - Template isolation
- [ ] `test_profile_created_from_old_template_unchanged()` - Profile stability

## Phase 4: Validation & Edge Cases

### 4.1 Device Profile Validation
- [ ] `test_invalid_device_type_rejection()` - Enum validation
- [ ] `test_invalid_window_dimensions()` - Range validation
- [ ] `test_duplicate_profile_name_same_user()` - Name uniqueness
- [ ] `test_profile_name_case_insensitivity()` - Case handling
- [ ] `test_custom_headers_validation()` - Header validation

### 4.2 Soft Delete Edge Cases
- [ ] `test_soft_deleted_profile_name_reuse()` - Name reuse after delete
- [ ] `test_unique_constraint_with_soft_delete()` - Constraint behavior

## Phase 5: Error Handling

### 5.1 API Error Scenarios
- [ ] `test_malformed_json_request()` - Invalid JSON
- [ ] `test_missing_required_fields()` - Required field validation
- [ ] `test_invalid_uuid_format()` - UUID validation
- [ ] `test_oversized_request_body()` - Request size limits

### 5.2 Database Error Handling
- [ ] `test_constraint_violation_handling()` - Database constraints
- [ ] `test_transaction_rollback_on_error()` - Transaction integrity

## Phase 6: Pagination Tests

### 6.1 Pagination Functionality
- [ ] `test_pagination_first_page()` - First page results
- [ ] `test_pagination_middle_page()` - Middle page results
- [ ] `test_pagination_last_page()` - Last page results
- [ ] `test_pagination_empty_results()` - No results
- [ ] `test_pagination_invalid_parameters()` - Invalid pagination params

## Phase 7: Integration Tests

### 7.1 Complete Workflows
- [ ] `test_complete_user_registration_workflow()` - End-to-end user creation
- [ ] `test_complete_profile_management_workflow()` - End-to-end profile CRUD
- [ ] `test_complete_template_to_profile_workflow()` - Template to profile flow

### 7.2 Multi-User Scenarios
- [ ] `test_multiple_users_same_profile_names()` - Name collision handling
- [ ] `test_concurrent_user_operations()` - Concurrent access

## Test Implementation Notes

### Test Structure
- Use `pytest` with `pytest-asyncio` for async tests
- Use `httpx.AsyncClient` for API testing
- Use `app.dependency_overrides` for test doubles
- Create test fixtures for common data setup

### Test Data
- Create test users with API keys
- Create test device profiles with various configurations
- Create test templates with different versions
- Use factories for consistent test data generation

### Database Testing
- Use test database with transactions that rollback
- Isolate tests to prevent data leakage
- Test both success and failure scenarios

### Security Testing Focus
- Multi-tenant data isolation
- API key authentication and authorization
- Input validation and sanitization
- Soft delete data protection

### Concurrency Testing
- Test version conflicts with ETag/If-Match
- Test concurrent profile operations
- Test template versioning scenarios
- Test soft delete concurrency

### Performance Considerations
- Test pagination with reasonable data volumes
- Test response times for typical operations
- Test memory usage with large responses
- Test concurrent request handling
