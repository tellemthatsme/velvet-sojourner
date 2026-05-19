# AgentForge — Troubleshooting Guide

**Last updated:** 2026-05-17

---

## Network Issues

### GitHub Connection Timeout

**Symptom:** `git pull` or `git fetch` hangs indefinitely.

**Cause:** Network firewall or proxy blocking git protocol.

**Solutions:**
1. Try from a different network (home, VPS, mobile hotspot)
2. Set `GIT_TERMINAL_PROMPT=0` to avoid credential prompt hangs
3. Set low-speed timeout:
   ```bash
   export GIT_HTTP_LOW_SPEED_LIMIT=1000
   export GIT_HTTP_LOW_SPEED_TIME=10
   ```
4. Use HTTPS instead of git:// protocol:
   ```bash
   git config --global url."https://".insteadOf git://
   ```

### GHCR (GitHub Container Registry) Unreachable

**Symptom:** `docker pull ghcr.io/...` fails with connection timeout.

**Cause:** GHCR blocked by network firewall.

**Solutions:**
1. Pull images on VPS (usually not blocked)
2. Mirror images from accessible network:
   ```bash
   docker pull ghcr.io/berriai/litellm:main-latest
   docker save ghcr.io/berriai/litellm:main-latest > litellm.tar
   # Transfer to VPS
   docker load < litellm.tar
   ```
3. Comment out GHCR services in docker-compose.yml for local testing

---

## Docker Issues

### Docker Daemon Crashed

**Symptom:** `docker ps` returns error or hangs.

**Solutions:**
```bash
# Windows
net start docker
# May require admin rights

# Linux
sudo systemctl restart docker
sudo systemctl status docker
```

### Container Won't Start

**Symptom:** `docker compose up -d` fails for a specific service.

**Debug:**
```bash
docker compose logs <service-name>
# Look for specific error messages
```

**Common fixes:**
- **Port conflict:** Change port in docker-compose.yml
- **Missing image:** `docker compose pull` first
- **Volume permission:** `sudo chown -R 1000:1000 /path/to/volume`
- **Out of memory:** Stop non-essential services or upgrade VPS

### Deployer API Returns 500

**Symptom:** `curl http://localhost:8000/api/repos` returns 500 error.

**Debug:**
```bash
docker compose logs deployer
```

**Common causes:**
- Database not ready: Wait 30 seconds for Postgres to initialize
- REPOS_DIR not mounted correctly: Check volume mount in docker-compose.yml
- Missing migrations: `docker compose exec deployer python -m alembic upgrade head`

---

## Git Issues

### 19 Repos Behind Remote

**Symptom:** `git status -sb` shows "behind" for some repos.

**Cause:** Upstream has new commits not pulled locally.

**Solutions:**
1. Pull from unrestricted network:
   ```bash
   cd repos/<repo-name>
   git pull --ff-only
   ```
2. If token was stripped (no authentication):
   - Public repos: Should pull without auth
   - Private repos: Need to re-add token or use SSH

### Embedded Git Repos in Git

**Symptom:** `git add` warns about embedded git repositories.

**Cause:** Repos inside repos/ directories have their own .git folders.

**Solution:** Add to .gitignore:
```
repos/
repos_duplicates/
repos_low_quality/
```

### LF/CRLF Warnings

**Symptom:** "LF will be replaced by CRLF the next time Git touches it"

**Cause:** Windows line ending conversion.

**Solution:** Safe to ignore. Or set:
```bash
git config --global core.autocrlf true
```

---

## QA Tool Issues

### All Repos Show as "Dirty"

**Symptom:** QA report shows 840 "dirty" issues, 0 "passed".

**Cause:** Batch enhancement added files that aren't committed.

**Solution:** This is expected behavior. Dirty = uncommitted changes from enhancement. To clean:
```bash
cd repos/<repo-name>
git add -A
git commit -m "Add enhancement files"
```

### License Check False Positives

**Symptom:** QA reports missing licenses when LICENSE file exists.

**Cause:** QA tool doesn't recognize the license type.

**Solution:** QA tool now recognizes:
- MIT
- Apache 2.0
- GPL (v2, v3)
- CC0
- Creative Commons
- Community License

If still failing, check LICENSE file content matches expected format.

### Zero-Byte File False Positives

**Symptom:** QA reports zero-byte files that are actually fine.

**Cause:** Some zero-byte files are intentional.

**Solution:** QA tool now ignores:
- `.gitkeep`
- `__init__.py`
- `.nojekyll`
- `.DS_Store`
- Files in `.git/` directory

---

## EXE Build Issues

### PyInstaller Build Fails

**Symptom:** `python build_cli_exe.py` fails with import error.

**Solutions:**
```bash
pip install --upgrade pyinstaller
pip install -r requirements.txt
python build_cli_exe.py
```

### CLI EXE --help Doesn't Work

**Symptom:** Running `GitHubDownloader-CLI.exe --help` crashes.

**Cause:** Old build used main.py which imports PyQt6.

**Solution:** Use rebuilt EXE from `cli_main.py`:
```bash
python build_cli_exe.py
# Output: dist/GitHubDownloader-CLI.exe
```

### EXE Too Large

**Symptom:** CLI EXE is >50 MB.

**Cause:** Unnecessary modules included.

**Solution:** Add more `--exclude-module` flags to build script:
```python
'--exclude-module=PyQt6',
'--exclude-module=matplotlib',
'--exclude-module=numpy',
```

---

## Vercel Deploy Issues

### Deploy Fails

**Symptom:** `vercel deploy --prod` returns error.

**Solutions:**
1. Check you're logged in: `vercel whoami`
2. Check project link: `vercel link`
3. Check build output for specific errors
4. Try `vercel --debug` for verbose output

### SEO Meta Tags Not Updating

**Symptom:** Site still shows old numbers (740 instead of 843).

**Cause:** Vercel cached the old deployment.

**Solution:**
```bash
vercel deploy --prod --force
# Forces a fresh deployment
```

---

## Gumroad Issues

### Upload Fails

**Symptom:** Can't upload product ZIP to Gumroad.

**Solutions:**
1. Check file size — Gumroad limit is 5 GB
2. Try a different browser
3. Compress ZIP further: `zip -9 product.zip files/`
4. Split into multiple files if needed

### Product Not Visible

**Symptom:** Product page returns 404.

**Solutions:**
1. Check product is published (not draft)
2. Check URL slug is correct
3. Wait 5 minutes for propagation

---

## Form Submission Issues

### Formsubmit.co Not Working

**Symptom:** Contact form doesn't send email.

**Cause:** First submission triggers verification email.

**Solution:**
1. Submit the form once with your email
2. Check inbox for verification email from Formsubmit
3. Click verification link
4. Subsequent submissions will work

---

## Screenshot Capture Issues

### Selenium Timeout

**Symptom:** Screenshot script hangs.

**Solutions:**
```python
# Add timeout to Chrome options
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--timeout=30000')
```

### Missing Screenshots

**Symptom:** `docs/screenshots/` directory has fewer files than expected.

**Solution:** Re-run screenshot capture:
```bash
python capture_screenshots.py
# Or manually open repo-browser.html and take screenshots
```
