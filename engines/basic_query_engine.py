import pandas as pd
from handlers.citation_query_handler import CitationQueryHandler
from handlers.bibliographic_entity_query_handler import BibliographicEntityQueryHandler
from model.identifiable_entity import IdentifiableEntity
from model.citation import Citation
from model.bibliographic_entity import BibliographicEntity
from model.author_self_citation import AuthorSelfCitation
from model.journal_self_citation import JournalSelfCitation
from typing import Optional
from functools import lru_cache
import json

class BasicQueryEngine:
    def __init__(self) -> None:
        self.citationQuery = []
        self.bibliographicEntityQuery = []

        # this is the cache dictionary which is used to store entities by ids,
        # in order to speed up entity lookup by id
        # The leading underscore is just a convetion to show that the attribute will
        # only be used internally
        
        self._entity_cache: dict[str, IdentifiableEntity] = {}
    
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

    # added this, but actually one could just call self.citationQuery

    def getCitationHandlers(self) -> list[CitationQueryHandler]:
        return self.citationQuery
    
    def addBibliographicEntityHandler(self, handler: BibliographicEntityQueryHandler) -> bool:
        self.bibliographicEntityQuery.append(handler)
        return True
    
    def getEntityById(self, id: str, is_citation: bool = None) -> IdentifiableEntity | None:
        # is_citation optional argument is used only when calling getEntityById 
        # when looking up bibliographic entities to complete citation etities.
        # This skips looking the id in the citationQuery, looking them up directly in the 
        # bibliographicEntityQuery. This also constitutes a sort of "base case" for recursion
        
        # Check cache first. If entity with that id is already stored, just return it!
        if id in self._entity_cache:
            return self._entity_cache[id]
        
        entity = None
        
        # if is_citation is True or None, look first into citations
        if is_citation is not False:
            for cit_qh in self.citationQuery:
                df = cit_qh.getById(id)
                if not df.empty:
                    row = df.iloc[0] # pick the first (and perhaps only) result
                    # recursive step! check for citing and cited bibliographic entities
                    citing = self.getEntityById(row["citing"], False)
                    cited = self.getEntityById(row["cited"], False)
                    # citations have only one id, but we store it in a list anyways
                    ids = []
                    ids.append(row["oci"])
                    # Create the actual citation entity. Calling each of the attributes explicitly by name
                    # in the constructor makes the code more robust, in case new attributes are added later
                    entity = Citation(identifiers= ids,
                                      creation=row["creation"],
                                      timespan=row["timespan"],
                                      citing_entity=citing,
                                      cited_entity=cited)

                    self._entity_cache[id] = entity
                    return entity

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
        
        # first add the entity, even if it's None, to the cache dictionary, then return it
        self._entity_cache[id] = entity
        return entity
        
    def getAllCitations(self) -> list[Citation]:
        # retrieve DataFrames from all citation handlers
        handlers = self.getCitationHandlers() 

        dataframes: list[pd.DataFrame]  = []

        for handler in handlers:
            new_df = handler.getAllCitations()
            dataframes.append(new_df)

        # concatenate the results from all citation handlers in a single DataFrame
        df_citations = pd.concat(dataframes, ignore_index=True)

        # prepare a list of citation
        citations = []

        # iterate over citations and instantiate the appropriate object type
        for idx, row in df_citations.iterrows():
            ids = []
            ids.append(row["oci"])
            citing = self.getEntityById(row["citing"], False)
            cited = self.getEntityById(row["cited"], False)

            # prioritizing AuthorSelfCitation if a citation meets both self-citation conditions
            if row["author_sc"]:
                citation = AuthorSelfCitation(identifiers=ids,
                                              creation=row["creation"],
                                              timespan=row["timespan"],
                                              citing_entity=citing,
                                              cited_entity=cited)
            elif row["journal_sc"]:
                citation = JournalSelfCitation(identifiers=ids,
                                               creation=row["creation"],
                                               timespan=row["timespan"],
                                               citing_entity=citing,
                                               cited_entity=cited)
            else:
                citation = Citation(identifiers=ids,
                                               creation=row["creation"],
                                               timespan=row["timespan"],
                                               citing_entity=citing,
                                               cited_entity=cited)
            citations.append(citation)         
        
        return citations
    
    def getAllAuthorSelfCitations(self) -> list[AuthorSelfCitation]:
        # retrieve author self-citation DataFrames from all citation handlers
        handlers = self.getCitationHandlers()

        # create a list of dataframes first, then concatenate them later
        dataframes: list[pd.DataFrame]  = []
        for handler in handlers:
            new_df = handler.getAllAuthorSelfCitations()
            dataframes.append(new_df)

        # concatenate the results from all citation handlers in a single DataFrame
        df_citations = pd.concat(dataframes, ignore_index=True)

        # prepare a list of citation
        citations = []

        # iterate over citations and instantiate the appropriate object type
        for idx, row in df_citations.iterrows():
            ids = []
            ids.append(row["oci"])
            citing = self.getEntityById(row["citing"], False)
            cited = self.getEntityById(row["cited"], False)
            citation = AuthorSelfCitation(identifiers=ids,
                                          creation=row["creation"],
                                          timespan=row["timespan"],
                                          citing_entity=citing,
                                          cited_entity=cited)
            citations.append(citation)
        return citations
    
    def getAllJournalSelfCitations(self) -> list[JournalSelfCitation]:
        # retrieve journal self-citation DataFrames from all citation handlers
        handlers = self.getCitationHandlers()

        dataframes: list[pd.DataFrame] = []

        for handler in handlers:
            new_df = handler.getAllJournalSelfCitations()
            dataframes.append(new_df)

        # concatenate the results from all citation handlers in a single DataFrame
        df_citations = pd.concat(dataframes, ignore_index=True)

        # prepare a list of citation
        citations = []

        # iterate over citations and instantiate the appropriate object type
        for idx, row in df_citations.iterrows():
            ids = []
            ids.append(row["oci"])
            citing = self.getEntityById(row["citing"], False)
            cited = self.getEntityById(row["cited"], False)
            citation = JournalSelfCitation(identifiers=ids,
                                           creation=row["creation"],
                                           timespan=row["timespan"],
                                           citing_entity=citing,
                                           cited_entity=cited)
            citations.append(citation)
        return citations
    
    def getCitationsWithinTimespan(self, min_timespan: str = None, max_timespan: str = None) -> list[Citation]:
        # retrieve filtered DataFrames from all citation handlers
        handlers = self.getCitationHandlers()

        dataframes: list[pd.DataFrame]  = []

        for handler in handlers:
            new_df = handler.getCitationsWithinTimespan(min_timespan, max_timespan)
            dataframes.append(new_df)

        # concatenate the results from all citation handlers in a single DataFrame
        df_citations = pd.concat(dataframes, ignore_index=True)

        # prepare a list of citation
        citations = []

        # iterate over citations and instantiate the appropriate object type
        for idx, row in df_citations.iterrows():
            ids = []
            ids.append(row["oci"])
            citing = self.getEntityById(row["citing"], False)
            cited = self.getEntityById(row["cited"], False)
            if row["author_sc"]:
                citation = AuthorSelfCitation(identifiers=ids,
                                              creation=row["creation"],
                                              timespan=row["timespan"],
                                              citing_entity=citing,
                                              cited_entity=cited)
            elif row["journal_sc"]:
                citation = JournalSelfCitation(identifiers=ids,
                                               creation=row["creation"],
                                               timespan=row["timespan"],
                                               citing_entity=citing,
                                               cited_entity=cited)
            else:
                citation = Citation(identifiers=ids,
                                               creation=row["creation"],
                                               timespan=row["timespan"],
                                               citing_entity=citing,
                                               cited_entity=cited)
            citations.append(citation)
        return citations

    def getCitationsWithinDate(self, start_date: str = None, end_date: str = None) -> list[Citation]:
        # retrieve filtered DataFrames from all citation handlers
        handlers = self.getCitationHandlers()

        dataframes: list[pd.DataFrame]  = []

        for handler in handlers:
            new_df = handler.getCitationsWithinDate(start_date, end_date)
            dataframes.append(new_df)

        # concatenate the results from all citation handlers in a single DataFrame
        df_citations = pd.concat(dataframes, ignore_index=True)

        # prepare a list of citation
        citations = []

        # iterate over citations and instantiate the appropriate object type
        for idx, row in df_citations.iterrows():
            ids = []
            ids.append(row["oci"])
            citing = self.getEntityById(row["citing"], False)
            cited = self.getEntityById(row["cited"], False)
            if row["author_sc"]:
                citation = AuthorSelfCitation(identifiers=ids,
                                              creation=row["creation"],
                                              timespan=row["timespan"],
                                              citing_entity=citing,
                                              cited_entity=cited)
            elif row["journal_sc"]:
                citation = JournalSelfCitation(identifiers=ids,
                                               creation=row["creation"],
                                               timespan=row["timespan"],
                                               citing_entity=citing,
                                               cited_entity=cited)
            else:
                citation = Citation(identifiers=ids,
                                               creation=row["creation"],
                                               timespan=row["timespan"],
                                               citing_entity=citing,
                                               cited_entity=cited)
            citations.append(citation)
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
    
    def getBibliographicEntitiesWithinPublicationDate(self, start_date: str = None, end_date: str = None) -> list[BibliographicEntity]:
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


        
