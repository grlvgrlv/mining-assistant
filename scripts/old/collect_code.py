#!/usr/bin/env python3
"""
Εργαλείο συλλογής κώδικα για το AI Mining Assistant
Συλλέγει όλα τα σημαντικά αρχεία του έργου και τα αποθηκεύει σε ένα ενιαίο αρχείο
για διατήρηση της θεσμικής μνήμης και ανάλυση.
"""
import os
import json
import glob
from datetime import datetime

def collect_code(root_dir, output_file, log_file, processed_file, missing_file, json_file, logs_dir):
    """
    Συλλέγει όλα τα σημαντικά αρχεία του έργου
    
    Args:
        root_dir: Η βασική διαδρομή του έργου
        output_file: Το αρχείο εξόδου για το πλήρες κείμενο
        log_file: Το αρχείο καταγραφής για τα παραλειπόμενα αρχεία
        processed_file: Το αρχείο καταγραφής για τα επεξεργασμένα αρχεία
        missing_file: Το αρχείο καταγραφής για τα αρχεία που λείπουν
        json_file: Το αρχείο εξόδου για τα δεδομένα JSON
        logs_dir: Η διαδρομή του φακέλου logs για εξαίρεση
    """
    print("Εκκίνηση συλλογής κώδικα για institutional memory...")
    
    supported_extensions = [".py", ".sh", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".md", ".log", ".txt"]
    excluded_dirs = {"venv", "node_modules", "__pycache__", ".git"}
    excluded_files = {".gitignore", "README", "old", "copy", "skipped_files", "processed_files", "missing_files"}

    # Ρητά συμπεριλαμβανόμενα αρχεία από τον φάκελο logs
    include_patterns = [
        os.path.join(logs_dir, "system_check_results.json"),    # Σταθερό όνομα
        os.path.join(logs_dir, "diagnostic_report_*.json"),     # Μεταβλητό όνομα με timestamp
        os.path.join(logs_dir, ".project_progress.json")        # Αρχείο προόδου
    ]

    # Χρησιμοποιούμε το glob για να βρούμε τα ρητά συμπεριλαμβανόμενα αρχεία
    include_files = set()
    for pattern in include_patterns:
        for file in glob.glob(pattern):
            include_files.add(file)
    
    print(f"Ρητά συμπεριλαμβανόμενα αρχεία από logs: {len(include_files)}")
    for file in include_files:
        print(f"  - {os.path.basename(file)}")

    max_file_size_mb = 10
    
    # Συλλογή όλων των αρχείων και ρητή παράλειψη του φακέλου logs
    all_files = set()
    for root, dirs, files in os.walk(root_dir):
        # Παράλειψη εξαιρούμενων καταλόγων τροποποιώντας το dirs επί τόπου
        dirs[:] = [d for d in dirs if d not in excluded_dirs and os.path.join(root, d) != logs_dir]
        
        for file in files:
            file_path = os.path.join(root, file)
            if not any(excluded in file for excluded in excluded_files):
                all_files.add(file_path)
    
    # Επιπλέον φιλτράρισμα για τον κατάλογο logs (διπλός έλεγχος)
    all_files = {f for f in all_files if not f.startswith(logs_dir)}
    
    # Προσθήκη των ρητά συμπεριλαμβανόμενων αρχείων
    all_files.update(include_files)

    processed_files = set()
    skipped_files = []
    json_data = []

    # Προσθήκη καταχωρήσεων καταγραφής
    print(f"Συνολικά αρχεία που βρέθηκαν πριν το φιλτράρισμα: {len(all_files)}")
    print(f"Ο κατάλογος logs που εξαιρείται: {logs_dir}")

    with open(output_file, "w", encoding="utf-8") as outfile, open(log_file, "w", encoding="utf-8") as log, open(processed_file, "w", encoding="utf-8") as processed:
        outfile.write("# AI Mining Assistant - Institutional Memory\n")
        log.write("# Skipped Files Log\n")
        processed.write("# Processed Files Log\n")

        for file_path in sorted(all_files):
            root = os.path.dirname(file_path)
            file = os.path.basename(file_path)

            # Παράλειψη των αρχείων εξόδου
            if file_path in {output_file, log_file, processed_file, missing_file, json_file}:
                continue
                
            # Παράλειψη των αρχείων στον κατάλογο logs εκτός από τα ρητά συμπεριλαμβανόμενα
            if logs_dir in file_path and file_path not in include_files:
                skipped_files.append(f"{file_path} - Αρχείο σε κατάλογο logs")
                continue

            # Έλεγχος μεγέθους αρχείου
            if os.path.getsize(file_path) > max_file_size_mb * 1024 * 1024:
                skipped_files.append(f"{file_path} - Μέγεθος αρχείου μεγαλύτερο από {max_file_size_mb}MB")
                continue

            if file.endswith(".env") or any(file.endswith(ext) for ext in supported_extensions) or file_path in include_files:
                processed_files.add(file_path)
                file_content = ""
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as infile:
                        file_content = infile.read()
                    outfile.write(f"\n# === File: {file_path} ===\n")
                    outfile.write(f"# Path: {root}\n\n{file_content}\n\n")
                    json_data.append({"file_path": file_path, "content": file_content})
                except Exception as e:
                    skipped_files.append(f"{file_path} - Σφάλμα ανάγνωσης: {e}")

        for skipped in skipped_files:
            log.write(skipped + "\n")
        for processed_path in processed_files:
            processed.write(processed_path + "\n")

    with open(json_file, "w", encoding="utf-8") as jfile:
        json.dump(json_data, jfile, ensure_ascii=False, indent=4)

    missing_files = sorted(all_files - processed_files)
    with open(missing_file, "w", encoding="utf-8") as missing:
        missing.write("# Missing Files Log\n")
        for missing_file_path in missing_files:
            missing.write(missing_file_path + "\n")
    
    # Εμφάνιση των αρχείων που λείπουν στο terminal
    if missing_files:
        print("\nΛίστα αρχείων που λείπουν:")
        for missing_file_path in missing_files:
            print(f"  - {missing_file_path}")
    
    # Συγκρίνουμε με το προηγούμενο αρχείο institutional memory αν υπάρχει
    previous_json_files = [f for f in glob.glob(os.path.join(logs_dir, "institutional_memory_*.json")) 
                         if f != json_file]
    
    if previous_json_files:
        # Βρίσκουμε το πιο πρόσφατο προηγούμενο αρχείο
        previous_json_file = max(previous_json_files, key=os.path.getmtime)
        prev_size = os.path.getsize(previous_json_file)
        curr_size = os.path.getsize(json_file)
        
        try:
            with open(previous_json_file, 'r', encoding='utf-8') as f:
                prev_data = json.load(f)
                prev_items = len(prev_data)
                curr_items = len(json_data)
                
                size_diff = curr_size - prev_size
                items_diff = curr_items - prev_items
                
                print(f"\nΣύγκριση με προηγούμενο institutional memory:")
                print(f"  Προηγούμενο: {os.path.basename(previous_json_file)}")
                print(f"    - Στοιχεία: {prev_items}")
                print(f"    - Μέγεθος: {prev_size / 1024:.2f} KB")
                print(f"  Τρέχον: {os.path.basename(json_file)}")
                print(f"    - Στοιχεία: {curr_items} ({'+' if items_diff>=0 else ''}{items_diff})")
                print(f"    - Μέγεθος: {curr_size / 1024:.2f} KB ({'+' if size_diff>=0 else ''}{size_diff / 1024:.2f} KB)")
        except Exception as e:
            print(f"Σφάλμα κατά τη σύγκριση με το προηγούμενο αρχείο: {e}")
            
    print(f"\nΣτατιστικά institutional memory:")
    print(f"Αρχεία που επεξεργάστηκαν: {len(processed_files)}")
    print(f"Αρχεία που παραλείφθηκαν: {len(skipped_files)}")
    print(f"Αρχεία που λείπουν: {len(missing_files)}")
    print(f"Συνολικά αρχεία στο JSON: {len(json_data)}")
    print(f"Μέγεθος αρχείου JSON: {os.path.getsize(json_file) / 1024:.2f} KB")
    print(f"Το institutional memory αποθηκεύτηκε στο: {output_file}")
    print(f"Το αρχείο JSON αποθηκεύτηκε στο: {json_file}")
    print("Συλλογή κώδικα ολοκληρώθηκε επιτυχώς")

