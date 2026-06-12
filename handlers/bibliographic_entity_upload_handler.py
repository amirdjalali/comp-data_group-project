import sqlite3
import pandas as pd
from .upload_handler import UploadHandler

class BibliographicEntityUploadHandler(UploadHandler):
    def pushDataToDb(self, path: str) -> bool:
        bibdf = pd.read_json(path)
        for i, row in bibdf.iterrows():
            if isinstance(row['id'], list):
                bibdf.at[i, 'id'] = '; '.join(row['id'])
            if isinstance(row['author'], list):
                bibdf.at[i, 'author'] = '; '.join(row['author'])
       
        with sqlite3.connect(self.dbPathOrUrl) as con:
            bibdf.to_sql('BibliographicEntity', con, if_exists='replace', index=False)

        return True

       