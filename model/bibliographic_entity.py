from identifiable_entity import IdentifiableEntity

class BibliographicEntity(IdentifiableEntity):
    def __init__(self, identifiers: list[str], title: str, author: list[str], publication_date: str, venue: str) -> None:
        super().__init__(identifiers)
        self.title = title
        self.author = author
        self.publication_date = publication_date
        self.venue = venue

    def getTitle(self) -> str:
        return self.title
    
    def getAuthors(self) -> list[str]:
        return self.author
    
    def getPublicationDate(self) -> str:
        return self.publication_date
    
    def getVenue(self) -> str:
        return self.venue