if __name__ == "__main__":
    # Ορισμός διαδρομών
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    
    # Υπολογίζουμε το project_base_path
    if os.path.basename(script_dir) == "scripts":
        # Αν το script είναι στον φάκελο scripts, το project_base_path είναι ο γονικός φάκελος
        project_base_path = os.path.dirname(script_dir)
    else:
        # Αλλιώς, υποθέτουμε ότι το script είναι στο project root
        project_base_path = os.path.expanduser("~/mining-assistant")
    
    print(f"Script path: {script_path}")
    print(f"Script directory: {script_dir}")
    print(f"Project base path: {project_base_path}")
    
    # Καθορισμός του φακέλου logs
    LOGS_DIR = os.path.join(project_base_path, "logs")
    
    # Δημιουργία του καταλόγου logs αν δεν υπάρχει
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Δημιουργία χρονικής σήμανσης για τα ονόματα αρχείων
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Ορισμός αρχείων εξόδου
    OUTPUT_FILE = os.path.join(LOGS_DIR, f"institutional_memory_{timestamp}.txt")
    LOG_FILE = os.path.join(LOGS_DIR, f"skipped_files_{timestamp}.log")
    PROCESSED_FILE = os.path.join(LOGS_DIR, f"processed_files_{timestamp}.log")
    MISSING_FILE = os.path.join(LOGS_DIR, f"missing_files_{timestamp}.log")
    JSON_FILE = os.path.join(LOGS_DIR, f"institutional_memory_{timestamp}.json")
    
    # Εκτέλεση της συλλογής κώδικα
    collect_code(project_base_path, OUTPUT_FILE, LOG_FILE, PROCESSED_FILE, MISSING_FILE, JSON_FILE, LOGS_DIR)
