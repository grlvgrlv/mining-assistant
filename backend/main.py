import logging
import os
import time
from typing import Dict, List, Optional
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Εσωτερικά modules
from backend.models import Base
from backend.database import engine, get_db, init_db
from backend.schemas import (
    MiningStats, EnergyData, ProfitabilityRequest, ProfitabilityResponse,
    UserCreate, User, MiningConfig, MiningStat, EnergyConsumption, CryptoPrice
)
from backend.connectors.mining_connector import MiningConnector
from backend.connectors.energy_connector import EnergyConnector
from backend.connectors.cloreai_connector import CloreAIConnector
from backend.ai_engine import AIEngine

# Απενεργοποίηση προειδοποιήσεων TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0=all, 1=no INFO, 2=no WARNING, 3=no ERROR

# Φόρτωση περιβαλλοντικών μεταβλητών
load_dotenv()

# Ρύθμιση φακέλου logs αν δεν υπάρχει
os.makedirs("logs", exist_ok=True)

# Ρύθμιση logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mining-assistant")

# Δημιουργία του FastAPI app
app = FastAPI(
    title="AI Mining Assistant API",
    description="Backend API για το AI Mining Assistant",
    version="0.1.0"
)

# Προσθήκη CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Σε παραγωγή, περιορίστε το στο domain του frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware για response time logging και χειρισμό σφαλμάτων
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"Request to {request.url.path} completed in {process_time:.4f}s")
        return response
    except Exception as e:
        logger.error(f"Error processing request to {request.url.path}: {str(e)}")
        process_time = time.time() - start_time
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Εσωτερικό σφάλμα εξυπηρετητή"},
        )

# Αρχικοποίηση των connectors και του AI engine
mining_connector = MiningConnector()
energy_connector = EnergyConnector()
cloreai_connector = CloreAIConnector()
ai_engine = AIEngine()

# Εκτέλεση στην εκκίνηση της εφαρμογής
@app.on_event("startup")
async def startup_event():
    logger.info("Εκκίνηση του AI Mining Assistant API")
    init_db()
    logger.info("Βάση δεδομένων αρχικοποιήθηκε")
    # Αρχικοποίηση σύνδεσης με εξωτερικά APIs
    try:
        await mining_connector.initialize()
        await energy_connector.initialize()
        await cloreai_connector.initialize()
        # Φόρτωση του AI μοντέλου στο παρασκήνιο
        await ai_engine.load_model()
        logger.info("Connectors και AI Engine αρχικοποιήθηκαν επιτυχώς")
    except Exception as e:
        logger.error(f"Αποτυχία αρχικοποίησης υπηρεσιών: {str(e)}")

# Τερματισμός της εφαρμογής
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Τερματισμός του AI Mining Assistant API")
    # Κλείσιμο συνδέσεων
    await mining_connector.close()
    await energy_connector.close()
    await cloreai_connector.close()

# ---------- ΒΑΣΙΚΑ ENDPOINTS ---------- #

@app.get("/")
def read_root():
    return {"message": "Καλωσήρθατε στο AI Mining Assistant API"}

@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "version": app.version,
        "services": {
            "mining_connector": mining_connector.is_initialized,
            "energy_connector": energy_connector.is_initialized,
            "cloreai_connector": cloreai_connector.is_initialized,
            "ai_engine": ai_engine.model is not None
        }
    }

# ---------- MINING ENDPOINTS ---------- #

@app.get("/api/mining/stats", response_model=MiningStats)
async def get_mining_stats(db: Session = Depends(get_db)):
    try:
        stats = await mining_connector.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Σφάλμα κατά τη λήψη στατιστικών mining: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mining/profitability", response_model=List[Dict])
async def get_coin_profitability(db: Session = Depends(get_db)):
    """
    Λήψη κερδοφορίας κρυπτονομισμάτων.
    """
    try:
        profitability = await mining_connector.get_coin_profitability()
        return profitability
    except Exception as e:
        logger.error(f"Σφάλμα κατά τη λήψη κερδοφορίας: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mining/start", response_model=Dict)
async def start_mining(config_id: int, db: Session = Depends(get_db)):
    """
    Εκκίνηση διαδικασίας εξόρυξης.
    """
    try:
        result = await mining_connector.start_mining(config_id)
        return result
    except Exception as e:
        logger.error(f"Σφάλμα κατά την εκκίνηση mining: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mining/stop", response_model=Dict)
async def stop_mining(config_id: int, db: Session = Depends(get_db)):
    """
    Διακοπή διαδικασίας εξόρυξης.
    """
    try:
        result = await mining_connector.stop_mining(config_id)
        return result
    except Exception as e:
        logger.error(f"Σφάλμα κατά τη διακοπή mining: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/gpus/stats", response_model=List[Dict])
