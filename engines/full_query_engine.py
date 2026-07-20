from .basic_query_engine import BasicQueryEngine
from model.author_self_citation import AuthorSelfCitation
from model.journal_self_citation import JournalSelfCitation
from model.citation import Citation

class FullQueryEngine(BasicQueryEngine):

    def getAuthorSelfCitationsByName(self, author_name: str) -> list[AuthorSelfCitation]:

        #create a list to store the author self-citations
        author_self_citations = []

        #create variables to store the list of all the author self-citations and the bibliographic entities associated with the author
        all_author_self_citations = self.getAllAuthorSelfCitations()
        author_bib_entities = self.getBibliographicEntitiesWithAuthor(author_name)

        entities_set = set()

        #loop through the bibliographic entities associated with the author and add their IDs to the set 
        for author_entity in author_bib_entities:   
            entities_set.update(author_entity.getIds())
        
        #if the author has no bibliographic entities associated with them, return an empty list
        if not entities_set:
            return []
    
        #loop through the list of all the author self-citations and check if both citing and cited entities belong to the  (i.e. if both citing and cited entity's id is in the set). If so, then append to the list "author_self_citations"
        for citation in all_author_self_citations:
            
            citing_entity = citation.getCitingEntity()
            cited_entity = citation.getCitedEntity()

            if citing_entity is not None and cited_entity is not None:
                has_citing_entity = False
                has_cited_entity = False

                for id in citing_entity.getIds():
                    if id in entities_set:
                        has_citing_entity = True
                        
                for id in cited_entity.getIds():
                    if id in entities_set:
                        has_cited_entity = True
                        
                if has_citing_entity and has_cited_entity:
                    author_self_citations.append(citation)

        return author_self_citations
    

    def getJournalSelfCitationsByName(self, journal_name: str) -> list[JournalSelfCitation]:

        #create a list to store the journal self-citations
        journal_self_citations = []

        #create variables to store the list of all the journal self-citations and the bibliographic entities published by the same venue
        all_journal_self_citations = self.getAllJournalSelfCitations()
        journal_bib_entities = self.getBibliographicEntitiesWithVenue(journal_name)

        entities_set = set()

        #loop through the bibliographic entities associated with the venue and add their IDs to the set
        for journal_entity in journal_bib_entities:
            entities_set.update(journal_entity.getIds())

        #if the venue has no bibliographic entities associated with it, return an empty list
        if not entities_set:
            return []
        
        #loop through the list of all the journal self-citations and check if both citing and cited entities belong to the same venue (i.e. are stored inside of the set containing the BEs' IDs filtered by venue). If so, then append to the list "journal_self_citations"
        for citation in all_journal_self_citations:
           
            citing_entity = citation.getCitingEntity()
            cited_entity = citation.getCitedEntity()

            if citing_entity is not None and cited_entity is not None:
                has_citing = False
                has_cited = False

                for id in citing_entity.getIds():
                    if id in entities_set:
                        has_citing = True

                for id in cited_entity.getIds():
                    if id in entities_set:
                        has_cited = True

                if has_citing and has_cited:
                    journal_self_citations.append(citation)

        return journal_self_citations
    

    def getCitationsOfBibEntityByTitleWithinDate(self, bib_entity_title: str, min_date: str, max_date: str) -> list[Citation]:

        #create a list to store the citations of BEs filtered by title and by creation of said citation
        citations_of_bib_entity_within_date = []

        #create variables to store the list of all the matching BEs's title and the citations created within the min and max date
        bib_entities_with_title = self.getBibliographicEntitiesWithTitle(bib_entity_title)
        citations_within_date = self.getCitationsWithinDate(min_date, max_date)

        #creating a set and adding all of the ids of each BE
        entities_id_set = set()

        for entity in bib_entities_with_title:
            entities_id_set.update(entity.getIds())

        #if the set is empty, return an empty list
        if not entities_id_set:
            return []
        
        #looping through the citations filtered by date
        for citation in citations_within_date:

            cited_entity = citation.getCitedEntity()

            #checking if the citation has a BE object as cited entity in case of some missing data
            if cited_entity is not None:

                #setting to False the matching of the ID, looping through the ids of the cited entity and appending it to the result list if al least one of them is present in the set
                has_matching_id = False

                for cited_id in cited_entity.getIds():
                    if cited_id in entities_id_set:
                        has_matching_id = True
                
                if has_matching_id:
                    citations_of_bib_entity_within_date.append(citation)

        return citations_of_bib_entity_within_date
        
    
    def getReferencesOfBibEntityByTitleWithinTimespan(self, bib_entity_title: str, min_timespan: str, max_timespan: str) -> list[Citation]:
        #create a list to store the citations of BEs filtered by title and by creation of said citation
        references_of_bib_entity_within_timespan = []

        #create variables to store the list of all the citations within the input timespan and the bibliographic entities which match or contain the input title in their title
        citations_within_timespan = self.getCitationsWithinTimespan(min_timespan,max_timespan)
        bib_entities_with_title = self.getBibliographicEntitiesWithTitle(bib_entity_title)

        #creating a set and looping through the list of the BEs for storing their titles in the set
        entities_set = set()

        for bib_entity in bib_entities_with_title:
            entities_set.update(bib_entity.getIds())

        #looping through the citations filtered by timespan and checking if the citing entity's id is inside the set of BEs id with matching title. If so, then append to the result list
        for citation in citations_within_timespan:
            
            citing_entity = citation.getCitingEntity()

            if citing_entity is not None:

                has_matching_id = False

                for citation_id in citing_entity.getIds():

                    if citation_id in entities_set:
                        has_matching_id = True

                if has_matching_id:
                    references_of_bib_entity_within_timespan.append(citation)
            
        return references_of_bib_entity_within_timespan


    if __name__ == "__main__":
        from handlers.bibliographic_entity_query_handler import BibliographicEntityQueryHandler
        from handlers.citation_query_handler import CitationQueryHandler
        from engines.full_query_engine import FullQueryEngine
        from model import bibliographic_entity
        
        # 1. Configurazione dei due Handler
        bib_qh = BibliographicEntityQueryHandler()
        bib_qh.setDbPathOrUrl("relational.db")
        
        cit_qh = CitationQueryHandler()
        cit_qh.setDbPathOrUrl("http://localhost:9999/blazegraph/sparql")
        
        # 2. Inizializzazione del FullQueryEngine
        que = FullQueryEngine()
        que.addBibliographicEntityHandler(bib_qh)
        que.addCitationHandler(cit_qh)
        
        # 3. Esecuzione

        #res = que.getAuthorSelfCitationsByNam("Dan")
        #res = que.getAuthorSelfCitationsByName("Bostenaru")
        
        #res = que.getJournalSelfCitationsByName("Digital Scholarship In The Humanities")

        res = que.getCitationsOfBibEntityByTitleWithinDate("sick", "2016", "2018")

        #res = que.getReferencesOfBibEntityByTitleWithinTimespan("Beyond The One-Shot", "P1Y", "P4Y")

        #res1 = que.getCitationsOfBibEntityByTitleWithinDate("Teaching, Learning And Research In Final Year Humanities Computing Student Projects","2003", "2006")
        #res2 = que.getCitationsOfBibEntityByTitleWithinDat("Tree, Turf, Centre, Archipelago—or Wild Acre?  Metaphors And Stories For Humanities Computing121 For Sinéad O'Sullivan.2 This Essay Was Originally Delivered As A Plenary Address At ‘Computing Arts 2004’, Centre For Literary And Linguistic Computing, University Of Newcastle, NSW Australia, Www.Newcastle.Edu.Au/Centre/Cllc/Ca2004/. My Thanks To The Organizer, Professor Hugh Craig, For His Many Kindnesses And Patience, To The Anonymous Reviewers Who Stimulated Me To Improve The First Attempt And To John Burrows For Advice On The Connotations Of Words. All URLs Have Been Verified As Of 29 July 2005.","2004", "2006")

        #res = que.getJournalSelfCitationsByName("Industry And Higher Education")

        # 4. Stampe di controllo
        #print(f"il tipo è: {type(res[0])}")
        #print(res)
        
        print(len(res))
        #print(len(res2))
        
        print("PRIMO RISULTATO")
        for i in res:
            print(i.__dict__)
        #print("SECONDO RISULTATO")
        #for i in res2:
        #    print(i.__dict__)

        #print(type(res[0]))
        #x = 1
        #for i in res:
        #    print(f"citazione numero {x} \n")
        #    print(i.getCitingEntity().getVenue())
        #    print(i.getCitedEntity().getVenue())
        #for i in res:
        #    print(f"citazione numero {x}")
        #    print(i.getCitingEntity().getTitle())
        #    print(i.getCitedEntity().getTitle())
        #    x+=1
            #print(i.__dict__)
        
        #for i in res2:
        #    print("citation:\n")
        #    print(i.getCitedEntity().getAuthors(),i.getIds())
        #print(f"\n ci sono: {len(res)} risultati")
        #print(f"Il tipo di getcitingentity: {type(res[0].getCitingEntity())}")
        #if res:
            #print(res[0].getCitingEntity().getIds())
            #print(res[0].getCitedEntity().getIds())