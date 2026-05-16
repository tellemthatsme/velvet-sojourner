@echo off
echo ===========================================
echo AgentForge Redeploy Script
echo ===========================================
echo.

REM Sync source files to deploy-ready
echo Syncing source files...
copy /Y "C:\temp\velvet-sojourner\consulting\index.html" "C:\temp\velvet-sojourner\deploy-ready\consulting-page\index.html" >nul
copy /Y "C:\temp\velvet-sojourner\consulting\favicon.svg" "C:\temp\velvet-sojourner\deploy-ready\consulting-page\favicon.svg" >nul
copy /Y "C:\temp\velvet-sojourner\consulting\robots.txt" "C:\temp\velvet-sojourner\deploy-ready\consulting-page\robots.txt" >nul
copy /Y "C:\temp\velvet-sojourner\deployment-platform\landing-page\index.html" "C:\temp\velvet-sojourner\deploy-ready\saas-landing-page\index.html" >nul
copy /Y "C:\temp\velvet-sojourner\deployment-platform\landing-page\favicon.svg" "C:\temp\velvet-sojourner\deploy-ready\saas-landing-page\favicon.svg" >nul
copy /Y "C:\temp\velvet-sojourner\deployment-platform\landing-page\robots.txt" "C:\temp\velvet-sojourner\deploy-ready\saas-landing-page\robots.txt" >nul
echo Done.
echo.

REM Deploy consulting page
echo Deploying consulting page...
cd /d "C:\temp\velvet-sojourner\deploy-ready\consulting-page"
vercel --prod --yes
echo.

REM Deploy SaaS page
echo Deploying SaaS landing page...
cd /d "C:\temp\velvet-sojourner\deploy-ready\saas-landing-page"
vercel --prod --yes
echo.

echo ===========================================
echo Redeploy complete!
echo ===========================================
echo.
echo URLs:
echo   Consulting: https://agentforge-consulting.vercel.app
echo   SaaS:       https://agentforge-saas.vercel.app
echo.
pause
