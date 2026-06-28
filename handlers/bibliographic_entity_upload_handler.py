import sqlite3
import pandas as pd
from .upload_handler import UploadHandler

class BibliographicEntityUploadHandler(UploadHandler):
    def pushDataToDb(self, path: str) -> bool:
        general_df = pd.read_json(path)

        bibitem_rows = []
        author_rows = []
        authors_in_bibitem_rows = []
        ids_in_bibitem_rows = []

        #print(bibdf)
        author_set = set()
        author_counter = 0
        number_of_bibitems = len(general_df)

        for i, row in general_df.iterrows():
            print(f"Parsing bibliographic entity {i} of {number_of_bibitems}", end="\r")
            bib_item_id = f"bibitem_{i}"
            bibitem_rows.append([bib_item_id, row["title"], row["pub_date"], row["venue"]])
            for pos, author in enumerate(row['author']):
                author_counter += 1
                author_id = f"author_{author_counter}"
                # does not check for dupes
                author_rows.append([author_id, author])
                authors_in_bibitem_rows.append([bib_item_id, author_id, pos])
            for id in row["id"]:
                ids_in_bibitem_rows.append([bib_item_id, id])

        bibitem_df = pd.DataFrame(bibitem_rows, columns=["bib_item_id", "title", "pub_date", "venue"])
        author_df = pd.DataFrame(author_rows, columns=["author_id", "name"])
        authors_in_bibitem_df = pd.DataFrame(authors_in_bibitem_rows, columns=["bibitem_id", "author_id", "pos"])
        ids_in_bibitem_df = pd.DataFrame(ids_in_bibitem_rows, columns=["bibitem_id", "id"])

        print("Writing data into db")

        print(bibitem_df)
        #print(author_df)
        #print(authors_in_bibitem_df)
        #print(ids_in_bibitem_df)
            
        with sqlite3.connect(self.dbPathOrUrl) as con:
            bibitem_df.to_sql('BibliographicEntity', con, if_exists='replace', index=False)
            author_df.to_sql('Author', con, if_exists='replace', index=False)
            authors_in_bibitem_df.to_sql('BibliographicEntityAuthors', con, if_exists='replace', index=False)
            ids_in_bibitem_df.to_sql('BibliographicEntityIDs', con, if_exists='replace', index=False)

        print(f"Done! DB written in {self.dbPathOrUrl}")
        return True

if __name__ == "__main__":
    handler = BibliographicEntityUploadHandler()
    handler.setDbPathOrUrl("relational.db")
    handler.pushDataToDb("data/dh_metadata.json")
       