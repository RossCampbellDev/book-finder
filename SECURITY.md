# Security Features Documentation

This document outlines all the security features that have been implemented in the Book Finder application.

## Overview

The application now includes comprehensive security measures to protect against common web vulnerabilities and attacks.

## Security Features Implemented

### 1. Brute Force Protection

**Location:** `app/routes/store_routes.py`, `app/utils/login_attempts.py`

- **Account Lockout Mechanism:**
  - Maximum 5 failed login attempts within 30 minutes
  - Account locked for 15 minutes after exceeding limit
  - Failed attempts tracked by email address and IP
  - Successful login clears failed attempt history
  - Auto-cleanup of old attempt records after 30 days

- **User Feedback:**
  - Shows remaining attempts after failed login
  - Displays lockout duration when account is locked
  - Clear error messages without revealing whether email exists

### 2. Denial of Service (DoS) Protection

**Location:** `app/__init__.py`, all route files

- **Rate Limiting (Flask-Limiter):**
  - Global limits: 200 requests/day, 50 requests/hour per IP
  - Login endpoint: 10 requests/minute
  - Registration endpoint: 5 requests/hour
  - Search endpoint: 30 requests/minute
  - Autocomplete endpoint: 60 requests/minute
  - Book add endpoint: 20 requests/hour
  - Memory-based storage for development (can be upgraded to Redis for production)

- **Input Validation:**
  - Maximum string lengths enforced
  - Query parameter validation (coordinates, distances, limits)
  - Prevents excessive database queries

### 3. NoSQL Injection Prevention

**Location:** `app/utils/security.py`, all route files

- **Input Sanitization:**
  - All user inputs sanitized before database queries
  - MongoDB operator detection ($where, $ne, $regex, etc.)
  - Rejection of complex types (dicts, lists) in user input
  - String-based queries only with whitelisted patterns

- **Parameterized Queries:**
  - All MongoDB queries use sanitized inputs
  - No string concatenation in queries
  - Strict type validation for query parameters

### 4. Duplicate Username/Email Prevention

**Location:** `app/routes/store_routes.py`

- **Email Uniqueness:**
  - Unique index on email field in MongoDB
  - Pre-registration check for existing emails
  - Normalized email addresses (lowercase, validated format)
  - Clear error messages for duplicate registrations

### 5. Password Security

**Location:** `app/routes/store_routes.py`, `app/utils/security.py`

- **Password Requirements:**
  - Minimum 8 characters, maximum 128 characters
  - Must contain: uppercase, lowercase, digit, special character
  - Common password blacklist (20 most common passwords)
  - Password strength validation before registration

- **Password Storage:**
  - bcrypt hashing with automatic salting
  - Passwords never stored in plain text
  - Secure password comparison using bcrypt.checkpw

### 6. CSRF Protection

**Location:** `app/__init__.py`

- **Flask-WTF CSRF Protection:**
  - Automatic CSRF token generation
  - Token validation on all POST/PUT/DELETE requests
  - Integration with all forms

### 7. Security Headers

**Location:** `app/__init__.py`

- **Flask-Talisman Headers:**
  - **Production Mode:**
    - Force HTTPS enabled
    - Strict-Transport-Security header
    - Content Security Policy (CSP) configured
  - **Development Mode:**
    - HTTPS not forced (for local development)
    - Relaxed CSP for debugging

- **Content Security Policy:**
  - `default-src`: 'self' (only load from same origin)
  - `script-src`: 'self', CDN for external libraries
  - `style-src`: 'self', CDN for external styles
  - `img-src`: 'self', data URIs, HTTPS sources

### 8. Session Security

**Location:** `app/__init__.py`

- **Secure Cookie Configuration:**
  - `SESSION_COOKIE_SECURE`: True in production (HTTPS only)
  - `SESSION_COOKIE_HTTPONLY`: True (prevents JavaScript access)
  - `SESSION_COOKIE_SAMESITE`: 'Lax' (CSRF protection)
  - Session timeout: 1 hour (3600 seconds)

- **Secret Key Management:**
  - Auto-generated secure random key if not configured
  - 32-byte hexadecimal secret key
  - Should be set via environment variable in production

### 9. Input Validation

**Location:** `app/utils/security.py`, all route files

