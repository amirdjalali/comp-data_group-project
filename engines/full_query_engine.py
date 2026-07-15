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

        #creating a dictionary to map the IDs to their respective full bibliographic entities
        entities_dict = dict()

        #loop through the bibliographic entities associated with the author and add their IDs to the dictionary with the corresponding BibliographicEntity object as the value
        for author_entity in author_bib_entities:
            
            for id in author_entity.getIds():
                entities_dict[id] = author_entity
        
        #if the author has no bibliographic entities associated with them, return an empty list
        if not entities_dict:
            return []
    

        #loop through the list of all the author self-citations and check if both citing and cited entities belong to the author. If so, then append to the list "author_self_citations"
        for citation in all_author_self_citations:
            
            citing_entity = citation.getCitingEntity()
            cited_entity = citation.getCitedEntity()

            has_citing_entity = 0
            has_cited_entity = 0

            for id in citing_entity.getIds():
                if id in entities_dict:
                    has_citing_entity += 1
                    

            for id in cited_entity.getIds():
                if id in entities_dict:
                    has_cited_entity += 1
                    
            if has_citing_entity and has_cited_entity:
                author_self_citations.append(citation)

        return author_self_citations
    

    def getJournalSelfCitationsByName(self, journal_name: str) -> list[JournalSelfCitation]:

        journal_self_citations = []

        all_journal_self_citations = self.getAllJournalSelfCitations()
        journal_bib_entities = self.getBibliographicEntitiesWithVenue(journal_name)

        entities_dict = dict()

        for journal_entity in journal_bib_entities:
            for id in journal_entity.getIds():
                entities_dict[id] = journal_entity

        if not entities_dict:
            return []
        
        for citation in all_journal_self_citations:
           
            citing_entity = citation.getCitingEntity()
            cited_entity = citation.getCitedEntity()

            has_citing = 0
            has_cited = 0

            for id in citing_entity.getIds():
                if id in entities_dict:
                    has_citing += 1

            for id in cited_entity.getIds():
                if id in entities_dict:
                    has_cited += 1

            if has_citing and has_cited:
                journal_self_citations.append(citation)

        return journal_self_citations

    
    def getCitationsOfBibEntityByTitleWithinDate(self, bib_entity_title: str, min_date: str, max_date: str) -> list[Citation]:

        citations_of_bib_entity_within_date = []

        bib_entities_with_title = self.getBibliographicEntitiesWithTitle(bib_entity_title)

        all_citations = self.getCitationsWithinDate(min_date, max_date)

        entities_dict = dict()

        for entity in bib_entities_with_title:
            for id in entity.getIds():      
                entities_dict[id] = entity
        
        if not entities_dict:
            return []

        for citation in all_citations:
            cited_entity = citation.getCitedEntity()

            is_in_dict = 0

            if cited_entity:
                for id in cited_entity.getIds():
                    if id in entities_dict:
                        is_in_dict += 1
                        

            if is_in_dict:
                
                citations_of_bib_entity_within_date.append(citation)
        
        return citations_of_bib_entity_within_date
    
    
    def getReferencesOfBibEntityByTitleWithinTimespan(self, bib_entity_title: str, min_timespan: str, max_timespan: str) -> list[Citation]:
        references_of_bib_entity_within_timespan = []

        bib_entities_with_title = self.getBibliographicEntitiesWithTitle(bib_entity_title)
        all_citations = self.getCitationsWithinTimespan(min_timespan, max_timespan)

        entities_dict = dict()

        for entity in bib_entities_with_title:
            for id in entity.getIds():      
                entities_dict[id] = entity

        if not entities_dict:
            return []
               

        for citation in all_citations:
            citing_entity = citation.getCitingEntity()

            has_citing_entity = 0

            for id in citing_entity.getIds():
                if id in entities_dict:
                    has_citing_entity += 1
            
            if has_citing_entity:
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

        #res = que.getCitationsOfBibEntityByTitleWithinDate("sick", "", "")

        res = que.getReferencesOfBibEntityByTitleWithinTimespan("Revisiting", "", "")

        #res = que.getCitationsOfBibEntityByTitleWithinDate("","2021", "2021-01-02")

        #res = que.getJournalSelfCitationsByName("Industry And Higher Education")

        # 4. Stampe di controllo
        #print(f"il tipo è: {type(res[0])}")
        #print(res)
        
        print(len(res))
        print(type(res[0]))
        x = 1
        for i in res:
            print(f"citazione numero {x}")
            print(i.getCitingEntity().getTitle())
            print(i.getCitedEntity().getTitle())
            x+=1
            #print(i.__dict__)
        
        #for i in res2:
        #    print("citation:\n")
        #    print(i.getCitedEntity().getAuthors(),i.getIds())
        #print(f"\n ci sono: {len(res)} risultati")
        #print(f"Il tipo di getcitingentity: {type(res[0].getCitingEntity())}")
        #if res:
            #print(res[0].getCitingEntity().getIds())
            #print(res[0].getCitedEntity().getIds())