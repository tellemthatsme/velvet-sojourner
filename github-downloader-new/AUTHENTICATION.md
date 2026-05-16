# GitHub Authentication Methods

This document describes all authentication methods supported by GitHub Repo Downloader.

## 1. Personal Access Token (PAT) - Recommended

### Create a PAT:
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Select scopes: `repo` (full control of private repositories)
4. Copy the token

### Using the token:

**GUI:**
- Open app → Account → GitHub Authentication
- Enter your PAT

**CLI:**
```bash
python main.py --cli download --url owner/repo -t ghp_your_token_here
```

**Environment variable:**
```bash
set GITHUB_TOKEN=ghp_your_token_here
python main.py --cli download --url owner/repo
```

---

## 2. OAuth2 (Alternative)

### Setup OAuth App:
1. Go to GitHub → Settings → Developer settings → OAuth Apps → New OAuth App
2. Set Authorization callback URL: `http://localhost:8080/callback`
3. Copy Client ID and Client Secret

### Using OAuth:

**GUI:**
- Open app → Account → GitHub Authentication
- Select "OAuth" tab
- Enter Client ID and Secret

**Environment variables:**
```bash
set GITHUB_CLIENT_ID=your_client_id
set GITHUB_CLIENT_SECRET=your_client_secret
```

---

## 3. GitHub CLI (gh auth)

If you have GitHub CLI installed and authenticated:
```bash
gh auth login
```

The app will detect and use your GitHub CLI session.

---

## 4. SSH Key (For Git Clone Only)

For git clone operations, you can use SSH keys:

```bash
# Add your key to ssh-agent
ssh-add ~/.ssh/id_ed25519

# Ensure ~/.ssh/config has:
Host github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

The app will use SSH automatically if available.

---

## Authentication Comparison

| Method | Private Repos | Public Repos | Setup Difficulty |
|--------|---------------|--------------|------------------|
| PAT (Classic) | ✅ Yes | ✅ Yes | Easy |
| OAuth2 | ✅ Yes | ✅ Yes | Medium |
| GitHub CLI | ✅ Yes | ✅ Yes | Easy |
| SSH | ✅ Yes | ✅ Yes | Medium |

---

## Rate Limits by Authentication

| Method | Rate Limit |
|--------|------------|
| Unauthenticated | 60/hour |
| PAT/OAuth | 5,000/hour |
| GitHub CLI | 5,000/hour |

**Note:** The app uses 80% safety margin (4,000 requests max for authenticated).

---

## Security Best Practices

1. **Never commit tokens** to version control
2. **Use environment variables** for tokens in CI/CD
3. **Rotate tokens regularly**
4. **Use minimal scopes** - only `repo` for repository access
5. **Delete unused tokens**

---

## Troubleshooting

**"Authentication Failed" error:**
- Verify token is valid and has `repo` scope
- Check token hasn't expired
- Ensure no trailing spaces in token

**"Rate limit exceeded":**
- You're making too many requests
- Wait for rate limit to reset
- Consider reducing concurrency

**"Permission denied" for private repo:**
- Token doesn't have `repo` scope
- You don't have access to the repository
- Token belongs to a different account
