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

    def getCitationHandlers(self) -> list[CitationQueryHandler]:
        return self.citationQuery
    
    def addBibliographicEntityHandler(self, handler: BibliographicEntityQueryHandler) -> bool:
        self.bibliographicEntityQuery.append(handler)
        return True
    
    def getEntityById(self, id: str, is_citation: bool = None) -> IdentifiableEntity | None:
        entity = None
        if is_citation is not False:
            for cit_qh in self.citationQuery:
                df = cit_qh.getById(id)
                if not df.empty:
                    row = df.iloc[0]
                    citing = self.getEntityById(row["citing"], False) 
                    cited = self.getEntityById(row["cited"], False)
                    ids = []
                    ids.append(row["oci"])
                    entity = Citation(ids, row["creation"], row["timespan"], citing, cited)

        if entity is None:    
            for bib_qh in self.bibliographicEntityQuery:  # loop through all bibliographic query handlers
                df = bib_qh.getById(id)  # ask the handler to search the relational database for this id
                #print(df)
                if not df.empty:  # if a match was found (dataframe has at least one row)
                    row = df.iloc[0]  # take the first (and should be only) matching row
                    entity = BibliographicEntity(  # build and return a BibliographicEntity object from that row
                        identifiers=row["ids"].split("; ") if pd.notna(row["ids"]) else [],  # split id string into list, or return empty list if none
                        author=row["authors"].split("; ") if pd.notna(row["authors"]) else [],  # split author string into list, or return empty list if none
                        title=row["title"],  # pass title directly
                        publication_date=row["publication_date"],  # pass publication date directly
                        venue=row["venue"],  # pass venue directly
                    )
                    #print(entity.__dict__)
        
        return entity
        
 
    def getAllCitations(self) -> list[Citation]:
        # placeholder for looping through citationQuery handler, merge Dataframes, convert into list of Citation objects
        handlers = self.getCitationHandlers() 
        #df_citations = pd.DataFrame()
        #for handler in handlers:
        #    df_citations =  pd.concat([df_citations, handler.getAllCitations()], ignore_index=True)
        #print(df_citations)

        dataframes: list[pd.DataFrame]  = []
        for handler in handlers:
            new_df = handler.getAllAuthorSelfCitations()
            dataframes.append(new_df)

        df_citations = pd.concat(dataframes, ignore_index=True)

        

        citations = []

        for idx, row in df_citations.iterrows():
            ids = []
            ids.append(row["oci"])
            citing = self.getEntityById(row["citing"], False)
            cited = self.getEntityById(row["cited"], False)
            if not row["author_sc"] and not row["journal_sc"]:
                citations.append(Citation(ids, row["creation"], row["timespan"], citing, cited))
            else:
                if row["author_sc"]:
                    citations.append(AuthorSelfCitation(ids, row["creation"], row["timespan"], citing, cited))
                if row["journal_sc"]:
                    citations.append(JournalSelfCitation(ids, row["creation"], row["timespan"], citing, cited))            
        
        return citations

    
    def getAllAuthorSelfCitations(self) -> list[AuthorSelfCitation]:

        handlers = self.getCitationHandlers()

        dataframes: list[pd.DataFrame]  = []
        for handler in handlers:
            new_df = handler.getAllAuthorSelfCitations()
            dataframes.append(new_df)

        df_citations = pd.concat(dataframes, ignore_index=True)

        citations = []

        for idx, row in df_citations.iterrows():
            ids = []
            ids.append(row["oci"])
            citing = self.getEntityById(row["citing"], False)
            cited = self.getEntityById(row["cited"], False)
            citation = AuthorSelfCitation(ids, row["creation"], row["timespan"], citing, cited)
            citations.append(citation)
        
        #print(len(citations))
        return citations
    
    def getAllJournalSelfCitations(self) -> list[JournalSelfCitation]:
        handlers = self.getCitationHandlers()

        dataframes: list[pd.DataFrame] = []
        for handler in handlers:
            new_df = handler.getAllJournalSelfCitations()
            dataframes.append(new_df)

        df_citations = pd.concat(dataframes, ignore_index=True)
        citations = []

        for idx, row in df_citations.iterrows():
            ids = []
            ids.append(row["oci"])
            citing = self.getEntityById(row["citing"], False)
            cited = self.getEntityById(row["cited"], False)
            citation = JournalSelfCitation(ids, row["creation"], row["timespan"], citing, cited)
            citations.append(citation)
        #print(len(citations))
        return citations
    
    def getCitationsWithinTimespan(self, min_timespan: str = None, max_timespan: str = None) -> list[Citation]:
        handlers = self.getCitationHandlers()
        #df_citations = pd.DataFrame()
        #for handler in handlers:
        #    df_citations =  pd.concat([df_citations, handler.getCitationsWithinTimespan(min_timespan, max_timespan)], ignore_index=True)
        #print(df_citations)

        dataframes: list[pd.DataFrame]  = []
        for handler in handlers:
            new_df = handler.getCitationsWithinTimespan(min_timespan, max_timespan)
            dataframes.append(new_df)

        df_citations = pd.concat(dataframes, ignore_index=True)

        citations = []

        for idx, row in df_citations.iterrows():
            ids = []
            ids.append(row["oci"])
            citing = self.getEntityById(row["citing"], False)
            cited = self.getEntityById(row["cited"], False)
            if row["author_sc"]:
                citation = AuthorSelfCitation(ids, row["creation"], row["timespan"], citing, cited)
            elif row["journal_sc"]:
                citation = JournalSelfCitation(ids, row["creation"], row["timespan"], citing, cited)
            else:
                citation = Citation(ids, row["creation"], row["timespan"], citing, cited)
            citations.append(citation)
        #print(len(citations))
        return citations

    def getCitationsWithinDate(self, start_date: str = None, end_date: str = None) -> list[Citation]:
        handlers = self.getCitationHandlers()
        dataframes: list[pd.DataFrame]  = []
        for handler in handlers:
            new_df = handler.getCitationsWithinDate(start_date, end_date)
            dataframes.append(new_df)

        df_citations = pd.concat(dataframes, ignore_index=True)
        citations = []

        for idx, row in df_citations.iterrows():
            ids = []
            ids.append(row["oci"])
            citing = self.getEntityById(row["citing"], False)
            cited = self.getEntityById(row["cited"], False)
            if row["author_sc"]:
                citation = AuthorSelfCitation(ids, row["creation"], row["timespan"], citing, cited)
            elif row["journal_sc"]:
                citation = JournalSelfCitation(ids, row["creation"], row["timespan"], citing, cited)
            else:
                citation = Citation(ids, row["creation"], row["timespan"], citing, cited)
            citations.append(citation)
        #print(len(citations))
        return citations
    
    def getAllBibliographicEntities(self) -> list[BibliographicEntity]:
        result = []
        for bib_qh in self.bibliographicEntityQuery:
            df = bib_qh.getAllBibliographicEntities() # calls query handler's getAllBibiliographicEntities method
            for i, row in df.iterrows(): # loops through every row
                result.append(BibliographicEntity( # adds an object for each row that contains the list of IDs, list of authors, the title, pub date, and venue of each row
                    identifiers=row["ids"].split("; ") if pd.notna(row["ids"]) else [], #if there are no ids, it will return a blank list instead of NaN
                    author=row["authors"].split("; ") if pd.notna(row["authors"]) else [],  #if there are no authors, it will return a blank list instead of NaN 
                    title=row["title"],
                    publication_date=row["publication_date"],
                    venue=row["venue"],
                ))
        return result
     
    
    def getBibliographicEntitiesWithTitle(self, title: str) -> list[BibliographicEntity]:
        result = []
        for bib_qh in self.bibliographicEntityQuery:
            df = bib_qh.getBibliographicEntitiesWithTitle(title) # calls query handler's getAllBibiliographicEntitiesWithTitle method
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
            df = bib_qh.getBibliographicEntitiesWithAuthor(author) # calls query handler's getAllBibiliographicEntitiesWithAuthor method
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
            df = bib_qh.getBibliographicEntitiesWithinPublicationDate(start_date, end_date) # calls query handler's getAllBibiliographicEntitiesWithinPublicationDate method
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
            df = bib_qh.getBibliographicEntitiesWithVenue(venue) # calls query handler's getAllBibiliographicEntitiesWithVenue method
            for i, row in df.iterrows(): # loops through every row
                result.append(BibliographicEntity( # adds an object for each row that contains the list of IDs, list of authors, the title, pub date, and venue of each row
                    identifiers=row["ids"].split("; ") if pd.notna(row["ids"]) else [],
                    author=row["authors"].split("; ") if pd.notna(row["authors"]) else [],  
                    title=row["title"],
                    publication_date=row["publication_date"],
                    venue=row["venue"],
                ))
        return result

if __name__ == "__main__":
    cit_qh = CitationQueryHandler()
    cit_qh.setDbPathOrUrl("http://localhost:9999/blazegraph/sparql")
    bib_qh = BibliographicEntityQueryHandler()
    bib_qh.setDbPathOrUrl("relational.db")
    que = BasicQueryEngine()
    que.addCitationHandler(cit_qh)
    que.addBibliographicEntityHandler(bib_qh)
    #print(que.bibliographicEntityQuery)
    #print(que.citationQuery)
    #que.getAllCitations()
    #print(que.getEntityById("0603926682-06160449684").__dict__)

        #que.getAllAuthorSelfCitations()
    #que.getAllJournalSelfCitations()
    res = que.getCitationsWithinTimespan("P1Y", "P4Y")
    print(len(res))
    # que.getCitationsWithinDate()


        
