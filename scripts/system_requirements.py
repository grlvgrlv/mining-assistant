#!/usr/bin/env python3
"""
Εργαλείο Ελέγχου Συστημικών Απαιτήσεων για το AI Mining Assistant

Το script πραγματοποιεί έναν ολοκληρωμένο έλεγχο των προαπαιτούμενων συστήματος 
για την εγκατάσταση και λειτουργία του AI Mining Assistant. 

Βασικοί έλεγχοι:
1. Έκδοση Python (απαίτηση: 3.9+)
2. Διαθέσιμη RAM (απαίτηση: 16GB+)
3. GPU και CUDA συμβατότητα (απαίτηση: NVIDIA GPU με 6GB+ VRAM, CUDA 11.7+)
4. Έκδοση Node.js (απαίτηση: 16+)
5. Διαθέσιμος χώρος δίσκου (απαίτηση: 20GB+)
6. Εγκατεστημένα Python πακέτα

Επιπλέον λειτουργίες:
- Χρωματιστή εκτύπωση αποτελεσμάτων ελέγχου
- Δυνατότητα αυτόματης εγκατάστασης λειπόντων πακέτων
- Αποθήκευση αποτελεσμάτων σε JSON για περαιτέρω ανάλυση

Χρήση:
- Με το όρισμα 'check': Έλεγχος συστημικών απαιτήσεων
- Με το όρισμα 'install': Αυτόματη εγκατάσταση λειπόντων πακέτων
"""

# Υπόλοιπος κώδικας παραμένει ο ίδιος
import sys
import platform
import subprocess
import shutil
import os
import re
import argparse
import json
from typing import Dict, List, Tuple, Optional

