@echo off
echo Starting Comprehensive Audit...
echo ====================================

REM 1. Verify Python environment
echo Checking Python version...
python --version
echo.

REM 2. Run syntax check for all Python files
echo Running syntax check for all Python files...
python -m py_compile **/*.py 2>nul || echo Syntax errors found. Check logs.
echo.

REM 3. Run unit tests
echo Running unit tests...
python -m pytest tests/ --cov=src/ --cov-report=term-missing
echo.

REM 4. Security scan
echo Running security scan...
python -m pip install bandit
bandit -r src/ -f json -o security_report.json
echo Security scan complete.
echo.

REM 5. Linting
echo Running linting checks...
python -m pip install flake8 black
flake8 src/ tests/
black --check src/ tests/
echo.

REM 6. Documentation check
echo Checking documentation...
python -m pydocstyle src/
echo.

REM 7. Build verification
echo Building executable...
python build_exe.py
echo.

echo ====================================
echo Audit Complete!
echo ====================================
echo.
echo Results:
echo - Syntax check: ^<check_output^>
echo - Test coverage: ^<coverage_report^>
echo - Security issues: ^<security_report^>
echo - Linting: ^<lint_output^>
echo.
pause