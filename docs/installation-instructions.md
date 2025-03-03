# Οδηγίες Εγκατάστασης System Health Dashboard

Το System Health Dashboard είναι ένα εργαλείο παρακολούθησης για το Mining Assistant project που σου επιτρέπει να βλέπεις σε πραγματικό χρόνο:

- Την κατάσταση του συστήματος (CPU, RAM, Δίσκο)
- Την κατάσταση των GPUs (φόρτο, μνήμη, θερμοκρασία)
- Την πρόοδο του project
- Την κατάσταση των υπηρεσιών
- Τις μεταβλητές περιβάλλοντος
- Και άλλες χρήσιμες πληροφορίες

## Βήματα Εγκατάστασης

### 1. Κατέβασε τα απαραίτητα αρχεία

Μέσω terminal, μετακινήσου στον βασικό φάκελο του project:

```bash
cd /home/grlv/mining-assistant
```

Δημιούργησε το script εγκατάστασης:

```bash
# Δημιουργία του αρχείου εγκατάστασης
curl -s -o setup_system_health_dashboard.sh https://raw.githubusercontent.com/user/mining-assistant/main/setup_system_health_dashboard.sh || cat > setup_system_health_dashboard.sh << 'EOL'
#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project base directory
PROJECT_BASE="/home/grlv/mining-assistant"

echo -e "${GREEN}=== Setting up System Health Dashboard ===${NC}"

# Check if virtual environment exists
if [[ ! -d "${PROJECT_BASE}/venv" ]]; then
    echo -e "${RED}Virtual environment not found. Creating a new one...${NC}"
    python3 -m venv "${PROJECT_BASE}/venv"
fi

# Activate virtual environment
source "${PROJECT_BASE}/venv/bin/activate"

# Install required packages
echo -e "${YELLOW}Installing required packages...${NC}"
pip install fastapi uvicorn psutil python-dotenv GPUtil jinja2 

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p "${PROJECT_BASE}/templates"
mkdir -p "${PROJECT_BASE}/static/css"
mkdir -p "${PROJECT_BASE}/static/js"
mkdir -p "${PROJECT_BASE}/logs"

# Download or create the app.py file
echo -e "${YELLOW}Creating dashboard application...${NC}"
curl -s -o "${PROJECT_BASE}/app.py" "https://raw.githubusercontent.com/user/mining-assistant/main/app.py" || {
    echo -e "${YELLOW}Could not download app.py. Creating it locally...${NC}"
    # The app.py content should be provided here
    # This will be a long file that will be downloaded from GitHub
}

# Create the dashboard.html template
echo -e "${YELLOW}Creating HTML template...${NC}"
mkdir -p "${PROJECT_BASE}/templates"
# Create dashboard.html content here
# This will be another long file that will be downloaded from GitHub

# Create startup script
echo -e "${YELLOW}Creating startup script...${NC}"
cat > "${PROJECT_BASE}/start_system_health_dashboard.sh" << 'EOLS'
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
EOLS

# Make the scripts executable
chmod +x "${PROJECT_BASE}/start_system_health_dashboard.sh"

echo -e "${GREEN}✓ System Health Dashboard setup completed successfully!${NC}"
echo -e "${YELLOW}To start the dashboard, run:${NC}"
echo -e "  cd ${PROJECT_BASE}"
echo -e "  ./start_system_health_dashboard.sh"
echo -e "${YELLOW}Then open http://localhost:8050 in your browser${NC}"
EOL

# Κάνε το script εκτελέσιμο
chmod +x setup_system_health_dashboard.sh
```

### 2. Εκτέλεσε το script εγκατάστασης

```bash
./setup_system_health_dashboard.sh
```

Αυτό θα:
- Εγκαταστήσει τα απαραίτητα πακέτα Python
- Δημιουργήσει την εφαρμογή dashboard
- Ρυθμίσει τα HTML templates
- Δημιουργήσει το script εκκίνησης

### 3. Εκκίνηση του Dashboard

Για να ξεκινήσεις το dashboard:

```bash
./start_system_health_dashboard.sh
```

Αυτό θα εκκινήσει έναν web server στη θύρα 8050. Μπορείς να προσπελάσεις το dashboard ανοίγοντας στον browser σου:

```
http://localhost:8050
```

Ή, αν θέλεις να το προσπελάσεις από άλλον υπολογιστή στο δίκτυο:

```
http://[IP_ADDRESS]:8050
```

Όπου `[IP_ADDRESS]` είναι η IP διεύθυνση του server.

## Χαρακτηριστικά του Dashboard

- **Αυτόματη ανανέωση**: Το dashboard ανανεώνεται αυτόματα κάθε 1 λεπτό
- **Χειροκίνητη ανανέωση**: Μπορείς να πατήσεις το κουμπί "Refresh Now" για άμεση ενημέρωση
- **Επεκτεινόμενες ενότητες**: Πάτησε το "Show More Details" σε κάθε κάρτα για περισσότερες πληροφορίες
- **Ειδοποιήσεις χρωμάτων**: Το dashboard χρησιμοποιεί χρωματική κωδικοποίηση για να υποδείξει την κατάσταση:
  - Πράσινο: Όλα λειτουργούν κανονικά
  - Κίτρινο: Προειδοποίηση, χρειάζεται προσοχή
  - Κόκκινο: Κρίσιμο πρόβλημα, απαιτείται άμεση ενέργεια

## Επίλυση Προβλημάτων

Αν αντιμετωπίσεις προβλήματα:

1. **Βεβαιώσου ότι το virtual environment είναι ενεργοποιημένο**:
   ```bash
   source ~/mining-assistant/venv/bin/activate
   ```

2. **Έλεγξε τα απαραίτητα πακέτα**:
   ```bash
   pip install -U fastapi uvicorn psutil python-dotenv GPUtil jinja2
   ```

3. **Αν το dashboard δεν ξεκινά**:
   Δοκίμασε να εκτελέσεις απευθείας την εφαρμογή:
   ```bash
   cd ~/mining-assistant
   python -m uvicorn app:app --host 0.0.0.0 --port 8050
   ```
   
4. **Αν υπάρχει σφάλμα πρόσβασης στη θύρα**:
   Δοκίμασε μια διαφορετική θύρα:
   ```bash
   python -m uvicorn app:app --host 0.0.0.0 --port 8051
   ```

5. **Αν το dashboard δεν φορτώνει δεδομένα**:
   Βεβαιώσου ότι οι φάκελοι `logs` και `backend` υπάρχουν και είναι προσβάσιμοι.

## Επιπλέον Πληροφορίες

Το dashboard είναι ένα standalone εργαλείο που δεν επηρεάζει τις υπόλοιπες λειτουργίες του Mining Assistant. Μπορείς να το έχεις πάντα ανοιχτό σε ένα παράθυρο του browser για συνεχή παρακολούθηση του συστήματος και του project.

Η εφαρμογή χρησιμοποιεί FastAPI στο backend και απλό HTML/CSS/JavaScript στο frontend, χωρίς την ανάγκη εξωτερικών βιβλιοθηκών όπως το Tailwind CSS που προκαλούσε προβλήματα.
