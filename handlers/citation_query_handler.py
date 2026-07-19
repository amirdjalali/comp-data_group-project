from .query_handler import QueryHandler
import pandas as pd
from sparql_dataframe import get
import re # regular expressions to validate dates and timespans
from pandas import read_csv, Series


class CitationQueryHandler(QueryHandler):

    def getById(self, id: str) -> pd.DataFrame:
    
        endpoint = self.getDbPathOrUrl()

        #if the user provides the full url, in case there are errors in the input, we can extract the clean id from the url and use it to query the database
        clean_id = id.split("/")[-1]

        oci = "https://w3id.org/oc/index/ci/" + clean_id
        #try to understand if we need to check whether the id needs to be checked or not from citation_upload_handler.py (maybe not, since the upload handler already checks that the OCIs are in the correct format, but maybe we can add this check just to be sure)
    
        query = f"""
                PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX cito: <http://purl.org/spar/cito/>
            
                SELECT ?oci ?citing ?cited ?creation ?timespan ?journal_sc ?author_sc
                WHERE {{
            
                    BIND(<{oci}> AS ?oci)

                    ?oci a cito:Citation .
                    ?oci cito:hasCitingEntity ?citing .
                    ?oci cito:hasCitedEntity ?cited .
                    ?oci cito:hasCitationCreationDate ?creation .
                    ?oci cito:hasCitationTimeSpan ?timespan .

                    BIND(IF(EXISTS {{ ?oci a cito:JournalSelfCitation }}, "True", "False") AS ?journal_sc)
                    BIND(IF(EXISTS {{ ?oci a cito:AuthorSelfCitation }}, "True", "False") AS ?author_sc)
                }}
            """
        
        # BIND assigns the result of an expression to a variable
        # BIND (expression AS ?variable)
        # IF assigns a value to a condition
        # IF (condition, value if true, value if false)
        # EXISTS returns true if a graph pattern has at least one match
        # EXISTS { pattern }

        # So, EXISTS { ?oci a cito:JournalSelfCitation } means
        # if ?oci is a journal self citation, it retursn true, otherwise it returns false

        # IF assings the value "True" in case the EXISTS condition is true
        # otherwise, it assignes "False"

        # BIND saves the result as ?journal_sc
    
        df_sparql = get(endpoint, query, True)
        return df_sparql

    def getAllCitations(self) -> pd.DataFrame:

        endpoint = self.getDbPathOrUrl()

        query = f"""
                PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX cito: <http://purl.org/spar/cito/>

                SELECT ?oci ?citing ?cited ?creation ?timespan ?journal_sc ?author_sc
                WHERE {{
                    ?oci a cito:Citation .
                    ?oci cito:hasCitingEntity ?citing .
                    ?oci cito:hasCitedEntity ?cited .
                    ?oci cito:hasCitationCreationDate ?creation .
                    ?oci cito:hasCitationTimeSpan ?timespan .

                    BIND(IF(EXISTS {{ ?oci a cito:JournalSelfCitation }}, "True", "False") AS ?journal_sc)
                    BIND(IF(EXISTS {{ ?oci a cito:AuthorSelfCitation }}, "True", "False") AS ?author_sc)
                }}
            """
        
        df_sparql = get(endpoint, query, True)
        return df_sparql
    
    def getAllAuthorSelfCitations(self) -> pd.DataFrame:

        # first connect to db
        endpoint = self.getDbPathOrUrl()

        # query the graph. Should i get also author_sc: true or false?
        # the query also checks if the author self citation is also a journal self citation
        query = """
                PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX schema: <https://schema.org/>
                PREFIX cito: <http://purl.org/spar/cito/>

                SELECT ?oci ?citing ?cited ?creation ?timespan ?journal_sc
                WHERE {
                    ?oci a cito:AuthorSelfCitation .
                    ?oci cito:hasCitingEntity ?citing .
                    ?oci cito:hasCitedEntity ?cited .
                    ?oci cito:hasCitationCreationDate ?creation .
                    ?oci cito:hasCitationTimeSpan ?timespan .

                    BIND(IF(EXISTS { ?oci a cito:JournalSelfCitation }, "True", "False") AS ?journal_sc)
                }
        """
        # transform the tripes into a dataframe with the following columns: oci,citing,cited,creation,timespan,journal_sc
        df_sparql = get(endpoint, query, True)
       
        return df_sparql

    def getAllJournalSelfCitations(self) -> pd.DataFrame:
    
        # first connect to db
        endpoint = "http://localhost:9999/blazegraph/sparql"

        # query the graph. Should i get also author_sc: true or false?
        # the query also checks if the journal self citation is also an author self citation
        query = """
                PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX schema: <https://schema.org/>
                PREFIX cito: <http://purl.org/spar/cito/>

                SELECT ?oci ?citing ?cited ?creation ?timespan ?author_sc
                WHERE {
                    ?oci a cito:JournalSelfCitation .
                    ?oci cito:hasCitingEntity ?citing .
                    ?oci cito:hasCitedEntity ?cited .
                    ?oci cito:hasCitationCreationDate ?creation .
                    ?oci cito:hasCitationTimeSpan ?timespan .
                    BIND(IF(EXISTS { ?oci a cito:AuthorSelfCitation }, "True", "False") AS ?author_sc)
                }
        """
        # transform the tripes into a dataframe with the following columns: oci,citing,cited,creation,timespan,journal_sc
        df_sparql = get(endpoint, query, True)

        return df_sparql

    def getCitationsWithinTimespan(self, min_timespan: str = None, max_timespan: str = None) -> pd.DataFrame:
        # Works with timespans in formats PxY, PxYyM, PxYyMzD, but also without "P"
        # Roughly convert input timespans in days
        if min_timespan == "":
            min_timespan = None
        if max_timespan == "":
            max_timespan = None

        if not min_timespan and max_timespan:
            df_query = "timespan_days <= @max_timespan_days"
        elif not max_timespan and min_timespan:
            df_query = "timespan_days >= @min_timespan_days"
        elif not max_timespan and not min_timespan:
            df_query = "oci == oci"
        else:
            df_query = "timespan_days >= @min_timespan_days and timespan_days <= @max_timespan_days"

        min_timespan_days = self.duration_to_days(min_timespan)
        max_timespan_days = self.duration_to_days(max_timespan)
    
        # first connect to db
        endpoint = "http://localhost:9999/blazegraph/sparql"

        # query the graph and get everything that has a timeframe         
        query = """
            PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX schema: <https://schema.org/>
            PREFIX cito: <http://purl.org/spar/cito/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 

            SELECT ?oci ?citing ?cited ?creation ?timespan ?journal_sc ?author_sc
            WHERE {
                ?oci a cito:Citation .
                ?oci cito:hasCitingEntity ?citing .
                ?oci cito:hasCitedEntity ?cited .
                ?oci cito:hasCitationCreationDate ?creation .
                ?oci cito:hasCitationTimeSpan ?timespan .
                
                BIND(IF(EXISTS { ?oci a cito:JournalSelfCitation }, "True", "False") AS ?journal_sc)
                BIND(IF(EXISTS { ?oci a cito:AuthorSelfCitation }, "True", "False") AS ?author_sc)
                
                #FILTER (?timespan != "")
            }
        """
        # transform the tripes into a dataframe with the following columns: oci,citing,cited,creation,timespan,journal_sc
        df_sparql = get(endpoint, query, True)

        # Add a column with timespans converted to days
        df_sparql["timespan_days"] = df_sparql["timespan"].apply(self.duration_to_days)

        # Filter the results according to timespans
        df_sparql = df_sparql.query(df_query)

        # Remove timespan_days column
        df_sparql.drop(columns=["timespan_days"], inplace=True)
       
        return df_sparql
    

    def getCitationsWithinDate(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        # Works with dates in formats YYYY, YYYY-MM, YYYY-MM-DD
        # For start date, in case YYYY is provided, it considers YYYY-01-01, 
        # and in case YYYY-MM is provided, it considers YYYY-MM-01
        # For end date, in case YYYY is provided, it considers YYYY-12-31,
        # and in case YYYY-MM is provided, it considers YYYY-MM-28

        filters = ""

        start_date = self._validate(start_date)
        end_date = self._validate(end_date)

        if start_date:
            start_date_parts = start_date.split("-")

            if len(start_date_parts) == 2:
                start_date = f"{start_date}-01"
            elif len(start_date_parts) == 1:
                start_date = f"{start_date}-01-01"

            filters += f"    FILTER (STR(?creation) >= \"{start_date}\")\n"

        if end_date:

            end_date_parts = end_date.split("-")

            if len(end_date_parts) == 2:
                end_date = f"{end_date}-28"
            elif len(end_date_parts) == 1:
                end_date = f"{end_date}-12-31"

            filters += f"    FILTER (STR(?creation) <= \"{end_date}\")\n"
            
    
        # first connect to db
        endpoint = "http://localhost:9999/blazegraph/sparql"

        # query the graph.            
        query = """
            PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX schema: <https://schema.org/>
            PREFIX cito: <http://purl.org/spar/cito/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 

            SELECT ?oci ?citing ?cited ?creation ?timespan ?journal_sc ?author_sc
            
            WHERE {
                ?oci a cito:Citation .
                ?oci cito:hasCitingEntity ?citing .
                ?oci cito:hasCitedEntity ?cited .
                ?oci cito:hasCitationCreationDate ?creation .
                ?oci cito:hasCitationTimeSpan ?timespan .
                
                BIND(IF(EXISTS { ?oci a cito:JournalSelfCitation }, "True", "False") AS ?journal_sc)
                BIND(IF(EXISTS { ?oci a cito:AuthorSelfCitation }, "True", "False") AS ?author_sc)
        """

        query = query + filters + "\n}\nORDER BY ?creation"
        #print(query)

        # transform the tripes into a dataframe with the following columns: oci,citing,cited,creation,timespan,journal_sc
        df_sparql = get(endpoint, query, True)

        return df_sparql
    

    @staticmethod
    def _validate(d: str) -> str:
    # validate dates. It performs a regex query on the date. if date is not in the format
    # YYYY or YYYY-MM or YYYY-MM-DD, it raises ValueError

    # regex explained
    # r"" means raw string, so \ characters are not escaped
    # first four digits \d{4}
    # optionally, find "-" followed by two digits \d{2}
    # optionally, find "-" followed by two digits \d{2}

        if d is None or d == "":
            return None
        if not re.fullmatch(r"\d{4}(-\d{2}(-\d{2})?)?", d):
            raise ValueError(f"Invalid date format: {d!r}")
        return d
        
    @staticmethod
    def duration_to_days(timespan: str) -> int:
        # Durations are expressed as PxxYyyMzzD
        # Roughly converts durations into days assuming 1 year = 365 days and 1 month = 30 days
        
        # This is redundant, empty timespans already filtered, but let's keep this anyways

        if pd.isna(timespan):
            return None
        
        # initialize to zero
        days = 0
        years = 0
        months = 0
        
        # Regex to find Years in timespan string, looking for one or more digits before character Y
        # returns re.Match object or None if not found
        years_match = re.search(r"(\d+)Y", timespan)
        if years_match:
            years = int(years_match.group(1)) #return first group into brackets and convert to integer
        
        # Do the same for months and days
        months_match = re.search(r"(\d+)M", timespan)
        if months_match:
            months = int(months_match.group(1))

        days_match = re.search(r"(\d+)D", timespan)
        if days_match:
            days = int(days_match.group(1))

        # Calculate timespan in days
        timespan_days = years * 365 + months * 30 + days

        # It works also with negative timespans!!!
        if timespan[0] == "-":
            return -timespan_days
        else:
            return timespan_days

if __name__ == "__main__":
    
    handler = CitationQueryHandler()
    handler.setDbPathOrUrl("http://localhost:9999/blazegraph/sparql")
    print(handler.getById("0603926682-06160449684"))
    
    # df_all_author_sc = handler.getAllAuthorSelfCitations()
    # print(df_all_author_sc.dtypes)
    # print(df_all_author_sc)

    # df_all_journal_sc = handler.getAllJournalSelfCitations()
    # print(df_all_journal_sc.dtypes)
    # print(df_all_journal_sc)

    df_citations_within_dates = handler.getCitationsWithinDate("2020-99")
    print(df_citations_within_dates.dtypes)
    print(df_citations_within_dates)

    #df_citations_within_timespans = handler.getCitationsWithinTimespan("-99Y", "0")
    #print(df_citations_within_timespans.dtypes)
    #print(df_citations_within_timespans)
    #print(handler.getById("https://w3id.org/oc/index/ci/0603927919-0603927914"))

    # citations = read_csv("../data/dh_citations.csv",
    #                         keep_default_na=False,
    #                         dtype={
    #                             "oci": "string",
    #                             "citing": "string",
    #                             "cited": "string",
    #                             "creation": "string",
    #                             "timespan": "string",
    #                             "journal_sc": "string",
    #                             "author_sc": "string"
    #                         })
    # all_citations = handler.getAllCitations()


    # missing_ones = citations[~citations["oci"].isin(all_citations["oci"].str.replace("https://w3id.org/oc/index/ci/",""))]
    # missing_ones.to_csv("missing.csv", index=False)
    #print(citations["oci"].duplicated().sum())
    #pprint(missing_ones)
    #print(handler.getCitationsWithinDate(2020, 2021))


    