import logging
import os
from typing import Dict, List, Optional
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Εσωτερικά modules
from . import models, schemas
from .database import engine, get_db
from .connectors.mining_connector import MiningConnector
from .connectors.energy_connector import EnergyConnector
from .connectors.cloreai_connector import CloreAIConnector
from .ai_engine import AIEngine

# Φόρτωση περιβαλλοντικών μεταβλητών
load_dotenv()

# Ρύθμιση logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Δημιουργία των πινάκων της βάσης δεδομένων
models.Base.metadata.create_all(bind=engine)

# Αρχικοποίηση του FastAPI app
app = FastAPI(
    title="AI Mining Assistant API",
    description="API για το AI Mining Assistant chatbot",
    version="0.1.0"
)

# Προσθήκη CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Για development, στο production θα περιοριστεί
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Αρχικοποίηση των connectors και του AI engine
mining_connector = MiningConnector()
energy_connector = EnergyConnector()
cloreai_connector = CloreAIConnector()
ai_engine = AIEngine()

# Βασικά endpoints

@app.get("/")
def read_root():
    return {"message": "Καλωσήρθατε στο AI Mining Assistant API"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "0.1.0",
    }

# Endpoints για mining

@app.get("/mining/stats", response_model=Dict)
async def get_mining_stats(user_id: Optional[int] = None):
    """
    Λήψη στατιστικών εξόρυξης.
    """
    return await mining_connector.get_mining_stats(user_id)

@app.get("/mining/profitability", response_model=List[Dict])
async def get_coin_profitability():
    """
    Λήψη κερδοφορίας κρυπτονομισμάτων.
    """
    return await mining_connector.get_coin_profitability()

@app.post("/mining/start", response_model=Dict)
async def start_mining(config_id: int):
    """
    Εκκίνηση διαδικασίας εξόρυξης.
    """
    return await mining_connector.start_mining(config_id)

@app.post("/mining/stop", response_model=Dict)
async def stop_mining(config_id: int):
    """
    Διακοπή διαδικασίας εξόρυξης.
    """
    return await mining_connector.stop_mining(config_id)

@app.get("/gpus/stats", response_model=List[Dict])
async def get_gpu_stats():
    """
    Λήψη στατιστικών GPU.
    """
    return await mining_connector.get_gpu_stats()

# Endpoints για ενέργεια

@app.get("/energy/consumption", response_model=Dict)
async def get_current_consumption():
    """
    Λήψη τρέχουσας κατανάλωσης ενέργειας.
    """
    return await energy_connector.get_current_consumption()

@app.get("/energy/solar", response_model=Dict)
async def get_solar_production():
    """
    Λήψη παραγωγής από φωτοβολταϊκά.
    """
    return await energy_connector.get_solar_production()

# Endpoints για CloreAI

@app.get("/cloreai/gpus", response_model=List[Dict])
async def get_gpu_availability():
    """
    Λήψη διαθεσιμότητας GPU από το CloreAI.
    """
    return await cloreai_connector.get_gpu_availability()

@app.get("/cloreai/pricing", response_model=List[Dict])
async def get_gpu_pricing():
    """
    Λήψη τιμών ενοικίασης GPU από το CloreAI.
    """
    return await cloreai_connector.get_gpu_pricing()

# Endpoints για AI ανάλυση

@app.post("/ai/chat", response_model=Dict)
async def chat_with_ai(message: str = Query(..., description="Μήνυμα προς το AI")):
    """
    Συνομιλία με το AI chatbot.
    """
    response = await ai_engine.generate_response(message)
    return {"response": response}

@app.post("/ai/analyze", response_model=Dict)
async def analyze_mining(data: Dict):
    """
    Ανάλυση δεδομένων εξόρυξης.
    """
    analysis = await ai_engine.analyze_mining_data(data)
    return analysis

@app.post("/ai/optimize", response_model=Dict)
async def optimize_mining_strategy(
    user_config: Dict,
    market_data: Dict,
    energy_data: Dict
):
    """
    Βελτιστοποίηση στρατηγικής εξόρυξης.
    """
    optimization = await ai_engine.optimize_mining_strategy(user_config, market_data, energy_data)
    return optimization

# Endpoints για διαχείριση χρηστών

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Δημιουργία νέου χρήστη.
    """
    # Έλεγχος αν υπάρχει ήδη χρήστης με το ίδιο email
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Δημιουργία και αποθήκευση νέου χρήστη
    # Σε πραγματική εφαρμογή θα κάναμε hash το password
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=user.password  # Προσοχή: Αυτό θα έπρεπε να είναι hashed!
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Ανάκτηση δεδομένων χρήστη.
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Εκκίνηση του server
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run("main:app", host=host, port=port, reload=debug)
