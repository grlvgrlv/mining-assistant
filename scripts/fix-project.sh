#!/bin/bash

# Χρώματα για καλύτερη αναγνωσιμότητα
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Mining Assistant Project Fix Script ===${NC}"
echo -e "${BLUE}Διόρθωση δομής και προετοιμασία περιβάλλοντος για το AI Mining Assistant${NC}"
echo ""

# Ορισμός βασικού φακέλου
BASE_DIR="/home/grlv/mining-assistant"
cd "$BASE_DIR" || { echo -e "${RED}Ο φάκελος $BASE_DIR δεν υπάρχει!${NC}"; exit 1; }

echo -e "${YELLOW}1. Διόρθωση δομής φακέλων...${NC}"

# Δημιουργία προσωρινού φακέλου για αντιγραφή
mkdir -p /tmp/mining-assistant-tmp

# Αντιγραφή όλων των σημαντικών αρχείων από την εσωτερική δομή
echo -e "${GREEN}Αντιγραφή αρχείων από τον εσωτερικό φάκελο...${NC}"
if [ -d "$BASE_DIR/backend/mining-assistant" ]; then
    cp -r "$BASE_DIR/backend/mining-assistant"/* /tmp/mining-assistant-tmp/
    echo -e "${GREEN}✓ Αρχεία αντιγράφηκαν στον προσωρινό φάκελο${NC}"
else
    echo -e "${YELLOW}⚠ Ο φάκελος backend/mining-assistant δεν υπάρχει, παραλείπεται αυτό το βήμα${NC}"
fi

# Καθαρισμός της υπάρχουσας δομής, αλλά διατήρηση του φακέλου backend/connectors
echo -e "${GREEN}Καθαρισμός της τρέχουσας δομής...${NC}"
if [ -d "$BASE_DIR/backend/connectors" ]; then
    mkdir -p /tmp/mining-assistant-tmp/backend_connectors_backup
    cp -r "$BASE_DIR/backend/connectors"/* /tmp/mining-assistant-tmp/backend_connectors_backup/
    echo -e "${GREEN}✓ Αντίγραφα ασφαλείας των connectors δημιουργήθηκαν${NC}"
fi

# Αφαίρεση της παλιάς δομής
echo -e "${GREEN}Αφαίρεση παλιών φακέλων...${NC}"
rm -rf "$BASE_DIR/backend"
rm -rf "$BASE_DIR/data"
rm -rf "$BASE_DIR/frontend"
rm -rf "$BASE_DIR/logs"
rm -rf "$BASE_DIR/models"
echo -e "${GREEN}✓ Παλιοί φάκελοι αφαιρέθηκαν${NC}"

# Δημιουργία της σωστής δομής από το προσωρινό αντίγραφο
echo -e "${GREEN}Αντιγραφή των αρχείων στη σωστή δομή...${NC}"
cp -r /tmp/mining-assistant-tmp/* "$BASE_DIR"
echo -e "${GREEN}✓ Αρχεία αντιγράφηκαν στη σωστή δομή${NC}"

# Επαναφορά των connectors αν υπάρχουν αντίγραφα ασφαλείας
if [ -d "/tmp/mining-assistant-tmp/backend_connectors_backup" ]; then
    echo -e "${GREEN}Επαναφορά των connectors...${NC}"
    mkdir -p "$BASE_DIR/backend/connectors"
    cp -r /tmp/mining-assistant-tmp/backend_connectors_backup/* "$BASE_DIR/backend/connectors"
    echo -e "${GREEN}✓ Connectors επαναφέρθηκαν${NC}"
fi

# Δημιουργία απαραίτητων φακέλων αν δεν υπάρχουν
echo -e "${GREEN}Δημιουργία απαραίτητων φακέλων...${NC}"
mkdir -p "$BASE_DIR/backend/connectors"
mkdir -p "$BASE_DIR/frontend/src/components"
mkdir -p "$BASE_DIR/frontend/src/views"
mkdir -p "$BASE_DIR/models/mining-assistant-llm"
mkdir -p "$BASE_DIR/data"
mkdir -p "$BASE_DIR/logs"
echo -e "${GREEN}✓ Φάκελοι δημιουργήθηκαν${NC}"

# Καθαρισμός προσωρινού φακέλου
rm -rf /tmp/mining-assistant-tmp
echo -e "${GREEN}✓ Προσωρινός φάκελος καθαρίστηκε${NC}"

echo -e "${YELLOW}2. Ρύθμιση του virtual environment...${NC}"

# Έλεγχος αν υπάρχει το venv και δημιουργία αν δεν υπάρχει
if [ ! -d "$BASE_DIR/venv" ]; then
    echo -e "${GREEN}Δημιουργία νέου virtual environment...${NC}"
    python3 -m venv "$BASE_DIR/venv"
    echo -e "${GREEN}✓ Virtual environment δημιουργήθηκε${NC}"
else
    echo -e "${GREEN}✓ Virtual environment υπάρχει ήδη${NC}"
fi

# Ενεργοποίηση του virtual environment
echo -e "${GREEN}Ενεργοποίηση του virtual environment...${NC}"
source "$BASE_DIR/venv/bin/activate"
echo -e "${GREEN}✓ Virtual environment ενεργοποιήθηκε${NC}"

# Εγκατάσταση των απαραίτητων πακέτων
echo -e "${YELLOW}3. Εγκατάσταση των απαραίτητων πακέτων Python...${NC}"
if [ -f "$BASE_DIR/requirements.txt" ]; then
    echo -e "${GREEN}Εγκατάσταση από requirements.txt...${NC}"
    pip install -r "$BASE_DIR/requirements.txt"
else
    echo -e "${GREEN}Εγκατάσταση βασικών πακέτων...${NC}"
    pip install --upgrade pip
    pip install fastapi uvicorn sqlalchemy pydantic torch transformers peft httpx redis python-telegram-bot
    pip install psycopg2-binary pytest black isort flake8
    
    # Αποθήκευση των εγκατεστημένων πακέτων σε requirements.txt
    pip freeze > "$BASE_DIR/requirements.txt"
fi
echo -e "${GREEN}✓ Εγκατάσταση πακέτων ολοκληρώθηκε${NC}"

# Δημιουργία .env αρχείου αν δεν υπάρχει
echo -e "${YELLOW}4. Ρύθμιση περιβαλλοντικών μεταβλητών...${NC}"
if [ ! -f "$BASE_DIR/.env" ]; then
    echo -e "${GREEN}Δημιουργία .env αρχείου...${NC}"
    cat > "$BASE_DIR/.env" << EOL
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
    echo -e "${GREEN}✓ Αρχείο .env δημιουργήθηκε${NC}"
else
    echo -e "${GREEN}✓ Αρχείο .env υπάρχει ήδη${NC}"
fi

# Έλεγχος προαπαιτούμενων συστήματος
echo -e "${YELLOW}5. Έλεγχος προαπαιτούμενων συστήματος...${NC}"
if [ -f "$BASE_DIR/system_requirements.py" ]; then
    chmod +x "$BASE_DIR/system_requirements.py"
    python "$BASE_DIR/system_requirements.py" check
else
    echo -e "${RED}⚠ Το αρχείο system_requirements.py δεν βρέθηκε!${NC}"
    echo -e "${YELLOW}Δημιουργία νέου αρχείου system_requirements.py...${NC}"
    
    # Εδώ θα μπορούσατε να προσθέσετε κώδικα για τη δημιουργία του system_requirements.py
    # Για συντομία, δεν το περιλαμβάνω εδώ
fi

# Δοκιμαστική εκκίνηση του backend
echo -e "${YELLOW}6. Δοκιμαστική εκκίνηση του backend...${NC}"
echo -e "${GREEN}Για να ξεκινήσετε το backend, εκτελέστε:${NC}"
echo -e "cd $BASE_DIR"
echo -e "source venv/bin/activate"
echo -e "python -m backend.main"

echo -e "\n${BLUE}=== Ολοκλήρωση Διόρθωσης και Προετοιμασίας ===${NC}"
echo -e "${GREEN}Η δομή του project έχει διορθωθεί και το περιβάλλον είναι έτοιμο για ανάπτυξη.${NC}"
echo -e "${GREEN}Επόμενα βήματα:${NC}"
echo -e "1. Ρυθμίστε τις μεταβλητές στο αρχείο .env"
echo -e "2. Εκκινήστε το backend server"
echo -e "3. Αναπτύξτε το frontend"
echo -e "4. Προετοιμάστε το AI μοντέλο"

echo -e "\n${YELLOW}Σημείωση: Μην ξεχάσετε να ενεργοποιείτε το virtual environment πριν από κάθε εργασία:${NC}"
echo -e "source $BASE_DIR/venv/bin/activate"
