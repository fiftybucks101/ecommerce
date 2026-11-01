# Feature Testing Specifications

## 1. Purpose

This document defines the project-wide testing standards for the e-commerce application.

Whenever a feature is implemented or modified, the AI coding agent must use this document to independently determine the appropriate testing strategy, identify test scenarios, generate automated test scripts, execute them, and report the results.

The objective is to maintain consistent testing standards across all application features without requiring feature-specific testing instructions every time.

## 2. General Testing Principles

All automated testing must follow these principles:

1. Tests must reflect the actual implementation, requirements, and expected business behavior.
2. Cover successful scenarios (positive testing) and failure scenarios (negative testing).
3. Verify business rules, input validation, authorization, and data integrity.
4. Verify API responses and database changes where applicable.
5. Tests must be independent, repeatable, and predictable.
6. Avoid unnecessary duplication of test cases.
7. Never weaken assertions or modify expected behavior simply to make tests pass.
8. Inspect existing testing utilities and infrastructure before creating new ones.
9. Follow the existing project architecture and coding conventions.

## 3. Types of Testing

The agent must identify which testing types are relevant to each feature.

### 3.1 Unit Testing

**Purpose:** Verify individual components independently.

Focus on:
- Service-layer business logic.
- Input and output handling.
- Validation rules.
- Conditional logic and edge cases.
- Exception handling.
- Dependency behavior using mocks or stubs.

Unit tests should isolate the component being tested from external dependencies such as databases, APIs, and other services.

### 3.2 Integration Testing

**Purpose:** Verify that multiple application components work correctly together.

Focus on:
- Router, service, repository, and database interactions.
- API endpoint behavior.
- Database operations and persistence.
- Relationships between database entities.
- Authentication and authorization.
- Application-level exception handling.
- Interactions with dependent modules.

Integration tests should verify that the feature works correctly within the application's actual architecture.

### 3.3 End-to-End Testing

**Purpose:** Verify complete user workflows across multiple application components.

Focus on:
- Complete business workflows.
- Interactions between related features.
- Sequential API operations.
- User-specific operations and permissions.
- Expected final application and database state.

Use end-to-end testing when a feature involves complete workflows or interactions between multiple features.

### 3.4 Additional Testing Where Applicable

The agent should also consider:

- **Security Testing:** Authentication, authorization, access restrictions, and unauthorized operations.
- **Validation Testing:** Missing fields, invalid values, incorrect formats, and boundary conditions.
- **Edge Case Testing:** Empty data, nonexistent records, duplicate operations, and unexpected inputs.
- **Concurrency Testing:** Simultaneous requests, conflicting updates, and race conditions where relevant.

Not every testing type is mandatory for every feature. The agent must select appropriate testing types based on the feature's responsibilities and complexity.

## 4. Test Case Identification

Before generating test scripts, the agent must inspect the feature's implementation and identify its expected behavior.

Review relevant components, including:

- Routers and API endpoints.
- Services and business logic.
- Repositories and database operations.
- Database models and relationships.
- Pydantic schemas and validation rules.
- Authentication and authorization dependencies.
- Interactions with other modules.
- Existing test cases and shared testing utilities.

Identify relevant scenarios using the following categories:

| Area | What to Verify |
|---|---|
| Core Functionality | Main feature operations work correctly. |
| Input Validation | Invalid or incomplete inputs are rejected. |
| Business Logic | Defined business rules are enforced. |
| Database Operations | Records are created, updated, retrieved, and deleted correctly. |
| Data Integrity | Relationships, constraints, and consistency are maintained. |
| Authentication | Protected operations require valid authentication. |
| Authorization | Users can only perform permitted operations. |
| Error Handling | Appropriate errors and HTTP status codes are returned. |
| Edge Cases | Empty, duplicate, missing, and boundary-value scenarios work correctly. |
| Integration | The feature interacts correctly with dependent modules. |

The agent must select scenarios based on actual implementation and requirements rather than blindly applying every category.

## 5. Testing Environment and Database Safety

This section contains mandatory safety requirements.

### 5.1 Dedicated Test Database

Automated tests must use a dedicated test database that is completely separate from development and production databases.

Before executing any test, the agent must:

1. Inspect the existing database configuration and environment variables.
2. Identify the configured test database connection.
3. Verify that the test database exists and that the connection is accessible.
4. Verify that the connected database is the intended test database.
5. Ensure the test database is not the development or production database.

If a dedicated test database does not exist:

- Create one if the agent has the necessary permissions and the database configuration is clear.
- Configure the appropriate test database connection.
- If creation requires additional permissions or information, ask the user instead of making assumptions.

**Absolute restrictions:**

- Never execute automated tests against the development database.
- Never execute automated tests against the production database.
- Never fall back to `DATABASE_URL` when `TEST_DATABASE_URL` is missing.
- Never assume a database is safe simply because its connection variable contains the word `test`.
- Never run destructive database operations until the target database has been verified.

If database isolation cannot be guaranteed, stop test execution and report the issue.

### 5.2 Database Schema and Cleanup

