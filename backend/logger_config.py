"""
Logger Configuration Module for AI Mining Assistant
Παρέχει προηγμένες λειτουργίες καταγραφής για όλα τα components του συστήματος.
"""
import os
import logging
import logging.handlers
from datetime import datetime
import json
import traceback

class CustomJsonFormatter(logging.Formatter):
    """
    Προσαρμοσμένος formatter που παράγει JSON για καλύτερη ανάλυση των logs
    """
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Προσθήκη exception πληροφοριών αν υπάρχουν
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Προσθήκη επιπλέον πληροφοριών από το record
        if hasattr(record, 'extra') and record.extra:
            log_data.update(record.extra)
        
        return json.dumps(log_data)

def setup_logger(name, log_file=None, level=logging.INFO, use_json=False):
    """
    Δημιουργία και ρύθμιση logger
    
    Args:
        name (str): Το όνομα του logger
        log_file (str, optional): Διαδρομή αρχείου για την αποθήκευση των logs
        level (int, optional): Το επίπεδο καταγραφής (default: INFO)
        use_json (bool, optional): Αν True, καταγράφει σε μορφή JSON
        
    Returns:
        logging.Logger: Ο διαμορφωμένος logger
    """
    # Δημιουργία του logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Αν έχει ήδη handlers, επιστρέφουμε τον υπάρχοντα logger
    if logger.handlers:
        return logger
    
    # Δημιουργία formatter
    if use_json:
        formatter = CustomJsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(module)s.%(funcName)s:%(lineno)d | %(message)s', 
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Προσθήκη console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Προσθήκη file handler αν δοθεί αρχείο
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10485760, backupCount=5  # ~10MB με μέγιστο 5 αρχεία
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_component_logger(component_name, use_json=False):
    """
    Λήψη logger για συγκεκριμένο component
    
    Args:
        component_name (str): Το όνομα του component (πχ. 'mining_connector')
        use_json (bool, optional): Αν True, καταγράφει σε μορφή JSON
        
    Returns:
        logging.Logger: Ο διαμορφωμένος logger
    """
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = f"{log_dir}/{component_name}.log"
    return setup_logger(f"mining-assistant.{component_name}", log_file, use_json=use_json)

class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger Adapter για προσθήκη επιπλέον πληροφοριών στα log μηνύματα
    """
    def process(self, msg, kwargs):
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        kwargs['extra'].update(self.extra)
        return msg, kwargs

def get_request_logger(request_id):
    """
    Λήψη logger για συγκεκριμένο request (για χρήση στο FastAPI)
    
    Args:
        request_id (str): Το ID του request
        
    Returns:
        LoggerAdapter: Logger με προστιθέμενο request_id
    """
    logger = get_component_logger('api')
    return LoggerAdapter(logger, {'request_id': request_id})

# Παραδείγματα χρήσης:

# 1. Απλή χρήση για component
# from logger_config import get_component_logger
# logger = get_component_logger("mining_connector")
# logger.info("Σύνδεση με το mining API...")
# logger.error("Σφάλμα σύνδεσης", exc_info=True)  # Αυτόματη καταγραφή exception

# 2. Χρήση με request ID (για FastAPI)
# from logger_config import get_request_logger
# import uuid
# 
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     request_id = str(uuid.uuid4())
#     request.state.logger = get_request_logger(request_id)
#     request.state.logger.info(f"Νέο αίτημα: {request.method} {request.url}")
#     response = await call_next(request)
#     return response
# 
# @app.get("/api/example")
# async def example(request: Request):
#     request.state.logger.info("Επεξεργασία αιτήματος...")
#     return {"message": "success"}
