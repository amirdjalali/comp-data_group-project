from .upload_handler import UploadHandler
from rdflib import Graph, Namespace, Literal, URIRef, RDF, XSD
from pandas import read_csv
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

class CitationUploadHandler(UploadHandler):
    def pushDataToDb(self, path: str = None) -> bool:

        # Initialize the graph that will be pushed later to the db
        citation_graph = Graph()

        # Using Namespaces makes code more readable, by adding prefixes to specific base URIs
        # In this case, we have used http://purl.org/spar/cito/, which is the ontology used
        # by OpenCitations in real life

        CITO = Namespace("http://purl.org/spar/cito/")
        SCHEMA = Namespace("http://schema.org/")

        # Usage: CITO.Citation means "http://purl.org/spar/cito/Citation"
        # SCHEMA.identifier means "https://schema.org/identifier"

        # We use OCIs as citation IDs. We append OCIs to the OCI url.
        # OCIs built in this way are resolvable

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
            # Adding a print statement to show progress
            print(f"Adding row {idx} of {number_of_citations}", end="\r")
            citation_url = URIRef(oci_base_url + row["oci"])

            citation_graph.add((citation_url, SCHEMA.identifier, Literal(row["oci"])))
            citation_graph.add((citation_url, RDF.type, CITO.Citation))
            citation_graph.add((citation_url, CITO.hasCitingEntity, Literal(row["citing"])))
            citation_graph.add((citation_url, CITO.hasCitedEntity, Literal(row["cited"])))

            # Not all dates are in format YYYY-MM-DD, some are in YYYY-DD and some in YYYY.
            # To parse the dates correctly, i have used the parse_dates static method below.
            # Parsing the dates in this way makes them consistent for later querying.
            # The downside is that original data is modified. The BibliographicUploadHandler handles
            # this differently: data is preserved in its original form and stored in the DB.
            # The normalisation of the date format is made when a query is performed.

            citation_graph.add((citation_url, CITO.hasCitationCreationDate, Literal(row["creation"], datatype=XSD.string)))
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
            # Shows the progress so humans know what's happening
            print(f"Storing triple {i} of {number_of_triples}", end="\r")
            i+=1
            store.add(triple)

        store.close()

        print(f"All {number_of_citations} citations were stored successfully!")
        print(f"Check them here: {endpoint}")

        return True
