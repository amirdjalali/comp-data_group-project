from identifiable_entity import IdentifiableEntity
from bibliographic_entity import BibliographicEntity

class Citation(IdentifiableEntity):
    def __init__(self, identifiers: list[str], creation: str, timespan: str, citing_entity: BibliographicEntity, cited_entity: BibliographicEntity) -> None:
        super().__init__(identifiers)
        self.creation = creation
        self.timespan = timespan
        self.citing_entity = citing_entity
        self.cited_entity = cited_entity
    
    def getCreation(self) -> str:
        return self.creation
    
    def getTimespan(self) -> str:
        return self.timespan
    
    def getCitingEntity(self) -> BibliographicEntity:
        return self.citing_entity
    
    def getCitedEntity(self) -> BibliographicEntity:
        return self.cited_entity