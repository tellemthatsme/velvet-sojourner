import json
import os
import subprocess
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

REPOS_DIR = Path("C:/temp/velvet-sojourner/repos")
QA_REPORT = Path("C:/temp/velvet-sojourner/qa/QA_REPORT.json")
QA_CSV = Path("C:/temp/velvet-sojourner/qa/QA_REPORT.csv")

def ensure_dir():
    Path("C:/temp/velvet-sojourner/qa").mkdir(exist_ok=True)

def test_repo_build(repo_path):
    """Quick QA test on a repo"""
    name = repo_path.name
    results = {
        "name": name,
        "has_readme": (repo_path / "README.md").exists(),
        "has_license": (repo_path / "LICENSE").exists() or (repo_path / "LICENSE.md").exists(),
        "has_dockerfile": (repo_path / "Dockerfile").exists(),
        "has_compose": (repo_path / "docker-compose.yml").exists(),
        "has_env": (repo_path / ".env.example").exists(),
        "has_gitignore": (repo_path / ".gitignore").exists(),
        "has_tests": False,
        "test_passed": False,
        "docker_build": False,
        "size_mb": 0,
        "file_count": 0,
        "languages": [],
        "frameworks": [],
        "quality_score": 0,
        "deployable": False,
    }
    
    try:
        # Size and file count
        files = list(repo_path.rglob("*"))
        results["file_count"] = len(files)
        size = sum(f.stat().st_size for f in files if f.is_file())
        results["size_mb"] = round(size / (1024*1024), 2)
        
        # Detect languages
        langs = set()
        if (repo_path / "package.json").exists(): langs.add("javascript")
        if (repo_path / "requirements.txt").exists() or (repo_path / "pyproject.toml").exists(): langs.add("python")
        if (repo_path / "Cargo.toml").exists(): langs.add("rust")
        if (repo_path / "go.mod").exists(): langs.add("go")
        if list(repo_path.glob("*.ts")): langs.add("typescript")
        if list(repo_path.glob("*.tsx")): langs.add("react")
        results["languages"] = sorted(langs)
        
        # Detect tests
        test_dirs = ["tests", "test", "spec", "__tests__"]
        test_files = ["test_*.py", "*_test.py", "*.test.js", "*.spec.js"]
        for td in test_dirs:
            if (repo_path / td).exists():
                results["has_tests"] = True
                break
        if not results["has_tests"]:
            for pattern in test_files:
                if list(repo_path.rglob(pattern)):
                    results["has_tests"] = True
                    break
        
        # Test Docker build (if Dockerfile exists)
        if results["has_dockerfile"]:
            try:
                proc = subprocess.run(
                    ["docker", "build", "-t", f"qa-{name}", "."],
                    cwd=str(repo_path),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                results["docker_build"] = proc.returncode == 0
            except:
                results["docker_build"] = False
        
        # Calculate quality score
        score = 0
        if results["has_readme"]: score += 20
        if results["has_license"]: score += 15
        if results["has_dockerfile"]: score += 25
        if results["has_env"]: score += 10
        if results["has_gitignore"]: score += 10
        if results["has_tests"]: score += 10
        if results["file_count"] > 20: score += 10
        results["quality_score"] = min(100, score)
        
        # Deployable = has Dockerfile + good quality
        results["deployable"] = results["has_dockerfile"] and results["quality_score"] >= 40
        
    except Exception as e:
        results["error"] = str(e)
    
    return results

def main():
    print("=" * 70)
    print("AGENTFORGE: QA SYSTEM - Testing All Repositories")
    print("=" * 70)
    
    ensure_dir()
    
    # Get all repos
    repos = [d for d in REPOS_DIR.iterdir() if d.is_dir()]
    total = len(repos)
    print(f"Found {total} repos to QA")
    
    results = []
    passed = 0
    failed = 0
    
    # Test each repo
    for i, repo_path in enumerate(repos, 1):
        if i % 50 == 0:
            print(f"  Progress: {i}/{total} ({i/total*100:.0f}%)")
        
        try:
            result = test_repo_build(repo_path)
            results.append(result)
            if result.get("error"):
                failed += 1
            else:
                passed += 1
        except Exception as e:
            failed += 1
            results.append({"name": repo_path.name, "error": str(e)})
    
    # Stats
    deployable = sum(1 for r in results if r.get("deployable"))
    with_docker = sum(1 for r in results if r.get("has_dockerfile"))
    with_tests = sum(1 for r in results if r.get("has_tests"))
    avg_quality = sum(r.get("quality_score", 0) for r in results) / len(results) if results else 0
    
    summary = {
        "qa_date": datetime.now().isoformat(),
        "total_repos": total,
        "passed_qa": passed,
        "failed_qa": failed,
        "deployable": deployable,
        "with_dockerfile": with_docker,
        "with_tests": with_tests,
        "avg_quality": round(avg_quality, 1),
        "repos": results
    }
    
    # Save JSON
    with open(QA_REPORT, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    
    # Save CSV
    with open(QA_CSV, "w", encoding="utf-8") as f:
        f.write("name,quality_score,deployable,has_dockerfile,has_tests,size_mb,file_count,has_readme,has_license\n")
        for r in results:
            f.write(f"{r['name']},{r.get('quality_score',0)},{r.get('deployable',False)},{r.get('has_dockerfile',False)},{r.get('has_tests',False)},{r.get('size_mb',0)},{r.get('file_count',0)},{r.get('has_readme',False)},{r.get('has_license',False)}\n")
    
    print(f"\n{'='*70}")
    print("QA COMPLETE")
    print(f"{'='*70}")
    print(f"Total repos:     {total}")
    print(f"Passed QA:       {passed}")
    print(f"Failed QA:       {failed}")
    print(f"Deployable:      {deployable}")
    print(f"With Dockerfile: {with_docker}")
    print(f"With Tests:      {with_tests}")
    print(f"Avg Quality:     {avg_quality:.1f}/100")
    print(f"\nReports saved:")
    print(f"  {QA_REPORT}")
    print(f"  {QA_CSV}")

if __name__ == "__main__":
    main()
