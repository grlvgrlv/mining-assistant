def filter_directory_structure(file_path, root_dir):
    """
    Φιλτράρει τη δομή του καταλόγου αφαιρώντας αποκλεισμένους φακέλους.
    
    Args:
        file_path: Διαδρομή προς το αρχείο δομής καταλόγου
        root_dir: Η ριζική διαδρομή του project
    
    Returns:
        str: Φιλτραρισμένη δομή καταλόγου
    """
    # Λίστα πλήρως εξαιρούμενων καταλόγων
    excluded_dirs = {
        "venv", "node_modules", "__pycache__", ".git", 
        "dist", "build", ".ipynb_checkpoints", 
        "old", "logs", "models"
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Φιλτράρισμα των γραμμών
        filtered_lines = []
        for line in lines:
            # Αφαίρεση της αρχικής διαδρομής του root_dir
            stripped_line = line.replace(root_dir, '').strip('./')
            
            # Έλεγχος εάν η γραμμή περιέχει αποκλεισμένο κατάλογο
            if not any(excluded_dir in stripped_line.split('/') for excluded_dir in excluded_dirs):
                filtered_lines.append(line)
        
        return ''.join(filtered_lines)
    
    except Exception as e:
        print(f"Σφάλμα κατά την ανάγνωση του αρχείου δομής καταλόγου: {e}")
        return ""

def collect_code(root_dir, output_file, log_file, processed_file, missing_file, json_file):
    """
    Συλλέγει κώδικα από αρχεία του project και δημιουργεί ένα institutional memory.
    
    Args:
        root_dir: Γονικός φάκελος του project
        output_file: Αρχείο εξόδου κειμένου (.txt)
        log_file: Αρχείο καταγραφής παραλειφθέντων αρχείων
        processed_file: Αρχείο καταγραφής επεξεργασμένων αρχείων
        missing_file: Αρχείο καταγραφής αγνοημένων αρχείων
        json_file: Αρχείο εξόδου JSON
    """
    supported_extensions = [".py", ".sh", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".md", ".log", ".txt"]
    
    # Λίστα αποκλεισμού αρχείων με ειδική σήμανση ιστορικών εκδόσεων
    excluded_files = {
        ".gitignore", "README", "copy", "skipped_files", "processed_files", "missing_files",
        # Αποκλεισμός αρχείων με ενδείξεις παλαιότερων εκδόσεων
        ".old", ".bak", ".backup", ".working", ".tmp", ".temp"
    }

    max_file_size_mb = 10
    all_files = {
        os.path.join(root, file) 
        for root, _, files in os.walk(root_dir) 
        for file in files
        if not is_excluded_path(os.path.join(root, file), root_dir)
        and file not in excluded_files
        and not any(excluded in file for excluded in excluded_files)
        and not is_historical_version(os.path.join(root, file))
    }

    processed_files = set()
    skipped_files = []
    json_data = []
    
    # Προσθήκη πληροφοριών συστήματος
    system_info = get_system_info()
    json_data.append({"file_path": "system_info", "content": json.dumps(system_info, indent=2)})

    with open(output_file, "w", encoding="utf-8") as outfile, \
         open(log_file, "w", encoding="utf-8") as log, \
         open(processed_file, "w", encoding="utf-8") as processed:
        
        outfile.write("# AI Mining Assistant - Institutional Memory\n")
        outfile.write(f"# Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Προσθήκη πληροφοριών συστήματος στο αρχείο κειμένου
        outfile.write("# === System Information ===\n")
        for key, value in system_info.items():
            outfile.write(f"# {key}: {value}\n")
        outfile.write("\n\n")
        
        log.write("# Skipped Files Log\n")
        processed.write("# Processed Files Log\n")

        # Προσθήκη δομής του project
        project_structure = get_project_structure(root_dir)
        outfile.write("# === Project Structure ===\n")
        outfile.write(project_structure)
        outfile.write("\n\n")
        json_data.append({"file_path": "project_structure", "content": project_structure})

        # Ειδική διαχείριση για αρχεία δομής καταλόγου
        directory_structure_files = [
            os.path.join(root, file) 
            for root, _, files in os.walk(root_dir) 
            for file in files 
            if file == "directory_structure.txt"
        ]

        for ds_file in directory_structure_files:
            filtered_structure = filter_directory_structure(ds_file, root_dir)
            if filtered_structure:
                outfile.write(f"# === Filtered Directory Structure: {ds_file} ===\n")
                outfile.write(filtered_structure)
                outfile.write("\n\n")
                json_data.append({
                    "file_path": ds_file, 
                    "content": filtered_structure
                })

        # Συλλογή αρχείων
        for file_path in sorted(all_files):
            root = os.path.dirname(file_path)
            file = os.path.basename(file_path)

            if file_path in {output_file, log_file, processed_file, missing_file, json_file}:
                continue

            if os.path.getsize(file_path) > max_file_size_mb * 1024 * 1024:
                skipped_files.append(f"{file_path} - Μέγεθος αρχείου μεγαλύτερο από {max_file_size_mb}MB")
                continue

            if file.endswith(".env") or any(file.endswith(ext) for ext in supported_extensions):
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

        # Καταγραφή παρακαμφθέντων και επεξεργασμένων αρχείων
        for skipped in skipped_files:
            log.write(skipped + "\n")
        
        for processed_path in processed_files:
            processed.write(processed_path + "\n")

    # Προσθήκη περίληψης στο αρχείο JSON
    json_summary = {
        "file_path": "_project_summary",
        "content": {
            "title": "Mining Assistant Project",
            "total_files": len(all_files),
            "processed_files": len(processed_files),
            "skipped_files": len(skipped_files),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "generated_files": {
                "text_memory": output_file,
                "json_memory": json_file,
                "log_file": log_file,
                "processed_log": processed_file,
                "missing_log": missing_file
            }
        }
    }
    json_data.append(json_summary)

    with open(json_file, "w", encoding="utf-8") as jfile:
        json.dump(json_data, jfile, ensure_ascii=False, indent=2)

    missing_files = sorted(all_files - processed_files)
    with open(missing_file, "w", encoding="utf-8") as missing:
        missing.write("# Missing Files Log\n")
        for missing_file_path in missing_files:
            missing.write(missing_file_path + "\n")
            
    print(f"Συνολικά αρχεία: {len(all_files)}")
    print(f"Επεξεργασμένα αρχεία: {len(processed_files)}")
    print(f"Παρακαμφθέντα αρχεία: {len(skipped_files)}")

    def collect_code(root_dir, output_file, log_file, processed_file, missing_file, json_file):
    """
    Συλλέγει κώδικα από αρχεία του project και δημιουργεί ένα institutional memory.
    
    Args:
        root_dir: Γονικός φάκελος του project
        output_file: Αρχείο εξόδου κειμένου (.txt)
        log_file: Αρχείο καταγραφής παραλειφθέντων αρχείων
        processed_file: Αρχείο καταγραφής επεξεργασμένων αρχείων
        missing_file: Αρχείο καταγραφής αγνοημένων αρχείων
        json_file: Αρχείο εξόδου JSON
    """
    supported_extensions = [".py", ".sh", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".md", ".log", ".txt"]

    
    # Λίστα αποκλεισμού αρχείων με ειδική σήμανση ιστορικών εκδόσεων
    excluded_files = {
        ".gitignore", "README", "copy", "skipped_files", "processed_files", "missing_files",
        # Αποκλεισμός αρχείων με ενδείξεις παλαιότερων εκδόσεων
        ".old", ".bak", ".backup", ".working", ".tmp", ".temp",
        # Αποκλεισμός συγκεκριμένων αρχείων που δεν θέλουμε
        "directory_structure.txt"
    }

    max_file_size_mb = 10
    all_files = {
        os.path.join(root, file) 
        for root, _, files in os.walk(root_dir) 
        for file in files
        if not is_excluded_path(os.path.join(root, file), root_dir)
        and file not in excluded_files
        and not any(excluded in file for excluded in excluded_files)
        and not is_historical_version(os.path.join(root, file))
    }

    processed_files = set()
    skipped_files = []
    json_data = []
    
    # Προσθήκη πληροφοριών συστήματος
    system_info = get_system_info()
    json_data.append({"file_path": "system_info", "content": json.dumps(system_info, indent=2)})

    with open(output_file, "w", encoding="utf-8") as outfile, \
         open(log_file, "w", encoding="utf-8") as log, \
         open(processed_file, "w", encoding="utf-8") as processed:
        
        outfile.write("# AI Mining Assistant - Institutional Memory\n")
        outfile.write(f"# Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Προσθήκη πληροφοριών συστήματος στο αρχείο κειμένου
        outfile.write("# === System Information ===\n")
        for key, value in system_info.items():
            outfile.write(f"# {key}: {value}\n")
        outfile.write("\n\n")
        
        log.write("# Skipped Files Log\n")
        processed.write("# Processed Files Log\n")

        # Προσθήκη δομής του project
        project_structure = get_project_structure(root_dir)
        outfile.write("# === Project Structure ===\n")
        outfile.write(project_structure)
        outfile.write("\n\n")
        json_data.append({"file_path": "project_structure", "content": project_structure})

        # Συλλογή αρχείων
        for file_path in sorted(all_files):
            root = os.path.dirname(file_path)
            file = os.path.basename(file_path)

            if file_path in {output_file, log_file, processed_file, missing_file, json_file}:
                continue

            if os.path.getsize(file_path) > max_file_size_mb * 1024 * 1024:
                skipped_files.append(f"{file_path} - Μέγεθος αρχείου μεγαλύτερο από {max_file_size_mb}MB")
                continue

            if file.endswith(".env") or any(file.endswith(ext) for ext in supported_extensions):
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

        # Καταγραφή παρακαμφθέντων και επεξεργασμένων αρχείων
        for skipped in skipped_files:
            log.write(skipped + "\n")
        
        for processed_path in processed_files:
            processed.write(processed_path + "\n")

    # Προσθήκη περίληψης στο αρχείο JSON
    json_summary = {
        "file_path": "_project_summary",
        "content": {
            "title": "Mining Assistant Project",
            "total_files": len(all_files),
            "processed_files": len(processed_files),
            "skipped_files": len(skipped_files),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "generated_files": {
                "text_memory": output_file,
                "json_memory": json_file,
                "log_file": log_file,
                "processed_log": processed_file,
                "missing_log": missing_file
            }
        }
    }
    json_data.append(json_summary)

    with open(json_file, "w", encoding="utf-8") as jfile:
        json.dump(json_data, jfile, ensure_ascii=False, indent=2)

    missing_files = sorted(all_files - processed_files)
    with open(missing_file, "w", encoding="utf-8") as missing:
        missing.write("# Missing Files Log\n")
        for missing_file_path in missing_files:
            missing.write(missing_file_path + "\n")
            
    print(f"Συνολικά αρχεία: {len(all_files)}")
    print(f"Επεξεργασμένα αρχεία: {len(processed_files)}")
    print(f"Παρακαμφθέντα αρχεία: {len(skipped_files)}")import os
import json
import platform
import sys
from datetime import datetime

def is_excluded_path(path, root_dir):
    """
    Ελέγχει εάν μια διαδρομή πρέπει να εξαιρεθεί από την επεξεργασία.
    
    Args:
        path: Πλήρης διαδρομή προς τον φάκελο ή αρχείο
        root_dir: Η ριζική διαδρομή του project
    
    Returns:
        bool: True αν η διαδρομή πρέπει να εξαιρεθεί, False διαφορετικά
    """
    # Λίστα πλήρως εξαιρούμενων καταλόγων
    excluded_dirs = {
        "venv", "node_modules", "__pycache__", ".git", 
        "dist", "build", ".ipynb_checkpoints", 
        "old", "logs", "models"
    }
    
    # Μετατροπή σε σχετική διαδρομή από τη ρίζα του project
    relative_path = os.path.relpath(path, root_dir)
    
    # Διαίρεση της διαδρομής σε τμήματα
    path_parts = relative_path.split(os.sep)
    
    # Έλεγχος εάν οποιοδήποτε τμήμα της διαδρομής είναι σε εξαιρούμενους καταλόγους
    return any(part.lower() in excluded_dirs for part in path_parts)

def get_system_info():
    """
    Συλλέγει βασικές πληροφορίες για το σύστημα.
    
    Returns:
        Dictionary με βασικές πληροφορίες συστήματος
    """
    system_info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": sys.version.split()[0],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hostname": platform.node()
    }
    
    # Ανίχνευση CUDA/GPU αν είναι διαθέσιμο
    try:
        import torch
        system_info["cuda_available"] = torch.cuda.is_available()
        if system_info["cuda_available"]:
            system_info["gpu_count"] = torch.cuda.device_count()
            system_info["gpu_name"] = torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else "Unknown"
    except ImportError:
        system_info["cuda_available"] = "torch not installed"
    
    return system_info

def is_historical_version(file_path):
    """
    Ελέγχει εάν ένα αρχείο είναι παλαιότερη έκδοση.
    
    Εξετάζει διάφορες κοινές ενδείξεις όπως:
    - collect_code.py.old
    - collect_code.py.working
    - collect_code.old.py
    - collect_code.bak
    
    Returns:
        bool: True αν είναι παλαιά έκδοση, False διαφορετικά
    """
    filename = os.path.basename(file_path)
    base_name, ext = os.path.splitext(filename)
    
    # Λίστα με πιθανές σημάνσεις παλαιών εκδόσεων
    historical_suffixes = [
        ".old", ".bak", ".backup", ".working", 
        ".tmp", ".temp", ".previous", ".orig"
    ]
    
    # Έλεγχος για παραλλαγές όπως: 
    # collect_code.py.old, collect_code.py.working, collect_code.old.py κλπ
    for suffix in historical_suffixes:
        if suffix in filename or filename.endswith(suffix):
            return True
    
    return False

def get_project_structure(root_dir):
    """
    Δημιουργεί μια συνοπτική αναπαράσταση της δομής του project.
    
    Args:
        root_dir: Η ριζική διαδρομή του project
    
    Returns:
        String με τη δομή του project
    """
    structure = []
    
    # Ενημερωμένη λίστα εξαιρούμενων καταλόγων
    excluded_dirs = {"venv", "node_modules", "__pycache__", ".git", "dist", "build", ".ipynb_checkpoints", "old", "logs", "models"}
    
    for root, dirs, files in os.walk(root_dir):
        # Αφαίρεση εξαιρούμενων καταλόγων
        dirs[:] = [d for d in dirs if d.lower() not in excluded_dirs]
        
        level = root.replace(root_dir, '').count(os.sep)
        indent = ' ' * 4 * level
        structure.append(f"{indent}{os.path.basename(root)}/")
        
        # Περιορισμός βάθους ανάλυσης για μεγάλα projects
        if level >= 3:
            if files:
                structure.append(f"{indent}    [...]")
            continue
            
        # Ομαδοποίηση αρχείων ανά επέκταση
        file_extensions = {}
        for file in files:
            ext = os.path.splitext(file)[1].lower() or "no_extension"
            if ext not in file_extensions:
                file_extensions[ext] = []
            file_extensions[ext].append(file)
        
        # Εμφάνιση αριθμού αρχείων ανά επέκταση αν είναι πολλά
        for ext, ext_files in sorted(file_extensions.items()):
            if len(ext_files) > 5:
                structure.append(f"{indent}    [{len(ext_files)} {ext} files]")
            else:
                for file in sorted(ext_files):
                    structure.append(f"{indent}    {file}")
    
    return "\n".join(structure)

def collect_code(root_dir, output_file, log_file, processed_file, missing_file, json_file):
    """
    Συλλέγει κώδικα από αρχεία του project και δημιουργεί ένα institutional memory.
    
    Args:
        root_dir: Γονικός φάκελος του project
        output_file: Αρχείο εξόδου κειμένου (.txt)
        log_file: Αρχείο καταγραφής παραλειφθέντων αρχείων
        processed_file: Αρχείο καταγραφής επεξεργασμένων αρχείων
        missing_file: Αρχείο καταγραφής αγνοημένων αρχείων
        json_file: Αρχείο εξόδου JSON
    """
    supported_extensions = [".py", ".sh", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".md", ".log", ".txt"]
    
    # Λίστα αποκλεισμού αρχείων με ειδική σήμανση ιστορικών εκδόσεων
    excluded_files = {
        ".gitignore", "README", "copy", "skipped_files", "processed_files", "missing_files",
        # Αποκλεισμός αρχείων με ενδείξεις παλαιότερων εκδόσεων
        ".old", ".bak", ".backup", ".working", ".tmp", ".temp"
    }

    max_file_size_mb = 10
    all_files = {
        os.path.join(root, file) 
        for root, _, files in os.walk(root_dir) 
        for file in files
        if not is_excluded_path(os.path.join(root, file), root_dir)
        and not any(excluded in file for excluded in excluded_files)
        and not is_historical_version(os.path.join(root, file))
    }

    processed_files = set()
    skipped_files = []
    json_data = []
    
    # Προσθήκη πληροφοριών συστήματος
    system_info = get_system_info()
    json_data.append({"file_path": "system_info", "content": json.dumps(system_info, indent=2)})

    with open(output_file, "w", encoding="utf-8") as outfile, \
         open(log_file, "w", encoding="utf-8") as log, \
         open(processed_file, "w", encoding="utf-8") as processed:
        
        outfile.write("# AI Mining Assistant - Institutional Memory\n")
        outfile.write(f"# Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Προσθήκη πληροφοριών συστήματος στο αρχείο κειμένου
        outfile.write("# === System Information ===\n")
        for key, value in system_info.items():
            outfile.write(f"# {key}: {value}\n")
        outfile.write("\n\n")
        
        log.write("# Skipped Files Log\n")
        processed.write("# Processed Files Log\n")

        # Προσθήκη δομής του project
        project_structure = get_project_structure(root_dir)
        outfile.write("# === Project Structure ===\n")
        outfile.write(project_structure)
        outfile.write("\n\n")
        json_data.append({"file_path": "project_structure", "content": project_structure})

        # Συλλογή αρχείων
        for file_path in sorted(all_files):
            root = os.path.dirname(file_path)
            file = os.path.basename(file_path)

            if file_path in {output_file, log_file, processed_file, missing_file, json_file}:
                continue

            if os.path.getsize(file_path) > max_file_size_mb * 1024 * 1024:
                skipped_files.append(f"{file_path} - Μέγεθος αρχείου μεγαλύτερο από {max_file_size_mb}MB")
                continue

            if file.endswith(".env") or any(file.endswith(ext) for ext in supported_extensions):
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

        # Καταγραφή παρακαμφθέντων και επεξεργασμένων αρχείων
        for skipped in skipped_files:
            log.write(skipped + "\n")
        
        for processed_path in processed_files:
            processed.write(processed_path + "\n")

    # Προσθήκη περίληψης στο αρχείο JSON
    json_summary = {
        "file_path": "_project_summary",
        "content": {
            "title": "Mining Assistant Project",
            "total_files": len(all_files),
            "processed_files": len(processed_files),
            "skipped_files": len(skipped_files),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "generated_files": {
                "text_memory": output_file,
                "json_memory": json_file,
                "log_file": log_file,
                "processed_log": processed_file,
                "missing_log": missing_file
            }
        }
    }
    json_data.append(json_summary)

    with open(json_file, "w", encoding="utf-8") as jfile:
        json.dump(json_data, jfile, ensure_ascii=False, indent=2)

    missing_files = sorted(all_files - processed_files)
    with open(missing_file, "w", encoding="utf-8") as missing:
        missing.write("# Missing Files Log\n")
        for missing_file_path in missing_files:
            missing.write(missing_file_path + "\n")
            
    print(f"Συνολικά αρχεία: {len(all_files)}")
    print(f"Επεξεργασμένα αρχεία: {len(processed_files)}")
    print(f"Παρακαμφθέντα αρχεία: {len(skipped_files)}")

if __name__ == "__main__":
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    SCRIPTS_DIR = os.path.join(ROOT_DIR, "scripts")
    LOGS_DIR = os.path.join(ROOT_DIR, "logs")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    OUTPUT_FILE = os.path.join(LOGS_DIR, f"institutional_memory_{timestamp}.txt")
    LOG_FILE = os.path.join(LOGS_DIR, f"skipped_files_{timestamp}.log")
    PROCESSED_FILE = os.path.join(LOGS_DIR, f"processed_files_{timestamp}.log")
    MISSING_FILE = os.path.join(LOGS_DIR, f"missing_files_{timestamp}.log")
    JSON_FILE = os.path.join(LOGS_DIR, f"institutional_memory_{timestamp}.json")

    os.makedirs(LOGS_DIR, exist_ok=True)
    collect_code(ROOT_DIR, OUTPUT_FILE, LOG_FILE, PROCESSED_FILE, MISSING_FILE, JSON_FILE)
