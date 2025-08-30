# Requirements Document

## Introduction

This feature involves separating the Telegram dating bot from the API service into completely independent services. Currently, the bot directly accesses database models and shared utilities from the app folder, creating tight coupling. The goal is to create a clean architectural separation where the bot communicates with the API service through HTTP requests only, enabling independent deployment, scaling, and development of both services.

## Alignment with Product Vision

This separation supports scalability and maintainability goals by:
- Enabling independent deployment and scaling of bot and API services
- Supporting multiple client types (Telegram bot, web app, mobile app) through a unified API
- Improving development velocity through service isolation
- Reducing deployment risks by containerizing services separately

## Requirements

### Requirement 1

**User Story:** As a developer, I want the Telegram bot to be completely independent from the API service, so that I can deploy, scale, and maintain them separately without affecting each other.

#### Acceptance Criteria

1. WHEN the bot starts THEN it SHALL NOT import any modules from the app folder
2. WHEN the bot performs any data operation THEN it SHALL communicate with the API service via HTTP requests only
3. WHEN the API service is updated THEN the bot SHALL continue to function without code changes (assuming API compatibility)
4. WHEN the bot is deployed THEN it SHALL have its own Dockerfile and container configuration

### Requirement 2

**User Story:** As a developer, I want the bot to have its own database configuration and connection management, so that it can operate independently from the API service's database layer.

#### Acceptance Criteria

1. WHEN the bot needs database access for FSM storage THEN it SHALL use MongoDB directly for session management only
2. WHEN the bot needs user data THEN it SHALL request it from the API service via HTTP
3. WHEN the bot configuration is loaded THEN it SHALL NOT depend on app.core.config
4. IF the API service database is unavailable THEN the bot's session storage SHALL continue to work

### Requirement 3

**User Story:** As a developer, I want the bot to use a single HTTP client with connection pooling, so that API communication is efficient and performant.

#### Acceptance Criteria

1. WHEN the bot starts THEN it SHALL initialize a single httpx.AsyncClient instance with connection pooling
2. WHEN the bot shuts down THEN it SHALL properly close the HTTP client and release resources
3. WHEN making multiple API requests THEN they SHALL reuse connections from the pool for better performance
4. WHEN API requests fail THEN the bot SHALL handle errors gracefully with appropriate user feedback
5. WHEN making API requests THEN the bot SHALL include proper authentication headers

### Requirement 4

**User Story:** As a developer, I want the bot to have its own data models and schemas, so that it doesn't depend on the API service's internal data structures.

#### Acceptance Criteria

1. WHEN the bot processes data THEN it SHALL use its own Pydantic models that match API responses
2. WHEN the API response format changes THEN only the bot's schemas SHALL need updating
3. WHEN the bot validates input THEN it SHALL use its own validation functions
4. WHEN the bot handles media THEN it SHALL use its own file handling utilities

### Requirement 5

**User Story:** As a system administrator, I want both services to have separate Docker containers, so that I can deploy, monitor, and scale them independently.

#### Acceptance Criteria

1. WHEN deploying the bot THEN it SHALL have its own Dockerfile optimized for the bot service
2. WHEN deploying the API THEN it SHALL have its own Dockerfile optimized for the web service
3. WHEN using docker-compose THEN both services SHALL be defined as separate containers
4. WHEN one service fails THEN the other service SHALL continue to operate independently

### Requirement 6

**User Story:** As a developer, I want shared utilities and enums to be duplicated or accessed via API, so that there are no cross-service dependencies.

#### Acceptance Criteria

1. WHEN the bot needs common enums THEN it SHALL either duplicate them or fetch them from the API
2. WHEN the bot needs validation functions THEN it SHALL have its own implementation
3. WHEN the bot needs utility functions THEN it SHALL have its own bot-specific utilities
4. WHEN common functionality changes THEN updates SHALL be made independently in each service

### Requirement 7

**User Story:** As a developer, I want both services to have comprehensive test coverage, so that I can confidently make changes and deploy updates without breaking functionality.

#### Acceptance Criteria

1. WHEN the bot service is tested THEN it SHALL have unit tests for all handler functions, services, and utilities
2. WHEN the API service is tested THEN it SHALL have unit tests for all endpoints, services, and business logic
3. WHEN testing bot-API communication THEN there SHALL be integration tests with mocked API responses
4. WHEN testing API endpoints THEN there SHALL be integration tests with test database
5. WHEN running tests THEN both services SHALL achieve minimum 80% code coverage
6. WHEN tests are executed THEN they SHALL run independently for each service without cross-dependencies

### Requirement 8

**User Story:** As a developer, I want the bot to have proper HTTP client lifecycle management, so that connections are efficiently managed and resources are not leaked.

#### Acceptance Criteria

1. WHEN the bot application starts THEN it SHALL create a single httpx.AsyncClient instance during startup
2. WHEN the bot application stops THEN it SHALL properly await client.aclose() to clean up connections
3. WHEN configuring the HTTP client THEN it SHALL use appropriate timeout settings and connection limits
4. WHEN the bot makes concurrent API requests THEN they SHALL share the connection pool efficiently
5. WHEN monitoring the bot THEN connection pool metrics SHALL be available for debugging

## Non-Functional Requirements

### Code Architecture and Modularity
- **Single Responsibility Principle**: Bot service handles only Telegram interactions, API service handles business logic and data persistence
- **Modular Design**: Each service should have clear boundaries with no shared code dependencies
- **Dependency Management**: Bot should only depend on Telegram bot libraries and HTTP clients, not on SQLAlchemy or API-specific packages
- **Clear Interfaces**: HTTP API contracts should be well-defined and versioned
- **Testability**: All components should be designed for easy unit testing with dependency injection

### Performance
- HTTP communication between bot and API should add minimal latency (<100ms for typical requests)
- Bot should implement appropriate caching for frequently accessed data
- Database connections should be optimized per service (MongoDB for bot sessions, PostgreSQL for API data)
- Single HTTP client with connection pooling should reduce connection overhead by 50-80%
- Connection pool should handle at least 100 concurrent connections efficiently

### Security
- All bot-to-API communication must be authenticated with internal tokens
- Sensitive data should not be logged in bot service
- Bot should validate all user inputs before sending to API
- HTTP client should enforce proper SSL/TLS verification

### Reliability
- Bot should gracefully handle API service unavailability
- Services should have independent health checks and monitoring
- Failed API requests should be retried with exponential backoff
- HTTP client should have appropriate timeout configurations to prevent hanging requests

### Testing
- Both services must achieve minimum 80% test coverage
- Unit tests should run in under 30 seconds for each service
- Integration tests should use test databases and mock external services
- Tests should be runnable independently without cross-service dependencies
- CI/CD pipeline should run tests for both services in parallel

### Usability
- Bot users should experience no functionality changes during the separation
- Error messages should be user-friendly even when API errors occur
- Bot response times should remain consistent or improve