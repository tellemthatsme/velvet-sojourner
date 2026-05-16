from .cli import CLIMode

def __getattr__(name):
    import importlib
    lazy_map = {
        'ThemeManager': '.managers',
        'NotificationManager': '.managers',
        'SyncManager': '.managers',
        'BookmarksManager': '.managers',
        'MultiAccountManager': '.managers',
        'DownloadThread': '.threads',
        'LoginDialog': '.dialogs',
        'GitHubAuthDialog': '.dialogs',
        'SettingsDialog': '.dialogs',
        'SelectiveDownloadDialog': '.dialogs',
        'ScheduledDownloadDialog': '.dialogs',
    }
    if name in lazy_map:
        mod = importlib.import_module(lazy_map[name], __package__)
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
