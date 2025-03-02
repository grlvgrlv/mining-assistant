import os

def process_log_file(input_file, keep_file, discard_file):
    """Επεξεργάζεται το log αρχείο για να εντοπίσει επαναλαμβανόμενες γραμμές και να τις διαχωρίσει σε δύο αρχεία."""
    seen_lines = set()  # Σετ για να αποθηκεύσουμε τις μοναδικές γραμμές
    kept_lines = []     # Λίστα για τις γραμμές που θα κρατήσουμε
    discarded_lines = [] # Λίστα για τις επαναλαμβανόμενες γραμμές

    with open(input_file, 'r', encoding="utf-8") as infile:
        for line in infile:
            # Αν η γραμμή δεν έχει εμφανιστεί, την κρατάμε
            if line not in seen_lines:
                kept_lines.append(line)
                seen_lines.add(line)
            else:
                discarded_lines.append(line)
    
    # Αποθήκευση των γραμμών που κρατήσαμε
    with open(keep_file, 'w', encoding="utf-8") as keep_out:
        keep_out.writelines(kept_lines)

    # Αποθήκευση των γραμμών που πετάξαμε
    with open(discard_file, 'w', encoding="utf-8") as discard_out:
        discard_out.writelines(discarded_lines)

    print(f"✅ Ολοκληρώθηκε η επεξεργασία του αρχείου. Τα αποτελέσματα αποθηκεύτηκαν στα εξής αρχεία:")
    print(f"📄 Αρχεία που κρατήθηκαν: {keep_file}")
    print(f"📄 Επαναλαμβανόμενα αρχεία: {discard_file}")

# Καθορίζουμε τον φάκελο logs χρησιμοποιώντας την πλήρη διαδρομή
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Βρίσκουμε τον φάκελο του script
LOGS_DIR = os.path.join(BASE_DIR, "../logs")  # Προσθέτουμε το μονοπάτι για τον φάκελο logs

# Ελέγχουμε αν ο φάκελος logs υπάρχει
if os.path.isdir(LOGS_DIR):
    # Λαμβάνουμε τα αρχεία του φακέλου logs
    log_files = [f for f in os.listdir(LOGS_DIR) if os.path.isfile(os.path.join(LOGS_DIR, f))]

    if log_files:
        # Εκτύπωση των διαθέσιμων αρχείων για επιλογή
        print("Διαθέσιμα αρχεία στον φάκελο logs:")
        for idx, file in enumerate(log_files, 1):
            print(f"{idx}. {file}")
        
        # Ζητάμε από τον χρήστη να επιλέξει το αρχείο
        try:
            choice = int(input("Εισάγετε τον αριθμό του αρχείου που θέλετε να επεξεργαστείτε: "))
            if 1 <= choice <= len(log_files):
                input_log_file = os.path.join(LOGS_DIR, log_files[choice - 1])

                # Καθορίζουμε τα ονόματα των αρχείων εξόδου
                base_name = os.path.splitext(input_log_file)[0]  # Αφαίρεση επέκτασης
                kept_log_file = base_name + "_kept.txt"
                discarded_log_file = base_name + "_discarded.txt"

                # Καλούμε την συνάρτηση για να επεξεργαστεί το αρχείο
                process_log_file(input_log_file, kept_log_file, discarded_log_file)
            else:
                print("❌ Άκυρη επιλογή. Παρακαλώ επιλέξτε έναν έγκυρο αριθμό.")
        except ValueError:
            print("❌ Παρακαλώ εισάγετε έναν έγκυρο αριθμό.")
    else:
        print("❌ Δεν βρέθηκαν αρχεία στον φάκελο logs.")
else:
    print(f"❌ Ο φάκελος '{LOGS_DIR}' δεν υπάρχει.")

