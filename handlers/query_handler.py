from .handler import Handler
import pandas as pd

class QueryHandler(Handler):

    def getById(self, id: str) -> pd.DataFrame:
        return pd.DataFrame()