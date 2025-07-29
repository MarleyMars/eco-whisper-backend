# Railway Deployment Guide

## Prerequisites
1. Create a Railway account at https://railway.app
2. Install Railway CLI (optional): `npm install -g @railway/cli`

## Deployment Steps

### Method 1: Using Railway Web Interface
1. Go to https://railway.app and sign in
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your GitHub account and select this repository
4. Set the root directory to `project/backend`
5. Railway will automatically detect the Python app and deploy it

### Method 2: Using Railway CLI
1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Navigate to backend directory: `cd project/backend`
4. Initialize project: `railway init`
5. Deploy: `railway up`

## Environment Variables
Railway will automatically set:
- `PORT`: The port to run the application on
- `RAILWAY_ENVIRONMENT`: Set to 'true' when deployed

## API Endpoints
After deployment, your API will be available at:
- Health check: `https://your-app-name.up.railway.app/`
- Transcribe: `https://your-app-name.up.railway.app/api/transcribe`
- Text ask: `https://your-app-name.up.railway.app/api/text_ask`

## Notes
- The SQLite database will be created automatically on first run
- Audio files are temporarily stored and may be cleaned up by Railway
- Make sure to update your frontend API configuration with the new Railway URL