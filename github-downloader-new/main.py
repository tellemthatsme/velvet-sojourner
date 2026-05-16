"""
GitHub Repo Downloader v2.1.0 - Main Entry Point
Supports CLI, GUI, Batch, Verify, Export, Health Check modes
"""
import sys


def main():
    """Main entry point. Detects GUI availability automatically."""
    cli_args = ['--cli', '-c']
    has_cli_flag = any(arg in sys.argv for arg in cli_args)

    def run_cli():
        from github_downloader.gui.cli import CLIMode
        from github_downloader.user_auth import UserDatabase
        user_auth = UserDatabase()
        cli = CLIMode(user_auth)
        clean_argv = [a for a in sys.argv if a not in cli_args]
        if len(clean_argv) == 1 or clean_argv[1] in ('--help', '-h'):
            cli.parse_args().print_help()
            sys.exit(0)
        sys.argv = clean_argv
        sys.exit(cli.run())

    if has_cli_flag:
        run_cli()

    try:
        from github_downloader.gui_enhanced import main as gui_main
        gui_main()
    except ImportError:
        run_cli()


if __name__ == '__main__':
    main()
