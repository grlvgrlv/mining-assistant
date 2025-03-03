#!/usr/bin/env python3
"""
Αναβαθμισμένο μενού επιλογής scripts για το AI Mining Assistant
Υποστηρίζει ιεραρχική οργάνωση scripts σε κατηγορίες και υποκατηγορίες
"""
import os
import sys
import glob
import subprocess
import time
import platform
import shutil
from datetime import datetime

# Χρώματα για τερματικό
COLOR_RESET = "\033[0m"
COLOR_BLUE = "\033[1;36m"
COLOR_GREEN = "\033[1;32m"
COLOR_YELLOW = "\033[1;33m"
COLOR_RED = "\033[1;31m"
COLOR_BOLD = "\033[1m"

class Script:
    """Κλάση που αναπαριστά ένα script με τις πληροφορίες του"""
    def __init__(self, name, path, description, categories=None):
        self.name = name
        self.path = path
        self.description = description
        self.categories = categories or []

def clear_screen():
    """Καθαρίζει την οθόνη του τερματικού"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title="AI MINING ASSISTANT - MENU"):
    """Εκτυπώνει την κεφαλίδα του μενού"""
    clear_screen()
    print(f"{COLOR_BLUE}═════════════════════════════════════════════{COLOR_RESET}")
    print(f"{COLOR_BLUE}        {title}            {COLOR_RESET}")
    print(f"{COLOR_BLUE}═════════════════════════════════════════════{COLOR_RESET}")
    print(f"Ημερομηνία/Ώρα: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def get_script_description(script_path):
    """Εξάγει την περιγραφή από ένα script"""
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
                # Χρησιμοποιούμε την πρώτη ουσιαστική γραμμή του docstring
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

def find_available_scripts(project_base_path):
    """Βρίσκει όλα τα διαθέσιμα scripts και τα οργανώνει σε κατηγορίες"""
    scripts = []
    
    # Ορισμός των κατηγοριών για κάθε script (χειροκίνητη αντιστοίχιση)
    script_categories = {
        "collect_code.py": ["Development Tools"],
        "debug_tools.py": ["Development Tools"],
        "fix-project.sh": ["Development Tools", "Problem Solving"],
        "startup-script.sh": ["Startup"],
        "status.py": ["Development Tools"],
        "system_requirements.py": ["Development Tools"],
        "start_dashboard.sh": ["Startup"]  # Το script βρίσκεται στον υποφάκελο dashboard
    }
    
    # Εύρεση scripts στον κύριο φάκελο scripts
    scripts_dir = os.path.join(project_base_path, "scripts")
    script_paths = glob.glob(os.path.join(scripts_dir, "*.py")) + glob.glob(os.path.join(scripts_dir, "*.sh"))
    
    # Εύρεση scripts στον υποφάκελο dashboard
    dashboard_dir = os.path.join(scripts_dir, "dashboard")
    if os.path.exists(dashboard_dir):
        script_paths += glob.glob(os.path.join(dashboard_dir, "*.py")) + glob.glob(os.path.join(dashboard_dir, "*.sh"))
    
    # Αγνοούμε το τρέχον script (menu.py)
    script_paths = [path for path in script_paths 
                   if os.path.basename(path).lower() != "menu.py"]
    
    # Συλλογή πληροφοριών για κάθε script
    for path in script_paths:
        name = os.path.basename(path)
        
        # Διαφορετική λογική για .py και .sh αρχεία
        if path.endswith('.py'):
            description = get_script_description(path)
        else:  # .sh αρχεία
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    # Διάβασε την πρώτη γραμμή σχολίου μετά το shebang
                    lines = f.readlines()
                    description = next((line.strip()[1:].strip() for line in lines 
                                        if line.strip().startswith('#') and not line.strip().startswith('#!')), 
                                       "(Χωρίς περιγραφή)")
            except Exception as e:
                description = f"(Αδύνατη η ανάγνωση περιγραφής: {str(e)})"
        
        # Ορίζουμε τις κατηγορίες για το script
        categories = script_categories.get(name, [])
        
        scripts.append(Script(name, path, description, categories))
    
    return scripts

def get_menu_structure(scripts):
    """Δημιουργεί την ιεραρχική δομή του μενού από τα scripts"""
    # Ορισμός της ιεραρχικής δομής των κατηγοριών
    menu_structure = {
        "Development Tools": {
            "scripts": [],
            "submenus": {
                "Problem Solving": {
                    "scripts": [],
                    "submenus": {}
                }
            }
        },
        "Startup": {
            "scripts": [],
            "submenus": {}
        }
    }
    
    # Κατηγοριοποίηση των scripts βάσει των καθορισμένων κατηγοριών τους
    for script in scripts:
        for category in script.categories:
            if category == "Development Tools" and "Problem Solving" not in script.categories:
                # Μόνο αν δεν ανήκει επίσης στο Problem Solving
                menu_structure["Development Tools"]["scripts"].append(script)
            elif category == "Problem Solving":
                menu_structure["Development Tools"]["submenus"]["Problem Solving"]["scripts"].append(script)
            elif category == "Startup":
                menu_structure["Startup"]["scripts"].append(script)
    
    return menu_structure

def run_script(script_path, additional_args=None):
    """Εκτελεί ένα Python script ή shell script"""
    if script_path.endswith('.py'):
        command = [sys.executable, script_path]
        
        if additional_args:
            command.extend(additional_args)
            
        try:
            # Εκτελούμε το Python script και περιμένουμε να ολοκληρωθεί
            process = subprocess.Popen(command)
            process.wait()
            return process.returncode == 0
        except Exception as e:
            print(f"{COLOR_RED}Σφάλμα κατά την εκτέλεση του script: {e}{COLOR_RESET}")
            return False
    else:  # .sh αρχεία
        # Ελέγχουμε αν είναι το start_dashboard.sh ή οποιοδήποτε script που χρειάζεται νέο τερματικό
        script_name = os.path.basename(script_path)
        if script_name == "start_dashboard.sh" or "dashboard" in script_path:
            # Εκτέλεση σε νέο τερματικό
            terminal_cmd = ""
            if platform.system() == "Linux":
                # Έλεγχος για διαθέσιμα τερματικά
                if shutil.which("gnome-terminal"):
                    terminal_cmd = f"gnome-terminal -- bash -c 'bash {script_path}; echo Press Enter to close...; read'"
                elif shutil.which("xterm"):
                    terminal_cmd = f"xterm -e 'bash {script_path}; echo Press Enter to close...; read'"
                elif shutil.which("konsole"):
                    terminal_cmd = f"konsole -e 'bash {script_path}; echo Press Enter to close...; read'"
                else:
                    print(f"{COLOR_YELLOW}Δεν βρέθηκε υποστηριζόμενο τερματικό. Εκτέλεση στο τρέχον τερματικό...{COLOR_RESET}")
                    terminal_cmd = f"bash {script_path}"
            elif platform.system() == "Darwin":  # macOS
                terminal_cmd = f"open -a Terminal 'bash {script_path}'"
            elif platform.system() == "Windows":
                terminal_cmd = f"start cmd.exe /k bash {script_path}"
            
            try:
                # Εκτέλεση σε νέο τερματικό (χωρίς αναμονή)
                subprocess.Popen(terminal_cmd, shell=True)
                print(f"{COLOR_GREEN}Το dashboard ξεκίνησε σε νέο τερματικό.{COLOR_RESET}")
                return True
            except Exception as e:
                print(f"{COLOR_RED}Σφάλμα κατά την εκτέλεση σε νέο τερματικό: {e}{COLOR_RESET}")
                return False
        else:
            # Εκτέλεση κανονικά για τα υπόλοιπα .sh
            command = ['bash', script_path]
            
            if additional_args:
                command.extend(additional_args)
                
            try:
                # Εκτελούμε το script και περιμένουμε να ολοκληρωθεί
                process = subprocess.Popen(command)
                process.wait()
                return process.returncode == 0
            except Exception as e:
                print(f"{COLOR_RED}Σφάλμα κατά την εκτέλεση του script: {e}{COLOR_RESET}")
                return False

def run_institutional_memory_refresh(scripts_dir, project_base_path):
    """
    Εκτελεί τα scripts με συγκεκριμένη σειρά για ανανέωση institutional memory
    """
    scripts_to_run = ["debug_tools.py", "system_requirements.py", "status.py", "collect_code.py"]
    success = True
    
    print_header("INSTITUTIONAL MEMORY REFRESH")
    print(f"{COLOR_YELLOW}=== Εκτέλεση Institutional Memory Refresh ==={COLOR_RESET}\n")
    
    # Εκτέλεση των scripts με τη σειρά
    for script_name in scripts_to_run:
        script_path = os.path.join(scripts_dir, script_name)
        
        if not os.path.exists(script_path):
            print(f"{COLOR_RED}Το script {script_name} δεν βρέθηκε!{COLOR_RESET}")
            success = False
            continue
        
        print(f"{COLOR_BLUE}>> Εκτέλεση {script_name}...{COLOR_RESET}\n")
        
        if not run_script(script_path):
            print(f"{COLOR_RED}Η εκτέλεση του {script_name} απέτυχε!{COLOR_RESET}")
            success = False
        
        print(f"\n{COLOR_GREEN}>> Το {script_name} ολοκληρώθηκε{COLOR_RESET}")
        print(f"{COLOR_BLUE}------------------------------------------{COLOR_RESET}")
    
    # Έλεγχος του status του project progress
    logs_dir = os.path.join(project_base_path, "logs")
    progress_file = os.path.join(logs_dir, ".project_progress.json")
    
    print(f"\n{COLOR_YELLOW}=== Σύνοψη ==={COLOR_RESET}")
    
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
            
            print(f"{COLOR_GREEN}Συνολική πρόοδος έργου: {total_progress*100:.2f}%{COLOR_RESET}")
        else:
            print(f"{COLOR_RED}Το αρχείο προόδου δεν βρέθηκε!{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_RED}Σφάλμα κατά τον έλεγχο της προόδου: {e}{COLOR_RESET}")
    
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
            
            print(f"{COLOR_GREEN}Institutional Memory: {os.path.basename(latest_file)}{COLOR_RESET}")
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
            print(f"{COLOR_RED}Δεν βρέθηκαν αρχεία institutional memory!{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_RED}Σφάλμα κατά τον έλεγχο του institutional memory: {e}{COLOR_RESET}")
    
    print(f"\n{COLOR_BLUE}------------------------------------------{COLOR_RESET}")
    
    if success:
        print(f"{COLOR_GREEN}Η ανανέωση του Institutional Memory ολοκληρώθηκε επιτυχώς!{COLOR_RESET}")
    else:
        print(f"{COLOR_RED}Η ανανέωση του Institutional Memory ολοκληρώθηκε με σφάλματα.{COLOR_RESET}")
    
    input("\nΠατήστε Enter για να επιστρέψετε στο κύριο μενού...")

def run_github_update(project_base_path):
    """
    Εκτελεί τη διαδικασία ενημέρωσης του GitHub με οπτικά ελκυστικό τρόπο
    και καταγράφει τα αποτελέσματα σε log file
    """
    print_header("GITHUB UPDATE")
    print(f"{COLOR_YELLOW}=== Διαδικασία Ενημέρωσης GitHub Repository ==={COLOR_RESET}\n")
    
    # Προετοιμασία log file
    logs_dir = os.path.join(project_base_path, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_filename = os.path.join(logs_dir, f"github_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Ξεκινάμε την καταγραφή
    with open(log_filename, 'w', encoding='utf-8') as log_file:
        log_file.write(f"=== GitHub Update Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
        
        # Αλλαγή στον φάκελο του project
        original_dir = os.getcwd()
        os.chdir(project_base_path)
        
        try:
            # Βήμα 1: git status
            print(f"{COLOR_BLUE}[1/4] Έλεγχος τρέχουσας κατάστασης (git status)...{COLOR_RESET}")
            log_file.write("[1/4] Έλεγχος τρέχουσας κατάστασης (git status)...\n")
            
            status_process = subprocess.run(['git', 'status'], capture_output=True, text=True)
            
            # Εμφάνιση αποτελεσμάτων με χρώματα
            status_output = status_process.stdout
            log_file.write(f"Αποτέλεσμα git status:\n{status_output}\n\n")
            
            # Χρωματισμός των εξόδων git status
            colored_status = ""
            for line in status_output.split('\n'):
                if "modified:" in line:
                    colored_status += f"{COLOR_YELLOW}{line}{COLOR_RESET}\n"
                elif "new file:" in line:
                    colored_status += f"{COLOR_GREEN}{line}{COLOR_RESET}\n"
                elif "deleted:" in line:
                    colored_status += f"{COLOR_RED}{line}{COLOR_RESET}\n"
                elif "Untracked files:" in line or "Changes not staged for commit:" in line:
                    colored_status += f"{COLOR_BOLD}{line}{COLOR_RESET}\n"
                else:
                    colored_status += f"{line}\n"
            
            print(colored_status)
            
            # Έλεγχος αν υπάρχουν αρχεία για commit
            if "nothing to commit" in status_output:
                message = "Δεν υπάρχουν αλλαγές για commit."
                print(f"{COLOR_YELLOW}{message}{COLOR_RESET}")
                log_file.write(f"{message}\n")
                log_file.write("\nΗ διαδικασία ενημέρωσης του GitHub ολοκληρώθηκε.\n")
                input("\nΠατήστε Enter για να επιστρέψετε στο μενού...")
                os.chdir(original_dir)
                return
            
            # Βήμα 2: git add .
            print(f"\n{COLOR_BLUE}[2/4] Προσθήκη όλων των αλλαγών (git add .)...{COLOR_RESET}")
            log_file.write("[2/4] Προσθήκη όλων των αλλαγών (git add .)...\n")
            
            add_process = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
            
            if add_process.returncode != 0:
                error_msg = f"Σφάλμα κατά την προσθήκη αρχείων: {add_process.stderr}"
                print(f"{COLOR_RED}{error_msg}{COLOR_RESET}")
                log_file.write(f"{error_msg}\n")
                log_file.write("\nΗ διαδικασία ενημέρωσης του GitHub απέτυχε.\n")
                input("\nΠατήστε Enter για να επιστρέψετε στο μενού...")
                os.chdir(original_dir)
                return
            
            success_msg = "Η προσθήκη των αρχείων ολοκληρώθηκε επιτυχώς"
            print(f"{COLOR_GREEN}✓ {success_msg}{COLOR_RESET}")
            log_file.write(f"{success_msg}\n\n")
            
            # Βήμα 3: git commit με εισαγωγή μηνύματος
            print(f"\n{COLOR_BLUE}[3/4] Δημιουργία commit...{COLOR_RESET}")
            log_file.write("[3/4] Δημιουργία commit...\n")
            
            commit_msg = input(f"{COLOR_YELLOW}Εισάγετε τίτλο για το commit: {COLOR_RESET}")
            
            if not commit_msg:
                commit_msg = "Αυτόματη ενημέρωση από το menu script"
            
            log_file.write(f"Μήνυμα commit: {commit_msg}\n")
            
            commit_process = subprocess.run(['git', 'commit', '-m', commit_msg], capture_output=True, text=True)
            
            if commit_process.returncode != 0:
                error_msg = f"Σφάλμα κατά το commit: {commit_process.stderr}"
                print(f"{COLOR_RED}{error_msg}{COLOR_RESET}")
                log_file.write(f"{error_msg}\n")
                log_file.write("\nΗ διαδικασία ενημέρωσης του GitHub απέτυχε.\n")
                input("\nΠατήστε Enter για να επιστρέψετε στο μενού...")
                os.chdir(original_dir)
                return
            
            # Εμφάνιση αποτελεσμάτων commit
            commit_output = commit_process.stdout
            print(f"{COLOR_GREEN}{commit_output}{COLOR_RESET}")
            log_file.write(f"Αποτέλεσμα commit:\n{commit_output}\n\n")
            
            # Βήμα 4: git push
            print(f"\n{COLOR_BLUE}[4/4] Αποστολή αλλαγών στο GitHub (git push origin main)...{COLOR_RESET}")
            log_file.write("[4/4] Αποστολή αλλαγών στο GitHub (git push origin main)...\n")
            
            push_process = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
            
            if push_process.returncode != 0:
                error_msg = f"Σφάλμα κατά το push: {push_process.stderr}"
                print(f"{COLOR_RED}{error_msg}{COLOR_RESET}")
                log_file.write(f"{error_msg}\n")
                log_file.write("\nΗ διαδικασία ενημέρωσης του GitHub απέτυχε.\n")
                input("\nΠατήστε Enter για να επιστρέψετε στο μενού...")
                os.chdir(original_dir)
                return
            
            push_output = push_process.stdout if push_process.stdout else "Επιτυχής αποστολή αλλαγών."
            log_file.write(f"Αποτέλεσμα push:\n{push_output}\n\n")
            
            success_msg = "Η αποστολή των αλλαγών ολοκληρώθηκε επιτυχώς"
            print(f"{COLOR_GREEN}✓ {success_msg}{COLOR_RESET}")
            print(f"\n{COLOR_GREEN}Όλη η διαδικασία ενημέρωσης του GitHub ολοκληρώθηκε επιτυχώς!{COLOR_RESET}")
            
            # Σύνοψη
            summary = f"""
