# Code Review Criteria

Detailed criteria for Gemini code review. This reference is loaded when deeper analysis is needed.

## Security Checks

### Critical (Must Fix)
- **SQL/NoSQL Injection**: Raw query concatenation, unsanitized user input
- **XSS Vulnerabilities**: Unescaped output, innerHTML with user data
- **Hardcoded Secrets**: API keys, passwords, tokens in source code
- **Authentication Bypass**: Missing auth checks, broken session handling
- **Path Traversal**: Unsanitized file paths, directory access

### High Priority
- **CSRF Vulnerabilities**: Missing tokens on state-changing operations
- **Insecure Deserialization**: Unpickling/unmarshaling untrusted data
- **Command Injection**: Shell command construction with user input
- **SSRF Risks**: Unvalidated URL fetching
- **Broken Access Control**: Missing authorization checks

## Performance Checks

### Critical
- **O(n²) or worse** on potentially large datasets
- **Memory leaks**: Unclosed resources, accumulating listeners
- **Blocking operations** in async contexts
- **Unbounded queries**: Missing LIMIT, fetching entire tables

### High Priority
- **N+1 query patterns**: Loop with database calls
- **Unnecessary re-renders**: Missing memoization in React
- **Large bundle imports**: Importing entire libraries for one function
- **Synchronous file I/O** in request handlers
- **Missing indexes**: Queries on unindexed columns

## Code Quality Checks

### Structure
- **Function length**: >50 lines is a warning, >100 is critical
- **Cyclomatic complexity**: >10 is concerning, >20 is critical
- **Nesting depth**: >4 levels of nesting
- **File length**: >500 lines suggests splitting needed

### Maintainability
- **Duplicate code**: >10 lines repeated
- **Magic numbers**: Unexplained numeric literals
- **Dead code**: Unreachable or unused code paths
- **Missing error handling**: Unhandled promise rejections, empty catch blocks
- **Inconsistent naming**: Mixed conventions in same file

### Best Practices
- **SOLID violations**: God classes, tight coupling
- **Missing types**: Any abuse in TypeScript, missing type hints in Python
- **Hardcoded values**: Should be constants or config
- **Console/print statements**: Left in production code

## Language-Specific Criteria

### Python
- Type hints on public functions
- Docstrings on public APIs
- Context managers for resources (`with` statements)
- f-strings over `.format()` or `%`
- List comprehensions where appropriate

### TypeScript/JavaScript
- Strict null checks
- No `any` without justification
- Async/await over raw promises
- Proper error boundaries (React)
- Immutable patterns where appropriate

### Go
- Proper error handling (no ignored errors)
- Context propagation
- Defer for cleanup
- Goroutine leak prevention
- Interface segregation

### Rust
- Proper Result/Option handling
- Lifetime annotations where needed
- No unsafe without justification
- Proper error types

## Review Priority Matrix

| Severity | Response Time | Examples |
|----------|---------------|----------|
| Critical | Immediate fix | Security vulnerabilities, data loss risks |
| High | Same session | Performance issues, missing validation |
| Medium | Next iteration | Code quality, missing types |
| Low | When convenient | Style issues, documentation |

## Positive Patterns to Recognize

- Clean separation of concerns
- Proper error handling with context
- Good test coverage
- Clear naming and documentation
- Efficient algorithms
- Security-conscious patterns
- Proper resource management
