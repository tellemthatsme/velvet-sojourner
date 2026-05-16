"""
CLI-only entry point for GitHub Downloader.
Use this for CLI-only builds (no PyQt6 dependency).
"""
import sys


def main():
    from github_downloader.gui.cli import CLIMode
    from github_downloader.user_auth import UserDatabase

    user_auth = UserDatabase()
    cli = CLIMode(user_auth)

    if len(sys.argv) == 1 or sys.argv[1] in ('--help', '-h'):
        cli.parse_args().print_help()
        sys.exit(0)

    sys.exit(cli.run())


if __name__ == '__main__':
    main()
