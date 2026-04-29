from .basic_query_engine import BasicQueryEngine
from model.author_self_citation import AuthorSelfCitation
from model.journal_self_citation import JournalSelfCitation
from model.citation import Citation

class FullQueryEngine(BasicQueryEngine):

    def getAuthorSelfCitationsByName(self, author_name: str) -> list[AuthorSelfCitation]:
        return []
    
    def getJournalSelfCitationsByName(self, journal_name: str) -> list[JournalSelfCitation]:
        return []
    
    def getCitationsOfBibEntityByTitleWithinDate(self, bib_entity_title: str, min_date: str, max_date: str) -> list[Citation]:
        return []
    
    def getReferencesOfBibEntityByTitleWithinTimespan(self, bib_entity_title: str, min_timespan: str, max_timespan: str) -> list[Citation]:
        return []