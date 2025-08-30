# Tasks Document

## Bot Service Independence Tasks

- [x] 1. Create independent bot configuration
  - File: backend/bot/config.py (modify existing)
  - Remove `from app.core.config import settings` import
  - Create independent BotSettings class extending BaseSettings
  - Add all necessary environment variables for bot service
  - Purpose: Make bot configuration completely independent from API service
  - _Leverage: app/core/config.py patterns_
  - _Requirements: 2.1, 6.1_

- [x] 2. Create HTTP client manager for bot service
  - File: backend/bot/http_client.py (new)
  - Implement HTTPClientManager class with startup/shutdown lifecycle
  - Configure connection pooling with proper limits and timeouts
  - Add base URL and default headers configuration
  - Purpose: Provide single HTTP client instance with connection pooling
  - _Leverage: httpx AsyncClient patterns_
  - _Requirements: 3.1, 8.1_

- [x] 3. Create independent bot enums
  - File: backend/bot/enums.py (new)
  - Duplicate necessary enums from app/enums.py for bot independence
  - Include Genders, PreferredGenders, ReactionType, FileTypes, UILanguages
  - Remove app/enums.py imports from bot files
  - Purpose: Eliminate cross-service enum dependencies
  - _Leverage: app/enums.py_
  - _Requirements: 6.2_

- [x] 4. Create independent bot validators
  - File: backend/bot/validators.py (new)
  - Duplicate essential validators from app/validators.py
  - Focus on user input validation (name, bio, age validation)
  - Remove app/validators.py imports from bot schemas
  - Purpose: Enable bot-side validation without API dependencies
  - _Leverage: app/validators.py patterns_
  - _Requirements: 6.2_

- [x] 5. Update bot schemas to use independent modules
  - File: backend/bot/schemas/user.py (modify existing)
  - File: backend/bot/schemas/media.py (modify existing)
  - File: backend/bot/schemas/reaction.py (modify existing)
  - File: backend/bot/schemas/report.py (modify existing)
  - Replace app imports with bot-specific modules (enums, validators)
  - Ensure schemas match API response formats exactly
  - Purpose: Make bot schemas independent while maintaining API compatibility
  - _Leverage: existing bot/schemas/ files_
  - _Requirements: 4.1, 4.2_

## Enhanced Bot Services Tasks

- [x] 6. Enhance user service with shared HTTP client
  - File: backend/bot/services/user.py (modify existing)
  - Replace `async with httpx.AsyncClient()` with injected HTTPClientManager
  - Add proper error handling and user-friendly error messages
  - Implement caching for frequently accessed user data
  - Purpose: Improve performance and user experience with connection pooling
  - _Leverage: existing bot/services/user.py structure_
  - _Requirements: 3.1, 3.2_

- [x] 7. Enhance match service with shared HTTP client
  - File: backend/bot/services/match.py (modify existing)
  - Replace multiple HTTP client instances with shared client
  - Add circuit breaker pattern for resilience
  - Improve error handling for match-related operations
  - Purpose: Optimize match-related API communication
  - _Leverage: existing bot/services/match.py structure_
  - _Requirements: 3.1, 3.2_

- [x] 8. Enhance media service with shared HTTP client
  - File: backend/bot/services/media.py (modify existing)
  - Replace individual HTTP clients with shared client
  - Add proper media validation and error handling
  - Implement media list caching with TTL
  - Purpose: Optimize media-related API communication
  - _Leverage: existing bot/services/media.py structure_
  - _Requirements: 3.1, 3.2_

- [x] 9. Enhance report service with shared HTTP client
  - File: backend/bot/services/report.py (modify existing)
  - Update to use shared HTTP client manager
  - Add proper error handling for report operations
  - Ensure user privacy in error logging
  - Purpose: Complete bot service layer enhancement
  - _Leverage: existing bot/services/report.py structure_
  - _Requirements: 3.1, 3.2_

## Bot Handler Independence Tasks

- [-] 10. Remove direct database imports from registration handler
  - File: backend/bot/handlers/registration.py (modify existing)
  - Remove `from app.core.db import session_factory`
  - Remove `from app.models.user import Place, PlaceName, Preferences, User`
  - Remove `from app.queries import get_user, is_user_banned`
  - Replace with HTTP API calls via enhanced services
  - Purpose: Eliminate direct database access from bot handlers
  - _Leverage: existing handler structure, enhanced bot services_
  - _Requirements: 1.1, 1.2_

