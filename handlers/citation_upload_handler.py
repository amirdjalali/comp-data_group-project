from .upload_handler import UploadHandler

class CitationUploadHandler(UploadHandler):
    def pushDataToDb(self, path: str) -> bool:
        # Placeholder for the actual CSV/Graph logic
        return True