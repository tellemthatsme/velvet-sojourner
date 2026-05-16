"""Package entry point for `python -m github_downloader`"""
from .gui.cli import CLIMode
from .user_auth import UserDatabase


def main():
    import sys
    user_auth = UserDatabase()
    cli = CLIMode(user_auth)
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
