"""
GitHub Repo Downloader - Main Entry Point
Supports both GUI and CLI modes
"""
import sys
import os

# Ensure src directory is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """Main entry point"""
    # Check for CLI mode - need to parse manually to handle subcommands
    cli_args = ['--cli', '-c']
    has_cli_flag = any(arg in sys.argv for arg in cli_args)
    
    if has_cli_flag and len(sys.argv) > 1:
        # Remove --cli or -c from arguments for argparse
        clean_argv = [a for a in sys.argv if a not in cli_args]
        
        # Import and run CLI mode
        from github_downloader.gui.cli import CLIMode
        from github_downloader.user_auth import UserDatabase
        
        user_auth = UserDatabase()
        cli = CLIMode(user_auth)
        
        # Handle the command
        if len(clean_argv) == 1 or clean_argv[1] in ['--help', '-h']:
            # Show help
            print("""
GitHub Repo Downloader CLI
=========================

Usage:
  python src/main.py --cli download --url <repo_url> [options]
  python src/main.py --cli list --user <username>
  python src/main.py --cli search -q <query>
  python src/main.py --cli sync [options]

Options:
  --url, -u        Repository URL (owner/repo format or full URL)
  --output, -o     Output directory (default: ~/Downloads)
  --token, -t      GitHub token (optional, uses saved credentials if not provided)
  --method         git, zip, or tar (default: git)
  --user           Username for listing repos
  --query, -q      Search query
  --all            Download all repos for user
  --branch         Branch to download (default: main)

Examples:
  python src/main.py --cli download --url owner/repo
  python src/main.py --cli download --url https://github.com/owner/repo -o ~/code
  python src/main.py --cli list --user octocat
  python src/main.py --cli search -q "python web framework"
  python src/main.py --cli sync --all -t YOUR_TOKEN

GUI Mode:
  python src/main.py
            """)
            sys.exit(0)
        
        # Run CLI with cleaned arguments
        sys.argv = clean_argv
        sys.exit(cli.run())
    
    # Run GUI mode
    from github_downloader.gui_enhanced_full import main as gui_main
    gui_main()


if __name__ == '__main__':
    main()
