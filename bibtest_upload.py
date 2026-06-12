from handlers.bibliographic_entity_upload_handler import BibliographicEntityUploadHandler
import sqlite3

be = BibliographicEntityUploadHandler()
be.setDbPathOrUrl("relational.db")
be.pushDataToDb("data/dh_metadata.json")

con = sqlite3.connect("relational.db")
cursor = con.cursor()
cursor.execute("SELECT * FROM BibliographicEntity LIMIT 5")
rows = cursor.fetchall()
for row in rows:
    print(row)
con.close()