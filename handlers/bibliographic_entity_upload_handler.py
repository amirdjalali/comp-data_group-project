from .upload_handler import UploadHandler

class BibliographicEntityUploadHandler(UploadHandler):
    def pushDataToDb(self, path: str) -> bool:
        # Placeholder for the actual JSON/Relational logic
        return True
