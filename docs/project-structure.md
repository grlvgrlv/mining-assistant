# Δομή Έργου AI Mining Assistant

## Βασική Δομή Φακέλων

```
/home/grlv/mining-assistant
├── backend             # Ο κύριος φάκελος του backend
│   ├── connectors      # Συνδέσεις με εξωτερικά APIs και συστήματα
│   └── ...             # Άλλα αρχεία Python του backend
├── data                # Δεδομένα για το σύστημα και το AI μοντέλο
├── frontend            # Ο φάκελος του frontend (Vue.js)
│   └── src             # Πηγαίος κώδικας frontend
├── logs                # Αρχεία καταγραφής
├── models              # AI μοντέλα
│   └── mining-assistant-llm  # Το fine-tuned μοντέλο
└── venv                # Python virtual environment
```

## Αναλυτική Περιγραφή Αρχείων

### Backend Core

- `backend/main.py`: Το κύριο αρχείο του FastAPI server που ορίζει τα endpoints και διαχειρίζεται τα αιτήματα.
- `backend/database.py`: Διαχειρίζεται τη σύνδεση με τη βάση δεδομένων (PostgreSQL) χρησιμοποιώντας SQLAlchemy.
- `backend/models.py`: Ορίζει τα SQLAlchemy μοντέλα που αντιστοιχούν στους πίνακες της βάσης δεδομένων.
- `backend/schemas.py`: Περιέχει τα Pydantic schemas που χρησιμοποιούνται για την επικύρωση δεδομένων στο API.
- `backend/ai_engine.py`: Υλοποιεί την AI λογική για την επεξεργασία αιτημάτων και τη βελτιστοποίηση mining.

### Connectors (Backend)

- `backend/connectors/mining_connector.py`: Συνδέεται με mining software και APIs για λήψη στατιστικών και έλεγχο εξόρυξης.
- `backend/connectors/energy_connector.py`: Διαχειρίζεται τη σύνδεση με συστήματα παρακολούθησης ενέργειας και φωτοβολταϊκά.
- `backend/connectors/cloreai_connector.py`: Επικοινωνεί με το CloreAI API για υπηρεσίες ενοικίασης GPU.
- `backend/connectors/__init__.py`: Αρχείο που επιτρέπει την εισαγωγή των connectors ως πακέτο Python.

### Frontend

- `frontend/package.json`: Ορίζει τις εξαρτήσεις και τα scripts του frontend.
- `frontend/src/`: Περιέχει τα Vue.js components, views και άλλα αρχεία του frontend.

### Scripts & Utilities

- `mining-assistant-setup.sh`: Script εγκατάστασης του συστήματος.
- `fix-project.sh`: Script για επιδιόρθωση της δομής φακέλων του project.
- `status.py`: Script για τον έλεγχο της κατάστασης των υπηρεσιών.
- `system_requirements.py`: Ελέγχει τα προαπαιτούμενα του συστήματος.

### Configuration Files

- `requirements.txt`: Λίστα με τα απαιτούμενα πακέτα Python.
- `visible_env.txt`: Περιέχει περιβαλλοντικές μεταβλητές που μπορούν να γίνουν ορατές.
- `.env`: (Δεν εμφανίζεται στη λίστα) Περιβαλλοντικές μεταβλητές για το project.

## Ροή Λειτουργίας

1. Ο χρήστης αλληλεπιδρά με το frontend (Vue.js) ή μέσω ενός chatbot (Telegram/Discord).
2. Τα αιτήματα δρομολογούνται στον FastAPI server (`backend/main.py`).
3. Ο server χρησιμοποιεί τους connectors για επικοινωνία με εξωτερικά συστήματα:
   - `mining_connector.py` για επικοινωνία με το mining software
   - `energy_connector.py` για επικοινωνία με συστήματα ενέργειας
   - `cloreai_connector.py` για επικοινωνία με το CloreAI API
4. Τα δεδομένα αναλύονται από το `ai_engine.py` για βελτιστοποίηση και προτάσεις.
5. Τα αποτελέσματα αποθηκεύονται στη βάση δεδομένων και επιστρέφονται στον χρήστη.

## Εξαρτήσεις Αρχείων

- `main.py` εξαρτάται από `database.py`, `models.py`, `schemas.py`, και τους connectors.
- `models.py` εξαρτάται από `database.py` (Base).
- Οι connectors εξαρτώνται από περιβαλλοντικές μεταβλητές στο `.env` για κλειδιά API και άλλες ρυθμίσεις.
- `ai_engine.py` φορτώνει το μοντέλο από τον φάκελο `models/mining-assistant-llm`.

## Σημαντικά Σημεία Προσοχής

1. **Εισαγωγές (Imports)**: Βεβαιωθείτε ότι χρησιμοποιείτε το σωστό πρόθεμα `backend.` όταν εισάγετε modules.
2. **Περιβαλλοντικές Μεταβλητές**: Όλα τα API keys και ευαίσθητες πληροφορίες πρέπει να αποθηκεύονται στο `.env`.
3. **Καταγραφή (Logging)**: Χρησιμοποιείτε το σύστημα καταγραφής για εύκολο εντοπισμό σφαλμάτων.
4. **Error Handling**: Χειριστείτε τα σφάλματα με try/except και καταγράψτε τα σφάλματα.
