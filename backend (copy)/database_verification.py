import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Προσθήκη του path του backend στο sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Φόρτωση περιβαλλοντικών μεταβλητών
load_dotenv()

# Τώρα μπορείς να κάνεις import από το backend
from backend.models import Base, User, MiningConfig, MiningStat, EnergyConsumption, CryptoPrice

def verify_database_connection():
    """
    Επαλήθευση σύνδεσης με τη βάση δεδομένων
    """
    try:
        # Λήψη URL βάσης δεδομένων από περιβαλλοντικές μεταβλητές
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        if not DATABASE_URL:
            raise ValueError("Δεν βρέθηκε DATABASE_URL στις περιβαλλοντικές μεταβλητές")
        
        # Δημιουργία engine
        engine = create_engine(DATABASE_URL)
        
        # Δημιουργία session
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        print("Επιτυχής σύνδεση με τη βάση δεδομένων!")
        return session
    except Exception as e:
        print(f"Σφάλμα σύνδεσης με τη βάση δεδομένων: {e}")
        return None

def insert_initial_data(session):
    """
    Εισαγωγή αρχικών δεδομένων για δοκιμή
    """
    try:
        # Δημιουργία δοκιμαστικού χρήστη
        test_user = User(
            username="mining_admin", 
            email="admin@mining-assistant.com", 
            hashed_password="temp_password_hash",  # Σημείωση: Σε πραγματική εφαρμογή, χρησιμοποιήστε κατακερματισμό
            is_active=True
        )
        session.add(test_user)
        
        # Εισαγωγή μιας αρχικής διαμόρφωσης mining
        mining_config = MiningConfig(
            name="Default GPU Mining Config",
            user_id=1,  # Θα πάρει το ID του πρώτου χρήστη
            gpu_config={
                "gpus": [
                    {"model": "NVIDIA GeForce RTX 3060", "count": 2},
                    {"model": "NVIDIA GeForce RTX 3070", "count": 1}
                ]
            },
            coin="BTC",
            pool="NiceHash",
            wallet="your_wallet_address",
            is_active=True
        )
        session.add(mining_config)
        
        # Εισαγωγή ενός δοκιμαστικού mining stat
        mining_stat = MiningStat(
            user_id=1,
            hashrate=120.5,
            coin="BTC",
            earnings=0.0005,
            power_consumption=550,
            temperature=65.5,
            efficiency=0.8
        )
        session.add(mining_stat)
        
        # Εισαγωγή δεδομένων κατανάλωσης ενέργειας
        energy_consumption = EnergyConsumption(
            power_usage=1.2,
            cost=0.15,
            grid_consumption=1.0,
            solar_generation=0.2,
            is_predicted=False
        )
        session.add(energy_consumption)
        
        # Εισαγωγή τιμών κρυπτονομισμάτων
        crypto_price = CryptoPrice(
            coin="BTC",
            price_usd=50000,
            price_eur=42000,
            market_cap=950000000000,
            volume_24h=25000000000
        )
        session.add(crypto_price)
        
        # Commit των αλλαγών
        session.commit()
        print("Επιτυχής εισαγωγή αρχικών δεδομένων!")
    except Exception as e:
        session.rollback()
        print(f"Σφάλμα κατά την εισαγωγή δεδομένων: {e}")

def main():
    """
    Κύρια συνάρτηση για επαλήθευση και αρχικοποίηση
    """
    # Επαλήθευση σύνδεσης
    session = verify_database_connection()
    
    if session:
        # Εισαγωγή αρχικών δεδομένων
        insert_initial_data(session)
        
        # Κλείσιμο της σύνδεσης
        session.close()

if __name__ == "__main__":
    main()
