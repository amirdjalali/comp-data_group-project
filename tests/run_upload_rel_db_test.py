
from handlers.bibliographic_entity_upload_handler import BibliographicEntityUploadHandler

# 1. Inizializza l'handler passando il percorso dove vuoi che venga creato il database
uploader = BibliographicEntityUploadHandler()
uploader.dbPathOrUrl = "my_database.db" # Assicurati che l'oggetto abbia questo attributo

# 2. Lancia la funzione passandogli il file JSON con i dati
successo = uploader.pushDataToDb("../data/dh_metadata.json")

if successo:
    print("Database creato e dati caricati con successo!")