#!/bin/bash
"""
Εργαλείο εκκίνησης περιβάλλοντος για το AI Mining Assistant

Ενεργοποιεί και προετοιμάζει το περιβάλλον για τη λειτουργία του AI Mining Assistant. 
Περιλαμβάνει την εκκίνηση της PostgreSQL, την προετοιμασία της βάσης δεδομένων, και τον έλεγχο του AI model.

Βασικές λειτουργίες:
- Ενεργοποίηση virtual environment και εκκίνηση PostgreSQL
- Προετοιμασία και ελεγχος βάσης δεδομένων
- Επιβεβαίωση και φόρτωση του AI model
"""
# Εργαλείο εκκίνησης περιβάλλοντος για το AI Mining Assistant
# Χρώματα για καλύτερη αναγνωσιμότητα
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Βασική διαδρομή του project
PROJECT_BASE="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

# Συνάρτηση για εκτύπωση με χρώμα
print_status() {
    echo -e "${1}${2}${NC}"
}

# Είσοδος στον βασικό φάκελο του project
cd "$PROJECT_BASE" || exit 1

# 1. Ενεργοποίηση Virtual Environment
if [ -d "venv" ]; then
    print_status "$GREEN" "✓ Ενεργοποίηση Virtual Environment..."
    source venv/bin/activate
else
    print_status "$RED" "✗ Το Virtual Environment δεν βρέθηκε!"
    exit 1
fi

# 2. Έλεγχος και εκκίνηση PostgreSQL
print_status "$YELLOW" "Έλεγχος κατάστασης PostgreSQL..."
pg_isready > /dev/null 2>&1
if [ $? -ne 0 ]; then
    print_status "$RED" "✗ PostgreSQL δεν είναι εκτελούμενη. Προσπάθεια εκκίνησης..."
    sudo service postgresql start
    sleep 5
    pg_isready > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        print_status "$RED" "✗ Αποτυχία εκκίνησης PostgreSQL!"
        exit 1
    fi
fi
print_status "$GREEN" "✓ PostgreSQL είναι λειτουργική"

# 3. Έλεγχος και προετοιμασία βάσης δεδομένων
print_status "$YELLOW" "Προετοιμασία βάσης δεδομένων..."
python -c "
import sys
sys.path.append('.')
from backend.database_verification import verify_database_connection, insert_initial_data

# Έλεγχος σύνδεσης
session = verify_database_connection()
if session:
    # Εισαγωγή αρχικών δεδομένων αν χρειάζεται
    insert_initial_data(session)
    session.close()
    print('Βάση δεδομένων έτοιμη.')
else:
    print('Σφάλμα σύνδεσης με τη βάση δεδομένων.')
    sys.exit(1)
"

# 4. Προετοιμασία AI Model (προαιρετικό)
print_status "$YELLOW" "Προετοιμασία AI Model..."
python -c "
import sys
sys.path.append('.')
from backend.ai_engine import AIEngine
import asyncio

async def load_model():
    ai_engine = AIEngine()
    await ai_engine.load_model()

asyncio.run(load_model())
"

# 5. Έλεγχος απαραίτητων υπηρεσιών
print_status "$GREEN" "✓ Όλες οι υπηρεσίες προετοιμάστηκαν επιτυχώς!"

# Προαιρετικό: Εκτέλεση διαγνωστικών
if [ "$1" == "diagnose" ]; then
    print_status "$YELLOW" "Εκτέλεση διαγνωστικών ελέγχων..."
    python scripts/debug_tools.py
    python scripts/system_requirements.py
    python scripts/status.py
fi

# Επιστροφή στον χρήστη για περαιτέρω ενέργειες
print_status "$GREEN" "Το περιβάλλον είναι έτοιμο. Μπορείτε να συνεχίσετε με τις εργασίες σας."
