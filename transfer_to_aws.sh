#!/bin/bash
# Transfer fixed files to AWS and deploy
# Run this from your LOCAL machine (where you have the project)

set -e

echo "🚀 PDFPixie - Transfer & Deploy to AWS"
echo "======================================="
echo ""

# Check if SSH key is provided
if [ -z "$1" ]; then
    echo "Usage: ./transfer_to_aws.sh <path-to-your-key.pem>"
    echo "Example: ./transfer_to_aws.sh ~/.ssh/aws-key.pem"
    exit 1
fi

SSH_KEY="$1"
AWS_IP="13.201.129.219"
AWS_USER="ubuntu"  # Change if your AWS user is different (e.g., ec2-user)
REMOTE_PATH="/home/ubuntu/chatpdf"  # Change if your project is elsewhere

echo "📋 Configuration:"
echo "   AWS IP: $AWS_IP"
echo "   SSH Key: $SSH_KEY"
echo "   Remote Path: $REMOTE_PATH"
echo ""

# Check if key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH key not found: $SSH_KEY"
    exit 1
fi

# Set proper permissions on key
chmod 600 "$SSH_KEY"

# Test connection
echo "🔍 Testing SSH connection..."
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=5 "${AWS_USER}@${AWS_IP}" "echo 'Connection successful'" 2>/dev/null; then
    echo "❌ Cannot connect to AWS instance"
    echo "Please check:"
    echo "  1. AWS security group allows SSH from your IP"
    echo "  2. SSH key is correct"
    echo "  3. AWS instance is running"
    exit 1
fi
echo "✅ SSH connection successful"
echo ""

# Transfer updated files
echo "📤 Transferring updated files to AWS..."

# Transfer frontend files
echo "  - Frontend environment config..."
scp -i "$SSH_KEY" frontend/.env.production "${AWS_USER}@${AWS_IP}:${REMOTE_PATH}/frontend/"

echo "  - Frontend components..."
scp -i "$SSH_KEY" frontend/src/components/ChatWorkspace.tsx "${AWS_USER}@${AWS_IP}:${REMOTE_PATH}/frontend/src/components/"
scp -i "$SSH_KEY" frontend/src/components/UploadScreen.tsx "${AWS_USER}@${AWS_IP}:${REMOTE_PATH}/frontend/src/components/"
scp -i "$SSH_KEY" frontend/src/components/PdfViewer.tsx "${AWS_USER}@${AWS_IP}:${REMOTE_PATH}/frontend/src/components/"
scp -i "$SSH_KEY" frontend/src/components/ChatPanel.tsx "${AWS_USER}@${AWS_IP}:${REMOTE_PATH}/frontend/src/components/"

echo "  - Frontend App.tsx..."
scp -i "$SSH_KEY" frontend/src/App.tsx "${AWS_USER}@${AWS_IP}:${REMOTE_PATH}/frontend/src/"

# Transfer nginx configs
echo "  - Nginx configurations..."
scp -i "$SSH_KEY" nginx/nginx.conf "${AWS_USER}@${AWS_IP}:${REMOTE_PATH}/nginx/"
scp -i "$SSH_KEY" nginx/conf.d/pdfpixie.conf "${AWS_USER}@${AWS_IP}:${REMOTE_PATH}/nginx/conf.d/"

# Transfer deployment scripts
echo "  - Deployment scripts..."
scp -i "$SSH_KEY" deploy.sh "${AWS_USER}@${AWS_IP}:${REMOTE_PATH}/"
scp -i "$SSH_KEY" Dockerfile "${AWS_USER}@${AWS_IP}:${REMOTE_PATH}/"

# Transfer documentation
echo "  - Documentation..."
scp -i "$SSH_KEY" AWS_DEPLOYMENT_GUIDE.md "${AWS_USER}@${AWS_IP}:${REMOTE_PATH}/"
scp -i "$SSH_KEY" FIX_SUMMARY.md "${AWS_USER}@${AWS_IP}:${REMOTE_PATH}/"
scp -i "$SSH_KEY" QUICK_DEPLOY.md "${AWS_USER}@${AWS_IP}:${REMOTE_PATH}/"

echo "✅ Files transferred successfully"
echo ""

# Deploy on AWS
echo "🚀 Deploying on AWS instance..."
ssh -i "$SSH_KEY" "${AWS_USER}@${AWS_IP}" << 'ENDSSH'
    cd /home/ubuntu/chatpdf
    
    echo "📦 Installing frontend dependencies (if needed)..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    
    echo "🔨 Building frontend with production config..."
    npm run build
    cd ..
    
    echo "🐳 Building Docker image..."
    docker build -t pdfpixie:latest -f Dockerfile .
    
    echo "🛑 Stopping old container..."
    docker stop pdfpixie 2>/dev/null || true
    docker rm pdfpixie 2>/dev/null || true
    
    echo "▶️  Starting new container..."
    docker run -d \
      --name pdfpixie \
      -p 80:80 \
      -p 8000:8000 \
      -v $(pwd)/backend/data:/app/data \
      -e OPENROUTER_API_KEY="${OPENROUTER_API_KEY}" \
      --restart unless-stopped \
      pdfpixie:latest
    
    echo "⏳ Waiting for container to start..."
    sleep 10
    
    echo "✅ Checking deployment..."
    if docker ps | grep -q pdfpixie; then
        echo "✅ Container is running!"
        docker ps | grep pdfpixie
    else
        echo "❌ Container failed to start"
        docker logs pdfpixie --tail 20
        exit 1
    fi
    
    echo ""
    echo "🎉 Deployment complete!"
    echo "🌐 Access your app at: http://13.201.129.219"
ENDSSH

echo ""
echo "✅ All done!"
echo ""
echo "🌐 Your app is now accessible from any device at:"
echo "   • http://13.201.129.219"
echo "   • http://pdfpixie.duckdns.org (after DNS setup)"
echo ""
echo "📱 Test it from your phone or another device!"
echo ""
echo "🔧 Useful commands on AWS:"
echo "   ssh -i $SSH_KEY ${AWS_USER}@${AWS_IP}"
echo "   docker logs pdfpixie -f"
echo "   docker restart pdfpixie"
echo ""
