import sqlite3
import pandas as pd
from .upload_handler import UploadHandler

class BibliographicEntityUploadHandler(UploadHandler):
    def pushDataToDb(self, path: str) -> bool:
        bibdf = pd.read_json(path) # opens and reads the JSON file into a dataframe

        entities = [] # empty list that will become the BibliographicEntity table and will contain one row per publication, each with an internalId, title, venue, and publication_date
        authors = [] # empty list that will become BibliographEntityAuthor table and will contain one row per author, each with the author's name and the entityID (internalID) linking back to their publication in the BibliographicEntity table
        ids =[] # empty list that will become the BibliographicEntityID table and will contain one row per identifier, each with the identifier strong and the entityID (internalID) linking back to their publication in the BibliographicEntity table

        for idx, row in bibdf.iterrows():
            internal_id = f"entity-{idx}" # generate a unique ID for each bibliographic entity

            entities.append({
                "internalId": internal_id, # create a column for internalID using previously generated unique ID
                "title": row.get("title"), # create a column for title
                "publication_date": row.get("pub_date"), # create a column for publication date
                "venue": row.get("venue") # create a column for venue
            })
        
            for author in row.get("author", []):
                authors.append({"entityId": internal_id, "author": author}) # create the author table with one column for internalID using previously gnerated unique ID and the author. If no author, [] returns an empty list
        
            for identifier in row.get("id", []): # create the ID table with one column for the internalID using the previously generated unique ID and the doi/OMID/etc. If no ID, [] returns an empty list
                ids.append({"entityID": internal_id, "id": identifier})

        df_entities = pd.DataFrame(entities) # turns the list into a DataFrame object
        df_authors = pd.DataFrame(authors)
        df_ids = pd.DataFrame(ids)

        with sqlite3.connect(self.dbPathOrUrl) as con: # create/open database file
            df_entities.to_sql("BibliographicEntity", con, if_exists="replace", index=False) # write DataFrame object to database as table, if it already exists, overwrite it. Don't include index since we already have internalID
            df_authors.to_sql("BibliographicEntityAuthor", con, if_exists="replace", index=False)
            df_ids.to_sql("BibliographicEntityId", con, if_exists="replace", index=False) 
        
        return True
       

       