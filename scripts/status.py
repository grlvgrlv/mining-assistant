#!/usr/bin/env python3

import os
import json
import sys
import glob
from datetime import datetime

class ProjectProgressTracker:
    def __init__(self, project_base_path):
        self.project_base_path = project_base_path
        self.progress_file = os.path.join(project_base_path, '.project_progress.json')
        self.logs_dir = os.path.join(project_base_path, 'logs')
        self.institutional_memory = self.find_latest_institutional_memory()
        self.diagnostic_report = self.find_latest_diagnostic_report()
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
        self.analyze_institutional_memory()

    def find_latest_institutional_memory(self):
        """Εύρεση του πιο πρόσφατου optimized institutional memory αρχείου"""
        try:
            if not os.path.exists(self.logs_dir):
                return None
                
            # Αναζήτηση αρχείων optimized
            optimized_files = glob.glob(os.path.join(self.logs_dir, "optimized_institutional_memory_*.json"))
            
            if not optimized_files:
                # Αν δεν υπάρχουν optimized, ψάχνουμε κανονικά institutional memory αρχεία
                regular_files = glob.glob(os.path.join(self.logs_dir, "institutional_memory_*.json"))
                if not regular_files:
                    return None
                optimized_files = regular_files
            
            # Ταξινόμηση με βάση την ημερομηνία τροποποίησης (πιο πρόσφατα πρώτα)
            latest_file = max(optimized_files, key=os.path.getmtime)
            
            # Φόρτωση του αρχείου
            with open(latest_file, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
                print(f"Φορτώθηκε το institutional memory: {os.path.basename(latest_file)}")
                return memory_data
        except Exception as e:
            print(f"Σφάλμα κατά τη φόρτωση του institutional memory: {e}")
            return None

    def find_latest_diagnostic_report(self):
        """Εύρεση του πιο πρόσφατου αρχείου diagnostic report"""
        try:
            # Αναζήτηση στο current directory και στο logs directory
            diagnostic_files = glob.glob("diagnostic_report_*.json") + \
                              glob.glob(os.path.join(self.logs_dir, "diagnostic_report_*.json"))
            
            if not diagnostic_files:
                return None
                
            # Ταξινόμηση με βάση την ημερομηνία τροποποίησης (πιο πρόσφατα πρώτα)
            latest_file = max(diagnostic_files, key=os.path.getmtime)
            
            # Φόρτωση του αρχείου
            with open(latest_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
                print(f"Φορτώθηκε το diagnostic report: {os.path.basename(latest_file)}")
                return report_data
        except Exception as e:
            print(f"Σφάλμα κατά τη φόρτωση του diagnostic report: {e}")
            return None

    def analyze_institutional_memory(self):
        """Ανάλυση του institutional memory για εύρεση δεικτών προόδου"""
        if not self.institutional_memory:
            return
            
        # Μετρικές που θα συλλέξουμε
        self.memory_metrics = {
            "python_files": 0,
            "config_files": 0,
            "total_files": 0,
            "python_packages": 0,
            "implementation_files": {
                "backend": 0,
                "frontend": 0,
                "database": 0,
                "ai": 0,
                "mining": 0,
                "energy": 0,
                "api": 0
            },
            "latest_modified_files": [],
            "system_info": {}
        }
        
        # Εύρεση των Python αρχείων
        for item in self.institutional_memory:
            if not isinstance(item, dict) or "file_path" not in item:
                continue
                
            file_path = item.get("file_path", "")
            
            # Αγνόηση μεταδεδομένων
            if file_path in ["system_info", "project_structure", "project_progress"]:
                if file_path == "system_info" and "content" in item:
                    try:
                        self.memory_metrics["system_info"] = json.loads(item["content"])
                    except:
                        pass
                continue
                
            # Καταμέτρηση αρχείων ανά τύπο
            self.memory_metrics["total_files"] += 1
            
            if file_path.endswith(".py"):
                self.memory_metrics["python_files"] += 1
                
                # Κατηγοριοποίηση Python αρχείων
                file_content = item.get("content", "").lower()
                if "database" in file_path or "db" in file_path or "sqlalchemy" in file_content or "postgres" in file_content:
                    self.memory_metrics["implementation_files"]["database"] += 1
                elif "api" in file_path or "fastapi" in file_content or "endpoint" in file_content:
                    self.memory_metrics["implementation_files"]["api"] += 1
                elif "mining" in file_path or "hashrate" in file_content or "crypto" in file_content:
                    self.memory_metrics["implementation_files"]["mining"] += 1
                elif "energy" in file_path or "power" in file_content or "consumption" in file_content:
                    self.memory_metrics["implementation_files"]["energy"] += 1
                elif "model" in file_path or "ai" in file_path or "ml" in file_content or "torch" in file_content:
                    self.memory_metrics["implementation_files"]["ai"] += 1
                elif "frontend" in file_path or "vue" in file_content or "react" in file_content or "ui" in file_path:
                    self.memory_metrics["implementation_files"]["frontend"] += 1
                else:
                    self.memory_metrics["implementation_files"]["backend"] += 1
            
            elif any(file_path.endswith(ext) for ext in [".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env"]):
                self.memory_metrics["config_files"] += 1
        
        # Εύρεση των πακέτων Python
        for item in self.institutional_memory:
            if isinstance(item, dict) and item.get("file_path") == "./venv/lib/python3.10/site-packages (packages)":
                content = item.get("content", "")
                # Μέτρηση γραμμών, αφαιρώντας τις κενές
                self.memory_metrics["python_packages"] = len([line for line in content.split("\n") if line.strip()])
                break
                
        # Ανάλυση του diagnostic report αν υπάρχει
        self.analyze_diagnostic_report()
                
        # Ενημέρωση της προόδου με βάση τις μετρικές
        self.update_progress_based_on_metrics()

    def analyze_diagnostic_report(self):
        """Ανάλυση του diagnostic report για εύρεση δεικτών προόδου"""
        if not self.diagnostic_report or not hasattr(self, 'memory_metrics'):
            return
            
        # Προσθήκη διαγνωστικών μετρικών
        self.memory_metrics["diagnostic"] = {
            "system": {},
            "dependencies": {},
            "database": {},
            "modules": {}
        }
        
        # Ανάλυση πληροφοριών συστήματος
        if "system_info" in self.diagnostic_report:
            system_info = self.diagnostic_report["system_info"]
            
            # Εξαγωγή βασικών πληροφοριών
            self.memory_metrics["diagnostic"]["system"] = {
                "os": system_info.get("os", "Unknown"),
                "python_version": system_info.get("python_version", "Unknown"),
                "cuda_available": system_info.get("cuda_available", False),
                "gpu_count": system_info.get("gpu_count", 0),
                "gpu_name": system_info.get("gpu_name", []),
                "total_memory_gb": system_info.get("total_memory_gb", 0),
                "available_memory_gb": system_info.get("available_memory_gb", 0)
            }
        
        # Ανάλυση εξαρτήσεων
        if "dependencies" in self.diagnostic_report:
            deps = self.diagnostic_report["dependencies"]
            
            # Καταμέτρηση εγκατεστημένων πακέτων
            installed_count = 0
            critical_deps = []
            
            for package, info in deps.items():
                if isinstance(info, dict) and info.get("status") == "installed":
                    installed_count += 1
                    
                    # Έλεγχος για κρίσιμα πακέτα
                    if package in ["fastapi", "sqlalchemy", "torch", "transformers"]:
                        critical_deps.append({
                            "name": package,
                            "version": info.get("version", "Unknown"),
                            "import_time": info.get("import_time", 0)
                        })
            
            self.memory_metrics["diagnostic"]["dependencies"] = {
                "installed_count": installed_count,
                "total_count": deps.get("installed_count", 0),
                "critical_deps": critical_deps
            }
        
        # Ανάλυση βάσης δεδομένων
        if "database" in self.diagnostic_report:
            db_info = self.diagnostic_report["database"]
            
            self.memory_metrics["diagnostic"]["database"] = {
                "status": db_info.get("status", "unknown"),
                "connection_time": db_info.get("connection_time", 0),
                "tables": db_info.get("tables", [])
            }
            
            # Ενημέρωση του PostgreSQL setup αν ήταν επιτυχής
            if db_info.get("status") == "connected":
                self.update_step_status_if_lower(
                    "Infrastructure Setup",
                    "PostgreSQL Database Setup",
                    "completed"
                )
                # Ενημέρωση Database Models αν υπάρχουν πίνακες
                if len(db_info.get("tables", [])) >= 3:
                    self.update_step_status_if_lower(
                        "Backend Development",
                        "Database Models",
                        "completed"
                    )
        
        # Ανάλυση modules
        if "modules" in self.diagnostic_report:
            modules = self.diagnostic_report["modules"]
            
            imported_count = sum(1 for module, info in modules.items() 
                               if isinstance(info, dict) and info.get("status") == "imported")
            
            self.memory_metrics["diagnostic"]["modules"] = {
                "imported_count": imported_count,
                "total_count": len(modules),
                "backend_main_status": modules.get("backend.main", {}).get("status", "unknown"),
                "models_count": len(modules.get("backend.models", {}).get("models", []))
            }
            
            # Ενημέρωση της κατάστασης του FastAPI Setup αν το main module φορτώθηκε
            if (modules.get("backend.main", {}).get("status") == "imported"):
                self.update_step_status_if_lower(
                    "Backend Development",
                    "FastAPI Setup",
                    "completed"
                )
                
            # Έλεγχος για mining connectors
            if (modules.get("backend.connectors.mining_connector", {}).get("status") == "imported"):
                self.update_step_status_if_lower(
                    "Backend Development",
                    "Mining Connectors",
                    "completed"
                )
                
            # Έλεγχος για energy monitoring
            if (modules.get("backend.connectors.energy_connector", {}).get("status") == "imported"):
                self.update_step_status_if_lower(
                    "Backend Development",
                    "Energy Monitoring Integration",
                    "in_progress"
                )
                
            # Έλεγχος για AI Engine
            if (modules.get("backend.ai_engine", {}).get("status") == "imported"):
                self.update_step_status_if_lower(
                    "AI Model Preparation",
                    "Base Model Download",
                    "completed"
                )
        
        # Ανάλυση αρχείων
        if "files" in self.diagnostic_report:
            files = self.diagnostic_report["files"]
            
            # Εύρεση των πιο πρόσφατα τροποποιημένων αρχείων
            files_with_dates = []
            for file_info in files:
                try:
                    modified = datetime.fromisoformat(file_info.get("modified", ""))
                    files_with_dates.append((file_info["path"], modified, file_info["size_kb"]))
                except (ValueError, KeyError):
                    continue
            
            # Ταξινόμηση και διατήρηση των 10 πιο πρόσφατα τροποποιημένων
            recent_files = sorted(files_with_dates, key=lambda x: x[1], reverse=True)[:10]
            
            self.memory_metrics["diagnostic"]["recent_files"] = [
                {"path": path, "modified": modified.isoformat(), "size_kb": size}
                for path, modified, size in recent_files
            ]

    def update_progress_based_on_metrics(self):
        """Ενημέρωση της προόδου με βάση τις μετρικές του institutional memory"""
        metrics = self.memory_metrics
        
        # Έλεγχος για PostgreSQL setup
        if metrics["implementation_files"]["database"] >= 2:
            self.update_step_status_if_lower(
                "Infrastructure Setup",
                "PostgreSQL Database Setup",
                "in_progress"
            )
        
        # Έλεγχος για FastAPI setup
        if metrics["implementation_files"]["api"] >= 1:
            self.update_step_status_if_lower(
                "Backend Development",
                "FastAPI Setup",
                "in_progress"
            )
        
        # Έλεγχος για Mining Connectors
        if metrics["implementation_files"]["mining"] >= 1:
            self.update_step_status_if_lower(
                "Backend Development",
                "Mining Connectors",
                "in_progress"
            )
        
        # Έλεγχος για Energy Monitoring
        if metrics["implementation_files"]["energy"] >= 1:
            self.update_step_status_if_lower(
                "Backend Development",
                "Energy Monitoring Integration",
                "in_progress"
            )
        
        # Έλεγχος για Database Models
        if metrics["implementation_files"]["database"] >= 3:
            self.update_step_status_if_lower(
                "Backend Development",
                "Database Models",
                "in_progress"
            )
        
        # Έλεγχος για Frontend setup
        if metrics["implementation_files"]["frontend"] >= 1:
            self.update_step_status_if_lower(
                "Frontend Development",
                "Vue.js Project Setup",
                "in_progress"
            )
        
        # Έλεγχος για AI Model setup
        if metrics["implementation_files"]["ai"] >= 1:
            self.update_step_status_if_lower(
                "AI Model Preparation",
                "Base Model Download",
                "in_progress"
            )
            
        # Έλεγχος για CUDA compatibility (based on GPU info)
        gpu_info = metrics["system_info"].get("gpu_info", "").lower()
        if "nvidia" in gpu_info and "cuda" in gpu_info:
            self.update_step_status_if_lower(
                "AI Model Preparation",
                "CUDA Compatibility Check",
                "completed"
            )

    def update_step_status_if_lower(self, phase, step_name, new_status):
        """
        Ενημερώνει το status ενός βήματος μόνο αν το νέο status είναι υψηλότερο από το τρέχον
        (pending < in_progress < completed)
        """
        status_rank = {
            "pending": 0,
            "in_progress": 1,
            "completed": 2
        }
        
        current_status = "pending"
        for step in self.phases[phase]["steps"]:
            if step["name"] == step_name:
                current_status = step["status"]
                break
                
        if status_rank.get(new_status, 0) > status_rank.get(current_status, 0):
            self.update_step_status(phase, step_name, new_status)

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

        # Εμφάνιση μετρικών από institutional memory αν υπάρχουν
        if hasattr(self, 'memory_metrics'):
            metrics = self.memory_metrics
            
            print("=== Project Metrics ===")
            print(f"Python files: {metrics['python_files']}")
            print(f"Configuration files: {metrics['config_files']}")
            print(f"Total tracked files: {metrics['total_files']}")
            print(f"Python packages: {metrics['python_packages']}")
            
            print("\nImplementation Files by Category:")
            for category, count in metrics['implementation_files'].items():
                print(f"  {category.capitalize()}: {count}")
            
            # Εμφάνιση διαγνωστικών δεδομένων αν υπάρχουν
            if "diagnostic" in metrics:
                diag = metrics["diagnostic"]
                
                if "system" in diag:
                    print("\n=== System Information ===")
                    sys_info = diag["system"]
                    print(f"OS: {sys_info.get('os', 'Unknown')}")
                    print(f"Python: {sys_info.get('python_version', 'Unknown').split()[0]}")
                    
                    if sys_info.get("cuda_available") is True:
                        print(f"CUDA: Available - {sys_info.get('gpu_count', 0)} GPU(s)")
                        if "gpu_name" in sys_info and sys_info["gpu_name"]:
                            for i, gpu in enumerate(sys_info["gpu_name"]):
                                print(f"  GPU {i+1}: {gpu}")
                    else:
                        print("CUDA: Not available")
                    
                    print(f"Memory: {sys_info.get('total_memory_gb', 0)} GB total, "
                          f"{sys_info.get('available_memory_gb', 0)} GB available")
                
                if "database" in diag:
                    print("\n=== Database Status ===")
                    db_info = diag["database"]
                    status_symbol = "✅" if db_info.get("status") == "connected" else "❌"
                    print(f"Connection: {status_symbol} {db_info.get('status', 'unknown')}")
                    if "tables" in db_info and db_info["tables"]:
                        print(f"Tables: {len(db_info['tables'])}")
                        if len(db_info["tables"]) <= 10:  # Εμφάνιση όλων των πινάκων αν είναι λίγοι
                            for table in sorted(db_info["tables"]):
                                print(f"  - {table}")
                
                if "modules" in diag:
                    print("\n=== Modules Status ===")
                    modules_info = diag["modules"]
                    print(f"Imported modules: {modules_info.get('imported_count', 0)}/{modules_info.get('total_count', 0)}")
                    if modules_info.get("backend_main_status") == "imported":
                        print("✅ Backend main module successfully imported")
                    else:
                        print("❌ Backend main module not imported")
                
                if "recent_files" in diag:
                    print("\n=== Recently Modified Files ===")
                    for file_info in diag["recent_files"][:5]:  # Εμφάνιση μόνο των 5 πιο πρόσφατων
                        try:
                            date_str = datetime.fromisoformat(file_info["modified"]).strftime("%Y-%m-%d %H:%M")
                            print(f"  {date_str} - {file_info['path']} ({file_info['size_kb']} KB)")
                        except (ValueError, KeyError):
                            continue
            
            print()

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
