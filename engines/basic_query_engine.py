import pandas as pd
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
        result = []
        for bib_qh in self.bibliographicEntityQuery:
            df = bib_qh.getAllBibliographicEntities() # calls query handler's getAllBibiliographicEntities method
            for i, row in df.iterrows(): # loops through every row
                result.append(BibliographicEntity( # adds an object for each row that contains the list of IDs, list of authors, the title, pub date, and venue of each row
                    identifiers=row["ids"].split("; ") if pd.notna(row["ids"]) else [],
                    author=row["authors"].split("; ") if pd.notna(row["authors"]) else [],  
                    title=row["title"],
                    publication_date=row["publication_date"],
                    venue=row["venue"],
                ))
        return result
     
    
    def getBibliographicEntitiesWithTitle(self, title: str) -> list[BibliographicEntity]:
        result = []
        for bib_qh in self.bibliographicEntityQuery:
            df = bib_qh.getBibliographicEntitiesWithTitle(title) # calls query handler's getAllBibiliographicEntities method
            for i, row in df.iterrows(): # loops through every row
                result.append(BibliographicEntity( # adds an object for each row that contains the list of IDs, list of authors, the title, pub date, and venue of each row
                    identifiers=row["ids"].split("; ") if pd.notna(row["ids"]) else [],
                    author=row["authors"].split("; ") if pd.notna(row["authors"]) else [],  
                    title=row["title"],
                    publication_date=row["publication_date"],
                    venue=row["venue"],
                ))
        return result

    
    def getBibliographicEntitiesWithAuthor(self, author: str) -> list[BibliographicEntity]:
        result = []
        for bib_qh in self.bibliographicEntityQuery:
            df = bib_qh.getBibliographicEntitiesWithAuthor(author) # calls query handler's getAllBibiliographicEntities method
            for i, row in df.iterrows(): # loops through every row
                result.append(BibliographicEntity( # adds an object for each row that contains the list of IDs, list of authors, the title, pub date, and venue of each row
                    identifiers=row["ids"].split("; ") if pd.notna(row["ids"]) else [],
                    author=row["authors"].split("; ") if pd.notna(row["authors"]) else [],  
                    title=row["title"],
                    publication_date=row["publication_date"],
                    venue=row["venue"],
                ))
        return result
    
    def getBibliographicEntitiesWithinPublicationDate(self, start_date: str, end_date: str) -> list[BibliographicEntity]:
        result = []
        for bib_qh in self.bibliographicEntityQuery:
            df = bib_qh.getBibliographicEntitiesWithinPublicationDate(start_date, end_date) # calls query handler's getAllBibiliographicEntities method
            for i, row in df.iterrows(): # loops through every row
                result.append(BibliographicEntity( # adds an object for each row that contains the list of IDs, list of authors, the title, pub date, and venue of each row
                    identifiers=row["ids"].split("; ") if pd.notna(row["ids"]) else [],
                    author=row["authors"].split("; ") if pd.notna(row["authors"]) else [],  
                    title=row["title"],
                    publication_date=row["publication_date"],
                    venue=row["venue"],
                ))
        return result
    
    def getBibliographicEntitiesWithVenue(self, venue: str) -> list[BibliographicEntity]:
        result = []
        for bib_qh in self.bibliographicEntityQuery:
            df = bib_qh.getBibliographicEntitiesWithVenue(venue) # calls query handler's getAllBibiliographicEntities method
            for i, row in df.iterrows(): # loops through every row
                result.append(BibliographicEntity( # adds an object for each row that contains the list of IDs, list of authors, the title, pub date, and venue of each row
                    identifiers=row["ids"].split("; ") if pd.notna(row["ids"]) else [],
                    author=row["authors"].split("; ") if pd.notna(row["authors"]) else [],  
                    title=row["title"],
                    publication_date=row["publication_date"],
                    venue=row["venue"],
                ))
        return result




        
