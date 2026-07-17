from .upload_handler import UploadHandler
from rdflib import Graph, Namespace, Literal, URIRef, RDF, XSD
from pandas import read_csv, Series
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

class CitationUploadHandler(UploadHandler):
    def pushDataToDb(self, path: str = None) -> bool:
        # Placeholder for the actual CSV/Graph logic

        citation_graph = Graph()

        # It's nicer to use Namespaces instead of URIRef.

        CITO = Namespace("http://purl.org/spar/cito/")
        SCHEMA = Namespace("http://schema.org/")

        # So basically CITO.Citation is "http://purl.org/spar/cito/Citation"

        oci_base_url = "https://w3id.org/oc/index/ci/"

        citations = read_csv("data/dh_citations.csv",
                            keep_default_na=False,
                            dtype={
                                "oci": "string",
                                "citing": "string",
                                "cited": "string",
                                "creation": "string",
                                "timespan": "string",
                                "journal_sc": "string",
                                "author_sc": "string"
                            })
    
        number_of_citations = len(citations)
        print(f"Starting to parse citations from {path}")
        
        for idx, row in citations.iterrows():
            print(f"Adding row {idx} of {number_of_citations}", end="\r")
            citation_url = URIRef(oci_base_url + row["oci"])

            citation_graph.add((citation_url, SCHEMA.identifier, Literal(row["oci"])))
            citation_graph.add((citation_url, RDF.type, CITO.Citation))
            citation_graph.add((citation_url, CITO.hasCitingEntity, Literal(row["citing"])))
            citation_graph.add((citation_url, CITO.hasCitedEntity, Literal(row["cited"])))

            # Not all dates are in format YYYY-MM-DD, some are in YYYY-DD and some in YYYY.
            # To parse the dates correctly, i have used the parse_dates static method below.
            citation_graph.add((citation_url, CITO.hasCitationCreationDate, self.parse_dates(row["creation"])))


            citation_graph.add((citation_url, CITO.hasCitationTimeSpan, Literal(row["timespan"], datatype=XSD.string)))


            # Parse self citations 

            if row["journal_sc"] == "yes":
               citation_graph.add((citation_url, RDF.type, CITO.JournalSelfCitation))
            if row["author_sc"] == "yes":
                citation_graph.add((citation_url, RDF.type, CITO.AuthorSelfCitation))

        print(f"Done! Parsed {number_of_citations} citations")
        

        store = SPARQLUpdateStore()
        endpoint = self.getDbPathOrUrl()
        store.open((endpoint, endpoint))

        print(f"Starting to store citations to {endpoint}")

        # Use a counter for printing the status of the storing process
        i = 1 
        number_of_triples = len(citation_graph)

        for triple in citation_graph.triples((None, None, None)):
            print(f"Storing triple {i} of {number_of_triples}", end="\r")
            i+=1
            store.add(triple)

        store.close()

        print(f"All {number_of_citations} citations were stored successfully!")
        print(f"Check them here: {endpoint}")

        return True
    
    # Use this method to parse dates. YYYY dates are converted in YYYY-01-01 and
    # YYYY-MM dates are converted in YYYY-MM-01 for comparison

    @staticmethod
    def parse_dates(date_string: str) -> Literal:
        # Parses the dates
 
        if not date_string:
            return None
        
        date_parts = date_string.split("-")
        
        if len(date_parts) == 1:
            return Literal(f"{date_string}-01-01", datatype=XSD.date)
        elif len(date_parts) == 2:
            return Literal(f"{date_string}-01", datatype=XSD.date)
        elif len(date_parts) == 3:
            return Literal(date_string, datatype=XSD.date)
        
        return None # just in case dates are not formatted properly

# To upload citations directly from this file

if __name__ == "__main__":

    # You need to create a handler object first, and then call the method upon it
    handler = CitationUploadHandler()
    handler.setDbPathOrUrl("http://localhost:9999/blazegraph/sparql")
    handler.pushDataToDb()
