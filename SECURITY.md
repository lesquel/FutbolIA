# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in GoalMind, please report it responsibly.

### How to Report

1. **Do NOT** open a public GitHub issue for security vulnerabilities
2. Send an email to the project maintainers via the contact information in their GitHub profiles
3. Or use [GitHub's private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability)

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Assessment**: Within 1 week
- **Fix**: Depends on severity, typically within 2 weeks for critical issues

### What to Expect

- A confirmation that we received your report
- An assessment of the vulnerability and its severity
- A timeline for the fix
- Credit in the release notes (unless you prefer to remain anonymous)

## Security Best Practices for Contributors

- Never commit API keys, secrets, or credentials
- Use `.env.example` as template — never commit `.env` files
- Always validate and sanitize user input
- Use parameterized queries for database operations
- Keep dependencies up to date

## Known Security Considerations

- **JWT_SECRET_KEY**: Must be set via environment variable in production (the app will refuse to start without it)
- **DEEPSEEK_API_KEY**: Store securely, never expose in client-side code
- **FOOTBALL_DATA_API_KEY**: Free tier key, but should still be kept private
- **MongoDB**: Use authentication in production deployments
