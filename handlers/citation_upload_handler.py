from upload_handler import UploadHandler
from rdflib import Graph, Literal, URIRef, RDF
from pandas import read_csv, Series
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

class CitationUploadHandler(UploadHandler):
    def pushDataToDb(self, path: str = None) -> bool:
        # Placeholder for the actual CSV/Graph logic

        citation_graph = Graph()

        oci = URIRef("http://schema.org/identifier")
        citation = URIRef("http://purl.org/spar/cito/Citation")
        hasCitingEntity = URIRef("http://purl.org/spar/cito/hasCitingEntity")
        hasCitedEntity = URIRef("http://purl.org/spar/cito/hasCitedEntity")
        hasCitationCreationDate = URIRef("http://purl.org/spar/cito/hasCitationCreationDate")
        hasCitationTimeSpan = URIRef("http://purl.org/spar/cito/hasCitationTimeSpan")
        AuthorSelfCitation = URIRef("http://purl.org/spar/cito/AuthorSelfCitation")
        JournalSelfCitation = URIRef("http://purl.org/spar/cito/JournalSelfCitation")

        oci_base_url = "https://w3id.org/oc/index/ci/"

        citations = read_csv("data/test_citations.csv",
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
        
        citation_oci_urls = {}
        for idx, row in citations.iterrows():
            citation_url = URIRef(oci_base_url + row["oci"])
            citation_oci_urls["oci_url"] = citation_url

            citation_graph.add((citation_url, oci, Literal(row["oci"])))
            citation_graph.add((citation_url, RDF.type, citation))
            citation_graph.add((citation_url, hasCitingEntity, Literal(row["citing"])))
            citation_graph.add((citation_url, hasCitedEntity, Literal(row["cited"])))
            citation_graph.add((citation_url, hasCitationCreationDate, Literal(row["creation"])))
            citation_graph.add((citation_url, hasCitationTimeSpan, Literal(row["timespan"])))

            if row["journal_sc"] == "yes":
                citation_graph.add((citation_url, JournalSelfCitation, Literal(True)))
            else:
                citation_graph.add((citation_url, JournalSelfCitation, Literal(False)))

            if row["author_sc"] == "yes":
                citation_graph.add((citation_url, AuthorSelfCitation, Literal(True)))
            else:
                citation_graph.add((citation_url, AuthorSelfCitation, Literal(False)))

        store = SPARQLUpdateStore()
        endpoint = "http://172.17.0.1:9999/blazegraph/sparql"
        store.open((endpoint, endpoint))

        for triple in citation_graph.triples((None, None, None)):
            store.add(triple)

        store.close()

        return True

    pushDataToDb("")
