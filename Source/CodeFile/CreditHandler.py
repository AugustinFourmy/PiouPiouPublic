import logging, json, os

credit_dict = None

def play_credit():
    if credit_dict is None:
        logging.error("Pas de fichier de credit charger !")
        return False
    
def load_credit(file_path):
    global credit_dict
    if os.path.exists(file_path):
        with open(file_path, 'w') as f:
            credit_dict = json.load(f)
        logging.info("Fichier {file_path} charger !")
        return True
    logging.error(f"Fichier {file_path} n'existe pas !")
    return False

def unload_credit():
    global credit_dict
    credit_dict = None