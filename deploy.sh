#!/bin/bash

# ETAF v2 Railway Deployment Script
# Run this from the etaf_v2 directory

echo "🚀 ETAF v2 Railway Deployment"
echo "=============================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the etaf_v2 directory."
    exit 1
fi

echo "📁 Current directory contents:"
ls -la

echo ""
echo "✅ Step 1: Initialize Git Repository"
git init

echo ""
echo "✅ Step 2: Add all files to git"
git add .

echo ""
echo "✅ Step 3: Create initial commit"
git commit -m "Initial ETAF v2 microservice for Railway deployment"

echo ""
echo "🔗 Step 4: Add GitHub remote (you need to replace YOUR_USERNAME)"
echo "Run this command with your GitHub username:"
echo "git remote add origin https://github.com/YOUR_USERNAME/etaf_v2.git"

echo ""
echo "📤 Step 5: Push to GitHub"
echo "After adding the remote, run:"
echo "git branch -M main"
echo "git push -u origin main"

echo ""
echo "🚄 Step 6: Deploy to Railway"
echo "1. Go to https://railway.app"
echo "2. Click 'New Project' → 'Deploy from GitHub repo'"
echo "3. Select your etaf_v2 repository"
echo "4. Railway will auto-deploy using our railway.json config"

echo ""
echo "✅ Deployment preparation complete!"
echo "Follow the manual steps above to complete the deployment."