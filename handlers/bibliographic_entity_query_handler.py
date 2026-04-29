from .query_handler import QueryHandler
import pandas as pd

class BibliographicEntityQueryHandler(QueryHandler):

    def getById(self, id: str) -> pd.DataFrame:
        return pd.DataFrame()

    def getAllBibliographicEntities(self) -> pd.DataFrame:
        return pd.DataFrame()

    def getBibliographicEntitiesWithTitle(self, title: str) -> pd.DataFrame:
        return pd.DataFrame()

    def getBibliographicEntitiesWithAuthor(self, author: str) -> pd.DataFrame:
        return pd.DataFrame()

    def getBibliographicEntitiesWithinPublicationDate(self, start_date: str, end_date: str) -> pd.DataFrame:
        return pd.DataFrame()

    def getBibliographicEntitiesWithVenue(self, venue: str) -> pd.DataFrame:
        return pd.DataFrame()
