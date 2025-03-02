#!/usr/bin/env python3

import os
import json
import sys
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
import argparse

def get_json_files(log_dir: str) -> List[str]:
    """
    Αναζητά αρχεία JSON στον καθορισμένο κατάλογο logs.
    
    Args:
        log_dir: Διαδρομή του καταλόγου logs
    
    Returns:
        Λίστα των αρχείων JSON που βρέθηκαν
    """
    json_files = []
    try:
        for file in os.listdir(log_dir):
            if file.endswith('.json'):
                json_files.append(os.path.join(log_dir, file))
    except FileNotFoundError:
        print(f"Ο κατάλογος {log_dir} δεν βρέθηκε.")
    except PermissionError:
        print(f"Δεν έχετε άδεια πρόσβασης στον κατάλογο {log_dir}.")
    
    return json_files

def select_json_file(json_files: List[str]) -> str:
    """
    Εμφανίζει λίστα αρχείων JSON και ζητά από τον χρήστη να επιλέξει ένα.
    
    Args:
        json_files: Λίστα των αρχείων JSON
    
    Returns:
        Το επιλεγμένο αρχείο JSON
    """
    if not json_files:
        print("Δεν βρέθηκαν αρχεία JSON.")
        sys.exit(1)
    
    print("\nΔιαθέσιμα αρχεία JSON:")
    for i, file in enumerate(json_files, 1):
        file_size = os.path.getsize(file) / 1024  # KB
        print(f"{i}. {os.path.basename(file)} ({file_size:.2f} KB)")
    
    while True:
        choice = input("\nΕπιλέξτε αριθμό αρχείου (ή 'q' για έξοδο): ")
        if choice.lower() == 'q':
            sys.exit(0)
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(json_files):
                return json_files[index]
            else:
                print("Μη έγκυρη επιλογή. Δοκιμάστε ξανά.")
        except ValueError:
            print("Παρακαλώ εισάγετε έναν αριθμό.")

