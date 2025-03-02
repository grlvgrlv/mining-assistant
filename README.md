# AI Mining Assistant

Ένα AI chatbot που παρέχει πληροφορίες και αυτοματισμούς σχετικά με την εξόρυξη κρυπτονομισμάτων, την ενεργειακή κατανάλωση και τη βέλτιστη διαχείριση GPU πόρων.

## Προαπαιτούμενα

- Python 3.9+
- RAM 16GB+
- GPU με VRAM 6GB+
- CUDA 11.7+
- Node.js 16+

## Εγκατάσταση

1. Κλωνοποιήστε αυτό το repository
2. Εκτελέστε το script setup:
   ```
   bash setup.sh
   ```
3. Ρυθμίστε τις μεταβλητές περιβάλλοντος στο αρχείο `.env`

## Χρήση

1. Εκκίνηση του backend:
   ```
   cd backend
   uvicorn main:app --reload
   ```

2. Εκκίνηση του frontend (σε νέο τερματικό):
   ```
   cd frontend
   npm install
   npm run serve
   ```