- [-] 11. Remove direct database imports from profile handler
  - File: backend/bot/handlers/profile.py (modify existing)
  - Remove SQLAlchemy imports and direct database operations
  - Replace with API calls through enhanced services
  - Update validation to use bot-specific validators
  - Purpose: Make profile handler independent from API database layer
  - _Leverage: existing handler logic, enhanced services_
  - _Requirements: 1.1, 1.2_

- [ ] 12. Remove direct database imports from search handler
  - File: backend/bot/handlers/search.py (modify existing)
  - Remove direct database access and queries
  - Replace with API calls for user matching and reactions
  - Update to use shared HTTP client through services
  - Purpose: Make search functionality fully API-dependent
  - _Leverage: existing search logic, enhanced services_
  - _Requirements: 1.1, 1.2_

- [ ] 13. Remove direct database imports from matches handler
  - File: backend/bot/handlers/matches.py (modify existing)
  - Remove direct database queries and model imports
  - Replace with API calls for match retrieval and checking
  - Update error handling to use bot-friendly messages
  - Purpose: Make match handling fully API-dependent
  - _Leverage: existing match logic, enhanced services_
  - _Requirements: 1.1, 1.2_

- [ ] 14. Remove direct database imports from likes handler
  - File: backend/bot/handlers/likes.py (modify existing)
  - Remove database imports and direct queries
  - Replace with API calls for likes retrieval
  - Update to use enhanced services with shared HTTP client
  - Purpose: Complete handler independence from database layer
  - _Leverage: existing likes logic, enhanced services_
  - _Requirements: 1.1, 1.2_

- [ ] 15. Update default handler to remove app dependencies
  - File: backend/bot/handlers/default.py (modify existing)
  - Remove `from app.queries import get_user, is_user_banned`
  - Replace with API calls through enhanced user service
  - Remove bot/filters.py usage (outdated as mentioned)
  - Purpose: Make default handler fully independent
  - _Leverage: enhanced user service, existing handler structure_
  - _Requirements: 1.1, 1.2_

## Bot Application Lifecycle Tasks

- [x] 16. Create bot application factory with HTTP client lifecycle
  - File: backend/bot/app.py (new)
  - Implement bot application factory pattern
  - Initialize HTTP client manager during startup
  - Properly shutdown HTTP client during bot termination
  - Configure dependency injection for services
  - Purpose: Manage bot service lifecycle and dependencies
  - _Leverage: existing runbot.py patterns, FastAPI app factory patterns_
  - _Requirements: 8.1, 8.2_

- [x] 17. Update runbot.py to use application factory
  - File: backend/runbot.py (modify existing)
  - Replace direct initialization with app factory
  - Remove app-specific imports and configurations
  - Add proper graceful shutdown handling
  - Purpose: Clean bot startup with proper lifecycle management
  - _Leverage: existing bot initialization logic_
  - _Requirements: 8.1, 8.2_

- [ ] 18. Remove outdated bot components
  - File: backend/bot/filters.py (remove or clean up)
  - Remove outdated filter implementations as mentioned
  - Clean up any unused imports or dependencies
  - Update handlers to not use outdated filters
  - Purpose: Clean up deprecated code and reduce maintenance burden
  - _Leverage: current handler implementations_
  - _Requirements: Code cleanliness_

## Testing Infrastructure Tasks

- [ ] 19. Create bot service unit tests
  - File: backend/tests/bot/test_http_client.py (new)
  - File: backend/tests/bot/test_user_service.py (new)
  - File: backend/tests/bot/test_match_service.py (new)
  - Test HTTP client manager lifecycle and connection pooling
  - Test enhanced services with mocked API responses
  - Test error handling and retry mechanisms
  - Purpose: Ensure bot services work correctly in isolation
  - _Leverage: httpx-mock library, existing test patterns_
  - _Requirements: 7.1, 7.2_

- [ ] 20. Create bot schema validation tests
  - File: backend/tests/bot/test_schemas.py (new)
  - Test bot schema validation with independent validators
  - Test schema compatibility with API responses
  - Test edge cases and error scenarios
  - Purpose: Ensure bot schemas work independently and remain API-compatible
  - _Leverage: existing test patterns in tests/api/_
  - _Requirements: 7.1, 7.2_

- [ ] 21. Create bot handler integration tests
  - File: backend/tests/bot/test_handlers.py (new)
  - Test handlers with mocked HTTP client responses
  - Test user flows through bot handlers
  - Test error scenarios and fallback behavior
  - Purpose: Ensure handlers work correctly with API service separation
  - _Leverage: aiogram test utilities, httpx-mock_
  - _Requirements: 7.2, 7.3_

