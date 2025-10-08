#!/bin/bash
# ===================================================================
# PDF Pal - Restart Servers Script
# ===================================================================

echo "Restarting PDF Pal servers..."
echo ""

# Stop servers
./scripts/stop.sh

echo ""
echo "Waiting 2 seconds..."
sleep 2

echo ""
# Start servers
./start_app_universal.sh
