import sys
import os

sys.path.insert(0, 'src')
os.chdir('C:/temp/velvet-sojourner')

try:
    from github_downloader.gui_enhanced_full import AccountManager
    am = AccountManager()
    accounts = am.list_accounts()
    print('Accounts loaded:', len(accounts))
    for acc in accounts:
        print('  -', acc['id'], ':', acc['username'])
    print('OK: AccountManager works')
except Exception as e:
    print('ERROR:', e)
    import traceback
    traceback.print_exc()
