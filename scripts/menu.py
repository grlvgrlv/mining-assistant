#!/usr/bin/env python3
"""
Μενού επιλογής scripts για το AI Mining Assistant
Αυτόματα εντοπίζει τα διαθέσιμα scripts στον φάκελο scripts 
και παρέχει επιλογές για την εκτέλεσή τους.
"""
import os
import sys
import glob
import subprocess
import time
from datetime import datetime

def clear_screen():
    """Καθαρίζει την οθόνη του τερματικού"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Εκτυπώνει την κεφαλίδα του μενού"""
    clear_screen()
    print("\033[1;36m═════════════════════════════════════════════\033[0m")
    print("\033[1;36m        AI MINING ASSISTANT - MENU            \033[0m")
    print("\033[1;36m═════════════════════════════════════════════\033[0m")
    print(f"Ημερομηνία/Ώρα: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def get_script_description(script_path):
    """Εξάγει την περιγραφή από ένα script Python"""
    description = ""
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            # Εύρεση του docstring πολλαπλών γραμμών
            docstring_start = -1
            for i, line in enumerate(lines):
                if line.strip().startswith('"""') or line.strip().startswith("'''"):
                    docstring_start = i
                    break
            
            # Αν βρέθηκε docstring πολλαπλών γραμμών
            if docstring_start >= 0 and docstring_start + 1 < len(lines):
                # Χρησιμοποιούμε την πρώτη ουσιαστική γραμμή του docstring (συνήθως την 3η του αρχείου)
                next_line = lines[docstring_start + 1].strip()
                if next_line:  # Αν δεν είναι κενή γραμμή
                    description = next_line
            
            # Αν δεν βρέθηκε περιγραφή με την παραπάνω μέθοδο
            if not description:
                # Προσπαθούμε να βρούμε οποιαδήποτε γραμμή σχολίου
                for line in lines:
                    line = line.strip()
                    if line.startswith("#") and not line.startswith("#!"):
                        description = line[1:].strip()
                        break
    except Exception as e:
        description = f"(Αδύνατη η ανάγνωση περιγραφής: {str(e)})"
    
    return description or "(Χωρίς περιγραφή)"

def find_available_scripts(scripts_dir):
    """Βρίσκει όλα τα διαθέσιμα Python scripts στον φάκελο"""
    scripts = []
    
    # Εύρεση όλων των .py αρχείων
    script_paths = glob.glob(os.path.join(scripts_dir, "*.py"))
    
    # Αγνοούμε το τρέχον script (menu.py)
    script_paths = [path for path in script_paths 
                   if os.path.basename(path).lower() != "menu.py"]
    
    # Συλλογή πληροφοριών για κάθε script
    for path in script_paths:
        name = os.path.basename(path)
        description = get_script_description(path)
        scripts.append({"name": name, "path": path, "description": description})
    
    # Ταξινόμηση των scripts αλφαβητικά
    scripts.sort(key=lambda x: x["name"])
    return scripts

def run_script(script_path, additional_args=None):
    """Εκτελεί ένα Python script"""
    command = [sys.executable, script_path]
    if additional_args:
        command.extend(additional_args)
    
    try:
        # Εκτελούμε το script και περιμένουμε να ολοκληρωθεί
        process = subprocess.Popen(command)
        process.wait()
        return process.returncode == 0
    except Exception as e:
        print(f"\033[1;31mΣφάλμα κατά την εκτέλεση του script: {e}\033[0m")
        return False

def run_institutional_memory_refresh(scripts_dir, project_base_path):
    """
    Εκτελεί τα scripts με συγκεκριμένη σειρά για ανανέωση institutional memory:
    1. debug_tools.py
    2. system_requirements.py
    3. status.py
    4. collect_code.py
    """
    scripts_to_run = ["debug_tools.py", "system_requirements.py", "status.py", "collect_code.py"]
    success = True
    
    print_header()
    print("\033[1;33m=== Εκτέλεση Institutional Memory Refresh ===\033[0m\n")
    
    # Εκτέλεση των scripts με τη σειρά
    for script_name in scripts_to_run:
        script_path = os.path.join(scripts_dir, script_name)
        
        if not os.path.exists(script_path):
            print(f"\033[1;31mΤο script {script_name} δεν βρέθηκε!\033[0m")
            success = False
            continue
        
        print(f"\033[1;36m>> Εκτέλεση {script_name}...\033[0m\n")
        
        if not run_script(script_path):
            print(f"\033[1;31mΗ εκτέλεση του {script_name} απέτυχε!\033[0m")
            success = False
        
        print(f"\n\033[1;32m>> Το {script_name} ολοκληρώθηκε\033[0m")
        print("\033[1;36m------------------------------------------\033[0m")
    
    # Έλεγχος του status του project progress
    logs_dir = os.path.join(project_base_path, "logs")
    progress_file = os.path.join(logs_dir, ".project_progress.json")
    
    print("\n\033[1;33m=== Σύνοψη ===\033[0m")
    
    try:
        if os.path.exists(progress_file):
            import json
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
            
            # Υπολογισμός συνολικής προόδου
            total_progress = 0
            for phase, phase_data in progress_data.items():
                phase_completed_steps = sum(1 for step in phase_data["steps"] if step["status"] == "completed")
                phase_in_progress_steps = sum(1 for step in phase_data["steps"] if step["status"] == "in_progress")
                phase_total_steps = len(phase_data["steps"])
                
                # Completed steps count fully, in-progress steps count half
                phase_progress = (phase_completed_steps + 0.5 * phase_in_progress_steps) / phase_total_steps * phase_data["weight"]
                total_progress += phase_progress
            
            print(f"\033[1;32mΣυνολική πρόοδος έργου: {total_progress*100:.2f}%\033[0m")
        else:
            print("\033[1;31mΤο αρχείο προόδου δεν βρέθηκε!\033[0m")
    except Exception as e:
        print(f"\033[1;31mΣφάλμα κατά τον έλεγχο της προόδου: {e}\033[0m")
    
    # Έλεγχος στοιχείων institutional memory
    try:
        json_files = glob.glob(os.path.join(logs_dir, "institutional_memory_*.json"))
        
        if json_files:
            # Βρίσκουμε το πιο πρόσφατο αρχείο
            latest_file = max(json_files, key=os.path.getmtime)
            file_size = os.path.getsize(latest_file) / 1024  # KB
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                item_count = len(data)
            
            print(f"\033[1;32mInstitutional Memory: {os.path.basename(latest_file)}\033[0m")
            print(f"  - Συνολικά στοιχεία: {item_count}")
            print(f"  - Μέγεθος αρχείου: {file_size:.2f} KB")
            
            # Βρίσκουμε το προηγούμενο αρχείο αν υπάρχει
            previous_files = [f for f in json_files if f != latest_file]
            
            if previous_files:
                previous_file = max(previous_files, key=os.path.getmtime)
                prev_size = os.path.getsize(previous_file) / 1024  # KB
                
                with open(previous_file, 'r', encoding='utf-8') as f:
                    prev_data = json.load(f)
                    prev_item_count = len(prev_data)
                
                size_diff = file_size - prev_size
                item_diff = item_count - prev_item_count
                
                print(f"  - Σύγκριση με προηγούμενο ({os.path.basename(previous_file)}):")
                print(f"    * Διαφορά στοιχείων: {'+' if item_diff>=0 else ''}{item_diff}")
                print(f"    * Διαφορά μεγέθους: {'+' if size_diff>=0 else ''}{size_diff:.2f} KB")
        else:
            print("\033[1;31mΔεν βρέθηκαν αρχεία institutional memory!\033[0m")
    except Exception as e:
        print(f"\033[1;31mΣφάλμα κατά τον έλεγχο του institutional memory: {e}\033[0m")
    
    print("\n\033[1;36m------------------------------------------\033[0m")
    
    if success:
        print("\033[1;32mΗ ανανέωση του Institutional Memory ολοκληρώθηκε επιτυχώς!\033[0m")
    else:
        print("\033[1;31mΗ ανανέωση του Institutional Memory ολοκληρώθηκε με σφάλματα.\033[0m")
    
    input("\nΠατήστε Enter για να επιστρέψετε στο κύριο μενού...")

def display_menu_and_get_choice(scripts):
    """Εμφανίζει το μενού και επιστρέφει την επιλογή του χρήστη"""
    print_header()
    
    # Εμφάνιση των διαθέσιμων scripts
    print("\033[1;33m=== Διαθέσιμα Scripts ===\033[0m\n")
    for i, script in enumerate(scripts, 1):
        print(f"\033[1;36m{i}.\033[0m \033[1m{script['name']}\033[0m")
        print(f"   {script['description']}")
        print()
    
    # Προσθήκη της επιλογής για Institutional Memory Refresh
    special_option = len(scripts) + 1
    print(f"\033[1;32m{special_option}. Institutional Memory Refresh\033[0m")
    print("   Εκτελεί όλα τα βασικά scripts για ανανέωση του institutional memory")
    print()
    
    # Προσθήκη επιλογής εξόδου
    exit_option = special_option + 1
    print(f"\033[1;31m{exit_option}. Έξοδος\033[0m")
    print()
    
    # Λήψη επιλογής από τον χρήστη
    while True:
        try:
            choice = input("Επιλέξτε ένα script (1-{}): ".format(exit_option))
            choice = int(choice)
            
            if 1 <= choice <= len(scripts):
                return {"type": "script", "index": choice - 1}
            elif choice == special_option:
                return {"type": "refresh"}
            elif choice == exit_option:
                return {"type": "exit"}
            else:
                print("\033[1;31mΜη έγκυρη επιλογή. Παρακαλώ επιλέξτε έναν αριθμό από το 1 έως το {}.\033[0m".format(exit_option))
        except ValueError:
            print("\033[1;31mΠαρακαλώ εισάγετε έναν αριθμό.\033[0m")

def main():
    # Βρίσκουμε την διαδρομή του script
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    
    # Υπολογίζουμε το project_base_path
    if os.path.basename(script_dir) == "scripts":
        # Αν το script είναι στον φάκελο scripts, το project_base_path είναι ο γονικός φάκελος
        project_base_path = os.path.dirname(script_dir)
    else:
        # Αλλιώς, υποθέτουμε ότι το script είναι στο project root
        project_base_path = os.path.expanduser("~/mining-assistant")
        script_dir = os.path.join(project_base_path, "scripts")
    
    # Εύρεση διαθέσιμων scripts
    scripts = find_available_scripts(script_dir)
    
    if not scripts:
        print("\033[1;31mΔεν βρέθηκαν διαθέσιμα scripts στο φάκελο {}.\033[0m".format(script_dir))
        return
    
    while True:
        # Εμφάνιση μενού και λήψη επιλογής
        choice = display_menu_and_get_choice(scripts)
        
        if choice["type"] == "exit":
            print_header()
            print("\033[1;33mΈξοδος από το μενού. Αντίο!\033[0m")
            break
        elif choice["type"] == "refresh":
            run_institutional_memory_refresh(script_dir, project_base_path)
        elif choice["type"] == "script":
            script = scripts[choice["index"]]
            print_header()
            print("\033[1;33mΕκτέλεση του script: {}\033[0m".format(script["name"]))
            print("Περιγραφή: {}".format(script["description"]))
            print("\033[1;36m------------------------------------------\033[0m\n")
            
            run_script(script["path"])
            
            print("\n\033[1;32mΤο script ολοκληρώθηκε.\033[0m")
            input("\nΠατήστε Enter για να επιστρέψετε στο μενού...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[1;33mΔιακοπή από τον χρήστη. Αντίο!\033[0m")
    except Exception as e:
        print(f"\n\033[1;31mΑπροσδόκητο σφάλμα: {e}\033[0m")
