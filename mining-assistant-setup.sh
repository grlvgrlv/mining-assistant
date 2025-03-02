#!/bin/bash

# Mining Assistant Setup Script
# Comprehensive setup with error handling and system checks

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project base directory
PROJECT_BASE="/home/grlv/mining-assistant"

# Function to check and install system dependencies
check_and_install_dependencies() {
    echo -e "${BLUE}Checking and installing system dependencies...${NC}"
    
    # Update package list
    sudo apt update

    # Check and install Python 3 and venv
    if ! command -v python3 &> /dev/null; then
        echo -e "${YELLOW}Python 3 not found. Installing...${NC}"
        sudo apt install -y python3 python3-pip
    fi

    # Install venv package
    if ! dpkg -s python3-venv &> /dev/null; then
        echo -e "${YELLOW}Installing python3-venv package...${NC}"
        sudo apt install -y python3-venv
    fi

    # Install additional system dependencies
    sudo apt install -y \
        build-essential \
        git \
        libssl-dev \
        libffi-dev \
        python3-dev \
        cargo

    echo -e "${GREEN}✓ System dependencies installed successfully${NC}"
}

# Function to create and setup virtual environment
setup_virtual_environment() {
    echo -e "${BLUE}Setting up Python virtual environment...${NC}"
    
    # Remove existing venv if it exists
    if [ -d "$PROJECT_BASE/venv" ]; then
        rm -rf "$PROJECT_BASE/venv"
    fi

    # Create new virtual environment
    python3 -m venv "$PROJECT_BASE/venv"

    # Activate virtual environment
    source "$PROJECT_BASE/venv/bin/activate"

    # Upgrade pip and setuptools
    pip install --upgrade pip setuptools wheel

    echo -e "${GREEN}✓ Virtual environment created and activated${NC}"
}

# Function to clean and filter requirements
prepare_requirements() {
    echo -e "${BLUE}Preparing Python requirements...${NC}"
    
    # Create a clean requirements file
    cat > "$PROJECT_BASE/requirements.txt" << EOL
# Core dependencies
fastapi
uvicorn
sqlalchemy
pydantic
torch
transformers
peft
httpx
redis
python-telegram-bot
psycopg2-binary
pytest
black
isort
flake8

# Remove problematic packages
# apturl has been removed
# Add any other packages that might cause issues

# Mining and AI specific
numpy
pandas
scikit-learn
matplotlib
python-dotenv
EOL

    echo -e "${GREEN}✓ Requirements file updated${NC}"
}

# Function to install Python dependencies
install_python_dependencies() {
    echo -e "${BLUE}Installing Python dependencies...${NC}"
    
    # Install requirements
    pip install -r "$PROJECT_BASE/requirements.txt"

    echo -e "${GREEN}✓ Python dependencies installed successfully${NC}"
}

# Function to setup project structure
setup_project_structure() {
    echo -e "${BLUE}Setting up project directory structure...${NC}"
    
    # Create necessary directories
    mkdir -p "$PROJECT_BASE/backend/connectors"
    mkdir -p "$PROJECT_BASE/frontend/src/components"
    mkdir -p "$PROJECT_BASE/frontend/src/views"
    mkdir -p "$PROJECT_BASE/models/mining-assistant-llm"
    mkdir -p "$PROJECT_BASE/data"
    mkdir -p "$PROJECT_BASE/logs"

    echo -e "${GREEN}✓ Project structure created${NC}"
}

# Function to create .env file
create_env_file() {
    echo -e "${BLUE}Creating .env configuration file...${NC}"
    
    # Only create if .env doesn't exist
    if [ ! -f "$PROJECT_BASE/.env" ]; then
        cat > "$PROJECT_BASE/.env" << EOL
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/mining_assistant

# API Keys
CLOREAI_API_KEY=your_cloreai_api_key
MINING_API_KEY=your_mining_api_key
ENERGY_API_KEY=your_energy_api_key

# LLM Configuration
MODEL_PATH=./models/mining-assistant-llm
DEVICE=cuda

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
EOL
        echo -e "${GREEN}✓ .env file created${NC}"
    else
        echo -e "${YELLOW}⚠ .env file already exists. Skipping creation.${NC}"
    fi
}

# Main setup function
main() {
    echo -e "${BLUE}=== AI Mining Assistant Setup ===${NC}"
    
    # Change to project directory
    cd "$PROJECT_BASE" || exit

    # Run setup steps
    check_and_install_dependencies
    setup_virtual_environment
    prepare_requirements
    install_python_dependencies
    setup_project_structure
    create_env_file

    echo -e "\n${GREEN}✓ Setup completed successfully!${NC}"
    echo -e "${YELLOW}Next steps:${NC}"
    echo -e "1. Edit .env file with your specific configurations"
    echo -e "2. Activate virtual environment: source venv/bin/activate"
    echo -e "3. Start backend server: python -m backend.main"
}

# Run the main setup function
main
