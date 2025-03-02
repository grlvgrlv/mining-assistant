import os
import sys
import platform
import subprocess
import json
import importlib
import time
import traceback
from datetime import datetime

def run_command(command):
    """ Εκτελεί μια εντολή και επιστρέφει το output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error executing {command}: {str(e)}"

def check_system_info():
    """Έλεγχος πληροφοριών συστήματος."""
    print("🔍 Έλεγχος πληροφοριών συστήματος...")
    info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": sys.version,
        "timestamp": datetime.now().isoformat(),
        "cwd": os.getcwd(),
        "script_path": os.path.abspath(__file__),
        "python_path": sys.executable,
    }
    return info

def check_services():
    """ Έλεγχος λειτουργίας βασικών υπηρεσιών."""
    print("\n[1] Έλεγχος Υπηρεσιών...")
    services = {
        "FastAPI": run_command("ps aux | grep 'uvicorn backend.main:app'"),
        "Docker Containers": run_command("docker ps"),
        "PostgreSQL Status": run_command("sudo systemctl status postgresql"),
        "NVIDIA GPU Status": run_command("nvidia-smi"),
    }
    return services

def check_backend():
    """Έλεγχος backend και connectors."""
    print("\n[2] Έλεγχος Backend...")
    backend = {
        "FastAPI": run_command("uvicorn backend.main:app --reload & sleep 2 && curl -s http://localhost:5000/docs | grep 'OpenAPI'"),
        "Database Connection": run_command("python backend/database_verification.py"),
        "AI Engine Debug": run_command("python backend/ai_engine.py --debug"),
        "Mining Connector": run_command("python backend/connectors/mining_connector.py --test"),
        "Energy Connector": run_command("python backend/connectors/energy_connector.py --test"),
    }
    return backend

def check_frontend():
    """Έλεγχος frontend και συνδεσιμότητας."""
    print("\n[3] Έλεγχος Frontend...")
    frontend = {
        "Starting Frontend": run_command("cd frontend && npm run serve & sleep 2"),
        "Checking API Connection": run_command("curl -s http://localhost:5000/api/status"),
    }
    return frontend

def check_logs():
    """Έλεγχος logs και debugging mode."""
    print("\n[4] Logs & Debug Mode...")
    logs = {
        "Last 10 AI Engine Logs": run_command("tail -n 10 logs/ai_engine.log"),
    }
    if os.getenv("DEBUG") != "true":
        logs["DEBUG Mode"] = "Ενεργοποίηση DEBUG Mode..."
        os.environ["DEBUG"] = "true"
    return logs

def generate_report():
    """Συλλογή και αποθήκευση των αποτελεσμάτων."""
    report = {
        "system_info": check_system_info(),
        "services": check_services(),
        "backend": check_backend(),
        "frontend": check_frontend(),
        "logs": check_logs()
    }
    output_file = f"diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📝 Αναφορά αποθηκεύτηκε στο: {os.path.abspath(output_file)}")
    return report

def main():
    """Εκτέλεση όλων των ελέγχων."""
    print("=== AI Mining Assistant Diagnostic Tool ===")
    print(f"Ημερομηνία/Ώρα: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Τρέχων φάκελος: {os.getcwd()}")
    print("=" * 45 + "\n")
    generate_report()
    print("\n✅ Debugging Ολοκληρώθηκε!")

if __name__ == "__main__":
    main()
