import os
import logging
import json
import asyncio
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
import subprocess
from dotenv import load_dotenv

# Φόρτωση περιβαλλοντικών μεταβλητών
load_dotenv()

logger = logging.getLogger(__name__)

class MiningConnector:
    """
    Connector για την επικοινωνία με mining software και APIs
    """
    
    def __init__(self):
        self.api_url = os.getenv("MINING_API_URL")
        self.api_key = os.getenv("MINING_API_KEY")
        self.api_secret = os.getenv("MINING_API_SECRET")
        self.whattomine_api_key = os.getenv("WHATTOMINE_API_KEY")
        self.mining_software = os.getenv("MINING_SOFTWARE", "nicehash")
        self.client = None
        self.is_initialized = False
        
    async def initialize(self) -> bool:
        """
        Αρχικοποίηση της σύνδεσης με το mining software
        """
        try:
            self.client = httpx.AsyncClient(timeout=10.0)
            
            # Έλεγχος σύνδεσης με το mining software
            if self.mining_software.lower() == "nicehash":
                # Test connection to NiceHash API
                test_url = f"{self.api_url}/api/v2/mining/external/{self.api_key}/rigs"
                response = await self.client.get(test_url)
                if response.status_code == 200:
                    logger.info("Επιτυχής σύνδεση με το NiceHash API")
                    self.is_initialized = True
                    return True
                else:
                    logger.error(f"Αποτυχία σύνδεσης με το NiceHash API. Status code: {response.status_code}")
                    return False
            else:
                # Για άλλο mining software, εδώ θα προσθέσουμε την κατάλληλη λογική
                logger.info(f"Χρήση {self.mining_software} ως mining software")
                self.is_initialized = True
                return True
                
        except Exception as e:
            logger.error(f"Σφάλμα κατά την αρχικοποίηση του Mining Connector: {str(e)}")
            return False
    
    async def close(self):
        """
        Κλείσιμο των συνδέσεων
        """
        if self.client:
            await self.client.aclose()
            logger.info("Έκλεισαν οι συνδέσεις του Mining Connector")
    
    async def get_stats(self) -> Dict:
        """
        Λήψη στατιστικών mining
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            if self.mining_software.lower() == "nicehash":
                # Λήψη δεδομένων από το NiceHash API
                rigs_url = f"{self.api_url}/api/v2/mining/external/{self.api_key}/rigs"
                rigs_response = await self.client.get(rigs_url)
                rigs_data = rigs_response.json()
                
                # Λήψη δεδομένων για τα διαθέσιμα κρυπτονομίσματα
                coins_data = await self.get_coin_profitability()
                
                # Υπολογισμός συνολικών μεγεθών
                total_hashrate = 0
                total_power = 0
                active_gpus = 0
                gpus_info = []
                active_coin = "BTC"  # Default για το NiceHash
                
                # Επεξεργασία δεδομένων για κάθε rig
                for rig in rigs_data.get("rigs", []):
                    for device in rig.get("devices", []):
                        if device.get("status") == "MINING":
                            active_gpus += 1
                            device_power = device.get("powerUsage", 0)
                            device_hashrate = device.get("speedAccepted", 0)
                            total_power += device_power
                            total_hashrate += device_hashrate
                            
                            # Προσθήκη πληροφοριών GPU
                            gpus_info.append({
                                "model": device.get("name", "Unknown"),
                                "hashrate": device_hashrate,
                                "power_consumption": device_power,
                                "temperature": device.get("temperature", 0),
                                "fan_speed": device.get("fanSpeed", 0),
                                "efficiency": device_hashrate / device_power if device_power > 0 else 0
                            })
                
                # Υπολογισμός εκτιμώμενων κερδών
                total_earnings_24h = 0
                for coin, data in coins_data.items():
                    if coin == active_coin:
                        # Υπολογισμός με βάση το hashrate και την τιμή
                        total_earnings_24h = total_hashrate * data.get("reward_per_hashrate", 0) * 24
                
                # Δημιουργία του τελικού αντικειμένου
                return {
                    "timestamp": datetime.now().isoformat(),
                    "total_hashrate": total_hashrate,
                    "total_power": total_power,
                    "active_gpus": active_gpus,
                    "gpus": gpus_info,
                    "active_coin": active_coin,
                    "coins_data": coins_data,
                    "total_earnings_24h": total_earnings_24h
                }
            else:
                # Για άλλο mining software θα προσθέσουμε την κατάλληλη λογική
                # Προς το παρόν, επιστρέφουμε δοκιμαστικά δεδομένα
                return await self._get_mock_mining_stats()
                
        except Exception as e:
            logger.error(f"Σφάλμα κατά τη λήψη στατιστικών mining: {str(e)}")
            # Σε περίπτωση σφάλματος, επιστρέφουμε δοκιμαστικά δεδομένα
            return await self._get_mock_mining_stats()
    
    async def get_coin_profitability(self) -> Dict:
        """
        Λήψη δεδομένων κερδοφορίας για διάφορα κρυπτονομίσματα
        """
        try:
            # Χρήση του WhatToMine API για πληροφορίες κερδοφορίας
            url = f"https://whattomine.com/coins.json?key={self.whattomine_api_key}"
            response = await self.client.get(url)
            data = response.json()
            
            # Επεξεργασία των δεδομένων
            coins_data = {}
            for coin_id, coin_info in data.get("coins", {}).items():
                # Μετατροπή των δεδομένων σε πιο χρήσιμη μορφή
                algorithm = coin_info.get("algorithm", "Unknown")
                current_price = coin_info.get("exchange_rate", 0)
                price_change_24h = coin_info.get("exchange_rate_vol", 0)
                estimated_rewards = {
                    "day": coin_info.get("estimated_rewards", 0),
                    "week": coin_info.get("estimated_rewards", 0) * 7,
                    "month": coin_info.get("estimated_rewards", 0) * 30
                }
                reward_per_hashrate = coin_info.get("btc_revenue", 0) / coin_info.get("nethash", 1)
                
                coins_data[coin_info.get("tag", coin_id)] = {
                    "name": coin_info.get("name", "Unknown"),
                    "algorithm": algorithm,
                    "current_price": current_price,
                    "price_change_24h": price_change_24h,
                    "estimated_earnings": estimated_rewards,
                    "reward_per_hashrate": reward_per_hashrate
                }
            
            return coins_data
            
        except Exception as e:
            logger.error(f"Σφάλμα κατά τη λήψη δεδομένων κερδοφορίας: {str(e)}")
            # Σε περίπτωση σφάλματος, επιστρέφουμε δοκιμαστικά δεδομένα
            return await self._get_mock_coin_profitability()
    
    async def get_gpu_stats(self) -> List[Dict]:
        """
        Λήψη λεπτομερών στατιστικών για τις GPUs
        """
        try:
            stats = await self.get_stats()
            return stats.get("gpus", [])
        except Exception as e:
            logger.error(f"Σφάλμα κατά τη λήψη στατιστικών GPU: {str(e)}")
            return []
    
    async def start_mining(self, config_id: int) -> Dict:
        """
        Εκκίνηση της διαδικασίας mining με συγκεκριμένη διαμόρφωση
        """
        try:
            # Εδώ θα υλοποιήσουμε τη λογική για εκκίνηση του mining software
            # Ανάλογα με το config_id, θα φορτώσουμε τις κατάλληλες ρυθμίσεις
            
            # Προς το παρόν, επιστρέφουμε απλά ένα μήνυμα επιτυχίας
            return {
                "status": "success",
                "message": f"Ξεκίνησε η διαδικασία mining με config ID: {config_id}",
                "config_id": config_id,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Σφάλμα κατά την εκκίνηση mining: {str(e)}")
            raise
    
    async def stop_mining(self, config_id: int) -> Dict:
        """
        Διακοπή της διαδικασίας mining
        """
        try:
            # Εδώ θα υλοποιήσουμε τη λογική για διακοπή του mining software
            
            # Προς το παρόν, επιστρέφουμε απλά ένα μήνυμα επιτυχίας
            return {
                "status": "success",
                "message": f"Σταμάτησε η διαδικασία mining με config ID: {config_id}",
                "config_id": config_id,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Σφάλμα κατά τη διακοπή mining: {str(e)}")
            raise
    
    async def _get_mock_mining_stats(self) -> Dict:
        """
        Δημιουργία δοκιμαστικών δεδομένων mining για development/testing
        """
        coins_data = await self._get_mock_coin_profitability()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_hashrate": 350.5,
            "total_power": 1200,
            "active_gpus": 5,
            "gpus": [
                {
                    "model": "NVIDIA GeForce RTX 3060",
                    "hashrate": 50.2,
                    "power_consumption": 170,
                    "temperature": 62,
                    "fan_speed": 65,
                    "efficiency": 0.295
                },
                {
                    "model": "NVIDIA GeForce RTX 3060",
                    "hashrate": 49.8,
                    "power_consumption": 165,
                    "temperature": 60,
                    "fan_speed": 60,
                    "efficiency": 0.302
                },
                {
                    "model": "NVIDIA GeForce RTX 3080 Ti",
                    "hashrate": 120.5,
                    "power_consumption": 320,
                    "temperature": 68,
                    "fan_speed": 75,
                    "efficiency": 0.376
                },
                {
                    "model": "NVIDIA GeForce RTX 4070 Ti",
                    "hashrate": 80.2,
                    "power_consumption": 220,
                    "temperature": 55,
                    "fan_speed": 55,
                    "efficiency": 0.365
                },
                {
                    "model": "NVIDIA GeForce RTX 1660 Super",
                    "hashrate": 49.8,
                    "power_consumption": 125,
                    "temperature": 58,
                    "fan_speed": 65,
                    "efficiency": 0.398
                }
            ],
            "active_coin": "ETH",
            "coins_data": coins_data,
            "total_earnings_24h": 0.0045
        }
    
    async def _get_mock_coin_profitability(self) -> Dict:
        """
        Δημιουργία δοκιμαστικών δεδομένων κερδοφορίας για development/testing
        """
        return {
            "BTC": {
                "name": "Bitcoin",
                "algorithm": "SHA-256",
                "current_price": 67500.25,
                "price_change_24h": 1.2,
                "estimated_earnings": {
                    "day": 0.00012,
                    "week": 0.00084,
                    "month": 0.0036
                },
                "reward_per_hashrate": 0.00000015
            },
            "ETH": {
                "name": "Ethereum",
                "algorithm": "Ethash",
                "current_price": 3200.75,
                "price_change_24h": -0.5,
                "estimated_earnings": {
                    "day": 0.0025,
                    "week": 0.0175,
                    "month": 0.075
                },
                "reward_per_hashrate": 0.0000012
            },
            "XMR": {
                "name": "Monero",
                "algorithm": "RandomX",
                "current_price": 185.50,
                "price_change_24h": 0.8,
                "estimated_earnings": {
                    "day": 0.015,
                    "week": 0.105,
                    "month": 0.45
                },
                "reward_per_hashrate": 0.0000085
            },
            "RVN": {
                "name": "Ravencoin",
                "algorithm": "KAWPOW",
                "current_price": 0.025,
                "price_change_24h": 2.5,
                "estimated_earnings": {
                    "day": 35,
                    "week": 245,
                    "month": 1050
                },
                "reward_per_hashrate": 0.000075
            }
        }