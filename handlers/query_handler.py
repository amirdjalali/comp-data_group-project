from .handler import Handler
import pandas as pd
from abc import ABC, abstractmethod

class QueryHandler(Handler):

    @abstractmethod
    def getById(self, id: str) -> pd.DataFrame:

        pass