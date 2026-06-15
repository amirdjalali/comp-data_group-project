import sqlite3
import pandas as pd
from .query_handler import QueryHandler

class BibliographicEntityQueryHandler(QueryHandler):

# -- getting all metadata except for author and id (will come later in the basic query engine??)

    def getAllBibliographicEntities(self) -> pd.DataFrame: # creates a dataframe out of all the core metadata -> has no filters; this line defines the method, only self as input argument; output will be a pandas dataframe
        query = """  
            SELECT internal_id, title, pub_date, venue 
            FROM df_entities
        """ # stores multi-line SQL statement inside a text variable, query. commands the database to check the main metadata table df_entities and fetches every single record, using the four required columns. 
        with sqlite3.connect(self.dbPathOrUrl) as con: # opens pipe connection (con) to the local SQLite database file path -> placeholder will update automatically depending on the test file 
            return pd.read_sql_query(query, con) # pandas takes the query text and the database pipe con, collects the resulting rows using SQLite, converting them to a clean, labelled dataframe table 

# -- filtering by title substring

    def getBibliographicEntitiesWithTitle(self, title: str) -> pd.DataFrame:
        query = """
            SELECT internal_id, title, pub_date, venue
            FROM df_entities
            WHERE title LIKE ?
        """
        with sqlite3.connect(self.dbPathOrUrl) as con:
            return pd.read_sql_query(query, con, params=[f"%{title}%"]) # title is wrapped with front and back wildcards -> ensures partial matches 

# -- filtering by venue substring 

    def getBibliographicEntitiesWithVenue(self, venue: str) -> pd.DataFrame:
        query = """
            SELECT internal_id, title, pub_date, venue
            FROM df_entities
            WHERE venue LIKE ?
        """
        with sqlite3.connect(self.dbPathOrUrl) as con:
            return pd.read_sql_query(query, con, params=[f"%{venue}%"])

# -- filtering by dynamic date range

    def getBibliographicEntitiesWithinPublicationDate(self, start_date: str = None, end_date: str = None) -> pd.DataFrame: # assigning None will make them optional, in case one of the boundaries is left empty?
        query = """
            SELECT internal_id, title, pub_date, venue
            FROM df_entities
            WHERE 1=1
        """ # 1=1 is a trick to build dynamic queries without knowing what a user's filter will look like. -> placeholder that is always true
        
        # creates an empty list to collect the date values in the exact order the placeholders appear
        date_list = []

        # checks if a starting date limit was provided by the test file
        if start_date: # might appear in the test file
            query += " AND pub_date >= ?" # optional filters -> query is updated to include the start date
            date_list.append(start_date)

        # checks if a end date limit was provided by the test file
        if end_date: # might appear in the test file
            query += " AND pub_date <= ?" # optional filters -> query is updated to also include the end date 
            date_list.append(end_date)

        with sqlite3.connect(self.dbPathOrUrl) as con:
            return pd.read_sql_query(query, con, params=date_list)

# -- filter by entities with author

    def getBibliographicEntitiesWithAuthor(self, author: str) -> pd.DataFrame:
        # SELECT DISTINCT ensure a publication appears only once in the final table
        # even if an entity matches multiple criteria during the filtering process
        # JOIN temporarily matches main entities table with author table
        query = """
            SELECT DISTINCT df_entities.internal_id, df_entities.title, df_entities.pub_date, df_entities.venue 
            FROM df_entities
            JOIN df_authors ON df_entities.internal_id = df_authors.internal_id
            WHERE df_authors.author_name LIKE ?
        """
        # opens a temporary, secure connection bridge to the underlying SQLite database file
        with sqlite3.connect(self.dbPathOrUrl) as con:
            # percent wildcards ensure partial matches
            return pd.read_sql_query(query, con, params=[f"%{author}%"])

# -- filter by id 

    def getById(self, id: str) -> pd.DataFrame:
        # JOIN to temporarily match main entities table with identifier table
        # strict equals sign (=) instead of LIKE because unique identifier lookups must be exact
        # SELECT line only requests four core columns, dropping the ID string itself
        query = """
            SELECT df_entities.internal_id, df_entities.title, df_entities.pub_date, df_entities.venue 
            FROM df_entities
            JOIN df_ids ON df_entities.internal_id = df_ids.internal_id
            WHERE df_ids.identifier_value = ?
        """

        with sqlite3.connect(self.dbPathOrUrl) as con:
            return pd.read_sql_query(query, con, params=[id])
