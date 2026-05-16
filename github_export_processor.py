#!/usr/bin/env python3
"""
GitHub Export Processor v1.0
Processes downloaded repositories into exportable products, bundles, and analytics

Usage:
    python github_export_processor.py --input repos/ --output exports/
    python github_export_processor.py --analyze --input repos/
    python github_export_processor.py --bundle ai-agents --output products/
"""

import os
import sys
import json
import shutil
import zipfile
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import fnmatch


class colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'


class RepoAnalyzer:
    """Analyzes a repository and extracts metadata"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.name = self.repo_path.name
        self.metadata = {}
    
    def analyze(self) -> Dict:
        """Complete repository analysis"""
        self.metadata = {
            "name": self.name,
            "path": str(self.repo_path),
            "size_mb": self._get_size(),
            "file_count": self._count_files(),
            "languages": self._detect_languages(),
            "frameworks": self._detect_frameworks(),
            "has_readme": self._has_readme(),
            "has_docker": self._has_docker(),
            "has_tests": self._has_tests(),
            "license": self._detect_license(),
            "dependencies": self._detect_dependencies(),
            "category": self._categorize(),
            "monetization_score": 0,
            "export_ready": False
        }
        
        self.metadata["monetization_score"] = self._calculate_monetization_score()
        self.metadata["export_ready"] = self._is_export_ready()
        
        return self.metadata
    
    def _get_size(self) -> float:
        """Get repository size in MB"""
        total = 0
        for path in self.repo_path.rglob('*'):
            if path.is_file():
                try:
                    total += path.stat().st_size
                except:
                    pass
        return round(total / (1024 * 1024), 2)
    
    def _count_files(self) -> int:
        """Count total files"""
        return sum(1 for _ in self.repo_path.rglob('*') if _.is_file())
    
    def _detect_languages(self) -> Dict[str, int]:
        """Detect programming languages by file extension"""
        extensions = defaultdict(int)
        for path in self.repo_path.rglob('*'):
            if path.is_file():
                ext = path.suffix.lower()
                if ext:
                    extensions[ext] += 1
        
        # Map extensions to languages
        lang_map = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
            '.jsx': 'React', '.tsx': 'React', '.html': 'HTML',
            '.css': 'CSS', '.scss': 'SCSS', '.java': 'Java',
            '.go': 'Go', '.rs': 'Rust', '.cpp': 'C++',
            '.c': 'C', '.rb': 'Ruby', '.php': 'PHP',
            '.swift': 'Swift', '.kt': 'Kotlin', '.dart': 'Dart',
            '.sql': 'SQL', '.sh': 'Shell', '.ps1': 'PowerShell',
            '.json': 'JSON', '.yaml': 'YAML', '.yml': 'YAML',
            '.md': 'Markdown', '.dockerfile': 'Docker', '.tf': 'Terraform'
        }
        
        languages = defaultdict(int)
        for ext, count in extensions.items():
            lang = lang_map.get(ext, ext[1:] if ext.startswith('.') else ext)
            languages[lang] += count
        
        return dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _detect_frameworks(self) -> List[str]:
        """Detect frameworks from config files"""
        frameworks = []
        
        # Check for framework indicators
        checks = {
            'React': ['package.json', 'node_modules/react'],
            'Vue': ['vue.config.js', 'node_modules/vue'],
            'Angular': ['angular.json', 'node_modules/@angular'],
            'Django': ['manage.py', 'requirements.txt'],
            'Flask': ['app.py', 'requirements.txt'],
            'FastAPI': ['main.py', 'requirements.txt'],
            'Express': ['app.js', 'server.js'],
            'Next.js': ['next.config.js', 'pages/'],
            'CrewAI': ['crew.py', 'requirements.txt'],
            'LangChain': ['requirements.txt'],
            'TensorFlow': ['requirements.txt'],
            'PyTorch': ['requirements.txt'],
        }
        
        for framework, indicators in checks.items():
            for indicator in indicators:
                if any(self.repo_path.rglob(indicator)):
                    frameworks.append(framework)
                    break
        
        return frameworks
    
    def _has_readme(self) -> bool:
        """Check if repo has README"""
        return any(self.repo_path.glob('README*'))
    
    def _has_docker(self) -> bool:
        """Check if repo has Docker files"""
        return any(self.repo_path.glob('Dockerfile*')) or any(self.repo_path.glob('docker-compose*'))
    
    def _has_tests(self) -> bool:
        """Check if repo has tests"""
        test_dirs = ['test', 'tests', '__tests__', 'spec', 'specs']
        return any((self.repo_path / d).exists() for d in test_dirs)
    
    def _detect_license(self) -> str:
        """Detect license type"""
        license_files = list(self.repo_path.glob('LICENSE*')) + list(self.repo_path.glob('COPYING*'))
        if not license_files:
            return "Unknown"
        
        try:
            content = license_files[0].read_text().upper()
            if 'MIT' in content:
                return 'MIT'
            elif 'APACHE' in content:
                return 'Apache'
            elif 'GPL' in content:
                return 'GPL'
            elif 'BSD' in content:
                return 'BSD'
            else:
                return 'Other'
        except:
            return "Unknown"
    
    def _detect_dependencies(self) -> Dict[str, List[str]]:
        """Detect dependencies from package files"""
        deps = {}
        
        # Python
        req_files = list(self.repo_path.glob('requirements*.txt'))
        if req_files:
            try:
                deps['python'] = [line.strip() for line in req_files[0].read_text().split('\n') 
                                 if line.strip() and not line.startswith('#')][:20]
            except:
                pass
        
        # Node.js
        package_json = self.repo_path / 'package.json'
        if package_json.exists():
            try:
                pkg = json.loads(package_json.read_text())
                deps['nodejs'] = list(pkg.get('dependencies', {}).keys())[:20]
            except:
                pass
        
        return deps
    
    def _categorize(self) -> str:
        """Categorize repository"""
        name_lower = self.name.lower()
        
        categories = {
            'AI Agent': ['agent', 'ai', 'crew', 'autogen', 'langchain', 'llm', 'gpt', 'claude'],
            'Trading': ['trading', 'crypto', 'trade', 'bot', 'signal'],
            'MCP Server': ['mcp', 'context', 'server'],
            'Web App': ['web', 'app', 'dashboard', 'ui', 'frontend'],
            'Dev Tool': ['tool', 'cli', 'utility', 'dev'],
            'Automation': ['automation', 'workflow', 'n8n', 'pipeline'],
            'Documentation': ['awesome', 'list', 'resources', 'guide'],
            'Security': ['security', 'privacy', 'encrypt']
        }
        
        scores = {cat: sum(1 for kw in keywords if kw in name_lower) 
                  for cat, keywords in categories.items()}
        
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else 'Other'
    
    def _calculate_monetization_score(self) -> int:
        """Calculate monetization potential (0-100)"""
        score = 0
        
        # Size factor (larger = more value)
        size = self.metadata.get('size_mb', 0)
        score += min(20, int(size / 10))
        
        # Completeness
        if self._has_readme():
            score += 10
        if self._has_docker():
            score += 15
        if self._has_tests():
            score += 10
        
        # Language diversity
        langs = self.metadata.get('languages', {})
        score += min(15, len(langs) * 3)
        
        # Framework usage
        frameworks = self.metadata.get('frameworks', [])
        score += min(15, len(frameworks) * 5)
        
        # Dependencies (more = more integrated)
        deps = self.metadata.get('dependencies', {})
        score += min(15, sum(len(v) for v in deps.values()))
        
        return min(100, score)
    
    def _is_export_ready(self) -> bool:
        """Check if repo is ready for export"""
        return (
            self.metadata.get('size_mb', 0) > 0.1 and
            self._has_readme() and
            self.metadata.get('monetization_score', 0) > 30
        )


class BundleCreator:
    """Creates exportable bundles from repositories"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_zip_bundle(self, repos: List[str], bundle_name: str, 
                         exclude_patterns: List[str] = None) -> str:
        """Create ZIP bundle from repositories"""
        if exclude_patterns is None:
            exclude_patterns = ['.git', '__pycache__', '*.pyc', '.env', 'node_modules']
        
        zip_path = self.output_dir / f"{bundle_name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for repo_path in repos:
                repo = Path(repo_path)
                if not repo.exists():
                    continue
                
                for file_path in repo.rglob('*'):
                    if file_path.is_file():
                        # Check exclusions
                        rel_path = file_path.relative_to(repo.parent)
                        if any(fnmatch.fnmatch(str(rel_path), pat) or 
                               fnmatch.fnmatch(file_path.name, pat) 
                               for pat in exclude_patterns):
                            continue
                        
                        zf.write(file_path, rel_path)
        
        return str(zip_path)
    
    def create_product_package(self, repos: List[str], product_name: str,
                               metadata: Dict) -> str:
        """Create a complete product package with docs and configs"""
        product_dir = self.output_dir / product_name
        product_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy repos
        repos_dir = product_dir / 'repos'
        repos_dir.mkdir(exist_ok=True)
        
        for repo_path in repos:
            repo = Path(repo_path)
            if repo.exists():
                dest = repos_dir / repo.name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(repo, dest, ignore=shutil.ignore_patterns(
                    '.git', '__pycache__', '*.pyc', '.env', 'node_modules'
                ))
        
        # Generate product README
        readme = self._generate_product_readme(product_name, metadata)
        (product_dir / 'README.md').write_text(readme)
        
        # Generate manifest
        manifest = {
            "name": product_name,
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "repos": [Path(r).name for r in repos],
            "metadata": metadata
        }
        (product_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2))
        
        # Create ZIP
        zip_path = self.output_dir / f"{product_name}.zip"
        shutil.make_archive(
            str(self.output_dir / product_name),
            'zip',
            str(product_dir)
        )
        
        return str(zip_path)
    
    def _generate_product_readme(self, name: str, metadata: Dict) -> str:
        """Generate product README"""
        return f"""# {name}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Total Repositories:** {metadata.get('repo_count', 0)}
**Total Size:** {metadata.get('total_size_mb', 0)} MB

## Included Repositories

| Repository | Category | Size | Language |
|------------|----------|------|----------|
""" + "\n".join(
    f"| {r.get('name', 'Unknown')} | {r.get('category', 'N/A')} | {r.get('size_mb', 0)} MB | {list(r.get('languages', {}).keys())[0] if r.get('languages') else 'N/A'} |"
    for r in metadata.get('repos', [])
) + f"""

## Quick Start

```bash
# Extract the package
unzip {name}.zip
cd {name}

# Explore repositories
ls repos/

# Read individual READMEs
cat repos/[repo-name]/README.md
```

## Categories

""" + "\n".join(
    f"- **{cat}**: {count} repos"
    for cat, count in metadata.get('categories', {}).items()
) + f"""

## License

Each repository retains its original license.
This package is provided as-is for educational and development purposes.

---

*Generated by GitHub Export Processor*
"""


