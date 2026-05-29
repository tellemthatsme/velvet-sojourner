import subprocess
import sys


def run(args):
    cmd = " ".join(args) if isinstance(args, list) else args
    print(f"\n$ {cmd}")
    result = subprocess.run(args, capture_output=True, text=True)
    output = result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout
    print(output)
    if result.returncode != 0:
        print(result.stderr[-500:])
    return result.returncode


if __name__ == "__main__":
    exit_code = 0
    exit_code |= run([sys.executable, "-m", "pytest", "tests/", "-v"])
    exit_code |= run([sys.executable, "main.py", "--cli", "--help"])
    print(f"\n{'='*40}")
    print(f"Exit code: {exit_code}")
    sys.exit(exit_code)
