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

cursor.execute("SELECT * FROM BibliographicEntityAuthor LIMIT 5")
print("=== BibliographicEntityAuthor ===")
for row in cursor.fetchall():
    print(row)

cursor.execute("SELECT * FROM BibliographicEntityId LIMIT 5")
print("=== BibliographicEntityId ===")
for row in cursor.fetchall():
    print(row)

with sqlite3.connect("relational.db") as con:
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print(cursor.fetchall())
    
con.close()