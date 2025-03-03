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

class EnergyConnector:
    """
    Connector για την επικοινωνία με συστήματα μέτρησης ενέργειας και φωτοβολταϊκά
    """
    
    def __init__(self):
        self.energy_meter_url = os.getenv("ENERGY_METER_URL")
        self.energy_meter_token = os.getenv("ENERGY_METER_TOKEN")
        self.solar_api_url = os.getenv("SOLAR_API_URL")
        self.solar_api_token = os.getenv("SOLAR_API_TOKEN")
        self.energy_cost_per_kwh = float(os.getenv("ENERGY_COST_PER_KWH", 0.08))
        self.client = None
        self.is_initialized = False
        self.use_mock = os.getenv("USE_MOCK_ENERGY_DATA", "False").lower() == "true"
        
    async def initialize(self) -> bool:
        """
        Αρχικοποίηση της σύνδεσης με τα συστήματα μέτρησης ενέργειας
        """
        try:
            self.client = httpx.AsyncClient(timeout=10.0)
            
            # Αν χρησιμοποιούμε δοκιμαστικά δεδομένα, δεν χρειάζεται να ελέγξουμε τη σύνδεση
            if self.use_mock:
                logger.info("Χρήση δοκιμαστικών δεδομένων ενέργειας")
                self.is_initialized = True
                return True
            
            # Έλεγχος σύνδεσης με το σύστημα μέτρησης ενέργειας
            if self.energy_meter_url:
                headers = {"Authorization": f"Bearer {self.energy_meter_token}"} if self.energy_meter_token else {}
                response = await self.client.get(f"{self.energy_meter_url}/status", headers=headers)
                if response.status_code == 200:
                    logger.info("Επιτυχής σύνδεση με το σύστημα μέτρησης ενέργειας")
                else:
                    logger.warning(f"Αποτυχία σύνδεσης με το σύστημα μέτρησης ενέργειας. Status code: {response.status_code}")
            
            # Έλεγχος σύνδεσης με το API των φωτοβολταϊκών
            if self.solar_api_url:
                headers = {"Authorization": f"Bearer {self.solar_api_token}"} if self.solar_api_token else {}
                response = await self.client.get(f"{self.solar_api_url}/status", headers=headers)
                if response.status_code == 200:
                    logger.info("Επιτυχής σύνδεση με το API των φωτοβολταϊκών")
                else:
                    logger.warning(f"Αποτυχία σύνδεσης με το API των φωτοβολταϊκών. Status code: {response.status_code}")
            
            self.is_initialized = True
            return True
                
        except Exception as e:
            logger.error(f"Σφάλμα κατά την αρχικοποίηση του Energy Connector: {str(e)}")
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
            logger.info("Έκλεισαν οι συνδέσεις του Energy Connector")
    
    async def get_energy_data(self) -> Dict:
        """
        Λήψη ενεργειακών δεδομένων
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            if self.use_mock:
                return await self._get_mock_energy_data()
            
            # Λήψη δεδομένων κατανάλωσης ενέργειας
            energy_data = {}
            if self.energy_meter_url:
                headers = {"Authorization": f"Bearer {self.energy_meter_token}"} if self.energy_meter_token else {}
                response = await self.client.get(f"{self.energy_meter_url}/consumption", headers=headers)
                if response.status_code == 200:
                    energy_data = response.json()
            
            # Λήψη δεδομένων από φωτοβολταϊκά
            solar_data = None
            if self.solar_api_url:
                headers = {"Authorization": f"Bearer {self.solar_api_token}"} if self.solar_api_token else {}
                response = await self.client.get(f"{self.solar_api_url}/production", headers=headers)
                if response.status_code == 200:
                    solar_data = response.json()
            
            # Συνδυασμός των δεδομένων
            current_consumption = energy_data.get("current", 0)
            daily_consumption = energy_data.get("daily", 0)
            monthly_consumption = energy_data.get("monthly", 0)
            
            # Υπολογισμός ποσοστών και κόστους
            solar_production = None
            grid_percentage = 100
            solar_percentage = 0
            
            if solar_data:
                solar_production = {
                    "current_output": solar_data.get("current", 0),
                    "daily_production": solar_data.get("daily", 0),
                    "monthly_production": solar_data.get("monthly", 0),
                    "energy_saved": solar_data.get("monthly", 0) * self.energy_cost_per_kwh
                }
                
                # Υπολογισμός ποσοστών
                if daily_consumption > 0:
                    solar_percentage = min(100, (solar_data.get("daily", 0) / daily_consumption) * 100)
                    grid_percentage = 100 - solar_percentage
            
            # Υπολογισμός κόστους
            daily_cost = daily_consumption * self.energy_cost_per_kwh
            monthly_cost = monthly_consumption * self.energy_cost_per_kwh
            
            return {
                "timestamp": datetime.now().isoformat(),
                "current_consumption": current_consumption,
                "daily_consumption": daily_consumption,
                "monthly_consumption": monthly_consumption,
                "cost_per_kwh": self.energy_cost_per_kwh,
                "daily_cost": daily_cost,
                "monthly_cost": monthly_cost,
                "solar_production": solar_production,
                "grid_percentage": grid_percentage,
                "solar_percentage": solar_percentage
            }
                
        except Exception as e:
            logger.error(f"Σφάλμα κατά τη λήψη ενεργειακών δεδομένων: {str(e)}")
            # Σε περίπτωση σφάλματος, επιστρέφουμε δοκιμαστικά δεδομένα
            return await self._get_mock_energy_data()
    
    async def get_solar_production(self) -> Dict:
        """
        Λήψη δεδομένων παραγωγής από φωτοβολταϊκά
        """
        try:
            energy_data = await self.get_energy_data()
            return energy_data.get("solar_production", {})
        except Exception as e:
            logger.error(f"Σφάλμα κατά τη λήψη δεδομένων φωτοβολταϊκών: {str(e)}")
            return {}
    
    async def get_energy_forecast(self, days: int = 7) -> List[Dict]:
        """
        Πρόβλεψη κατανάλωσης και παραγωγής ενέργειας για τις επόμενες ημέρες
        """
        try:
            if self.use_mock:
                return await self._get_mock_energy_forecast(days)
            
            # Εδώ θα υλοποιήσουμε τη λογική για πρόβλεψη ενέργειας
            # Μπορεί να χρησιμοποιηθεί εξωτερικό API ή μοντέλο
            
            # Προς το παρόν, επιστρέφουμε δοκιμαστικά δεδομένα
            return await self._get_mock_energy_forecast(days)
        except Exception as e:
            logger.error(f"Σφάλμα κατά την πρόβλεψη ενέργειας: {str(e)}")
            return []
    
    async def _get_mock_energy_data(self) -> Dict:
        """
        Δημιουργία δοκιμαστικών ενεργειακών δεδομένων για development/testing
        """
        # Υπολογισμός δοκιμαστικών τιμών
        current_consumption = 1.5  # kW
        daily_consumption = 35.0  # kWh
        monthly_consumption = 950.0  # kWh
        
        # Δοκιμαστικά δεδομένα φωτοβολταϊκών
        solar_current = 0.8  # kW
        solar_daily = 15.0  # kWh
        solar_monthly = 420.0  # kWh
        
        # Υπολογισμός ποσοστών
        solar_percentage = (solar_daily / daily_consumption) * 100 if daily_consumption > 0 else 0
        grid_percentage = 100 - solar_percentage
        
        # Υπολογισμός κόστους
        daily_cost = (daily_consumption - solar_daily) * self.energy_cost_per_kwh
        monthly_cost = (monthly_consumption - solar_monthly) * self.energy_cost_per_kwh
        
        return {
            "timestamp": datetime.now().isoformat(),
            "current_consumption": current_consumption,
            "daily_consumption": daily_consumption,
            "monthly_consumption": monthly_consumption,
            "cost_per_kwh": self.energy_cost_per_kwh,
            "daily_cost": daily_cost,
            "monthly_cost": monthly_cost,
            "solar_production": {
                "current_output": solar_current,
                "daily_production": solar_daily,
                "monthly_production": solar_monthly,
                "energy_saved": solar_monthly * self.energy_cost_per_kwh
            },
            "grid_percentage": grid_percentage,
            "solar_percentage": solar_percentage
        }
    
    async def _get_mock_energy_forecast(self, days: int = 7) -> List[Dict]:
        """
        Δημιουργία δοκιμαστικής πρόβλεψης ενέργειας για development/testing
        """
        forecast = []
        
        # Δοκιμαστικές τιμές με μικρές διακυμάνσεις
        base_consumption = 35.0  # kWh
        base_solar = 15.0  # kWh
        
        for day in range(days):
            # Δημιουργία διακύμανσης για πιο ρεαλιστικά δεδομένα
            import random
            consumption_variation = random.uniform(0.9, 1.1)
            solar_variation = random.uniform(0.8, 1.2)
            
            daily_consumption = base_consumption * consumption_variation
            daily_solar = base_solar * solar_variation
            
            # Υπολογισμός κόστους και ποσοστών
            daily_cost = (daily_consumption - daily_solar) * self.energy_cost_per_kwh
            solar_percentage = (daily_solar / daily_consumption) * 100 if daily_consumption > 0 else 0
            grid_percentage = 100 - solar_percentage
            
            # Προσθήκη στην πρόβλεψη
            forecast.append({
                "day": day + 1,
                "date": (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + 
                         datetime.timedelta(days=day)).isoformat(),
                "consumption": daily_consumption,
                "solar_production": daily_solar,
                "cost": daily_cost,
                "grid_percentage": grid_percentage,
                "solar_percentage": solar_percentage
            })
        
        return forecast