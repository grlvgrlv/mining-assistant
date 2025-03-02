#!/usr/bin/env python3

import os
import json
import sys
from datetime import datetime

class ProjectProgressTracker:
    def __init__(self, project_base_path):
        self.project_base_path = project_base_path
        self.progress_file = os.path.join(project_base_path, '.project_progress.json')
        self.phases = {
            "Infrastructure Setup": {
                "steps": [
                    {"name": "System Requirements Check", "status": "completed", "priority": "high"},
                    {"name": "Python Virtual Environment", "status": "completed", "priority": "high"},
                    {"name": "Install Dependencies", "status": "completed", "priority": "high"},
                    {"name": "PostgreSQL Database Setup", "status": "in_progress", "priority": "high"}
                ],
                "weight": 0.15
            },
            "Backend Development": {
                "steps": [
                    {"name": "FastAPI Setup", "status": "pending", "priority": "high"},
                    {"name": "Database Models", "status": "pending", "priority": "medium"},
                    {"name": "Mining Connectors", "status": "in_progress", "priority": "high"},
                    {"name": "Energy Monitoring Integration", "status": "pending", "priority": "medium"}
                ],
                "weight": 0.25
            },
            "AI Model Preparation": {
                "steps": [
                    {"name": "Base Model Download", "status": "in_progress", "priority": "high"},
                    {"name": "CUDA Compatibility Check", "status": "completed", "priority": "high"},
                    {"name": "Model Quantization", "status": "pending", "priority": "medium"},
                    {"name": "Fine-tuning Preparation", "status": "pending", "priority": "low"}
                ],
                "weight": 0.20
            },
            "Frontend Development": {
                "steps": [
                    {"name": "Vue.js Project Setup", "status": "pending", "priority": "high"},
                    {"name": "Dashboard Layout", "status": "pending", "priority": "medium"},
                    {"name": "Real-time Data Visualization", "status": "pending", "priority": "low"}
                ],
                "weight": 0.15
            },
            "Integration and Deployment": {
                "steps": [
                    {"name": "API Endpoints", "status": "pending", "priority": "high"},
                    {"name": "Telegram Bot Integration", "status": "pending", "priority": "medium"},
                    {"name": "Docker Containerization", "status": "pending", "priority": "low"}
                ],
                "weight": 0.15
            },
            "Testing and Optimization": {
                "steps": [
                    {"name": "Unit Tests", "status": "pending", "priority": "medium"},
                    {"name": "Performance Benchmarking", "status": "pending", "priority": "low"}
                ],
                "weight": 0.10
            }
        }
        self.load_progress()

    def load_progress(self):
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    saved_progress = json.load(f)
                    # Update existing progress structure
                    for phase, phase_data in saved_progress.items():
                        if phase in self.phases:
                            self.phases[phase] = phase_data
            except (json.JSONDecodeError, IOError):
                print("Warning: Unable to load existing progress file.")

    def save_progress(self):
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.phases, f, indent=2)
        except IOError:
            print("Error: Unable to save progress file.")

    def update_step_status(self, phase, step_name, status):
        for step in self.phases[phase]["steps"]:
            if step["name"] == step_name:
                step["status"] = status
                step["last_updated"] = datetime.now().isoformat()
                break
        self.save_progress()

    def calculate_overall_progress(self):
        total_progress = 0
        for phase, phase_data in self.phases.items():
            phase_completed_steps = sum(1 for step in phase_data["steps"] if step["status"] == "completed")
            phase_in_progress_steps = sum(1 for step in phase_data["steps"] if step["status"] == "in_progress")
            phase_total_steps = len(phase_data["steps"])
            
            # Completed steps count fully, in-progress steps count half
            phase_progress = (phase_completed_steps + 0.5 * phase_in_progress_steps) / phase_total_steps * phase_data["weight"]
            total_progress += phase_progress
        return round(total_progress * 100, 2)

    def get_next_steps(self):
        next_steps = []
        for phase, phase_data in self.phases.items():
            for step in phase_data["steps"]:
                if step["status"] == "pending" and step["priority"] == "high":
                    next_steps.append(f"{phase} - {step['name']}")
        return next_steps

    def verify_postgresql_setup(self):
        """
        Επαλήθευση της πλήρους ρύθμισης της PostgreSQL
        
        Returns:
            bool: True αν όλα τα βήματα έχουν ολοκληρωθεί επιτυχώς
        """
        try:
            import os
            import sys
            from sqlalchemy import create_engine, inspect
            from sqlalchemy.orm import sessionmaker
            from dotenv import load_dotenv

            # Φόρτωση περιβαλλοντικών μεταβλητών
            load_dotenv()

            # Προσθήκη του path του backend στο sys.path
            backend_path = os.path.join(self.project_base_path, 'backend')
            sys.path.append(self.project_base_path)
            sys.path.append(backend_path)

            # Εισαγωγή των models
            from backend.models import Base, User, MiningConfig, MiningStat, EnergyConsumption, CryptoPrice

            # Λήψη URL βάσης δεδομένων
            DATABASE_URL = os.getenv("DATABASE_URL")
            
            if not DATABASE_URL:
                print("Δεν βρέθηκε DATABASE_URL")
                return False

            # Δημιουργία engine
            engine = create_engine(DATABASE_URL)
            
            # Δημιουργία session
            SessionLocal = sessionmaker(bind=engine)
            session = SessionLocal()

            # Έλεγχος ύπαρξης πινάκων
            inspector = inspect(engine)
            required_tables = [
                'users', 
                'mining_configs', 
                'mining_stats', 
                'energy_consumption', 
                'crypto_prices',
                'alembic_version'
            ]
            
            # Έλεγχος όλων των απαιτούμενων πινάκων
            missing_tables = [
                table for table in required_tables 
                if table not in inspector.get_table_names()
            ]
            
            if missing_tables:
                print(f"Λείπουν πίνακες: {missing_tables}")
                session.close()
                return False

            # Έλεγχος εγγραφών σε βασικούς πίνακες
            user_count = session.query(User).count()
            mining_config_count = session.query(MiningConfig).count()
            
            # Κλείσιμο της σύνδεσης
            session.close()

            # Επιβεβαίωση ότι υπάρχουν εγγραφές
            if user_count == 0 or mining_config_count == 0:
                print("Δεν υπάρχουν δεδομένα στους βασικούς πίνακες")
                return False

            return True

        except Exception as e:
            print(f"Σφάλμα κατά τον έλεγχο της βάσης δεδομένων: {e}")
            return False

    def print_detailed_progress(self):
        print("\n=== AI Mining Assistant - Project Progress ===")
        print(f"Overall Project Progress: {self.calculate_overall_progress()}%\n")

        for phase, phase_data in self.phases.items():
            print(f"{phase}:")
            for step in phase_data["steps"]:
                status_color = {
                    "pending": "\033[93m",  # Yellow
                    "in_progress": "\033[94m",  # Blue
                    "completed": "\033[92m",  # Green
                    "failed": "\033[91m"  # Red
                }
                status_symbol = {
                    "pending": "❌",
                    "in_progress": "🔨",
                    "completed": "✅",
                    "failed": "❗"
                }
                
                print(f"  {status_color.get(step['status'], '')}"
                      f"{status_symbol.get(step['status'], '')} "
                      f"{step['name']} - {step['status'].upper()}"
                      f"\033[0m")
            print()

        print("=== Suggested Next Steps ===")
        next_steps = self.get_next_steps()
        if next_steps:
            for step in next_steps:
                print(f"➡️ {step}")
        else:
            print("🎉 All high-priority tasks are in progress or completed!")

def main():
    project_base_path = os.path.expanduser("~/mining-assistant")
    tracker = ProjectProgressTracker(project_base_path)
    
    # Έλεγχος PostgreSQL setup
    if tracker.verify_postgresql_setup():
        # Ενημέρωση του βήματος σε completed
        tracker.update_step_status(
            "Infrastructure Setup", 
            "PostgreSQL Database Setup", 
            "completed"
        )
    
    tracker.print_detailed_progress()

if __name__ == "__main__":
    main()
