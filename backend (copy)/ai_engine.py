import os
import logging
from typing import Dict, List, Optional, Tuple, Union
from dotenv import load_dotenv
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from peft import PeftConfig, PeftModel

# Φόρτωση περιβαλλοντικών μεταβλητών
load_dotenv()

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        self.model_path = os.getenv("MODEL_PATH", "./models/mining-assistant-llm")
        self.device = os.getenv("DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        
    async def load_model(self):
        """
        Φορτώνει το LLM μοντέλο για χρήση.
        """
        try:
            logger.info(f"Loading model from {self.model_path} on {self.device}")
            
            # Έλεγχος για fine-tuned μοντέλο
            peft_config_path = os.path.join(self.model_path, "adapter_config.json")
            is_peft_model = os.path.exists(peft_config_path)
            
            # Φόρτωση του βασικού μοντέλου
            if is_peft_model:
                # Αν έχουμε PEFT μοντέλο, φορτώνουμε το βασικό και μετά τους adapters
                peft_config = PeftConfig.from_pretrained(self.model_path)
                self.tokenizer = AutoTokenizer.from_pretrained(peft_config.base_model_name_or_path)
                
                # Φόρτωση με quantization για περιορισμένη GPU μνήμη
                base_model = AutoModelForCausalLM.from_pretrained(
                    peft_config.base_model_name_or_path,
                    load_in_8bit=True,  # Χρήση 8-bit quantization για εξοικονόμηση μνήμης
                    device_map="auto",
                    torch_dtype=torch.float16
                )
                
                # Φόρτωση των fine-tuned παραμέτρων
                self.model = PeftModel.from_pretrained(base_model, self.model_path)
            else:
                # Απευθείας φόρτωση του μοντέλου αν δεν έχουμε PEFT
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    load_in_8bit=True,  # Χρήση 8-bit quantization για εξοικονόμηση μνήμης
                    device_map="auto",
                    torch_dtype=torch.float16
                )
            
            # Δημιουργία του pipeline για εύκολη χρήση
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=self.device
            )
            
            logger.info("Model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    async def generate_response(self, prompt: str, max_length: int = 512) -> str:
        """
        Παράγει απάντηση από το LLM με βάση το prompt.
        
        Args:
            prompt: Το prompt προς το μοντέλο.
            max_length: Μέγιστο μήκος απάντησης.
            
        Returns:
            str: Η απάντηση από το μοντέλο.
        """
        if not self.model or not self.tokenizer:
            success = await self.load_model()
            if not success:
                return "Δεν ήταν δυνατή η φόρτωση του μοντέλου. Παρακαλώ δοκιμάστε ξανά αργότερα."
        
        try:
            # Προσθήκη ενός system prompt για καλύτερο context
            system_prompt = "Είσαι ένας AI βοηθός εξειδικευμένος στην εξόρυξη κρυπτονομισμάτων, την ενεργειακή κατανάλωση και τη βελτιστοποίηση GPU. Απάντησε στην παρακάτω ερώτηση με ακρίβεια και λεπτομέρεια."
            full_prompt = f"{system_prompt}\n\nΕρώτηση: {prompt}\n\nΑπάντηση:"
            
            # Παραγωγή απάντησης
            outputs = self.pipeline(
                full_prompt,
                max_length=max_length,
                num_return_sequences=1,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
            )
            
            # Εξαγωγή της απάντησης από τα outputs
            generated_text = outputs[0]["generated_text"]
            
            # Αφαίρεση του αρχικού prompt για να πάρουμε μόνο την απάντηση
            response = generated_text.split("Απάντηση:")[1].strip() if "Απάντηση:" in generated_text else generated_text
            
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Παρουσιάστηκε σφάλμα κατά την παραγωγή απάντησης: {str(e)}"
    
    async def analyze_mining_data(self, data: Dict) -> Dict:
        """
        Αναλύει δεδομένα εξόρυξης και παρέχει προτάσεις βελτιστοποίησης.
        
        Args:
            data: Δεδομένα εξόρυξης προς ανάλυση.
            
        Returns:
            Dict: Αποτελέσματα ανάλυσης και προτάσεις.
        """
        # Μετατροπή των δεδομένων σε μορφή κατάλληλη για το prompt
        data_str = "\n".join([f"{key}: {value}" for key, value in data.items()])
        
        prompt = f"""
        Ανάλυσε τα παρακάτω δεδομένα εξόρυξης κρυπτονομισμάτων και παρέχε προτάσεις για βελτιστοποίηση:
        
        {data_str}
        
        Παρακαλώ παρέχε:
        1. Σύνοψη της τρέχουσας απόδοσης
        2. Αδύναμα σημεία ή προβλήματα
        3. Προτάσεις βελτιστοποίησης για καλύτερη απόδοση ή χαμηλότερη κατανάλωση ενέργειας
        4. Εκτίμηση για πιθανή βελτίωση της κερδοφορίας
        """
        
        # Παραγωγή ανάλυσης
        analysis_text = await self.generate_response(prompt, max_length=1024)
        
        # Επεξεργασία του κειμένου για δομημένο αποτέλεσμα
        sections = ["Σύνοψη", "Αδύναμα σημεία", "Προτάσεις βελτιστοποίησης", "Εκτίμηση βελτίωσης"]
        analysis_result = {}
        
        current_section = "general"
        analysis_result[current_section] = []
        
        for line in analysis_text.split("\n"):
            line = line.strip()
            if not line:
                continue
                
            # Έλεγχος αν η γραμμή είναι επικεφαλίδα ενότητας
            section_match = False
            for section in sections:
                if section in line.lower() or f"{sections.index(section) + 1}." in line:
                    current_section = section
                    analysis_result[current_section] = []
                    section_match = True
                    break
            
            # Αν δεν είναι επικεφαλίδα, προσθήκη στην τρέχουσα ενότητα
            if not section_match:
                analysis_result[current_section].append(line)
        
        # Μετατροπή των λιστών σε κείμενο
        for section in analysis_result:
            analysis_result[section] = "\n".join(analysis_result[section])
        
        return analysis_result
    
    async def predict_mining_profitability(self, gpu_data: List[Dict], coin_data: List[Dict], energy_cost: float) -> Dict:
        """
        Προβλέπει την κερδοφορία εξόρυξης για διάφορους συνδυασμούς GPU και κρυπτονομισμάτων.
        
        Args:
            gpu_data: Λίστα με δεδομένα GPU.
            coin_data: Λίστα με δεδομένα κρυπτονομισμάτων.
            energy_cost: Κόστος ενέργειας σε EUR/kWh.
            
        Returns:
            Dict: Προβλέψεις κερδοφορίας.
        """
        # Υλοποίηση αλγορίθμου πρόβλεψης κερδοφορίας
        # (Αυτό είναι ένα πλαίσιο - η πραγματική υλοποίηση θα είναι πιο περίπλοκη)
        
        predictions = {}
        
        for coin in coin_data:
            coin_name = coin.get("name", "unknown")
            predictions[coin_name] = []
            
            for gpu in gpu_data:
                gpu_name = gpu.get("name", "unknown")
                hashrate = gpu.get("hashrate", {}).get(coin_name, 0)
                power_consumption = gpu.get("power_consumption", 0)
                
                # Απλός υπολογισμός κερδοφορίας
                daily_reward = hashrate * coin.get("reward_per_hashrate", 0) * 24
                daily_energy_cost = power_consumption * energy_cost * 24 / 1000  # kWh
                daily_profit = daily_reward - daily_energy_cost
                
                predictions[coin_name].append({
                    "gpu": gpu_name,
                    "daily_reward": daily_reward,
                    "daily_energy_cost": daily_energy_cost,
                    "daily_profit": daily_profit,
                    "monthly_profit": daily_profit * 30,
                    "roi_days": gpu.get("price", 0) / daily_profit if daily_profit > 0 else float('inf')
                })
        
        # Εύρεση της καλύτερης επιλογής συνολικά
        best_option = {
            "coin": "",
            "gpu": "",
            "daily_profit": 0,
            "roi_days": float('inf')
        }
        
        for coin, gpu_profits in predictions.items():
            for gpu_profit in gpu_profits:
                if gpu_profit["daily_profit"] > best_option["daily_profit"]:
                    best_option = {
                        "coin": coin,
                        "gpu": gpu_profit["gpu"],
                        "daily_profit": gpu_profit["daily_profit"],
                        "monthly_profit": gpu_profit["monthly_profit"],
                        "roi_days": gpu_profit["roi_days"]
                    }
        
        return {
            "predictions": predictions,
            "best_option": best_option
        }
    
    async def optimize_mining_strategy(self, user_config: Dict, market_data: Dict, energy_data: Dict) -> Dict:
        """
        Βελτιστοποιεί τη στρατηγική εξόρυξης με βάση τα δεδομένα του χρήστη, της αγοράς και της ενέργειας.
        
        Args:
            user_config: Διαμόρφωση και προτιμήσεις του χρήστη.
            market_data: Δεδομένα αγοράς κρυπτονομισμάτων.
            energy_data: Δεδομένα κόστους και διαθεσιμότητας ενέργειας.
            
        Returns:
            Dict: Προτεινόμενη βελτιστοποιημένη στρατηγική.
        """
        # Σύνθεση δεδομένων σε μορφή κατάλληλη για ανάλυση από το LLM
        data_str = f"""
        Δεδομένα χρήστη:
        - GPUs: {user_config.get('gpus', [])}
        - Τρέχον κρυπτονόμισμα: {user_config.get('current_coin', 'none')}
        - Προϋπολογισμός για ενοικίαση: {user_config.get('rental_budget', 0)} EUR
        - Απαιτούμενο ROI: {user_config.get('roi_threshold', 0)} ημέρες
        
        Δεδομένα αγοράς:
        - Τιμές κρυπτονομισμάτων: {market_data.get('prices', {})}
        - Δυσκολία εξόρυξης: {market_data.get('mining_difficulty', {})}
        - Κερδοφορία ανά coin: {market_data.get('profitability', {})}
        
        Ενεργειακά δεδομένα:
        - Τρέχουσα τιμή: {energy_data.get('current_price', 0)} EUR/kWh
        - Πρόβλεψη φωτοβολταϊκών: {energy_data.get('solar_forecast', {})}
        - Διαθέσιμη ενέργεια: {energy_data.get('available_power', 0)} kW
        """
        
        prompt = f"""
        Με βάση τα παρακάτω δεδομένα, βελτιστοποίησε τη στρατηγική εξόρυξης κρυπτονομισμάτων:
        
        {data_str}
        
        Παρακαλώ παρέχε:
        1. Ποιο κρυπτονόμισμα είναι πιο κερδοφόρο για εξόρυξη
        2. Ποιες GPUs πρέπει να χρησιμοποιηθούν για κάθε coin
        3. Αν αξίζει η ενοικίαση επιπλέον GPUs μέσω CloreAI
        4. Βέλτιστο χρονοδιάγραμμα εξόρυξης με βάση το κόστος ενέργειας και την παραγωγή των φωτοβολταϊκών
        5. Εκτιμώμενη κερδοφορία με τη βελτιστοποιημένη στρατηγική
        """
        
        # Παραγωγή ανάλυσης
        optimization_text = await self.generate_response(prompt, max_length=1536)
        
        # Εξαγωγή προτάσεων και διαμόρφωση δομημένου αποτελέσματος
        # (Απλοποιημένη εκδοχή για αυτό το παράδειγμα)
        suggestions = {
            "recommended_coin": "",
            "gpu_allocation": {},
            "rental_recommendation": {},
            "mining_schedule": {},
            "estimated_profitability": {}
        }
        
        # Απλή ανάλυση κειμένου για την εξαγωγή προτάσεων
        lines = optimization_text.split("\n")
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "κρυπτονόμισμα" in line.lower() and "κερδοφόρο" in line.lower():
                current_section = "coin"
                # Απλή εξαγωγή του προτεινόμενου κρυπτονομίσματος
                for coin_name in market_data.get('prices', {}).keys():
                    if coin_name in line:
                        suggestions["recommended_coin"] = coin_name
                        break
            elif "gpu" in line.lower() or "κάρτ" in line.lower():
                current_section = "gpu"
                # Θα χρειαστεί πιο περίπλοκη ανάλυση για τις προτάσεις GPU
            elif "ενοικίαση" in line.lower() or "cloreai" in line.lower():
                current_section = "rental"
                suggestions["rental_recommendation"]["recommendation"] = "yes" if "αξίζει" in line.lower() and not "δεν αξίζει" in line.lower() else "no"
            elif "χρονοδιάγραμμα" in line.lower() or "πρόγραμμα" in line.lower():
                current_section = "schedule"
            elif "κερδοφορία" in line.lower() or "κέρδος" in line.lower() or "profit" in line.lower():
                current_section = "profit"
                # Απόπειρα εξαγωγής αριθμητικής τιμής κερδοφορίας
                import re
                profit_matches = re.findall(r'(\d+[.,]?\d*)\s*(?:EUR|€)', line)
                if profit_matches:
                    try:
                        suggestions["estimated_profitability"]["daily"] = float(profit_matches[0].replace(',', '.'))
                    except:
                        pass
        
        return {
            "raw_analysis": optimization_text,
            "suggestions": suggestions
        }