- [ ] 22. Enhance API service tests for bot authentication
  - File: backend/tests/api/ (modify existing tests)
  - Ensure existing tests cover internal token authentication paths
  - Test API endpoints with bot-style requests (internal token + telegram ID)
  - Verify API response formats match bot schema expectations
  - Purpose: Ensure API service continues to work correctly for bot clients
  - _Leverage: existing tests/api/conftest.py patterns_
  - _Requirements: 7.2, 7.3_

## Containerization Tasks

- [ ] 23. Create bot service Dockerfile
  - File: backend/Dockerfile.bot (new)
  - Create optimized Dockerfile for bot service only
  - Exclude API-specific dependencies (sqlalchemy, fastapi, sqladmin)
  - Include only bot dependencies (aiogram, httpx, motor)
  - Optimize image size and startup time
  - Purpose: Enable independent deployment of bot service
  - _Leverage: existing Dockerfile patterns_
  - _Requirements: 5.1, 5.2_

- [ ] 24. Create API service Dockerfile
  - File: backend/Dockerfile.api (new)
  - Create optimized Dockerfile for API service only
  - Exclude bot-specific dependencies (aiogram)
  - Include web service optimizations (uvicorn, fastapi)
  - Configure for high-throughput web serving
  - Purpose: Enable independent deployment of API service
  - _Leverage: existing Dockerfile patterns_
  - _Requirements: 5.1, 5.2_

- [ ] 25. Create docker-compose configuration
  - File: backend/docker-compose.yml (modify existing or new)
  - Define separate services for bot and API
  - Configure environment variables for each service
  - Set up service networking and dependencies
  - Add health checks for both services
  - Purpose: Enable local development and testing of separated services
  - _Leverage: existing Docker configuration patterns_
  - _Requirements: 5.3_

## Configuration and Environment Tasks

- [ ] 26. Create separate environment files
  - File: backend/.env.bot (new)
  - File: backend/.env.api (new)
  - Split current environment variables between services
  - Ensure no shared configuration dependencies
  - Document required environment variables for each service
  - Purpose: Enable independent configuration management
  - _Leverage: existing example.env patterns_
  - _Requirements: 5.4_

- [ ] 27. Update CI/CD configuration for dual services
  - File: .github/workflows/ or similar CI configuration
  - Configure separate build and test pipelines for bot and API
  - Add parallel testing for both services
  - Configure separate deployment strategies
  - Purpose: Enable independent development and deployment workflows
  - _Leverage: existing CI/CD patterns_
  - _Requirements: 5.3_

## Final Integration and Testing Tasks

- [ ] 28. End-to-end integration testing
  - File: backend/tests/integration/test_bot_api_separation.py (new)
  - Test complete user registration flow (bot → API → database)
  - Test profile updates and media handling flows
  - Test matching and reaction flows
  - Test error scenarios and recovery mechanisms
  - Purpose: Ensure separated services work together correctly
  - _Leverage: existing integration test patterns, docker-compose for testing_
  - _Requirements: 7.3_

- [ ] 29. Performance testing and optimization
  - File: backend/tests/performance/ (new directory and tests)
  - Test HTTP connection pool performance vs individual connections
  - Load test API endpoints with bot-like traffic patterns
  - Monitor memory usage and connection efficiency
  - Purpose: Verify performance improvements from connection pooling
  - _Leverage: pytest-benchmark, load testing tools_
  - _Requirements: Performance goals_

- [ ] 30. Documentation and deployment guide
  - File: backend/docs/deployment.md (new)
  - File: backend/docs/separation-guide.md (new)
  - Document new deployment process for separated services
  - Create troubleshooting guide for common issues
  - Document environment variable requirements
  - Purpose: Enable smooth deployment and maintenance of separated services
  - _Leverage: existing documentation patterns_
  - _Requirements: All requirements_

## Code Cleanup and Legacy Removal Tasks

- [ ] 31. Clean up unused imports and dependencies
  - Files: All modified bot files
  - Remove unused imports after separation
  - Update pyproject.toml to separate bot and API dependencies
  - Clean up any orphaned utility functions
  - Purpose: Reduce maintenance burden and improve code clarity
  - _Leverage: automated import checking tools_
  - _Requirements: Code maintenance_

- [ ] 32. Update logging configuration for separated services
  - File: backend/bot/logging.py (new)
  - File: backend/app/logging.py (enhance existing)
  - Configure independent logging for each service
  - Add request correlation IDs for tracing
  - Ensure no sensitive data leakage in logs
  - Purpose: Improve debugging and monitoring capabilities
  - _Leverage: existing logging patterns_
  - _Requirements: Security and monitoring_