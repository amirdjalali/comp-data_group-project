from handlers.bibliographic_entity_query_handler import BibliographicEntityQueryHandler
from engines.basic_query_engine import BasicQueryEngine

cq = BibliographicEntityQueryHandler()
cq.setDbPathOrUrl("./relational.db")

engine = BasicQueryEngine()
engine.addBibliographicEntityHandler(cq)

print("--- getAllBibliographicEntities ---")
r = engine.getAllBibliographicEntities()
print(type(r), len(r))
print(r[0].getTitle())
print(r[0].getAuthors())
print(r[0].getIds())

print("--- getBibliographicEntitiesWithTitle ---")
r = engine.getBibliographicEntitiesWithTitle("Machine learning")
print(type(r), len(r))
print(r[0].getTitle())

print("--- getBibliographicEntitiesWithAuthor ---")
r = engine.getBibliographicEntitiesWithAuthor("Rossi")
print(type(r), len(r))
print(r[0].getAuthors())
print(r[0].getTitle())

print("--- getBibliographicEntitiesWithinPublicationDate ---")
r = engine.getBibliographicEntitiesWithinPublicationDate("2022", "2024")
print(type(r), len(r))
print(r[0].getPublicationDate())
print(r[0].getAuthors())
print(r[0].getTitle())

print("--- getBibliographicEntitiesWithVenue ---")
r = engine.getBibliographicEntitiesWithVenue("Digital Scholarship In The Humanities")
print(type(r), len(r))
print(r[0].getVenue())
print(r[0].getPublicationDate())
print(r[0].getAuthors())
print(r[0].getTitle())