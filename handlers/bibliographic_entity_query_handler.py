import sqlite3
import pandas as pd
from .query_handler import QueryHandler

class BibliographicEntityQueryHandler(QueryHandler):

    def _buildQuery(self, where_clause="", params=None): # where_clause and params are optional -> default to "" and None
        # This is the core SELECT used by every method below.
        # For each entity, it fetches the four core fields (internalId,
        # title, publication_date, venue) plus two extra columns:
        # - authors: all author names joined into one string, e.g. "Smith, A; Jones, B"
        # - ids: all identifiers joined into one string, e.g. "doi:10.1/x; omid:br/1"
        #
        # The two inner SELECTs (one for authors, one for ids) are called
        # "correlated subqueries". They run once per entity row and look up
        # only the rows that belong to that entity (WHERE entityId = ...).
        # We use this instead of a JOIN because joining both the author table
        # AND the id table at once would create duplicate rows.
        #
        # GROUP_CONCAT joins multiple values into one string with "; " as the
        # separator. We avoid plain commas because author names already
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

# The parentheses (...) wrap a second, smaller SELECT query living inside the main one. This is a subquery — 
# a query inside a query. It runs once per row of the outer query, meaning once per publication.

# This means:

# FROM BibliographicEntityAuthor — go to the author table (which has one row per author per publication, so a 
# publication with 3 authors has 3 rows there)

# WHERE entityId = BibliographicEntity.internalId — only look at rows belonging to the publication currently 
# being processed by the outer query. This is what makes it "correlated" — the inner query is linked to (=) 
# the outer query's current row

# GROUP_CONCAT(author, '; ') — take all the author values found and concatenate them into a single string, 
# separated by '; '. So three authors become "Cohen, Jeffrey; Lemenager, Stephanie; Smith, Alice"

# AS authors — give this result column the name authors in the final output table

        if where_clause:
            query += " WHERE " + where_clause
# if where_clause: checks whether where_clause is non-empty: an empty string "" is treated as False in Python, 
# so this block only runs if an actual filter was passed in. query += means "add this to the end of the query 
# string that already exists."

        with sqlite3.connect(self.dbPathOrUrl) as con:
            return pd.read_sql_query(query, con, params=params or [])
        # params or [] means "use params if it has values, otherwise use an empty list" — this handles the case where 
        # params was left as None.

    # --- NO FILTER
    # Returns every entity with no filter applied
    def getAllBibliographicEntities(self) -> pd.DataFrame:
        return self._buildQuery()

    # --- Filtering by TITLE
    # Returns entities whose title contains the given substring
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
    @staticmethod
    def _normaliseDate(date_string: str, is_end_date: bool = False) -> str:
        # Converts a partial date string to a full YYYY-MM-DD so that SQLite
        # string comparisons work correctly across mixed formats.
        # For start dates, missing parts pad to the earliest possible day.
        # For end dates, missing parts pad to the latest possible day -
        # so that searching "2014" to "2014" catches everything in that year,
        # not just publications stored as exactly "2014-01-01".
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
    # Both start_date and end_date are optional - you can pass just one.
    # Dates are normalised to YYYY-MM-DD before comparison so that partial
    # formats like "2016" or "2016-03" are handled correctly.
    # If you want a list of every work published in a specific year (e.g., 2024), you need 
    # to input the year twice, so that it becomes the range 2024-01-01 to 2024-12-31
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

    # IN (...) means "only include rows where this value appears in the following list." The list 
    # here isn't written out by hand — it's produced by another SELECT query running inside the brackets. 
    # That inner query is called a subquery.

    # This means: "give me all entities whose internalId appears in the list of entityIds 
    # from the author table where the author name matches my search." The reason for doing it this way 
    # (rather than a JOIN): if you JOIN the author table and then also JOIN the 
    # id table, you get a multiplication of rows. The subquery avoids that by just using the author table to 
    # produce a list of matching ids, then filtering the main query by that list — the main query's own inner 
    # SELECTs then collect all authors and ids cleanly.

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
    
    # WHERE internalId IN ("e1", "e2") is a shorter way of saying WHERE internalId = "e1" OR internalId = "e2"
    # But you can't write it that way here because you don't know in advance how many results the inner query will 
    # return — it depends on what the user searches for. IN handles whatever size list comes back automatically, 
    # whether that's 1 result, 20 results, or 0 results.
    # So in one sentence: = is for one value, IN is for a list of values.