def process_json_file(file_path: str, output_path: str = None) -> None:
    """
    Επεξεργάζεται το αρχείο JSON και κάνει τις απαραίτητες αλλαγές.
    
    Args:
        file_path: Διαδρομή του αρχείου JSON προς επεξεργασία
        output_path: Προαιρετική διαδρομή για το αρχείο εξόδου. Αν δεν καθοριστεί,
                    δημιουργείται αυτόματα με βάση το όνομα του αρχικού αρχείου.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        # Αν δεν είναι έγκυρο JSON, προσπαθήστε να το διαβάσετε ως απλό κείμενο
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            process_text_content(content, file_path, output_path)
            return
    except Exception as e:
        print(f"Σφάλμα κατά την ανάγνωση του αρχείου: {e}")
        return
    
    # Επεξεργασία του JSON
    process_json_content(data, file_path, output_path)

def process_text_content(content: str, file_path: str, output_path: str = None) -> None:
    """
    Επεξεργάζεται το περιεχόμενο ως απλό κείμενο και αναζητά μοτίβα πακέτων.
    
    Args:
        content: Περιεχόμενο του αρχείου ως κείμενο
        file_path: Διαδρομή του αρχικού αρχείου
        output_path: Προαιρετική διαδρομή για το αρχείο εξόδου
    """
    # Δημιουργία διαδρομής εξόδου αν δεν έχει καθοριστεί
    if not output_path:
        base_name = os.path.basename(file_path)
        name, ext = os.path.splitext(base_name)
        output_path = os.path.join(os.path.dirname(file_path), f"{name}_processed{ext}")
    
    # Αναζήτηση μοτίβων πακέτων Python
    packages_found = process_package_paths(content)
    
    if packages_found:
        # Αντικατάσταση μοτίβων
        new_content = replace_package_listings(content, packages_found)
        
        # Αποθήκευση του νέου περιεχομένου
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Επεξεργασμένο αρχείο αποθηκεύτηκε ως: {output_path}")
        print(f"Βρέθηκαν και μορφοποιήθηκαν {len(packages_found)} ομάδες πακέτων Python.")
    else:
        print("Δεν βρέθηκαν μοτίβα καταλόγων πακέτων Python για επεξεργασία.")

def process_json_content(data: Dict, file_path: str, output_path: str = None) -> None:
    """
    Επεξεργάζεται το περιεχόμενο JSON και αναζητά μοτίβα πακέτων.
    
    Args:
        data: Δεδομένα JSON
        file_path: Διαδρομή του αρχικού αρχείου
        output_path: Προαιρετική διαδρομή για το αρχείο εξόδου
    """
    # Δημιουργία διαδρομής εξόδου αν δεν έχει καθοριστεί
    if not output_path:
        base_name = os.path.basename(file_path)
        name, ext = os.path.splitext(base_name)
        output_path = os.path.join(os.path.dirname(file_path), f"{name}_processed{ext}")
    
    # Αναζήτηση μοτίβων σε όλες τις συμβολοσειρές του JSON
    processed = False
    
    # Εξέταση ειδικά της περίπτωσης όπου υπάρχουν αρχεία στο πεδίο "files"
    if "files" in data and isinstance(data["files"], list):
        paths = [item.get("path", "") for item in data["files"] if isinstance(item, dict)]
        paths_str = "\n".join(paths)
        packages_found = process_package_paths(paths_str)
        
        if packages_found:
            processed = True
            # Δημιουργία νέας δομής για τα πακέτα
            packages_summary = []
            for package_name, version in packages_found.items():
                packages_summary.append({
                    "name": package_name,
                    "version": version,
                    "type": "python_package"
                })
            
            # Αντικατάσταση των πακέτων στο JSON
            data["python_packages"] = packages_summary
            
            # Αφαίρεση των σχετικών αρχείων από τη λίστα
            data["files"] = [item for item in data["files"] 
                           if not isinstance(item, dict) or 
                           not item.get("path", "").startswith("./venv/lib/python")]
    
    # Αποθήκευση του επεξεργασμένου JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    if processed:
        print(f"Επεξεργασμένο αρχείο JSON αποθηκεύτηκε ως: {output_path}")
        print(f"Βρέθηκαν και μορφοποιήθηκαν {len(packages_found)} πακέτα Python.")
    else:
        print(f"Δεν βρέθηκαν μοτίβα για επεξεργασία. Το αρχείο αποθηκεύτηκε ως: {output_path}")

def process_package_paths(content: str) -> Dict[str, str]:
    """
    Εντοπίζει μοτίβα καταλόγων πακέτων Python και εξάγει ονόματα και εκδόσεις.
    
    Args:
        content: Περιεχόμενο του αρχείου ως κείμενο
    
    Returns:
        Λεξικό με ονόματα πακέτων και εκδόσεις
    """
    # Εύρεση γραμμών που ξεκινούν με "./venv/lib/python" και περιέχουν "site-packages"
    pattern = r'\.\/venv\/lib\/python[0-9.]+\/site-packages\/([a-zA-Z0-9_.-]+)(?:-([0-9.]+(?:\.[a-z0-9]+)?).dist-info)?'
    
    matches = re.finditer(pattern, content)
    
    packages = {}
    for match in matches:
        package_name = match.group(1)
        version = match.group(2) if match.group(2) else ""
        
        # Αγνόηση καταλόγων __pycache__ και παρόμοιων
        if package_name.endswith('__pycache__') or package_name == '__pycache__':
            continue
            
        # Καθαρισμός ονόματος πακέτου (π.χ. αφαίρεση επεκτάσεων .dist-info)
        if package_name.endswith('.dist-info'):
            package_name = package_name[:-10]
        
        # Αφαίρεση αριθμών έκδοσης από το όνομα πακέτου αν υπάρχουν
        package_name = re.sub(r'-[0-9.]+$', '', package_name)
        
        # Αποθήκευση του πακέτου μόνο αν δεν υπάρχει ήδη ή αν δεν έχει έκδοση
        if package_name not in packages or not packages[package_name]:
            packages[package_name] = version
    
    return packages

def replace_package_listings(content: str, packages: Dict[str, str]) -> str:
    """
    Αντικαθιστά τις λίστες καταλόγων πακέτων με συνοπτική μορφή.
    
    Args:
        content: Περιεχόμενο του αρχείου
        packages: Λεξικό με ονόματα πακέτων και εκδόσεις
    
    Returns:
        Νέο περιεχόμενο με αντικατεστημένα μοτίβα
    """
    # Εύρεση μπλοκ γραμμών που ξεκινούν με "./venv/lib/python"
    venv_pattern = r'((?:\.\/venv\/lib\/python[0-9.]+\/site-packages\/[^\n]+\n)+)'
    
    # Συνάρτηση αντικατάστασης για κάθε μπλοκ
    def replace_block(match):
        block = match.group(1)
        # Έλεγχος αν το μπλοκ περιέχει πολλαπλές γραμμές site-packages
        if block.count('site-packages') > 5:  # Αυθαίρετο όριο για μεγάλα μπλοκ
            packages_list = "\n./venv/lib/python3.10/site-packages (packages):\n"
            # Προσθήκη όλων των πακέτων με τις εκδόσεις τους
            for package, version in sorted(packages.items()):
                version_str = f" ({version})" if version else ""
                packages_list += f"    {package}{version_str}\n"
            return packages_list
        else:
            # Επιστροφή του αρχικού μπλοκ αν είναι μικρό
            return block
    
    # Αντικατάσταση μπλοκ
    new_content = re.sub(venv_pattern, replace_block, content)
    
    return new_content

def main():
    """Κύρια συνάρτηση του script."""
    # Ορισμός διαδρομών
    home_dir = str(Path.home())
    mining_assistant_dir = os.path.join(home_dir, "mining-assistant")
    log_dir = os.path.join(mining_assistant_dir, "logs")
    
    # Ανάλυση παραμέτρων γραμμής εντολών
    parser = argparse.ArgumentParser(description='Επεξεργασία αρχείων καταγραφής JSON για τον Mining Assistant.')
    parser.add_argument('--logdir', default=log_dir, help='Διαδρομή καταλόγου logs (προεπιλογή: ~/mining-assistant/logs)')
    parser.add_argument('--file', help='Απευθείας επιλογή αρχείου για επεξεργασία')
    parser.add_argument('--output', help='Διαδρομή αρχείου εξόδου')
    
    args = parser.parse_args()
    
    # Έλεγχος αν έχει καθοριστεί απευθείας αρχείο
    if args.file:
        file_path = args.file
        if not os.path.exists(file_path):
            print(f"Το αρχείο {file_path} δεν βρέθηκε.")
            sys.exit(1)
    else:
        # Λήψη λίστας αρχείων JSON
        json_files = get_json_files(args.logdir)
        
        # Επιλογή αρχείου JSON
        if not json_files:
            print(f"Δεν βρέθηκαν αρχεία JSON στον κατάλογο {args.logdir}")
            sys.exit(1)
        
        file_path = select_json_file(json_files)
    
    # Επεξεργασία του επιλεγμένου αρχείου
    process_json_file(file_path, args.output)

if __name__ == "__main__":
    main()