- **Comprehensive Validation:**
  - Email format validation (RFC-compliant)
  - ISBN format validation (ISBN-10 and ISBN-13)
  - Latitude/longitude validation (-90 to 90, -180 to 180)
  - Quantity validation (0 to 1,000,000)
  - URL validation (must start with http:// or https://)
  - String length validation with configurable limits

- **Whitelist Approach:**
  - Store types: bookstore, library, thrift
  - Search types: isbn, title, author, all
  - Book conditions: new, like_new, good, acceptable, poor
  - Only whitelisted values accepted

### 10. Error Handling

**Location:** All route files

- **Graceful Error Handling:**
  - Try-catch blocks around all user inputs
  - Generic error messages to users (no system details)
  - Specific validation errors for user corrections
  - Proper HTTP status codes (400 for validation, 500 for server errors)

- **Information Disclosure Prevention:**
  - No stack traces exposed to users
  - No database error details in responses
  - Generic error messages for security-sensitive operations

## Additional Security Measures

### 11. Authentication & Authorization

- **Flask-Login Integration:**
  - Secure session management
  - @login_required decorators on protected routes
  - User identity verification on all authenticated operations

### 12. Database Security

- **MongoDB Indexes:**
  - Unique indexes prevent duplicates
  - TTL index on login_attempts for automatic cleanup
  - Optimized queries reduce DoS risk

## Dependencies Added

```toml
flask-limiter>=3.5.0      # Rate limiting
flask-wtf>=1.2.1          # CSRF protection
flask-talisman>=1.1.0     # Security headers
email-validator>=2.1.0    # Email validation
bcrypt>=4.1.2            # Password hashing
```

## Usage Instructions

### Installation

1. Install dependencies:
```bash
pip install -e .
```

### Configuration

Set these environment variables for production:

```bash
# Flask configuration
export FLASK_ENV=production
export SECRET_KEY=your-secure-random-secret-key

# MongoDB configuration
export MONGO_URI=mongodb://localhost:27017/
export MONGO_DB_NAME=bookfinder
```

### Testing Security Features

1. **Test Rate Limiting:**
   - Try logging in more than 10 times per minute
   - Try registering more than 5 times per hour

2. **Test Account Lockout:**
   - Enter wrong password 5 times
   - Verify account is locked for 15 minutes

3. **Test Input Validation:**
   - Try entering invalid emails
   - Try weak passwords
   - Try MongoDB operators in search queries

4. **Test CSRF Protection:**
   - Try submitting forms without CSRF tokens
   - Verify requests are rejected

## Security Best Practices for Production

1. **Use HTTPS:** Always use HTTPS in production (enforced by Talisman)
2. **Set SECRET_KEY:** Use a strong, random secret key from environment variable
3. **Use Redis for Rate Limiting:** Replace memory:// with redis://localhost:6379
4. **Monitor Login Attempts:** Set up alerts for unusual login patterns
5. **Regular Updates:** Keep all dependencies updated for security patches
6. **Database Backups:** Regular backups with encryption
7. **Log Monitoring:** Monitor logs for suspicious activity

## Security Checklist

- [x] Brute force protection (account lockout)
- [x] DoS protection (rate limiting)
- [x] NoSQL injection prevention (input sanitization)
- [x] Duplicate email prevention (unique indexes)
- [x] Password strength requirements
- [x] Password hashing (bcrypt)
- [x] CSRF protection
- [x] Security headers (HTTPS, CSP, etc.)
- [x] Secure sessions (HttpOnly, Secure, SameSite)
- [x] Input validation (all forms and queries)
- [x] Error handling (no information disclosure)
- [x] Authentication/Authorization (Flask-Login)

## Files Modified

1. `pyproject.toml` - Added security dependencies
2. `app/__init__.py` - Added security extensions initialization
3. `app/utils/security.py` - NEW: Security validation utilities
4. `app/utils/login_attempts.py` - NEW: Login attempt tracking
5. `app/utils/database.py` - Added login_attempts collection
6. `app/routes/store_routes.py` - Added security to auth routes
7. `app/routes/search_routes.py` - Added input sanitization
8. `app/routes/book_routes.py` - Added input validation

## Support

For security issues or questions, refer to the code comments in each security module or contact the development team.