=== Σύνοψη ===
- Commit: {commit_msg}
- Branch: main
- Log file: {log_filename}
"""
            print(f"{COLOR_YELLOW}Σύνοψη:{COLOR_RESET}")
            print(f"  - {COLOR_BLUE}Commit:{COLOR_RESET} {commit_msg}")
            print(f"  - {COLOR_BLUE}Branch:{COLOR_RESET} main")
            print(f"  - {COLOR_BLUE}Log file:{COLOR_RESET} {log_filename}")
            
            log_file.write(summary)
            log_file.write("\nΗ διαδικασία ενημέρωσης του GitHub ολοκληρώθηκε επιτυχώς.\n")
            
        except Exception as e:
            error_msg = f"Απροσδόκητο σφάλμα: {str(e)}"
            print(f"{COLOR_RED}{error_msg}{COLOR_RESET}")
            log_file.write(f"{error_msg}\n")
            log_file.write("\nΗ διαδικασία ενημέρωσης του GitHub απέτυχε λόγω σφάλματος.\n")
        finally:
            # Επιστροφή στον αρχικό φάκελο
            os.chdir(original_dir)
    
    print(f"\n{COLOR_GREEN}Το log αποθηκεύτηκε στο: {log_filename}{COLOR_RESET}")
    input("\nΠατήστε Enter για να επιστρέψετε στο μενού...")

def display_menu_and_navigate(menu_structure, scripts, project_base_path, current_path=[]):
    """Εμφανίζει το τρέχον μενού και επιτρέπει την πλοήγηση στα υπομενού και την εκτέλεση scripts"""
    while True:
        # Προσδιορισμός του τρέχοντος μενού και του τίτλου
        current_menu = menu_structure
        menu_title = "AI MINING ASSISTANT - MENU"
        
        # Πλοήγηση στο τρέχον μενού βάσει του μονοπατιού
        for category in current_path:
            if category in current_menu:
                current_menu = current_menu[category]["submenus"]
                menu_title = f"MENU > {category}"
            else:
                # Αν η κατηγορία δεν υπάρχει, επιστρέφουμε στο γονικό μενού
                current_path.pop()
                return
        
        # Εμφάνιση της κεφαλίδας του μενού
        print_header(menu_title)
        
        options = []
        
        # Εμφάνιση της διαδρομής πλοήγησης (breadcrumb)
        if current_path:
            breadcrumb = " > ".join(["MENU"] + current_path)
            print(f"{COLOR_BLUE}Τρέχουσα Διαδρομή: {breadcrumb}{COLOR_RESET}\n")
        
        # Προσθήκη επιλογής επιστροφής στο γονικό μενού αν είμαστε σε υπομενού
        if current_path:
            options.append({"type": "back", "name": "Επιστροφή στο προηγούμενο μενού"})
        
        # Προσθήκη των υπομενού
        for submenu_name, submenu_data in sorted(current_menu.items()):
            # Ελέγχουμε αν το υπομενού έχει scripts
            script_count = len(submenu_data["scripts"])
            submenu_display = f"{submenu_name} ({script_count} scripts)"
            options.append({"type": "submenu", "name": submenu_name, "display": submenu_display})
        
        # Συλλογή των scripts για το τρέχον μενού
        current_scripts = []
        if not current_path:  # Αν είμαστε στο κύριο μενού
            # Στο κύριο μενού δεν εμφανίζουμε scripts, μόνο κατηγορίες
            current_scripts = []
        else:  # Αν είμαστε σε υπομενού
            # Πλοήγηση στο σωστό υπομενού
            menu = menu_structure
            for path_item in current_path[:-1]:
                menu = menu[path_item]["submenus"]
            # Εμφάνιση των scripts αυτού του υπομενού
            current_scripts = menu[current_path[-1]]["scripts"]
        
        # Προσθήκη των scripts
        for script in current_scripts:
            options.append({"type": "script", "script": script})
        
        # Προσθήκη της επιλογής για Institutional Memory Refresh μόνο στο κύριο μενού
        if not current_path:  # Μόνο στο κύριο μενού
            options.append({"type": "refresh", "name": "Institutional Memory Refresh"})
            # Προσθήκη της επιλογής για GitHub Update μόνο στο κύριο μενού
            options.append({"type": "github", "name": "GitHub Update"})
        
        # Προσθήκη επιλογής εξόδου
        options.append({"type": "exit", "name": "Έξοδος"})
        
        # Εμφάνιση των επιλογών
        for i, option in enumerate(options, 1):
            if option["type"] == "back":
                print(f"{COLOR_BLUE}{i}. {option['name']}{COLOR_RESET}")
            elif option["type"] == "submenu":
                print(f"{COLOR_YELLOW}{i}. {option['display']}{COLOR_RESET}")
            elif option["type"] == "script":
                script = option["script"]
                print(f"{COLOR_GREEN}{i}. {script.name}{COLOR_RESET}")
                print(f"   {script.description}")
            elif option["type"] == "refresh":
                print(f"{COLOR_GREEN}{i}. {option['name']}{COLOR_RESET}")
                print("   Εκτελεί όλα τα βασικά scripts για ανανέωση του institutional memory")
            elif option["type"] == "github":
                print(f"{COLOR_GREEN}{i}. {option['name']}{COLOR_RESET}")
                print("   Ενημέρωση του GitHub repository με τις πρόσφατες αλλαγές")
            elif option["type"] == "exit":
                print(f"{COLOR_RED}{i}. {option['name']}{COLOR_RESET}")
            print()
        
        # Λήψη επιλογής από τον χρήστη
        try:
            choice = input(f"Επιλέξτε μια επιλογή (1-{len(options)}): ")
            choice = int(choice)
            
            if 1 <= choice <= len(options):
                option = options[choice - 1]
                
                if option["type"] == "back":
                    current_path.pop()
                    return
                elif option["type"] == "submenu":
                    current_path.append(option["name"])
                    return
                elif option["type"] == "script":
                    script = option["script"]
                    # Εκτέλεση του επιλεγμένου script
                    print_header(f"ΕΚΤΕΛΕΣΗ: {script.name}")
                    print(f"{COLOR_YELLOW}Εκτέλεση του script: {script.name}{COLOR_RESET}")
                    print(f"Περιγραφή: {script.description}")
                    print(f"{COLOR_BLUE}------------------------------------------{COLOR_RESET}\n")
                    
                    run_script(script.path)
                    
                    print(f"\n{COLOR_GREEN}Το script ολοκληρώθηκε.{COLOR_RESET}")
                    input("\nΠατήστε Enter για να επιστρέψετε στο μενού...")
                elif option["type"] == "refresh":
                    scripts_dir = os.path.join(project_base_path, "scripts")
                    run_institutional_memory_refresh(scripts_dir, project_base_path)
                elif option["type"] == "github":
                    run_github_update(project_base_path)
                elif option["type"] == "exit":
                    print_header()
                    print(f"{COLOR_YELLOW}Έξοδος από το μενού. Αντίο!{COLOR_RESET}")
                    sys.exit(0)
            else:
                print(f"{COLOR_RED}Μη έγκυρη επιλογή. Παρακαλώ επιλέξτε έναν αριθμό από το 1 έως το {len(options)}.{COLOR_RESET}")
                input("\nΠατήστε Enter για να συνεχίσετε...")
        except ValueError:
            print(f"{COLOR_RED}Παρακαλώ εισάγετε έναν αριθμό.{COLOR_RESET}")
            input("\nΠατήστε Enter για να συνεχίσετε...")

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
    
    print(f"Script path: {script_path}")
    print(f"Project base path: {project_base_path}")
    
    # Εύρεση και κατηγοριοποίηση των διαθέσιμων scripts
    scripts = find_available_scripts(project_base_path)
    
    if not scripts:
        print(f"{COLOR_RED}Δεν βρέθηκαν διαθέσιμα scripts.{COLOR_RESET}")
        return
    
    # Δημιουργία της ιεραρχικής δομής του μενού
    menu_structure = get_menu_structure(scripts)
    
    # Εμφάνιση του μενού και πλοήγηση
    current_path = []  # Αρχική διαδρομή (κύριο μενού)
    
    while True:
        display_menu_and_navigate(menu_structure, scripts, project_base_path, current_path)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{COLOR_YELLOW}Διακοπή από τον χρήστη. Αντίο!{COLOR_RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{COLOR_RED}Απροσδόκητο σφάλμα: {e}{COLOR_RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
