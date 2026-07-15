from .query_handler import QueryHandler
import pandas as pd
from sparql_dataframe import get
import re
from pandas import read_csv, Series


class CitationQueryHandler(QueryHandler):

    def getById(self, id: str) -> pd.DataFrame:
    
        endpoint = self.getDbPathOrUrl()

        oci = id
        if "https://w3id.org/oc/index/ci/" not in oci:
            oci = "https://w3id.org/oc/index/ci/" + id
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

        # replace NaN values with empty string
        # df_sparql = get(endpoint, query, True).fillna('')

        # convert creation date from string to datetime
        df_sparql["creation"] = pd.to_datetime(df_sparql["creation"], format="%Y-%m-%d")

        # Pandas already sees journal_sc as bool so no need for this
        # df_sparql["journal_sc"] = df_sparql["journal_sc"].astype("bool")

        # Convert timespan in timespans
       
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

        # replace NaN values with empty string
        # df_sparql = get(endpoint, query, True).fillna('')

        # convert creation date from string to datetime
        df_sparql["creation"] = pd.to_datetime(df_sparql["creation"], format="%Y-%m-%d")

        # Pandas already sees author_sc as bool so no need for this
        # df_sparql["author_sc"] = df_sparql["author_sc"].astype("bool")
       
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

        # Empty durations strings already filtered out
        # df_sparql = get(endpoint, query, True).fillna('')

        # convert creation date from string to datetime
        df_sparql["creation"] = pd.to_datetime(df_sparql["creation"], format="%Y-%m-%d")

        # Pandas already sees author_sc as bool so no need for this
        # df_sparql["author_sc"] = df_sparql["author_sc"].astype("bool")
       
        return df_sparql
    

    def getCitationsWithinDate(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        # Works with dates in formats YYYY, YYYY-MM, YYYY-MM-DD
        # In case YYYY is provided, it considers YYYY-01-01
        # In case YYYY-MM is provided, it considers YYYY-MM-01

        filters = ""

        if end_date:
            filters += f"    FILTER (?creation <= \"{end_date}\"^^xsd:date)\n"
        if start_date:
            filters += f"    FILTER (?creation >= \"{start_date}\"^^xsd:date)"
    
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

        # replace NaN values with empty string
        # df_sparql = get(endpoint, query, True).fillna('')

        # convert creation date from string to datetime
        df_sparql["creation"] = pd.to_datetime(df_sparql["creation"], format="%Y-%m-%d")

        # Pandas already sees author_sc as bool so no need for this
        # df_sparql["author_sc"] = df_sparql["author_sc"].astype("bool")
       
        return df_sparql
        
    
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

    #df_citations_within_dates = handler.getCitationsWithinDate("2024-01","2025")
    #print(df_citations_within_dates.dtypes)
    #print(df_citations_within_dates)

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


    