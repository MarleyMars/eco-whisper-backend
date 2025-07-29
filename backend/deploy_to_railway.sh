#!/bin/bash

# Quick deployment script for Railway
# This script helps prepare and deploy the backend to Railway

echo "🚀 Eco Whisper Backend Railway Deployment Script"
echo "================================================"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
else
    echo "✅ Railway CLI found"
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway..."
    railway login
else
    echo "✅ Already logged in to Railway"
fi

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Please run this script from the backend directory (project/backend)"
    exit 1
fi

echo ""
echo "📋 Current configuration:"
echo "- Python app: app.py"
echo "- Requirements: requirements.txt"
echo "- Procfile: Procfile"
echo "- Runtime: runtime.txt"

echo ""
echo "🚀 Starting deployment..."

# Initialize Railway project if not already done
if [ ! -f ".railway" ]; then
    echo "📦 Initializing Railway project..."
    railway init
fi

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

echo ""
echo "✅ Deployment completed!"
echo ""
echo "📝 Next steps:"
echo "1. Get your Railway URL from the deployment output"
echo "2. Update frontend/config/api.ts with the new URL"
echo "3. Test the deployment with: python test_deployment.py <your-url>"
echo ""
echo "🔗 Your API will be available at: https://your-app-name.up.railway.app"