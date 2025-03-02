#!/usr/bin/env python3
"""
Εργαλείο διάγνωσης για το AI Mining Assistant
Χρήση: python debug_tools.py [command]
Διαθέσιμες εντολές:
  - system: Έλεγχος πληροφοριών συστήματος
  - dependencies: Έλεγχος εξαρτήσεων
  - database: Έλεγχος σύνδεσης με βάση δεδομένων
  - files: Λίστα σημαντικών αρχείων του έργου
  - modules: Έλεγχος φόρτωσης modules
  - all: Εκτέλεση όλων των ελέγχων (προεπιλογή)
"""
import os
import sys
import platform
import subprocess
import json
import importlib
import time
import traceback
from datetime import datetime

def check_system_info():
    """Έλεγχος πληροφοριών συστήματος"""
    print("🔍 Έλεγχος πληροφοριών συστήματος...")
    info = {}
    info["os"] = platform.system()
    info["os_version"] = platform.version()
    info["python_version"] = sys.version
    info["timestamp"] = datetime.now().isoformat()
    info["cwd"] = os.getcwd()
    info["script_path"] = os.path.abspath(__file__)
    info["python_path"] = sys.executable
    
    # Έλεγχος διαθέσιμης μνήμης
    try:
        import psutil
        vm = psutil.virtual_memory()
        info["total_memory_gb"] = round(vm.total / (1024**3), 2)
        info["available_memory_gb"] = round(vm.available / (1024**3), 2)
        info["memory_percent"] = vm.percent
    except ImportError:
        info["memory"] = "psutil not installed"
    
    # Έλεγχος CUDA αν είναι διαθέσιμο
    try:
        import torch
        info["cuda_available"] = torch.cuda.is_available()
        if info["cuda_available"]:
            info["cuda_version"] = torch.version.cuda
            info["gpu_count"] = torch.cuda.device_count()
            info["gpu_name"] = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
            # Έλεγχος μνήμης GPU
            for i in range(torch.cuda.device_count()):
                try:
                    info[f"gpu_{i}_memory_total"] = round(torch.cuda.get_device_properties(i).total_memory / (1024**3), 2)
                    info[f"gpu_{i}_memory_allocated"] = round(torch.cuda.memory_allocated(i) / (1024**3), 2)
                    info[f"gpu_{i}_memory_reserved"] = round(torch.cuda.memory_reserved(i) / (1024**3), 2)
                except:
                    pass
    except ImportError:
        info["cuda_available"] = "torch not installed"
    
    print(json.dumps(info, indent=2))
    return info

def list_project_files(base_dir="."):
    """Δημιουργία λίστας αρχείων του έργου"""
    print("🔍 Καταγραφή αρχείων του project...")
    
    files = []
    skipped_dirs = [".git", "__pycache__", "venv", "node_modules", ".venv"]
    
    for root, dirs, filenames in os.walk(base_dir):
        # Αφαίρεση των φακέλων που πρέπει να παραλειφθούν
        dirs[:] = [d for d in dirs if d not in skipped_dirs and not d.startswith(".")]
        
        for filename in filenames:
            if filename.endswith((".py", ".js", ".vue", ".sql", ".env", ".sh", ".md", ".txt")):
                try:
                    file_path = os.path.join(root, filename)
                    size = os.path.getsize(file_path)
                    modified = os.path.getmtime(file_path)
                    files.append({
                        "path": file_path,
                        "size_kb": round(size / 1024, 2),
                        "modified": datetime.fromtimestamp(modified).isoformat()
                    })
                except Exception as e:
                    print(f"Σφάλμα στο αρχείο {os.path.join(root, filename)}: {str(e)}")
    
    # Ταξινόμηση αρχείων κατά μέγεθος
    files.sort(key=lambda x: x["path"])
    
    # Εμφάνιση συνοπτικών πληροφοριών
    print(f"Βρέθηκαν {len(files)} αρχεία")
    
    # Εμφάνιση των 20 μεγαλύτερων αρχείων
    largest_files = sorted(files, key=lambda x: x["size_kb"], reverse=True)[:20]
    print("\nΤα 20 μεγαλύτερα αρχεία:")
    for i, file in enumerate(largest_files):
        print(f"{i+1}. {file['path']} ({file['size_kb']} KB)")
    
    return files

def check_dependencies():
    """Έλεγχος εγκατεστημένων πακέτων Python"""
    print("🔍 Έλεγχος εξαρτήσεων Python...")
    dependencies = {}
    
    # Βασικά πακέτα που απαιτούνται από το project
    important_packages = [
        "fastapi", "uvicorn", "sqlalchemy", "pydantic", 
        "torch", "transformers", "peft", "httpx", "redis",
        "python-telegram-bot", "celery", "numpy", "pandas"
    ]
    
    for package in important_packages:
        try:
            start_time = time.time()
            module = importlib.import_module(package)
            end_time = time.time()
            
            dependencies[package] = {
                "status": "installed",
                "version": getattr(module, "__version__", "unknown"),
                "import_time": round((end_time - start_time) * 1000, 2)  # σε ms
            }
        except ImportError:
            dependencies[package] = {"status": "not installed"}
        except Exception as e:
            dependencies[package] = {"status": "error", "message": str(e)}
    
    # Έλεγχος εγκατεστημένων πακέτων από το pip
    try:
        import pkg_resources
        installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
        dependencies["installed_count"] = len(installed_packages)
    except Exception as e:
        dependencies["installed_count"] = {"status": "error", "message": str(e)}
    
    print(json.dumps(dependencies, indent=2))
    return dependencies

