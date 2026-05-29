from __future__ import annotations

import sys
from pathlib import Path

import click

from skill_scan import __version__
from skill_scan.allowlist import Allowlist
from skill_scan.engine import ScanEngine
from skill_scan.models import Severity
from skill_scan.rules import builtin_rules
from skill_scan.rules.base import Rule, RuleRegistry
from skill_scan.reporters import terminal, json_reporter, html


@click.group()
@click.version_option(version=__version__, prog_name="skill-scan")
def cli() -> None:
    """skill-scan — AI agent skills security scanner."""


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--output", "-o",
    type=click.Choice(["terminal", "json", "sarif", "html"]),
    default="terminal",
    help="Output format",
)
@click.option(
    "--severity", "-s",
    type=click.Choice([s.name.lower() for s in Severity], case_sensitive=False),
    default=None,
    help="Minimum severity level to report",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--ci", is_flag=True, help="CI mode — exit code 1 on any finding")
@click.option(
    "--exclude", multiple=True,
    help="Glob pattern of paths to exclude (can be used multiple times)",
)
@click.option(
    "--no-default-rules", is_flag=True,
    help="Disable built-in rules",
)
@click.option(
    "--rules", type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=None,
    help="Path to directory containing custom rule files",
)
@click.option(
    "--allowlist",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    default=None,
    help="Path to allowlist YAML file (default: .skill-scan-allowlist.yaml)",
)
def scan(path: str, output: str, severity: str | None, verbose: bool, ci: bool,
         exclude: tuple[str, ...], no_default_rules: bool, rules: str | None,
         allowlist: str | None) -> None:
    """Scan a skill directory or file for security issues."""
    target = Path(path)

    severity_filter = Severity.from_string(severity.upper()) if severity else None

    if no_default_rules:
        scan_rules: list[Rule] = []
    else:
        scan_rules = list(builtin_rules)

    if rules:
        registry = RuleRegistry()
        registry._rules.clear()
        registry.discover(Path(rules))
        scan_rules.extend(registry.rules)

    allowlist_obj = None
    if allowlist:
        allowlist_obj = Allowlist(Path(allowlist))
    else:
        default_allowlist = target / ".skill-scan-allowlist.yaml"
        if default_allowlist.is_file():
            allowlist_obj = Allowlist(default_allowlist)

    if allowlist_obj is not None and verbose:
        entries = allowlist_obj.load()
        if entries:
            click.echo(f"Allowlist loaded: {len(entries)} entr{'y' if len(entries) == 1 else 'ies'}")

    engine = ScanEngine(rules=scan_rules, exclude_patterns=list(exclude),
                        allowlist=allowlist_obj)
    try:
        if verbose:
            click.echo(f"Scanning: {target}")
            if exclude:
                click.echo(f"Excluding: {', '.join(exclude)}")
            if not no_default_rules:
                click.echo(f"Using {len(builtin_rules)} built-in rule(s)")
            if rules:
                click.echo(f"Using custom rules from: {rules}")

        if target.is_dir():
            files = [f for f in target.rglob("*") if f.is_file()]
        else:
            files = [target]

        if verbose:
            click.echo(f"Found {len(files)} file(s) to scan")

        result = engine.scan(target, severity_filter=severity_filter)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Scan failed: {e}", err=True)
        sys.exit(1)

    if output == "json":
        json_reporter.report(result)
    elif output == "html":
        html.report(result, str(target))
    elif output == "sarif":
        json_reporter.report_sarif(result)
    else:
        terminal.report(result, verbose=verbose)

    total = len(result.findings)
    if output == "terminal":
        if total > 0:
            click.echo(f"\nFound {total} issue(s) across {result.files_scanned} file(s).")
        else:
            click.echo(f"\nNo issues found across {result.files_scanned} file(s).")
    if ci and total > 0:
        sys.exit(1)


@cli.command("rules")
def list_rules() -> None:
    """List all available scan rules."""
    click.echo(f"{'Rule ID':<25} {'Severity':<10} Description")
    click.echo("-" * 80)
    for rule in builtin_rules:
        click.echo(f"{rule.name:<25} {rule.severity.name:<10} {rule.description}")


@cli.command()
@click.argument("path", type=click.Path(exists=True))
def info(path: str) -> None:
    """Show metadata for a skill file or directory."""
    target = Path(path)

    skill_file = None
    if target.is_file() and target.name.lower() == "skill.md":
        skill_file = target
    elif target.is_dir():
        for child in target.iterdir():
            if child.name.lower() == "skill.md":
                skill_file = child
                break

    if skill_file is None:
        click.echo("No SKILL.md found at the given path.")
        return

    try:
        from skill_scan.parsers.skill_md import SkillMDParser
        parser = SkillMDParser(skill_file).parse()
    except (FileNotFoundError, RuntimeError) as e:
        click.echo(f"Error reading SKILL.md: {e}")
        return

    sections = parser.sections
    header = sections.get("__header__", "").strip()
    desc = sections.get("description", "").strip() or header.split("\n", 1)[-1].strip() if header else ""
    click.echo(f"File: {skill_file}")
    click.echo(f"Name: {header.split(chr(10))[0].lstrip('#').strip() if header else 'N/A'}")
    click.echo(f"\nDescription:\n  {desc or 'N/A'}")
    click.echo(f"\nCode blocks: {len(parser.code_blocks)}")
    click.echo(f"URLs found: {len(parser.urls)}")

    if parser.urls:
        click.echo("\nURLs:")
        for url in parser.urls:
            click.echo(f"  - {url}")


@cli.command()
@click.option("--check", is_flag=True, help="Check for updates without downloading")
def update(check: bool) -> None:
    """Check for and install rule updates from remote source."""
    from skill_scan.updater import RuleUpdater

    updater = RuleUpdater()

    if check:
        click.echo("Checking for rule updates...")
        has_updates = updater.check_for_updates()
        if has_updates:
            click.echo("Updates are available. Run 'skill-scan update' to install.")
        else:
            click.echo("All rules are up to date.")
        return

    click.echo("Updating rules...")
    try:
        updated = updater.update_rules()
        if updated > 0:
            click.echo(f"Installed {updated} rule update(s).")
        else:
            click.echo("No updates available. All rules are current.")
    except Exception as e:
        click.echo(f"Update failed: {e}", err=True)
        sys.exit(1)