async def get_gpu_stats():
    """
    Λήψη στατιστικών GPU.
    """
    try:
        stats = await mining_connector.get_gpu_stats()
        return stats
    except Exception as e:
        logger.error(f"Σφάλμα κατά τη λήψη στατιστικών GPU: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- ENERGY ENDPOINTS ---------- #

@app.get("/api/energy/stats", response_model=EnergyData)
async def get_energy_stats(db: Session = Depends(get_db)):
    try:
        energy_data = await energy_connector.get_energy_data()
        return energy_data
    except Exception as e:
        logger.error(f"Σφάλμα κατά τη λήψη ενεργειακών δεδομένων: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/energy/solar", response_model=Dict)
async def get_solar_production():
    """
    Λήψη παραγωγής από φωτοβολταϊκά.
    """
    try:
        solar_data = await energy_connector.get_solar_production()
        return solar_data
    except Exception as e:
        logger.error(f"Σφάλμα κατά τη λήψη δεδομένων φωτοβολταϊκών: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- CLOREAI ENDPOINTS ---------- #

@app.get("/api/cloreai/gpus", response_model=List[Dict])
async def get_gpu_availability():
    """
    Λήψη διαθεσιμότητας GPU από το CloreAI.
    """
    try:
        availability = await cloreai_connector.get_gpu_availability()
        return availability
    except Exception as e:
        logger.error(f"Σφάλμα κατά τη λήψη διαθεσιμότητας GPU από CloreAI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cloreai/pricing", response_model=List[Dict])
async def get_gpu_pricing():
    """
    Λήψη τιμών ενοικίασης GPU από το CloreAI.
    """
    try:
        pricing = await cloreai_connector.get_gpu_pricing()
        return pricing
    except Exception as e:
        logger.error(f"Σφάλμα κατά τη λήψη τιμών ενοικίασης GPU από CloreAI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- PROFITABILITY ENDPOINTS ---------- #

@app.post("/api/profitability", response_model=ProfitabilityResponse)
async def calculate_profitability(request: ProfitabilityRequest, db: Session = Depends(get_db)):
    try:
        # Συνδυάζουμε δεδομένα από mining, ενέργεια και CloreAI
        mining_stats = await mining_connector.get_stats()
        energy_data = await energy_connector.get_energy_data()
        cloreai_data = await cloreai_connector.get_profitability(request.gpu_models)
        
        # Χρησιμοποιούμε το AI για πιο προηγμένη ανάλυση
        user_config = {"gpus": request.gpu_models}
        market_data = {"profitability": mining_stats.coins_data}
        
        # Βελτιστοποίηση στρατηγικής με AI
        optimization = await ai_engine.optimize_mining_strategy(
            user_config, market_data, energy_data.dict()
        )
        
        return {
            "mining_stats": mining_stats,
            "energy_data": energy_data,
            "cloreai_data": cloreai_data,
            "recommendation": optimization["suggestions"].get("recommended_coin", "")
        }
    except Exception as e:
        logger.error(f"Σφάλμα κατά τον υπολογισμό κερδοφορίας: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- AI ENDPOINTS ---------- #

@app.post("/api/ai/chat", response_model=Dict)
async def chat_with_ai(message: str = Query(..., description="Μήνυμα προς το AI")):
    """
    Συνομιλία με το AI chatbot.
    """
    try:
        response = await ai_engine.generate_response(message)
        return {"response": response}
    except Exception as e:
        logger.error(f"Σφάλμα κατά τη συνομιλία με το AI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/analyze", response_model=Dict)
async def analyze_mining(data: Dict):
    """
    Ανάλυση δεδομένων εξόρυξης.
    """
    try:
        analysis = await ai_engine.analyze_mining_data(data)
        return analysis
    except Exception as e:
        logger.error(f"Σφάλμα κατά την ανάλυση δεδομένων mining: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/optimize", response_model=Dict)
async def optimize_mining_strategy(
    user_config: Dict,
    market_data: Dict,
    energy_data: Dict
):
    """
    Βελτιστοποίηση στρατηγικής εξόρυξης.
    """
    try:
        optimization = await ai_engine.optimize_mining_strategy(user_config, market_data, energy_data)
        return optimization
    except Exception as e:
        logger.error(f"Σφάλμα κατά τη βελτιστοποίηση στρατηγικής: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- USER ENDPOINTS ---------- #

@app.post("/api/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Δημιουργία νέου χρήστη.
    """
    # Έλεγχος αν υπάρχει ήδη χρήστης με το ίδιο email ή username
    from backend.models import User as UserModel
    db_user = db.query(UserModel).filter(
        (UserModel.email == user.email) | (UserModel.username == user.username)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email ή username ήδη εγγεγραμμένα")
    
    # Δημιουργία και αποθήκευση νέου χρήστη
    # TODO: Να προστεθεί κρυπτογράφηση του password
    db_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=user.password  # Προσοχή: Αυτό θα έπρεπε να είναι hashed!
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Ανάκτηση δεδομένων χρήστη.
    """
    from backend.models import User as UserModel
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Εκτέλεση εφαρμογής αν το αρχείο εκτελείται απευθείας
if __name__ == "__main__":
    import uvicorn
    
    # Φόρτωση παραμέτρων από περιβαλλοντικές μεταβλητές
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    # Εκκίνηση του Uvicorn server
    uvicorn.run("backend.main:app", host=host, port=port, reload=debug)
