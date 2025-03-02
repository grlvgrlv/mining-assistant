import os
import logging
import json
import asyncio
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

# Φόρτωση περιβαλλοντικών μεταβλητών
load_dotenv()

logger = logging.getLogger(__name__)

class CloreAIConnector:
    """
    Connector για την επικοινωνία με το CloreAI API για ενοικίαση GPU
    """
    
    def __init__(self):
        self.api_url = os.getenv("CLOREAI_API_URL", "https://api.cloreai.com")
        self.api_key = os.getenv("CLOREAI_API_KEY")
        self.client = None
        self.is_initialized = False
        self.use_mock = os.getenv("USE_MOCK_CLOREAI_DATA", "False").lower() == "true" or not self.api_key
        
    async def initialize(self) -> bool:
        """
        Αρχικοποίηση της σύνδεσης με το CloreAI API
        """
        try:
            self.client = httpx.AsyncClient(timeout=10.0)
            
            # Αν χρησιμοποιούμε δοκιμαστικά δεδομένα, δεν χρειάζεται να ελέγξουμε τη σύνδεση
            if self.use_mock:
                logger.info("Χρήση δοκιμαστικών δεδομένων για το CloreAI")
                self.is_initialized = True
                return True
            
            # Έλεγχος σύνδεσης με το CloreAI API
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            response = await self.client.get(f"{self.api_url}/api/v1/status", headers=headers)
            
            if response.status_code == 200:
                logger.info("Επιτυχής σύνδεση με το CloreAI API")
                self.is_initialized = True
                return True
            else:
                logger.error(f"Αποτυχία σύνδεσης με το CloreAI API. Status code: {response.status_code}")
                self.use_mock = True
                self.is_initialized = True
                return False
                
        except Exception as e:
            logger.error(f"Σφάλμα κατά την αρχικοποίηση του CloreAI Connector: {str(e)}")
            # Θα συνεχίσουμε με δοκιμαστικά δεδομένα
            self.use_mock = True
            self.is_initialized = True
            return False
    
    async def close(self):
        """
        Κλείσιμο των συνδέσεων
        """
        if self.client:
            await self.client.aclose()
            logger.info("Έκλεισαν οι συνδέσεις του CloreAI Connector")
    
    async def get_gpu_availability(self) -> List[Dict]:
        """
        Λήψη διαθεσιμότητας GPU από το CloreAI
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            if self.use_mock:
                return await self._get_mock_gpu_availability()
            
            # Κλήση στο API για διαθεσιμότητα GPU
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            response = await self.client.get(f"{self.api_url}/api/v1/gpus/available", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Σφάλμα κατά τη λήψη διαθεσιμότητας GPU. Status code: {response.status_code}")
                return await self._get_mock_gpu_availability()
                
        except Exception as e:
            logger.error(f"Σφάλμα κατά τη λήψη διαθεσιμότητας GPU: {str(e)}")
            # Σε περίπτωση σφάλματος, επιστρέφουμε δοκιμαστικά δεδομένα
            return await self._get_mock_gpu_availability()
    
    async def get_gpu_pricing(self) -> List[Dict]:
        """
        Λήψη τιμών ενοικίασης GPU από το CloreAI
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            if self.use_mock:
                return await self._get_mock_gpu_pricing()
            
            # Κλήση στο API για τιμές GPU
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            response = await self.client.get(f"{self.api_url}/api/v1/gpus/pricing", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Σφάλμα κατά τη λήψη τιμών GPU. Status code: {response.status_code}")
                return await self._get_mock_gpu_pricing()
                
        except Exception as e:
            logger.error(f"Σφάλμα κατά τη λήψη τιμών GPU: {str(e)}")
            # Σε περίπτωση σφάλματος, επιστρέφουμε δοκιμαστικά δεδομένα
            return await self._get_mock_gpu_pricing()
    
    async def get_profitability(self, gpu_models: List[str]) -> Dict:
        """
        Λήψη δεδομένων κερδοφορίας για συγκεκριμένα μοντέλα GPU
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            if self.use_mock:
                return await self._get_mock_profitability(gpu_models)
            
            # Κλήση στο API για δεδομένα κερδοφορίας
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            data = {"gpu_models": gpu_models}
            response = await self.client.post(
                f"{self.api_url}/api/v1/profitability",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Σφάλμα κατά τη λήψη δεδομένων κερδοφορίας. Status code: {response.status_code}")
                return await self._get_mock_profitability(gpu_models)
                
        except Exception as e:
            logger.error(f"Σφάλμα κατά τη λήψη δεδομένων κερδοφορίας: {str(e)}")
            # Σε περίπτωση σφάλματος, επιστρέφουμε δοκιμαστικά δεδομένα
            return await self._get_mock_profitability(gpu_models)
    
    async def rent_gpu(self, gpu_model: str, duration_hours: int) -> Dict:
        """
        Ενοικίαση GPU από το CloreAI
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            if self.use_mock:
                return await self._get_mock_rental_response(gpu_model, duration_hours)
            
            # Κλήση στο API για ενοικίαση GPU
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            data = {
                "gpu_model": gpu_model,
                "duration_hours": duration_hours
            }
            response = await self.client.post(
                f"{self.api_url}/api/v1/gpus/rent",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Σφάλμα κατά την ενοικίαση GPU. Status code: {response.status_code}")
                return {
                    "status": "error",
                    "message": f"Αποτυχία ενοικίασης GPU. Status code: {response.status_code}",
                    "error": response.text
                }
                
        except Exception as e:
            logger.error(f"Σφάλμα κατά την ενοικίαση GPU: {str(e)}")
            return {
                "status": "error",
                "message": f"Σφάλμα κατά την ενοικίαση GPU: {str(e)}"
            }
    
    async def cancel_rental(self, rental_id: str) -> Dict:
        """
        Ακύρωση ενοικίασης GPU
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            if self.use_mock:
                return {
                    "status": "success",
                    "message": f"Η ενοικίαση {rental_id} ακυρώθηκε επιτυχώς"
                }
            
            # Κλήση στο API για ακύρωση ενοικίασης
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            response = await self.client.delete(
                f"{self.api_url}/api/v1/gpus/rentals/{rental_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Σφάλμα κατά την ακύρωση ενοικίασης. Status code: {response.status_code}")
                return {
                    "status": "error",
                    "message": f"Αποτυχία ακύρωσης ενοικίασης. Status code: {response.status_code}",
                    "error": response.text
                }
                
        except Exception as e:
            logger.error(f"Σφάλμα κατά την ακύρωση ενοικίασης: {str(e)}")
            return {
                "status": "error",
                "message": f"Σφάλμα κατά την ακύρωση ενοικίασης: {str(e)}"
            }
    
    async def _get_mock_gpu_availability(self) -> List[Dict]:
        """
        Δημιουργία δοκιμαστικών δεδομένων διαθεσιμότητας GPU για development/testing
        """
        return [
            {
                "gpu_model": "NVIDIA GeForce RTX 3060",
                "available": 15,
                "total": 50,
                "last_updated": datetime.now().isoformat()
            },
            {
                "gpu_model": "NVIDIA GeForce RTX 3070",
                "available": 8,
                "total": 30,
                "last_updated": datetime.now().isoformat()
            },
            {
                "gpu_model": "NVIDIA GeForce RTX 3080",
                "available": 5,
                "total": 25,
                "last_updated": datetime.now().isoformat()
            },
            {
                "gpu_model": "NVIDIA GeForce RTX 3090",
                "available": 3,
                "total": 20,
                "last_updated": datetime.now().isoformat()
            },
            {
                "gpu_model": "NVIDIA GeForce RTX 4070",
                "available": 10,
                "total": 30,
                "last_updated": datetime.now().isoformat()
            },
            {
                "gpu_model": "NVIDIA GeForce RTX 4080",
                "available": 6,
                "total": 20,
                "last_updated": datetime.now().isoformat()
            },
            {
                "gpu_model": "NVIDIA GeForce RTX 4090",
                "available": 2,
                "total": 15,
                "last_updated": datetime.now().isoformat()
            }
        ]
    
    async def _get_mock_gpu_pricing(self) -> List[Dict]:
        """
        Δημιουργία δοκιμαστικών δεδομένων τιμών GPU για development/testing
        """
        return [
            {
                "gpu_model": "NVIDIA GeForce RTX 3060",
                "price_per_hour": 0.25,
                "price_per_day": 5.50,
                "price_per_week": 35.00,
                "minimum_hours": 1,
                "performance_rating": 8.5
            },
            {
                "gpu_model": "NVIDIA GeForce RTX 3070",
                "price_per_hour": 0.35,
                "price_per_day": 7.50,
                "price_per_week": 48.00,
                "minimum_hours": 1,
                "performance_rating": 9.2
            },
            {
                "gpu_model": "NVIDIA GeForce RTX 3080",
                "price_per_hour": 0.50,
                "price_per_day": 10.50,
                "price_per_week": 68.00,
                "minimum_hours": 1,
                "performance_rating": 9.7
            },
            {
                "gpu_model": "NVIDIA GeForce RTX 3090",
                "price_per_hour": 0.70,
                "price_per_day": 15.00,
                "price_per_week": 95.00,
                "minimum_hours": 2,
                "performance_rating": 10.0
            },
            {
                "gpu_model": "NVIDIA GeForce RTX 4070",
                "price_per_hour": 0.45,
                "price_per_day": 9.50,
                "price_per_week": 60.00,
                "minimum_hours": 1,
                "performance_rating": 9.5
            },
            {
                "gpu_model": "NVIDIA GeForce RTX 4080",
                "price_per_hour": 0.65,
                "price_per_day": 14.00,
                "price_per_week": 88.00,
                "minimum_hours": 2,
                "performance_rating": 9.9
            },
            {
                "gpu_model": "NVIDIA GeForce RTX 4090",
                "price_per_hour": 0.90,
                "price_per_day": 19.00,
                "price_per_week": 120.00,
                "minimum_hours": 3,
                "performance_rating": 10.0
            }
        ]
    
    async def _get_mock_profitability(self, gpu_models: List[str]) -> Dict:
        """
        Δημιουργία δοκιμαστικών δεδομένων κερδοφορίας για development/testing
        """
        # Δοκιμαστικά δεδομένα των διαθέσιμων GPU για ενοικίαση
        rental_gpus = [
            {
                "gpu_model": "NVIDIA GeForce RTX 3060",
                "price_per_hour": 0.25,
                "price_per_day": 5.50,
                "availability": 15,
                "performance_index": 8.5
            },
            {
                "gpu_model": "NVIDIA GeForce RTX 3070",
                "price_per_hour": 0.35,
                "price_per_day": 7.50,
                "availability": 8,
                "performance_index": 9.2
            },
            {
                "gpu_model": "NVIDIA GeForce RTX 3080",
                "price_per_hour": 0.50,
                "price_per_day": 10.50,
                "availability": 5,
                "performance_index": 9.7
            },
            {
                "gpu_model": "NVIDIA GeForce RTX 4070",
                "price_per_hour": 0.45,
                "price_per_day": 9.50,
                "availability": 10,
                "performance_index": 9.5
            }
        ]
        
        # Φιλτράρισμα με βάση τα μοντέλα που ζητήθηκαν
        if gpu_models:
            rental_gpus = [gpu for gpu in rental_gpus if gpu["gpu_model"] in gpu_models]
        
        # Δοκιμαστικά δεδομένα τάσεων αγοράς
        market_trends = {
            "ETH": {
                "price_change_24h": 2.5,
                "profitability_change_24h": 1.8,
                "forecast_7d": "slightly_increasing"
            },
            "BTC": {
                "price_change_24h": 1.2,
                "profitability_change_24h": 0.5,
                "forecast_7d": "stable"
            },
            "RVN": {
                "price_change_24h": 5.7,
                "profitability_change_24h": 4.2,
                "forecast_7d": "increasing"
            }
        }
        
        # Προσδιορισμός συστάσεων με βάση τα δεδομένα
        recommendation = "Η ενοικίαση NVIDIA GeForce RTX 3060 είναι η πιο συμφέρουσα επιλογή για εξόρυξη RVN με βάση την τρέχουσα τιμή και τις τάσεις της αγοράς."
        
        return {
            "rentals": rental_gpus,
            "market_trends": market_trends,
            "recommendation": recommendation
        }
    
    async def _get_mock_rental_response(self, gpu_model: str, duration_hours: int) -> Dict:
        """
        Δημιουργία δοκιμαστικής απάντησης για ενοικίαση GPU
        """
        import uuid
        rental_id = str(uuid.uuid4())
        
        # Εύρεση της τιμής του μοντέλου GPU
        pricing = await self._get_mock_gpu_pricing()
        price_per_hour = 0.5  # Προεπιλογή
        
        for gpu in pricing:
            if gpu["gpu_model"] == gpu_model:
                price_per_hour = gpu["price_per_hour"]
                break
        
        total_cost = price_per_hour * duration_hours
        
        return {
            "status": "success",
            "rental_id": rental_id,
            "gpu_model": gpu_model,
            "duration_hours": duration_hours,
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() + datetime.timedelta(hours=duration_hours)).isoformat(),
            "price_per_hour": price_per_hour,
            "total_cost": total_cost,
            "connection_info": {
                "ip": "198.51.100.123",
                "port": 22,
                "username": "cloreai_user",
                "password": "demo_password_12345"
            }
        }
