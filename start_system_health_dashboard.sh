#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project base directory
PROJECT_BASE="/home/grlv/mining-assistant"

# Activate virtual environment
source "${PROJECT_BASE}/venv/bin/activate"

echo -e "${YELLOW}Starting System Health Dashboard...${NC}"

# Run the application
cd "${PROJECT_BASE}"
python -m uvicorn app:app --host 0.0.0.0 --port 8050

# The script will stay running as long as the application is running
