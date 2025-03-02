from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
from dotenv import load_dotenv

# Φόρτωση περιβαλλοντικών μεταβλητών
load_dotenv()

logger = logging.getLogger(__name__)

# Λήψη του Database URL από τις περιβαλλοντικές μεταβλητές
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.warning("DATABASE_URL δεν βρέθηκε. Χρήση SQLite ως fallback.")
    DATABASE_URL = "sqlite:///./mining_assistant.db"

# Δημιουργία του engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Ορίστε σε True για debugging
    pool_pre_ping=True,  # Έλεγχος σύνδεσης πριν τη χρήση
    pool_recycle=3600,  # Ανανέωση συνδέσεων μετά από 1 ώρα
)

# Δημιουργία session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Βασική κλάση για τα μοντέλα
Base = declarative_base()

def init_db():
    """
    Αρχικοποίηση της βάσης δεδομένων και δημιουργία των πινάκων
    """
    try:
        # Δημιουργία των πινάκων αν δεν υπάρχουν
        Base.metadata.create_all(bind=engine)
        logger.info("Επιτυχής αρχικοποίηση βάσης δεδομένων")
        return True
    except Exception as e:
        logger.error(f"Σφάλμα κατά την αρχικοποίηση της βάσης δεδομένων: {str(e)}")
        return False

# Βοηθητική συνάρτηση για τη διαχείριση της σύνδεσης της βάσης δεδομένων
def get_db():
    """
    Δημιουργία και διαχείριση μιας σύνδεσης με τη βάση δεδομένων ανά αίτημα.
    Χρησιμοποιείται ως dependency σε FastAPI endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_connection():
    """
    Έλεγχος της σύνδεσης με τη βάση δεδομένων
    """
    try:
        # Δημιουργία σύνδεσης και εκτέλεση ενός απλού ερωτήματος
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logger.error(f"Σφάλμα σύνδεσης με τη βάση δεδομένων: {str(e)}")
        return False
