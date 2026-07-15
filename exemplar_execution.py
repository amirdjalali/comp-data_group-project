# -*- coding: utf-8 -*-
# Copyright (c) 2026, Ivan Heibi <ivan.heibi2@unibo.it>
#
# Permission to use, copy, modify, and/or distribute this software for any purpose
# with or without fee is hereby granted, provided that the above copyright notice
# and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.



# 1) Importing all the classes for handling the relational database
from handlers.bibliographic_entity_upload_handler import BibliographicEntityUploadHandler
from handlers.bibliographic_entity_query_handler import BibliographicEntityQueryHandler

# 2) Importing all the classes for handling graph database
from handlers.citation_upload_handler import CitationUploadHandler
from handlers.citation_query_handler import CitationQueryHandler

# 3) Importing the class for dealing with mashup queries
from engines.full_query_engine import FullQueryEngine

# Once all the classes are imported, first create the relational
# database using the related source data
rel_path = "relational.db"
bib = BibliographicEntityUploadHandler()
bib.setDbPathOrUrl(rel_path)
# bib.pushDataToDb("data/dh_metadata.json")
# Please remember that one could, in principle, push one or more files
# calling the method one or more times (even calling the method twice
# specifying the same file!)

# Then, create the graph database (remember first to run the
# Blazegraph instance) using the related source data
grp_endpoint = "http://localhost:9999/blazegraph/sparql"
jou = CitationUploadHandler()
jou.setDbPathOrUrl(grp_endpoint)
# jou.pushDataToDb("data/dh_citations.csv")
# Please remember that one could, in principle, push one or more files
# calling the method one or more times (even calling the method twice
# specifying the same file!)

# In the next passage, create the query handlers for both
# the databases, using the related classes
bib_qh = BibliographicEntityQueryHandler()
bib_qh.setDbPathOrUrl(rel_path)

jou_qh = CitationQueryHandler()
jou_qh.setDbPathOrUrl(grp_endpoint)

# Finally, create a advanced mashup object for asking
# about data
que = FullQueryEngine()
que.addBibliographicEntityHandler(bib_qh)
que.addCitationHandler(jou_qh)

# result_q1 = que.getAllCitations()

# ENTITES BY ID
print("Printing enity by ID:")
result_q2 = que.getEntityById("0603926665-06180334360")
print(result_q2.__dict__)

# BIB ENTITIES WITH TITLE
print("Printing bib entities with title:")
result_q3 = que.getBibliographicEntitiesWithTitle("Neural networks")
for result in result_q3[:10]:
    attributes = result.__dict__
    for key, value in attributes.items():
        print(f"{key}: {value}:")
    print("-" * 40)
print(f"there are {len(result_q3)} results")

print("\n" + "=" * 50)

# BIB ENTITIES WITH AUTHOR
print("Printing bib entities with author:")
result_q5 = que.getBibliographicEntitiesWithAuthor("James")

for result in result_q5[:10]:
    # Safely extract the object's dictionary attributes
    attributes = result.__dict__
    
    # Print each attribute key and value on its own dedicated row
    for key, value in attributes.items():
        print(f"{key}: {value}")
        
    # Print a visible line break to separate the different entities clearly
    print("-" * 40)
print(f"there are {len(result_q5)} results")   

# AUTHOR SELF CITATION BY NAME
# print("Printing author self citation by name:")
# result_q4 = que.getAuthorSelfCitationsByName("James")
# for result in result_q4[:10]:
#     attributes = result.__dict__
#     for key, value in attributes.items():
#         print(f"{key}: {value}:")
#     print("-" * 40)
# print(f"there are {len(result_q4)} results") 

# print("\n" + "=" * 50)

# TESTING FOR SOMETHING UNRELATED
print("Testing for something that should not exist:")
result_q6 = que.getBibliographicEntitiesWithAuthor("Mickey Mouse")
print(result_q6)

# TESTING PARTIAL RESULTS
print("Testing for partial results:")
result_q7 = que.getBibliographicEntitiesWithTitle("etwor")
for result in result_q7[:10]:
    attributes = result.__dict__
    for key, value in attributes.items():
        print(f"{key}: {value}:")
    print("-" * 40)
print(f"there are {len(result_q7)} results")
