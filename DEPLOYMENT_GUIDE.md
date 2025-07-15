# ETAF v2 Railway Deployment Guide

## Step 1: Create GitHub Repository

1. Go to https://github.com and create a new repository named `etaf_v2`
2. Make it public (recommended) or private 
3. Do NOT initialize with README (we have files ready)

## Step 2: Push Code to GitHub

Run these commands in your terminal from the etaf_v2 directory:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit files
git commit -m "Initial ETAF v2 microservice deployment"

# Add remote origin (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/etaf_v2.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Deploy to Railway

1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `etaf_v2` repository
5. Railway will automatically detect Python and use our railway.json config

## Expected Railway Configuration

Railway will automatically use:
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Health Check**: `/health` endpoint
- **Python Version**: 3.11+
- **Environment Variables**: Already configured in railway.json

## Testing the Deployment

Once deployed, test with:

```bash
curl -X POST https://your-app-name.up.railway.app/score \
  -H "Content-Type: application/json" \
  -d '{
    "message_text": "نص عربي للاختبار", 
    "lang": "ar",
    "channel_metadata": {"source": "test"}
  }'
```

## Expected Response Format

```json
{
  "etaf_score": 125,
  "level": "Medium", 
  "components": {
    "temporal": 30,
    "operational": 25, 
    "specificity": 35,
    "source_intent": 35
  },
  "rationale": "Medium threat level based on content analysis"
}
```