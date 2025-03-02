from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# Πρόσθετα βασικά σχήματα 

class MiningStats(BaseModel):
    """
    Συγκεντρωτικά στατιστικά mining
    """
    timestamp: datetime
    total_hashrate: float
    total_power: float
    active_gpus: int
    gpus: List[Dict]
    active_coin: str
    coins_data: Dict
    total_earnings_24h: float

class EnergyData(BaseModel):
    """
    Δεδομένα κατανάλωσης ενέργειας
    """
    timestamp: datetime
    current_consumption: float
    daily_consumption: float
    monthly_consumption: float
    cost_per_kwh: float
    daily_cost: float
    monthly_cost: float
    solar_production: Optional[Dict] = None
    grid_percentage: float
    solar_percentage: float

class ProfitabilityRequest(BaseModel):
    """
    Αίτημα υπολογισμού κερδοφορίας
    """
    gpu_models: List[str]

class ProfitabilityResponse(BaseModel):
    """
    Απόκριση υπολογισμού κερδοφορίας
    """
    mining_stats: MiningStats
    energy_data: EnergyData
    cloreai_data: Dict
    recommendation: str

# Επίσης, προσθέτουμε τυχόν άλλα σχήματα που χρησιμοποιούνται 
# συγκεκριμένα στο main.py ή απαιτούνται από τα μοντέλα

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

class MiningConfigBase(BaseModel):
    gpu_models: str
    mining_pool: str
    wallet_address: str
    max_power_consumption: float

class MiningConfig(MiningConfigBase):
    id: int
    user_id: int
    is_active: bool = True

    class Config:
        orm_mode = True

class MiningStatBase(BaseModel):
    gpu_hashrate: float
    gpu_temperature: float
    gpu_power_consumption: float
    coin: str
    revenue_per_day: float
    profitability_score: float

class MiningStat(MiningStatBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class EnergyConsumption(BaseModel):
    total_power_consumption: float
    solar_production: float
    grid_consumption: float
    electricity_cost: float
    solar_offset: float

    class Config:
        orm_mode = True

class CryptoPrice(BaseModel):
    coin_symbol: str
    price_usd: float
    market_cap: float
    volume_24h: float
    timestamp: datetime

    class Config:
        orm_mode = True
