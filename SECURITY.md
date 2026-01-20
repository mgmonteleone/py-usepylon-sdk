# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.3.x   | :white_check_mark: |
| 0.2.x   | :white_check_mark: |
| < 0.2   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please report security issues via one of these methods:

1. **GitHub Security Advisories** (preferred):
   - Go to the [Security tab](https://github.com/mgmonteleone/py-usepylon-sdk/security)
   - Click "Report a vulnerability"
   - Provide details about the vulnerability

2. **Email**:
   - Send an email to the maintainers
   - Include "SECURITY" in the subject line

### What to Include

Please include the following information:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)
- Your contact information for follow-up

### Response Timeline

- **Initial response**: Within 48 hours
- **Status update**: Within 7 days
- **Resolution target**: Within 30 days (depending on severity)

### What to Expect

1. We will acknowledge receipt of your report
2. We will investigate and validate the issue
3. We will work on a fix and coordinate disclosure
4. We will credit you (unless you prefer anonymity)

## Security Best Practices

When using this SDK:

### API Key Management

- **Never commit API keys** to version control
- Use environment variables for credentials
- Rotate API keys periodically
- Use the minimum necessary permissions

```python
import os
from pylon import PylonClient

# Good: Load from environment
client = PylonClient(api_key=os.environ["PYLON_API_KEY"])

# Bad: Hardcoded key
# client = PylonClient(api_key="pk_live_...")
```

### Webhook Security

- Always verify webhook signatures
- Use HTTPS endpoints only
- Validate timestamp to prevent replay attacks

```python
from pylon.webhooks import WebhookHandler

handler = WebhookHandler(
    secret=os.environ["PYLON_WEBHOOK_SECRET"],
    require_timestamp=True  # Enable replay protection
)
```

## Known Security Considerations

- This SDK transmits data over HTTPS
- Webhook signatures use HMAC-SHA256
- Timing-safe comparison prevents timing attacks

## Dependencies

We regularly update dependencies to address security vulnerabilities. Run `uv lock --upgrade` to get the latest compatible versions.

