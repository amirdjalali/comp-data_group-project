from handlers.citation_query_handler import CitationQueryHandler
from handlers.bibliographic_entity_query_handler import BibliographicEntityQueryHandler
from model.identifiable_entity import IdentifiableEntity
from model.citation import Citation
from model.bibliographic_entity import BibliographicEntity
from model.author_self_citation import AuthorSelfCitation
from model.journal_self_citation import JournalSelfCitation
from typing import Optional
import pandas as pd

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
    
    def getCitationHandlers(self) -> list:
        return self.citationQuery
    
    def addBibliographicEntityHandler(self, handler: BibliographicEntityQueryHandler) -> bool:
        self.bibliographicEntityQuery.append(handler)
        return True
    
    def getEntityById(self, id: str) -> IdentifiableEntity | None:
        # placeholder for returning the specific entity object if ID matches, else None
        return None

    def getAllCitations(self) -> list[Citation]:
        # placeholder for looping through citationQuery handler, merge Dataframes, convert into list of Citation objects
        handlers = self.getCitationHandlers() 
        df_citations = pd.DataFrame()
        for handler in handlers:
            df_citations =  pd.concat([df_citations, handler.getAllCitations()], ignore_index=True)
        print(df_citations)

        citations = []

        for idx, row in df_citations.iterrows():
            ids = []
            ids.append(row["oci"])
            if not row["author_sc"] and not row["journal_sc"]:
                citations.append(Citation(ids, row["creation"], row["timespan"], row["citing"], row["cited"]))
            else:
                if row["author_sc"]:
                    citations.append(AuthorSelfCitation(ids, row["creation"], row["timespan"], row["citing"], row["cited"]))
                if row["journal_sc"]:
                    citations.append(JournalSelfCitation(ids, row["creation"], row["timespan"], row["citing"], row["cited"]))            
        
        print(len(citations))
        return citations

    
    def getAllAuthorSelfCitations(self) -> list[AuthorSelfCitation]:
        handlers = self.getCitationHandlers()
        df_citations = pd.DataFrame()
        for handler in handlers:
            df_citations =  pd.concat([df_citations, handler.getAllAuthorSelfCitations()], ignore_index=True)
        print(df_citations)

        citations = []

        for idx, row in df_citations.iterrows():
            ids = []
            ids.append(row["oci"])
            citation = AuthorSelfCitation(ids, row["creation"], row["timespan"], row["citing"], row["cited"])
            citations.append(citation)
        
        print(len(citations))
        return citations
    
    def getAllJournalSelfCitations(self) -> list[JournalSelfCitation]:
        handlers = self.getCitationHandlers()
        df_citations = pd.DataFrame()
        for handler in handlers:
            df_citations =  pd.concat([df_citations, handler.getAllJournalSelfCitations()], ignore_index=True)
        print(df_citations)
        citations = []

        for idx, row in df_citations.iterrows():
            ids = []
            ids.append(row["oci"])
            citation = JournalSelfCitation(ids, row["creation"], row["timespan"], row["citing"], row["cited"])
            citations.append(citation)
        print(len(citations))
        return citations
    
    def getCitationsWithinTimespan(self, min_timespan: str = None, max_timespan: str = None) -> list[Citation]:
        handlers = self.getCitationHandlers()
        df_citations = pd.DataFrame()
        for handler in handlers:
            df_citations =  pd.concat([df_citations, handler.getCitationsWithinTimespan(min_timespan, max_timespan)], ignore_index=True)
        print(df_citations)
        citations = []

        for idx, row in df_citations.iterrows():
            ids = []
            ids.append(row["oci"])
            if row["author_sc"]:
                citation = AuthorSelfCitation(ids, row["creation"], row["timespan"], row["citing"], row["cited"])
            elif row["journal_sc"]:
                citation = JournalSelfCitation(ids, row["creation"], row["timespan"], row["citing"], row["cited"])
            else:
                citation = Citation(ids, row["creation"], row["timespan"], row["citing"], row["cited"])
            citations.append(citation)
        print(len(citations))
        return citations

    def getCitationsWithinDate(self, start_date: str = None, end_date: str = None) -> list[Citation]:
        handlers = self.getCitationHandlers()
        df_citations = pd.DataFrame()
        for handler in handlers:
            df_citations =  pd.concat([df_citations, handler.getCitationsWithinDate(min_timespan, max_timespan)], ignore_index=True)
        print(df_citations)
        citations = []

        for idx, row in df_citations.iterrows():
            ids = []
            ids.append(row["oci"])
            if row["author_sc"]:
                citation = AuthorSelfCitation(ids, row["creation"], row["timespan"], row["citing"], row["cited"])
            elif row["journal_sc"]:
                citation = JournalSelfCitation(ids, row["creation"], row["timespan"], row["citing"], row["cited"])
            else:
                citation = Citation(ids, row["creation"], row["timespan"], row["citing"], row["cited"])
            citations.append(citation)
        print(len(citations))
        return citations
    
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


if __name__ == "__main__":
    cit_qh = CitationQueryHandler()
    cit_qh.setDbPathOrUrl("http://localhost:9999/blazegraph/sparql")
    que = BasicQueryEngine()
    que.addCitationHandler(cit_qh)
    # que.getAllCitations()
    #que.getAllAuthorSelfCitations()
    que.getAllJournalSelfCitations()
    # que.getCitationsWithinTimespan()
    # que.getCitationsWithinDate()



