from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


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
    name: str
    gpu_config: Dict
    coin: str
    pool: str
    wallet: str


class MiningConfigCreate(MiningConfigBase):
    pass


class MiningConfig(MiningConfigBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class MiningStatBase(BaseModel):
    hashrate: float
    coin: str
    earnings: float
    power_consumption: float
    temperature: float
    efficiency: float


class MiningStatCreate(MiningStatBase):
    user_id: int


class MiningStat(MiningStatBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        orm_mode = True


class EnergyConsumptionBase(BaseModel):
    power_usage: float
    cost: float
    grid_consumption: float
    solar_generation: Optional[float] = None
    is_predicted: bool = False


class EnergyConsumptionCreate(EnergyConsumptionBase):
    pass


class EnergyConsumption(EnergyConsumptionBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True


class CryptoPriceBase(BaseModel):
    coin: str
    price_usd: float
    price_eur: float
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None


class CryptoPriceCreate(CryptoPriceBase):
    pass


class CryptoPrice(CryptoPriceBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True
