from handlers.citation_query_handler import CitationQueryHandler
from handlers.bibliographic_entity_query_handler import BibliographicEntityQueryHandler
from model.identifiable_entity import IdentifiableEntity
from model.citation import Citation
from model.bibliographic_entity import BibliographicEntity
from model.author_self_citation import AuthorSelfCitation
from model.journal_self_citation import JournalSelfCitation
from typing import Optional

class BasicQueryEngine:
    def __init__(self) -> None:
        self.citationQuery = []
        self.bibliographicEntityQuery = []
    
    def cleanCitationHandlers(self) -> bool:
        self.citationQuery = []
        return True
    
    def cleanBibliographicEntityHandlers(self) -> bool:
        self.bibliographicEntityQuery = []
        return True
    
    def addCitationHandler(self, handler: CitationQueryHandler) -> bool:
        self.citationQuery.append(handler)
        # duplicate check?
        return True
    
    def addBibliographicEntityHandler(self, handler: BibliographicEntityQueryHandler) -> bool:
        self.bibliographicEntityQuery.append(handler)
        return True
    
    def getEntityById(self, id: str) -> IdentifiableEntity | None:
        # placeholder for returning the specific entity object if ID matches, else None
        return None

    def getAllCitations(self) -> list[Citation]:
        # placeholder for looping through citationQuery handler, merge Dataframes, convert into list of Citation objects
        return []
    
    def getAllAuthorSelfCitations(self) -> list[AuthorSelfCitation]:
        return []
    
    def getAllJournalSelfCitations(self) -> list[JournalSelfCitation]:
        return []
    
    def getCitationsWithinTimespan(self, min_timespan: str, max_timespan: str) -> list[Citation]:
        return []
    
    def getCitationsWithinDate(self, start_date: str, end_date: str) -> list[Citation]:
        return []
    
    def getAllBibliographicEntities(self) -> list[BibliographicEntity]:
        # placeholder for looping through bibliographicEntityQuery handler, merge Dataframes, convert into list of Bibliographic Entity objects
        return []
    
    def getBibliographicEntitiesWithTitle(self, title: str) -> list[BibliographicEntity]:
        return []
    
    def getBibliographicEntitiesWithAuthor(self, author: str) -> list[BibliographicEntity]:
        return []
    
    def getBibliographicEntitiesWithinDate(self, start_date: str, end_date: str) -> list[BibliographicEntity]:
        return []
    
    def getBibliographicEntitiesWithVenue(self, venue: str) -> list[BibliographicEntity]:
        return []







        
