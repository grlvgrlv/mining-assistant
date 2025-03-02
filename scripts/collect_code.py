import os
import json
from datetime import datetime

def collect_code(root_dir, output_file, log_file, processed_file, missing_file, json_file, logs_dir):
    supported_extensions = [".py", ".sh", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".md", ".log", ".txt"]
    excluded_dirs = {"venv", "node_modules", "__pycache__", ".git"}
    excluded_files = {".gitignore", "README", "old", "copy", "skipped_files", "processed_files", "missing_files"}

    max_file_size_mb = 10
    
    # Collect all files and explicitly skip logs directory
    all_files = set()
    for root, dirs, files in os.walk(root_dir):
        # Skip excluded directories by modifying dirs in-place
        dirs[:] = [d for d in dirs if d not in excluded_dirs and os.path.join(root, d) != logs_dir]
        
        for file in files:
            file_path = os.path.join(root, file)
            if not any(excluded in file for excluded in excluded_files):
                all_files.add(file_path)
    
    # Explicit logs directory filtering (double check)
    all_files = {f for f in all_files if not f.startswith(logs_dir)}

    processed_files = set()
    skipped_files = []
    json_data = []

    # Add log entries
    print(f"Total files found before filtering: {len(all_files)}")
    print(f"Logs directory being excluded: {logs_dir}")

    with open(output_file, "w", encoding="utf-8") as outfile, open(log_file, "w", encoding="utf-8") as log, open(processed_file, "w", encoding="utf-8") as processed:
        outfile.write("# AI Mining Assistant - Institutional Memory\n")
        log.write("# Skipped Files Log\n")
        processed.write("# Processed Files Log\n")

        for file_path in sorted(all_files):
            root = os.path.dirname(file_path)
            file = os.path.basename(file_path)

            # Skip our output files
            if file_path in {output_file, log_file, processed_file, missing_file, json_file}:
                continue
                
            # Skip any file in the logs directory
            if logs_dir in file_path:
                skipped_files.append(f"{file_path} - Αρχείο σε φάκελο logs")
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
            
    print(f"Files processed: {len(processed_files)}")
    print(f"Files skipped: {len(skipped_files)}")
    print(f"Missing files: {len(missing_files)}")
    print(f"Total files in JSON: {len(json_data)}")

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
    
    # Pass logs directory to function for explicit exclusion
    collect_code(ROOT_DIR, OUTPUT_FILE, LOG_FILE, PROCESSED_FILE, MISSING_FILE, JSON_FILE, LOGS_DIR)
