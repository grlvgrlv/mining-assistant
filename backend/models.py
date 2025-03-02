from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    mining_configs = relationship("MiningConfig", back_populates="owner")
    mining_stats = relationship("MiningStat", back_populates="user")


class MiningConfig(Base):
    __tablename__ = "mining_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    gpu_config = Column(JSON)  # Αποθήκευση της διαμόρφωσης των GPU
    coin = Column(String)
    pool = Column(String)
    wallet = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner = relationship("User", back_populates="mining_configs")
    

class MiningStat(Base):
    __tablename__ = "mining_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    hashrate = Column(Float)
    coin = Column(String)
    earnings = Column(Float)
    power_consumption = Column(Float)
    temperature = Column(Float)
    efficiency = Column(Float)
    
    user = relationship("User", back_populates="mining_stats")


class EnergyConsumption(Base):
    __tablename__ = "energy_consumption"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    power_usage = Column(Float)  # kWh
    cost = Column(Float)  # EUR
    solar_generation = Column(Float, nullable=True)  # kWh from solar panels
    grid_consumption = Column(Float)  # kWh from grid
    is_predicted = Column(Boolean, default=False)  # Whether this is a prediction or actual measurement


class CryptoPrice(Base):
    __tablename__ = "crypto_prices"

    id = Column(Integer, primary_key=True, index=True)
    coin = Column(String, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    price_usd = Column(Float)
    price_eur = Column(Float)
    market_cap = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
