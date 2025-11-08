#!/bin/bash
# SSL Setup Script using Let's Encrypt (Certbot)
# Run this script on your EC2 instance to obtain free SSL certificates

set -e

echo "🔐 PDFPixie SSL Setup with Let's Encrypt"
echo "========================================"

# Check if domain is configured
if [ -z "$1" ]; then
    echo "Usage: ./setup-ssl.sh your-subdomain.duckdns.org"
    exit 1
fi

DOMAIN=$1

echo "Installing Certbot..."
sudo apt-get update
sudo apt-get install -y certbot

echo "Stopping Docker containers temporarily..."
docker-compose down

echo "Obtaining SSL certificate for ${DOMAIN}..."
sudo certbot certonly --standalone \
    --preferred-challenges http \
    --email your-email@example.com \
    --agree-tos \
    --no-eff-email \
    -d ${DOMAIN}

echo "Updating Nginx configuration..."
# Backup current nginx config
cp Dockerfile Dockerfile.backup

# Update Dockerfile to use SSL nginx config
sed -i 's/COPY nginx.conf/COPY nginx-ssl.conf/' Dockerfile
sed -i "s/your-subdomain.duckdns.org/${DOMAIN}/g" nginx-ssl.conf

echo "Updating docker-compose.yml to mount SSL certificates..."
# Add SSL certificate volumes to docker-compose.yml
cat >> docker-compose.yml << EOF

    # SSL Certificates (uncomment after obtaining certs)
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt:ro
EOF

echo "Rebuilding Docker containers with SSL..."
docker-compose build
docker-compose up -d

echo ""
echo "✅ SSL Setup Complete!"
echo ""
echo "Your site is now accessible at:"
echo "  https://${DOMAIN}"
echo ""
echo "Certificate auto-renewal:"
echo "  Add this to crontab (run: crontab -e):"
echo "  0 0 1 * * certbot renew --quiet && docker-compose restart app"
echo ""
