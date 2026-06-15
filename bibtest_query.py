from handlers.bibliographic_entity_query_handler import BibliographicEntityQueryHandler

bq = BibliographicEntityQueryHandler()
bq.setDbPathOrUrl("relational.db")

print("=== getAllBibliographicEntities ===")
print(bq.getAllBibliographicEntities().head())

print("=== getBibliographicEntitiesWithTitle ===")
print(bq.getBibliographicEntitiesWithTitle("Digital").head())

print("=== getBibliographicEntitiesWithVenue ===")
print(bq.getBibliographicEntitiesWithVenue("Proceedings").head())

print("=== getBibliographicEntitiesWithinPublicationDate ===")
print(bq.getBibliographicEntitiesWithinPublicationDate(start_date="2020", end_date="2023").head())

print("=== getBibliographicEntitiesWithAuthor ===")
print(bq.getBibliographicEntitiesWithAuthor("Smith").head())

print("=== getById ===")
print(bq.getById("doi:10.1002/pra2.714"))