def check_database():
    """Έλεγχος σύνδεσης με τη βάση δεδομένων"""
    print("🔍 Έλεγχος σύνδεσης με τη βάση δεδομένων...")
    result = {}
    
    try:
        sys.path.append(os.getcwd())
        
        # Προσπάθεια εισαγωγής του database module
        start_time = time.time()
        from backend.database import check_db_connection, engine
        import_time = time.time() - start_time
        
        result["import_time"] = round(import_time * 1000, 2)  # σε ms
        result["connection_string"] = str(engine.url).replace(":password@", ":***@")
        
        # Έλεγχος σύνδεσης
        conn_start = time.time()
        status = check_db_connection()
        conn_time = time.time() - conn_start
        
        result["status"] = "connected" if status else "disconnected"
        result["connection_time"] = round(conn_time * 1000, 2)  # σε ms
        
        # Έλεγχος για τα μοντέλα της βάσης
        try:
            from backend.models import Base
            tables = Base.metadata.tables.keys()
            result["tables"] = list(tables)
        except Exception as e:
            result["tables_error"] = str(e)
        
    except ImportError as e:
        result["status"] = "import_error"
        result["message"] = f"Δεν ήταν δυνατή η εισαγωγή του database module: {str(e)}"
        result["traceback"] = traceback.format_exc()
    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)
        result["traceback"] = traceback.format_exc()
    
    print(json.dumps(result, indent=2))
    return result

def check_modules_import():
    """Έλεγχος φόρτωσης των βασικών modules του project"""
    print("🔍 Έλεγχος φόρτωσης βασικών modules...")
    modules = {}
    
    # Λίστα σημαντικών modules προς έλεγχο
    important_modules = [
        "backend.main", 
        "backend.database", 
        "backend.models", 
        "backend.schemas", 
        "backend.ai_engine",
        "backend.connectors.mining_connector",
        "backend.connectors.energy_connector",
        "backend.connectors.cloreai_connector"
    ]
    
    sys.path.append(os.getcwd())
    
    for module_name in important_modules:
        try:
            start_time = time.time()
            module = importlib.import_module(module_name)
            end_time = time.time()
            
            modules[module_name] = {
                "status": "imported",
                "import_time": round((end_time - start_time) * 1000, 2),  # σε ms
                "file": getattr(module, "__file__", "unknown")
            }
            
            # Έλεγχος για κλάσεις και συναρτήσεις
            if module_name == "backend.database":
                modules[module_name]["contains_get_db"] = hasattr(module, "get_db")
                modules[module_name]["contains_Base"] = hasattr(module, "Base")
            elif module_name == "backend.models":
                modules[module_name]["models"] = [name for name in dir(module) 
                                                if not name.startswith("__") and name[0].isupper()]
            elif module_name == "backend.ai_engine":
                modules[module_name]["contains_AIEngine"] = hasattr(module, "AIEngine")
                
        except ImportError as e:
            modules[module_name] = {
                "status": "import_error",
                "error": str(e)
            }
        except Exception as e:
            modules[module_name] = {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    print(json.dumps(modules, indent=2))
    return modules

def main():
    """Κύρια λειτουργία του εργαλείου διάγνωσης"""
    print("=== AI Mining Assistant Diagnostic Tool ===")
    print(f"Ημερομηνία/Ώρα: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Τρέχων φάκελος: {os.getcwd()}")
    print("=" * 45 + "\n")
    
    # Έλεγχος παραμέτρων γραμμής εντολών
    command = "all"
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    
    # Συλλογή πληροφοριών βάσει της εντολής
    report = {}
    
    if command in ["system", "all"]:
        report["system_info"] = check_system_info()
        print()
    
    if command in ["dependencies", "all"]:
        report["dependencies"] = check_dependencies()
        print()
    
    if command in ["database", "all"]:
        report["database"] = check_database()
        print()
    
    if command in ["modules", "all"]:
        report["modules"] = check_modules_import()
        print()
        
    if command in ["files", "all"]:
        report["files"] = list_project_files()
        print()
    
    # Αποθήκευση αναφοράς
    output_file = f"diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📝 Αναφορά διάγνωσης αποθηκεύτηκε στο: {os.path.abspath(output_file)}")
    print("\n=== Ολοκλήρωση Διάγνωσης ===")

if __name__ == "__main__":
    main()
