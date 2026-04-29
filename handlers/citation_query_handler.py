from .query_handler import QueryHandler
import pandas as pd

class CitationQueryHandler(QueryHandler):

    def getById(self, id: str) -> pd.DataFrame:
        return pd.DataFrame()

    def getAllCitations(self) -> pd.DataFrame:
        return pd.DataFrame()

    def getAllAuthorSelfCitations(self) -> pd.DataFrame:
        return pd.DataFrame()

    def getAllJournalSelfCitations(self) -> pd.DataFrame:
        return pd.DataFrame() 

    def getCitationsWithinTimespan(self, min_timespan: str, max_timespan: str) -> pd.DataFrame:
        return pd.DataFrame()

    def getCitationsWithinDate(self, start_date: str, end_date: str) -> pd.DataFrame:
        return pd.DataFrame()
