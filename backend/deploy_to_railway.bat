@echo off
echo 🚀 Eco Whisper Backend Railway Deployment Script
echo ================================================

REM Check if Railway CLI is installed
railway --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Railway CLI not found. Installing...
    npm install -g @railway/cli
) else (
    echo ✅ Railway CLI found
)

REM Check if user is logged in
railway whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔐 Please login to Railway...
    railway login
) else (
    echo ✅ Already logged in to Railway
)

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ Please run this script from the backend directory (project/backend)
    pause
    exit /b 1
)

echo.
echo 📋 Current configuration:
echo - Python app: app.py
echo - Requirements: requirements.txt
echo - Procfile: Procfile
echo - Runtime: runtime.txt

echo.
echo 🚀 Starting deployment...

REM Initialize Railway project if not already done
if not exist ".railway" (
    echo 📦 Initializing Railway project...
    railway init
)

REM Deploy to Railway
echo 🚀 Deploying to Railway...
railway up

echo.
echo ✅ Deployment completed!
echo.
echo 📝 Next steps:
echo 1. Get your Railway URL from the deployment output
echo 2. Update frontend/config/api.ts with the new URL
echo 3. Test the deployment with: python test_deployment.py ^<your-url^>
echo.
echo 🔗 Your API will be available at: https://your-app-name.up.railway.app
pause