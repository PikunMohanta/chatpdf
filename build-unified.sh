#!/bin/bash
# Unified Build Script for PDFPixie
# This script builds both frontend and backend for single-service deployment

echo "🚀 Starting unified build process..."

# Navigate to project root
cd "$(dirname "$0")"

# Install backend dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Build frontend
echo "🎨 Building frontend..."
cd frontend
npm install
npm run build

# Copy built frontend to backend static directory
echo "📁 Copying frontend build to backend..."
rm -rf ../backend/static
cp -r dist ../backend/static

# Verify the build
if [ -f "../backend/static/index.html" ]; then
    echo "✅ Unified build completed successfully!"
    echo "📂 Frontend files copied to backend/static/"
    echo "🚀 Ready for deployment!"
else
    echo "❌ Build failed - index.html not found in backend/static"
    exit 1
fi

cd ..
echo "🎉 Unified build process complete!"