@echo off
echo ==========================================
echo   GITHUB TOKEN FIX - BATCH MODE
echo ==========================================
echo.
echo This will update all 5 tokens in accounts.json
echo.
echo You need to generate new tokens at:
echo https://github.com/settings/tokens
echo.
echo Each token MUST have the 'repo' scope checked!
echo.
echo Press any key when ready...
pause > nul

python -c "
import json, os, time

APP_DATA = os.path.join(os.environ.get('APPDATA'), 'GitHubDownloader')
ACCOUNTS_FILE = os.path.join(APP_DATA, 'accounts.json')

with open(ACCOUNTS_FILE, 'r') as f:
    accounts = json.load(f)

print('\n=== TOKEN UPDATE UTILITY ===\n')

for acc_id, acc in accounts.items():
    username = acc['username']
    print(f'\nAccount: {username}')
    print(f'Current: {acc[\"token\"][:20]}...{acc[\"token\"][-10:]}')
    print('-' * 50)
    new_token = input(f'Enter new token for {username}: ').strip()
    if new_token:
        acc['token'] = new_token
        acc['updated_at'] = time.strftime('%Y-%m-%dT%H:%M:%S')
        print(f'Updated!')
    else:
        print('Skipped (no input)')

with open(ACCOUNTS_FILE, 'w') as f:
    json.dump(accounts, f, indent=2)

print('\n=== ALL ACCOUNTS SAVED ===')
print(f'Saved to: {ACCOUNTS_FILE}')
print('\nNext: Run check_tokens.py to verify')
"

pause
