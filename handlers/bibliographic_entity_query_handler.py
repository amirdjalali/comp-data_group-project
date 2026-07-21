import sqlite3
import pandas as pd
from .query_handler import QueryHandler

class BibliographicEntityQueryHandler(QueryHandler):

    def _buildQuery(self, where_clause="", params=None): # protected method; where_clause and params are optional -> default to "" and None
        # This is the core SELECT used by every method below.
        # For each entity, it fetches the four core fields (internalId,
        # title, publication_date, venue) plus two extra columns:
        # - authors: all author names joined into one string, e.g. "Smith, A; Jones, B"
        # - ids: all identifiers joined into one string, e.g. "doi:10.1/x; omid:br/1"
        #
        # The two inner SELECTs (one for authors, one for ids) are 
        # correlated subqueries. They run once per entity row and look up
        # only the rows that belong to that entity (WHERE entityId = ...).
        # This way, duplicate rows that would happen using a JOIN are avoided. 
        #
        # GROUP_CONCAT joins multiple values into one string with "; " as the
        # separator. Plain commas are avoided because author names already
        # contain commas (e.g. "Smith, Alice").

        query = """
            SELECT
                BibliographicEntity.internalId,
                BibliographicEntity.title,
                BibliographicEntity.publication_date,
                BibliographicEntity.venue,
                (
                    SELECT GROUP_CONCAT(author, '; ')
                    FROM BibliographicEntityAuthor
                    WHERE entityId = BibliographicEntity.internalId
                ) AS authors,
                (
                    SELECT GROUP_CONCAT(id, '; ')
                    FROM BibliographicEntityId
                    WHERE entityID = BibliographicEntity.internalId
                ) AS ids
            FROM BibliographicEntity
        """

# A smaller SELECT subquery is wrapped inside the main query. It runs once per row of the outer 
# query, meaning once per publication.

# This means:

# FROM BibliographicEntityAuthor goes to the author table (which has one row per author per publication, so a 
# publication with 3 authors has 3 rows there)

# WHERE entityId = BibliographicEntity.internalId only looks at rows belonging to the publication currently 
# being processed by the outer query. This is what makes it correlated: the inner query is linked to (=) 
# the outer query's current row.

# GROUP_CONCAT(author, '; ') takes all the author values found and concatenate them into a single string, 
# separated by '; '. 

# AS authors — give this result column the name authors in the final output table

        if where_clause:
            query += " WHERE " + where_clause
# if where_clause: checks whether where_clause is non-empty: an empty string "" is treated as False, 
# so this block only runs if an actual filter was passed in. query += means "add this to the end of the query 
# string that already exists."

        with sqlite3.connect(self.dbPathOrUrl) as con:
            return pd.read_sql_query(query, con, params=params or [])
        # params or [] means "use params if it has values, otherwise use an empty list", so this handles the case where 
        # params was left as None.

    # --- NO FILTER
    # Returns every entity with no filter applied
    def getAllBibliographicEntities(self) -> pd.DataFrame:
        return self._buildQuery()

    # --- Filtering by TITLE
    # Returns entities whose title contains the given substring (uses % wildcards to account for partial matches)
    # A placeholder (?) is used in the query to avoid SQL injection security flaws.
    # The actual value is then passed separately in a list ([f"%{title}%"]) as the second argument to _buildQuery.
    def getBibliographicEntitiesWithTitle(self, title: str) -> pd.DataFrame:
        return self._buildQuery(
            "BibliographicEntity.title LIKE ?",
            [f"%{title}%"]
        )

    # --- Filtering by VENUE
    # Returns entities whose venue contains the given substring
    def getBibliographicEntitiesWithVenue(self, venue: str) -> pd.DataFrame:
        return self._buildQuery(
            "BibliographicEntity.venue LIKE ?",
            [f"%{venue}%"]
        )

    # --- Filtering by DATE RANGE
    @staticmethod # function operates independently 
    def _normaliseDate(date_string: str, is_end_date: bool = False) -> str:

        if not date_string:
            return None

        parts = date_string.split("-")

        if len(parts) == 1:     # e.g. "2016"
            return f"{date_string}-12-31" if is_end_date else f"{date_string}-01-01"
        elif len(parts) == 2:   # e.g. "2016-03"
            return f"{date_string}-28" if is_end_date else f"{date_string}-01"
        else:                   # e.g. "2016-03-15" -> already full
            return date_string

    # Returns entities published within an optional date range.
    # Both start_date and end_date are optional. You can pass just one.
    # Dates are normalised to YYYY-MM-DD before comparison so that partial
    # formats like "2016" or "2016-03" are handled correctly.
    # Inputing the year twice returns everything published in that year.

    def getBibliographicEntitiesWithinPublicationDate(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        conditions = []
        params = []

        if start_date:
            conditions.append("BibliographicEntity.publication_date >= ?")
            params.append(self._normaliseDate(start_date, is_end_date=False))

        if end_date:
            conditions.append("BibliographicEntity.publication_date <= ?")
            params.append(self._normaliseDate(end_date, is_end_date=True))

        # If neither date was given, return everything
        where = " AND ".join(conditions) if conditions else ""
        return self._buildQuery(where, params)

    # --- Filtering by AUTHOR
    # Returns entities that have the given author (partial match).
    
    # The WHERE uses a subquery to find matching internalIds from the raw
    # author table first. This way, the outer query's GROUP_CONCAT still
    # collects ALL authors for the matched entity, not only the one that
    # matched the filter.
    # The ? is a placeholder, and the actual value gets passed separately in the params list.
    # This is called a parameterised query. 

    def getBibliographicEntitiesWithAuthor(self, author: str) -> pd.DataFrame:
        return self._buildQuery(
            """BibliographicEntity.internalId IN (
                SELECT entityId
                FROM BibliographicEntityAuthor
                WHERE author LIKE ?
            )""",
            [f"%{author}%"]
        )

    # IN (...) means "only include rows where this value appears in the following list." 
    # This avoids a multiplication of rows that would happen with a JOIN statement. 

    # --- Filtering by ID
    # Returns the entity with this exact id (e.g. "doi:10.1002/pra2.714").
    # Uses exact equality (=) not LIKE, because ids must match precisely.
    # Same subquery pattern as above so ALL ids/authors for the entity
    # are still returned, not just the one that matched.

    def getById(self, id: str) -> pd.DataFrame:
        return self._buildQuery(
            """BibliographicEntity.internalId IN (
                SELECT entityID
                FROM BibliographicEntityId
                WHERE id = ?
            )""",
            [id]
        )
    
    # WHERE internalId IN is a shorter way of saying WHERE internalId = "e1" OR internalId = "e2"
    # IN handles whatever size list comes back automatically, 
    # whether that's 1 result, 20 results, or 0 results.
