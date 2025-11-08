#!/bin/bash
# DuckDNS Dynamic DNS Update Script
# This script updates your DuckDNS domain with your EC2 instance's public IP

# Configuration
DUCKDNS_DOMAIN="your-subdomain"  # Change this to your DuckDNS subdomain (without .duckdns.org)
DUCKDNS_TOKEN="your-duckdns-token"  # Get this from https://www.duckdns.org/

# Update DuckDNS
echo "Updating DuckDNS..."
RESPONSE=$(curl -s "https://www.duckdns.org/update?domains=${DUCKDNS_DOMAIN}&token=${DUCKDNS_TOKEN}&ip=")

if [ "$RESPONSE" = "OK" ]; then
    echo "✅ DuckDNS updated successfully!"
    echo "Your domain: ${DUCKDNS_DOMAIN}.duckdns.org"
else
    echo "❌ DuckDNS update failed!"
    exit 1
fi
