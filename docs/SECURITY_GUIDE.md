# AgentForge — Security Guide

**Last updated:** 2026-05-17

---

## Lessons Learned: 837 Exposed Tokens

During the repo collection, we discovered **837 repositories** had GitHub tokens exposed in their `.git/config` files as plaintext in remote URLs:

```
# Before (INSECURE)
url = https://ghp_xxxxxxxxxxxx@github.com/user/repo.git

# After (SECURE)
url = https://github.com/user/repo.git
```

**Key takeaways:**
- Never embed tokens in URLs
- Use credential managers or environment variables
- Audit your own repos for exposed tokens
- Rotate any token you've ever put in a URL

---

## Token Handling Best Practices

### DO:
```bash
# Use environment variables
export GITHUB_TOKEN=your_token_here
git config --global credential.helper store

# Use GitHub CLI (handles auth securely)
gh auth login

# Use SSH keys
git clone git@github.com:user/repo.git
```

### DON'T:
```bash
# Never embed tokens in URLs
git clone https://ghp_TOKEN@github.com/user/repo.git

# Never commit .env files
git add .env  # BAD

# Never log tokens
print(f"Using token: {token}")  # BAD
```

---

## Environment Variable Security

### .env File Management

```env
# .env.example (safe to commit)
LITELLM_MASTER_KEY=sk-change-me
WEBUI_SECRET_KEY=change-me
N8N_PASSWORD=change-me
DEPLOYER_SECRET=change-me
GRAFANA_PASSWORD=change-me

# .env (NEVER commit)
LITELLM_MASTER_KEY=sk-actual-secret-key
WEBUI_SECRET_KEY=actual-secret-key
```

### .gitignore Rules

```gitignore
.env
.env.local
.env.production
*.key
*.pem
*.secret
```

---

## Docker Security

### Container Isolation

```yaml
# Good: Services on separate networks
networks:
  frontend:
  backend:
  database:

services:
  traefik:
    networks: [frontend]
  deployer:
    networks: [frontend, backend]
  postgres:
    networks: [backend, database]
```

### Secrets Management

```yaml
# Use Docker secrets instead of environment variables for sensitive data
services:
  postgres:
    secrets:
      - db_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

### Container User

```dockerfile
# Don't run as root
RUN useradd -m appuser
USER appuser
```

---

## API Security

### Deployer API Authentication

```python
# Always require API keys for sensitive endpoints
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.environ["DEPLOYER_SECRET"]:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
```

### Rate Limiting

```python
# Implement rate limiting to prevent abuse
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/deploy")
@limiter.limit("10/minute")
async def deploy_repo(request: Request):
    ...
```

### Input Validation

```python
# Always validate inputs
from pydantic import BaseModel, validator

class DeployRequest(BaseModel):
    repo: str
    port: int

    @validator('repo')
    def repo_must_be_safe(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Invalid repo name')
        return v
```

---

## Stripe Integration Security

### Webhook Verification

```python
# Always verify Stripe webhook signatures
import stripe

stripe_webhook_secret = os.environ["STRIPE_WEBHOOK_SECRET"]

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_webhook_secret
        )
    except stripe.error.SignatureVerificationError:
        return {"error": "Invalid signature"}
```

### PCI Compliance

- Never store credit card numbers
- Use Stripe Checkout or Elements
- Let Stripe handle all payment data
- Only store Stripe customer IDs

---

## Form Submission Security

### Formsubmit.co

- Uses POST to external service
- First submission requires email verification
- No sensitive data in form fields
- Consider self-hosted alternative for production

### Best Practices

```html
<!-- Use HTTPS forms only -->
<form action="https://formsubmit.co/your@email.com" method="POST">
  <!-- Add honeypot to prevent spam -->
  <input type="text" name="_honey" style="display:none">
  <!-- Disable captcha if you have your own -->
  <input type="hidden" name="_captcha" value="false">
</form>
```

---

## Data Privacy

### What We Collect

| Data Type | Purpose | Retention |
|-----------|---------|-----------|
| Email address | Product delivery, support | Duration of relationship + 12 months |
| Name | Consulting services | Duration of engagement |
| Usage analytics | Site improvement | 26 months (Google Analytics default) |

### What We DON'T Collect

- Passwords (OAuth/third-party auth)
- Credit card numbers (processed by Stripe/Gumroad)
- Browsing history beyond our sites
- Personal messages or communications

### GDPR Compliance

- Right to access: Users can request their data
- Right to deletion: Users can request data removal
- Right to portability: Users can export their data
- Consent: Explicit consent for email marketing

---

## License Compliance

### Understanding Repo Licenses

| License | Commercial Use | Modification | Distribution | Private Use |
|---------|---------------|--------------|--------------|-------------|
| MIT | ✓ | ✓ | ✓ | ✓ |
| Apache 2.0 | ✓ | ✓ | ✓ | ✓ |
| GPL v3 | ✓ | ✓ | ✓ (must share source) | ✓ |
| CC0 | ✓ | ✓ | ✓ | ✓ |
| No License | ✗ | ✗ | ✗ | ✗ |

### Our Responsibility

1. **Document license for every repo** — Done via QA check #3
2. **Flag commercial-safe repos** — MIT, Apache 2.0, CC0
3. **Warn about restricted repos** — GPL, custom licenses
4. **Don't redistribute code** — We sell analysis, not code

### Customer Responsibility

1. Check license before using any repo commercially
2. Comply with license terms (attribution, source sharing)
3. Contact original authors for unclear licenses
4. Enterprise tier includes redistribution rights for our analysis

---

## Secure Deployment Checklist

- [ ] All .env files excluded from git
- [ ] Docker secrets used for sensitive data
- [ ] API endpoints require authentication
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] HTTPS enforced (Traefik SSL)
- [ ] Firewall configured (only 80, 443, 22 open)
- [ ] SSH key-only authentication
- [ ] Regular security updates scheduled
- [ ] Automated backups configured
- [ ] Stripe webhooks verified
- [ ] No tokens in URLs or logs