class ColorPrint:
    """Κλάση για χρωματισμένη εκτύπωση στο τερματικό."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'
    
    @staticmethod
    def green(text: str) -> str:
        return f"{ColorPrint.GREEN}{text}{ColorPrint.END}"
    
    @staticmethod
    def yellow(text: str) -> str:
        return f"{ColorPrint.YELLOW}{text}{ColorPrint.END}"
    
    @staticmethod
    def red(text: str) -> str:
        return f"{ColorPrint.RED}{text}{ColorPrint.END}"
    
    @staticmethod
    def bold(text: str) -> str:
        return f"{ColorPrint.BOLD}{text}{ColorPrint.END}"

def check_python_version() -> Tuple[bool, str]:
    """Έλεγχος έκδοσης Python. Απαιτείται 3.9+."""
    version = platform.python_version()
    version_info = sys.version_info
    
    if version_info.major >= 3 and version_info.minor >= 9:
        return True, f"Python {version} ✓"
    else:
        return False, f"Python {version} ✗ (απαιτείται 3.9+)"

def check_ram() -> Tuple[bool, str]:
    """Έλεγχος μνήμης RAM. Απαιτούνται τουλάχιστον 16GB."""
    try:
        if platform.system() == "Linux":
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemTotal' in line:
                        # Μετατροπή από KB σε GB
                        total_ram = int(line.split()[1]) / (1024 * 1024)
                        break
        elif platform.system() == "Darwin":  # macOS
            output = subprocess.check_output(['sysctl', '-n', 'hw.memsize']).decode('utf-8').strip()
            total_ram = int(output) / (1024 * 1024 * 1024)
        elif platform.system() == "Windows":
            output = subprocess.check_output(['wmic', 'computersystem', 'get', 'totalphysicalmemory']).decode('utf-8')
            total_ram = int(output.strip().split('\n')[1]) / (1024 * 1024 * 1024)
        else:
            return False, "Μη υποστηριζόμενο λειτουργικό σύστημα"
        
        if total_ram >= 16:
            return True, f"RAM {total_ram:.2f}GB ✓"
        else:
            return False, f"RAM {total_ram:.2f}GB ✗ (απαιτούνται 16GB+)"
    except Exception as e:
        return False, f"Δεν ήταν δυνατός ο έλεγχος RAM: {str(e)}"

def check_gpu() -> Tuple[bool, str, Dict]:
    """Έλεγχος GPU. Απαιτείται NVIDIA GPU με τουλάχιστον 6GB VRAM."""
    gpu_info = {}
    
    try:
        if shutil.which('nvidia-smi'):
            output = subprocess.check_output(['nvidia-smi', '--query-gpu=name,memory.total,driver_version',
                                             '--format=csv,noheader,nounits']).decode('utf-8')
            gpus = []
            
            for line in output.strip().split('\n'):
                parts = line.split(', ')
                if len(parts) >= 3:
                    name = parts[0]
                    # Μετατροπή από MiB σε GB
                    memory = float(parts[1]) / 1024
                    driver = parts[2]
                    
                    gpus.append({
                        "name": name,
                        "memory": memory,
                        "driver": driver
                    })
            
            if gpus:
                gpu_info["gpus"] = gpus
                # Έλεγχος αν οποιαδήποτε GPU έχει τουλάχιστον 6GB VRAM
                has_suitable_gpu = any(gpu["memory"] >= 6 for gpu in gpus)
                
                if has_suitable_gpu:
                    return True, f"GPU {len(gpus)} NVIDIA GPU(s) με επαρκή VRAM ✓", gpu_info
                else:
                    return False, f"GPU(s) διαθέσιμες αλλά χωρίς επαρκή VRAM ✗ (απαιτούνται 6GB+)", gpu_info
            else:
                return False, "Δεν βρέθηκαν NVIDIA GPUs ✗", {}
        else:
            return False, "Το nvidia-smi δεν είναι εγκατεστημένο ✗", {}
    except Exception as e:
        return False, f"Δεν ήταν δυνατός ο έλεγχος GPU: {str(e)}", {}

def check_cuda() -> Tuple[bool, str]:
    """Έλεγχος έκδοσης CUDA. Απαιτείται 11.7+."""
    try:
        # Έλεγχος αν το nvcc είναι εγκατεστημένο
        if shutil.which('nvcc'):
            output = subprocess.check_output(['nvcc', '--version']).decode('utf-8')
            match = re.search(r'release (\d+\.\d+)', output)
            if match:
                version = match.group(1)
                if float(version) >= 11.7:
                    return True, f"CUDA {version} ✓"
                else:
                    return False, f"CUDA {version} ✗ (απαιτείται 11.7+)"
            else:
                return False, "Δεν βρέθηκε έκδοση CUDA ✗"
        else:
            # Εναλλακτικός έλεγχος μέσω nvidia-smi αν το nvcc δεν είναι διαθέσιμο
            if shutil.which('nvidia-smi'):
                output = subprocess.check_output(['nvidia-smi']).decode('utf-8')
                match = re.search(r'CUDA Version: (\d+\.\d+)', output)
                if match:
                    version = match.group(1)
                    if float(version) >= 11.7:
                        return True, f"CUDA {version} ✓"
                    else:
                        return False, f"CUDA {version} ✗ (απαιτείται 11.7+)"
                else:
                    return False, "Δεν βρέθηκε έκδοση CUDA ✗"
            else:
                return False, "Δεν είναι εγκατεστημένο το CUDA ✗"
    except Exception as e:
        return False, f"Δεν ήταν δυνατός ο έλεγχος CUDA: {str(e)}"

def check_nodejs() -> Tuple[bool, str]:
    """Έλεγχος έκδοσης Node.js. Απαιτείται 16+."""
    try:
        if shutil.which('node'):
            output = subprocess.check_output(['node', '--version']).decode('utf-8').strip()
            # Αφαίρεση του 'v' από την αρχή της έκδοσης, π.χ. 'v16.14.0' -> '16.14.0'
            if output.startswith('v'):
                output = output[1:]
            
            version_parts = output.split('.')
            major_version = int(version_parts[0])
            
            if major_version >= 16:
                return True, f"Node.js {output} ✓"
            else:
                return False, f"Node.js {output} ✗ (απαιτείται 16+)"
        else:
            return False, "Το Node.js δεν είναι εγκατεστημένο ✗"
    except Exception as e:
        return False, f"Δεν ήταν δυνατός ο έλεγχος Node.js: {str(e)}"

def check_disk_space(required_gb: int = 20) -> Tuple[bool, str]:
    """Έλεγχος διαθέσιμου χώρου στο δίσκο. Απαιτούνται τουλάχιστον 20GB."""
    try:
        if platform.system() == "Windows":
            # Έλεγχος στον τρέχοντα δίσκο
            free_bytes = shutil.disk_usage('.').free
        else:
            # Για Linux/macOS
            free_bytes = shutil.disk_usage('.').free
        
        free_gb = free_bytes / (1024 * 1024 * 1024)
        
        if free_gb >= required_gb:
            return True, f"Χώρος δίσκου {free_gb:.2f}GB ελεύθερος ✓"
        else:
            return False, f"Χώρος δίσκου {free_gb:.2f}GB ✗ (απαιτούνται {required_gb}GB+)"
    except Exception as e:
        return False, f"Δεν ήταν δυνατός ο έλεγχος χώρου δίσκου: {str(e)}"

def check_python_packages() -> Tuple[bool, List[str]]:
    """Έλεγχος απαραίτητων πακέτων Python."""
    required_packages = [
        "fastapi", "uvicorn", "sqlalchemy", "pydantic",
        "torch", "transformers", "peft", "httpx", "redis",
        "python-telegram-bot"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages

def install_missing_packages(packages: List[str]) -> bool:
    """Εγκατάσταση των πακέτων που λείπουν."""
    if not packages:
        return True
    
    print(f"\nΕγκατάσταση των πακέτων που λείπουν: {', '.join(packages)}")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("Εκκίνηση του system_requirements.py...")
    parser = argparse.ArgumentParser(description="Έλεγχος προαπαιτούμενων συστήματος για το AI Mining Assistant")
    parser.add_argument('action', choices=['check', 'install'], nargs='?', default='check',
                        help="'check' για έλεγχο προαπαιτούμενων, 'install' για εγκατάσταση των πακέτων που λείπουν")
    
    args = parser.parse_args()
    
    # Ορισμός των διαδρομών με διαχείριση σφαλμάτων
    try:
        script_path = os.path.abspath(__file__)
        print(f"Script path: {script_path}")
        
        script_dir = os.path.dirname(script_path)
        print(f"Script directory: {script_dir}")
        
        project_base_path = os.path.dirname(script_dir) if os.path.basename(script_dir) == "scripts" else os.path.dirname(os.path.dirname(script_path))
        print(f"Project base path: {project_base_path}")
        
        logs_dir = os.path.join(project_base_path, "logs")
        print(f"Logs directory: {logs_dir}")

        # Δημιουργία του καταλόγου logs αν δεν υπάρχει
        try:
            os.makedirs(logs_dir, exist_ok=True)
            print(f"Logs directory created/exists: {logs_dir}")
        except Exception as e:
            print(f"Σφάλμα δημιουργίας logs directory: {e}")
            logs_dir = os.getcwd()  # Fallback στο τρέχον directory
            print(f"Χρήση τρέχοντος καταλόγου: {logs_dir}")
    except Exception as e:
        print(f"Σφάλμα υπολογισμού διαδρομών: {e}")
        logs_dir = os.getcwd()  # Fallback στο τρέχον directory
        print(f"Χρήση τρέχοντος καταλόγου: {logs_dir}")
    
    print(ColorPrint.bold("\n=== Έλεγχος Προαπαιτούμενων Συστήματος ===\n"))
    
    # Έλεγχος βασικών προαπαιτούμενων
    python_ok, python_msg = check_python_version()
    ram_ok, ram_msg = check_ram()
    gpu_ok, gpu_msg, gpu_info = check_gpu()
    cuda_ok, cuda_msg = check_cuda()
    nodejs_ok, nodejs_msg = check_nodejs()
    disk_ok, disk_msg = check_disk_space()
    
    # Εκτύπωση αποτελεσμάτων
    print(f"• {ColorPrint.green(python_msg) if python_ok else ColorPrint.red(python_msg)}")
    print(f"• {ColorPrint.green(ram_msg) if ram_ok else ColorPrint.red(ram_msg)}")
    print(f"• {ColorPrint.green(gpu_msg) if gpu_ok else ColorPrint.red(gpu_msg)}")
    print(f"• {ColorPrint.green(cuda_msg) if cuda_ok else ColorPrint.red(cuda_msg)}")
    print(f"• {ColorPrint.green(nodejs_msg) if nodejs_ok else ColorPrint.red(nodejs_msg)}")
    print(f"• {ColorPrint.green(disk_msg) if disk_ok else ColorPrint.red(disk_msg)}")
    
    # Αναλυτικές πληροφορίες GPU
    if gpu_info and "gpus" in gpu_info:
        print("\nΛεπτομέρειες GPU:")
        for i, gpu in enumerate(gpu_info["gpus"]):
            print(f"  {i+1}. {gpu['name']} - {gpu['memory']:.2f}GB VRAM - Driver {gpu['driver']}")
    
    # Έλεγχος πακέτων Python
    packages_ok, missing_packages = check_python_packages()
    
    if packages_ok:
        print(f"\n• {ColorPrint.green('Όλα τα απαραίτητα πακέτα Python είναι εγκατεστημένα ✓')}")
    else:
        print(f"\n• {ColorPrint.red('Λείπουν τα εξής πακέτα Python: ' + ', '.join(missing_packages) + ' ✗')}")
        
        if args.action == 'install':
            if install_missing_packages(missing_packages):
                print(f"\n{ColorPrint.green('Η εγκατάσταση των πακέτων ολοκληρώθηκε επιτυχώς!')}")
            else:
                print(f"\n{ColorPrint.red('Παρουσιάστηκε σφάλμα κατά την εγκατάσταση των πακέτων.')}")
    
    # Συνολική αξιολόγηση
    all_ok = python_ok and ram_ok and gpu_ok and cuda_ok and nodejs_ok and disk_ok and packages_ok
    
    if all_ok:
        print(f"\n{ColorPrint.green('✓ Όλα τα προαπαιτούμενα πληρούνται!')}")
        print(f"{ColorPrint.green('✓ Το σύστημά σας είναι έτοιμο για την εγκατάσταση του AI Mining Assistant.')}")
    else:
        print(f"\n{ColorPrint.yellow('⚠ Κάποια προαπαιτούμενα δεν πληρούνται.')}")
        print(f"{ColorPrint.yellow('⚠ Παρακαλώ διορθώστε τα σημειωμένα προβλήματα και επανεκτελέστε τον έλεγχο.')}")
    
    # Εξαγωγή αποτελεσμάτων σε αρχείο JSON
    results = {
        "python_version": {
            "ok": python_ok,
            "message": python_msg
        },
        "ram": {
            "ok": ram_ok,
            "message": ram_msg
        },
        "gpu": {
            "ok": gpu_ok,
            "message": gpu_msg,
            "details": gpu_info
        },
        "cuda": {
            "ok": cuda_ok,
            "message": cuda_msg
        },
        "nodejs": {
            "ok": nodejs_ok,
            "message": nodejs_msg
        },
        "disk_space": {
            "ok": disk_ok,
            "message": disk_msg
        },
        "python_packages": {
            "ok": packages_ok,
            "missing": missing_packages
        },
        "all_requirements_met": all_ok
    }
    
    # Αποθήκευση αρχείου με διαχείριση σφαλμάτων
    try:
        # Αποθήκευση στο φάκελο logs
        output_file = os.path.join(logs_dir, 'system_check_results.json')
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nΤα αποτελέσματα του ελέγχου αποθηκεύτηκαν στο αρχείο '{output_file}'")
    except Exception as e:
        print(f"Σφάλμα αποθήκευσης αρχείου στο logs: {e}")
        try:
            # Fallback στο τρέχον directory
            output_file = 'system_check_results.json'
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nΤα αποτελέσματα του ελέγχου αποθηκεύτηκαν στο αρχείο '{output_file}'")
        except Exception as e2:
            print(f"Σφάλμα αποθήκευσης και στο τρέχον directory: {e2}")
    
    print("Τέλος εκτέλεσης system_requirements.py")
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