The agent must ensure that the test database has the correct schema before running tests.

- Follow the project's existing database setup and migration strategy.
- Use Alembic migrations when testing migration behavior or when required by the existing testing architecture.
- Ensure test data is isolated and cleaned up after execution.
- Use transaction rollback, database cleanup, or another reliable isolation strategy.
- Ensure one test does not depend on data created by another test.

Do not drop or recreate a database unnecessarily. Destructive schema operations must be restricted to the verified test database.

### 5.3 Environment and External Services

- Use test-specific environment configuration.
- Never expose database passwords, API keys, tokens, or other secrets in test files or reports.
- Avoid calling real external services during automated tests unless explicitly required.
- Mock external dependencies or use dedicated sandbox environments where appropriate.
- Never trigger real payments, emails, notifications, or other irreversible external operations during ordinary automated tests.

## 6. Testing Tools and Project Structure

The application uses Python, FastAPI, SQLAlchemy, PostgreSQL, and `uv`.

Follow the existing project configuration and use:

| Tool | Purpose |
|---|---|
| pytest | Primary testing framework |
| FastAPI TestClient | API integration testing |
| SQLAlchemy | Database testing |
| Mocks and stubs | Dependency isolation in unit tests |
| Fixtures | Reusable testing setup and cleanup |

Suggested project structure:

```text
backend/
│
├── app/
│   └── ...
│
├── tests/
│   ├── conftest.py
│   │
│   ├── unit/
│   │   ├── test_<feature>_service.py
│   │   └── ...
│   │
│   ├── integration/
│   │   ├── test_<feature>.py
│   │   └── ...
│   │
│   └── ...
```

The agent may adjust this structure when necessary but must maintain consistency across features.

### Shared Testing Infrastructure

- Reuse existing fixtures for database sessions, test clients, authentication, and common test data.
- Avoid duplicating shared fixtures across feature-specific test files.
- Keep feature-specific test scenarios in their appropriate test modules.
- Update shared testing utilities only when necessary.
- Maintain compatibility with the existing application architecture.

## 7. Test Implementation Standards

When generating test scripts:

1. Use descriptive test function names that explain the tested behavior.
2. Keep individual tests focused on a specific behavior or expectation.
3. Use fixtures for reusable setup and teardown.
4. Verify response data and relevant database state.
5. Include positive, negative, and boundary test cases where applicable.
6. Avoid dependence on test execution order.
7. Ensure tests can run independently and as part of the complete test suite.
8. Do not hardcode database IDs or depend on existing development records.
9. Follow existing naming conventions and code formatting.
10. Avoid unnecessary duplication and overly complicated test logic.

## 8. Test Execution and Failure Handling

After generating test scripts, the agent must execute them.

Follow this workflow:

1. Run the tests for the current feature.
2. Review all passed, failed, and skipped test cases.
3. Investigate the root cause of each failure.
4. Determine whether the failure originates from the test setup, incorrect test assumptions, or application implementation.
5. Fix confirmed application bugs when they are within the feature's scope.
6. Correct test scripts when their assumptions or implementation are incorrect.
7. Rerun affected tests.
8. Run the broader test suite to identify regressions.

Do not make unrelated application changes without justification or user approval.

The agent must not report successful testing without actually executing the test scripts.

If testing cannot be completed because of missing configuration, dependencies, database access, or another environmental issue, report it explicitly.

## 9. Testing Completion Criteria

Automated testing for a feature is considered complete when:

- Appropriate testing types have been identified.
- Relevant test scenarios have been implemented.
- Core functionality is covered.
- Positive and negative scenarios are covered.
- Relevant business rules and validations are verified.
- Authentication and authorization are tested where applicable.
- Database integrity and persistence are verified where applicable.
- All implemented tests execute successfully.
- No known test failures remain unresolved.
- The broader test suite has been checked for regressions.

Testing completion does not guarantee that every possible bug has been eliminated. It means that the identified requirements and expected behaviors have been verified through the implemented tests.

## 10. Agent Responsibilities and Final Report

After completing testing for a feature, provide a concise report containing:

1. **Feature Tested:** Name of the feature.
2. **Testing Types:** Unit, integration, end-to-end, or additional testing performed.
3. **Test Files Created/Modified:** List of generated or updated files.
4. **Test Coverage:** Main scenarios and behaviors verified.
5. **Execution Results:** Total passed, failed, and skipped tests.
6. **Issues Identified:** Bugs or implementation problems discovered.
7. **Changes Made:** Application or test-related fixes.
8. **Remaining Limitations:** Scenarios not tested and the reasons.

Clearly distinguish between tests that were generated, tests that were executed, and tests that successfully passed.

## 11. General Instruction

This document is a project-wide testing guideline, not a feature-specific test case document.

For every feature, the agent must independently inspect the relevant source code, requirements, architecture, and existing tests before deciding what needs to be tested.

The agent must understand the feature's responsibilities and business rules rather than simply generating generic test scripts.

The objective is to maintain a consistent, reliable, secure, and reusable automated testing strategy throughout the development of the entire e-commerce application.