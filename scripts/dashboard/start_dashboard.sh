#!/bin/bash
# Progress Dashboard
# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project base directory
PROJECT_BASE="/home/grlv/mining-assistant"
DASHBOARD_DIR="${PROJECT_BASE}/scripts/dashboard"

# Activate virtual environment
source "${PROJECT_BASE}/venv/bin/activate"

echo -e "${YELLOW}Starting System Health Dashboard...${NC}"

# Make sure static directories exist
mkdir -p "${DASHBOARD_DIR}/static/css"
mkdir -p "${DASHBOARD_DIR}/static/js"

# Run the application - uncomment the approach you want to use
cd "${DASHBOARD_DIR}"
python3 -m uvicorn app:app --host 0.0.0.0 --port 8050

# Alternative approach (uncomment if needed)
# cd "${PROJECT_BASE}"
# python app.py

# The script will stay running as long as the application is running