class ExportProcessor:
    """Main export processing engine"""
    
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.analyzer = None
        self.bundle_creator = BundleCreator(output_dir)
        self.results = []
    
    def scan_repositories(self) -> List[Dict]:
        """Scan all repositories in input directory"""
        print(f"{colors.CYAN}Scanning repositories in {self.input_dir}...{colors.END}")
        
        repos = []
        for item in self.input_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                print(f"  Analyzing {item.name}...", end=' ')
                analyzer = RepoAnalyzer(str(item))
                metadata = analyzer.analyze()
                repos.append(metadata)
                
                score = metadata.get('monetization_score', 0)
                ready = "OK" if metadata.get('export_ready') else "NO"
                print(f"  [{ready}] Score: {score}/100")
        
        self.results = repos
        print(f"\n{colors.GREEN}Scanned {len(repos)} repositories{colors.END}")
        return repos
    
    def generate_analytics(self) -> Dict:
        """Generate analytics report"""
        if not self.results:
            self.scan_repositories()
        
        total_size = sum(r.get('size_mb', 0) for r in self.results)
        total_files = sum(r.get('file_count', 0) for r in self.results)
        
        categories = defaultdict(int)
        languages = defaultdict(int)
        licenses = defaultdict(int)
        
        for repo in self.results:
            categories[repo.get('category', 'Other')] += 1
            for lang, count in repo.get('languages', {}).items():
                languages[lang] += count
            licenses[repo.get('license', 'Unknown')] += 1
        
        analytics = {
            "total_repos": len(self.results),
            "total_size_mb": round(total_size, 2),
            "total_files": total_files,
            "export_ready": sum(1 for r in self.results if r.get('export_ready')),
            "categories": dict(categories),
            "languages": dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)[:20]),
            "licenses": dict(licenses),
            "avg_monetization_score": round(
                sum(r.get('monetization_score', 0) for r in self.results) / len(self.results), 1
            ) if self.results else 0,
            "top_repos": sorted(self.results, key=lambda x: x.get('monetization_score', 0), reverse=True)[:10]
        }
        
        return analytics
    
    def export_by_category(self):
        """Export repositories grouped by category"""
        if not self.results:
            self.scan_repositories()
        
        print(f"\n{colors.CYAN}Exporting by category...{colors.END}")
        
        categories = defaultdict(list)
        for repo in self.results:
            cat = repo.get('category', 'Other')
            categories[cat].append(repo)
        
        exported = []
        for category, repos in categories.items():
            if len(repos) < 2:
                continue
            
            category_name = category.lower().replace(' ', '-')
            repo_paths = [r['path'] for r in repos]
            
            metadata = {
                'repo_count': len(repos),
                'total_size_mb': round(sum(r.get('size_mb', 0) for r in repos), 2),
                'repos': repos,
                'categories': {category: len(repos)}
            }
            
            zip_path = self.bundle_creator.create_product_package(
                repo_paths, 
                f"{category_name}-bundle",
                metadata
            )
            
            exported.append({
                'category': category,
                'path': zip_path,
                'size_mb': metadata['total_size_mb'],
                'repo_count': len(repos)
            })
            
            print(f"  {colors.GREEN}[OK]{colors.END} {category}: {len(repos)} repos -> {zip_path}")
        
        return exported
    
    def export_top_products(self, count: int = 5):
        """Export top monetizable products"""
        if not self.results:
            self.scan_repositories()
        
        print(f"\n{colors.CYAN}Exporting top {count} products...{colors.END}")
        
        top_repos = sorted(
            self.results, 
            key=lambda x: x.get('monetization_score', 0), 
            reverse=True
        )[:count]
        
        repo_paths = [r['path'] for r in top_repos]
        
        metadata = {
            'repo_count': len(top_repos),
            'total_size_mb': round(sum(r.get('size_mb', 0) for r in top_repos), 2),
            'repos': top_repos,
            'categories': defaultdict(int)
        }
        
        for r in top_repos:
            metadata['categories'][r.get('category', 'Other')] += 1
        metadata['categories'] = dict(metadata['categories'])
        
        zip_path = self.bundle_creator.create_product_package(
            repo_paths,
            'top-products-bundle',
            metadata
        )
        
        print(f"  {colors.GREEN}[OK]{colors.END} Top {count} products -> {zip_path}")
        return zip_path
    
    def generate_report(self):
        """Generate comprehensive analytics report"""
        analytics = self.generate_analytics()
        
        report_path = self.output_dir / 'analytics-report.json'
        with open(report_path, 'w') as f:
            json.dump(analytics, f, indent=2)
        
        # Generate Markdown report
        md_report = f"""# Repository Analytics Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Source:** {self.input_dir}

## Summary

| Metric | Value |
|--------|-------|
| Total Repositories | {analytics['total_repos']} |
| Total Size | {analytics['total_size_mb']} MB |
| Total Files | {analytics['total_files']:,} |
| Export Ready | {analytics['export_ready']} |
| Avg Monetization Score | {analytics['avg_monetization_score']}/100 |

## Categories

| Category | Count |
|----------|-------|
"""
        for cat, count in sorted(analytics['categories'].items(), key=lambda x: x[1], reverse=True):
            md_report += f"| {cat} | {count} |\n"
        
        md_report += f"""
## Top Languages

| Language | Files |
|----------|-------|
"""
        for lang, count in list(analytics['languages'].items())[:10]:
            md_report += f"| {lang} | {count} |\n"
        
        md_report += f"""
## Top Monetizable Repositories

| Repository | Category | Score | Size |
|------------|----------|-------|------|
"""
        for repo in analytics['top_repos']:
            md_report += f"| {repo['name']} | {repo.get('category', 'N/A')} | {repo.get('monetization_score', 0)} | {repo.get('size_mb', 0)} MB |\n"
        
        md_path = self.output_dir / 'analytics-report.md'
        with open(md_path, 'w') as f:
            f.write(md_report)
        
        print(f"\n{colors.GREEN}Reports generated:{colors.END}")
        print(f"  JSON: {report_path}")
        print(f"  Markdown: {md_path}")
        
        return analytics
    
    def run_full_pipeline(self):
        """Run complete export pipeline"""
        print(f"{colors.BOLD}{colors.CYAN}{'='*80}{colors.END}")
        print(f"{colors.BOLD}{colors.CYAN}{'GITHUB EXPORT PROCESSOR v1.0'.center(80)}{colors.END}")
        print(f"{colors.BOLD}{colors.CYAN}{'='*80}{colors.END}\n")
        
        print(f"Input:  {self.input_dir}")
        print(f"Output: {self.output_dir}\n")
        
        # Step 1: Scan
        self.scan_repositories()
        
        # Step 2: Analytics
        print(f"\n{colors.CYAN}Generating analytics...{colors.END}")
        analytics = self.generate_report()
        
        # Step 3: Export by category
        category_exports = self.export_by_category()
        
        # Step 4: Export top products
        top_product = self.export_top_products(10)
        
        # Summary
        print(f"\n{colors.BOLD}{colors.GREEN}{'='*80}{colors.END}")
        print(f"{colors.BOLD}{colors.GREEN}{'EXPORT COMPLETE'.center(80)}{colors.END}")
        print(f"{colors.BOLD}{colors.GREEN}{'='*80}{colors.END}\n")
        
        print(f"Repositories scanned: {analytics['total_repos']}")
        print(f"Total size: {analytics['total_size_mb']} MB")
        print(f"Export ready: {analytics['export_ready']}")
        print(f"Category bundles: {len(category_exports)}")
        print(f"Output directory: {self.output_dir}")
        
        print(f"\n{colors.YELLOW}Next steps:{colors.END}")
        print(f"  1. Review analytics-report.md")
        print(f"  2. Upload product bundles to Gumroad")
        print(f"  3. Deploy landing page")
        print(f"  4. Start marketing!")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub Export Processor')
    parser.add_argument('--input', '-i', default='repos', help='Input directory with repos')
    parser.add_argument('--output', '-o', default='exports', help='Output directory')
    parser.add_argument('--analyze', '-a', action='store_true', help='Only generate analytics')
    parser.add_argument('--bundle', '-b', help='Create specific category bundle')
    parser.add_argument('--top', '-t', type=int, default=10, help='Number of top products')
    
    args = parser.parse_args()
    
    processor = ExportProcessor(args.input, args.output)
    
    if args.analyze:
        processor.scan_repositories()
        processor.generate_report()
    elif args.bundle:
        processor.scan_repositories()
        # Filter by category
        category_repos = [r['path'] for r in processor.results 
                         if r.get('category', '').lower().replace(' ', '-') == args.bundle]
        if category_repos:
            metadata = {
                'repo_count': len(category_repos),
                'repos': [r for r in processor.results if r['path'] in category_repos],
                'categories': {args.bundle: len(category_repos)}
            }
            zip_path = processor.bundle_creator.create_product_package(
                category_repos, args.bundle, metadata
            )
            print(f"Created: {zip_path}")
        else:
            print(f"No repos found in category: {args.bundle}")
            print(f"Available categories: {set(r.get('category', 'Other') for r in processor.results)}")
    else:
        processor.run_full_pipeline()


if __name__ == "__main__":
    main()
