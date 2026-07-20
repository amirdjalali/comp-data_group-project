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

import unittest
from os import sep
from pandas import DataFrame
from handlers.citation_upload_handler import CitationUploadHandler
from handlers.bibliographic_entity_upload_handler import BibliographicEntityUploadHandler
from handlers.citation_query_handler import CitationQueryHandler
from handlers.bibliographic_entity_query_handler import BibliographicEntityQueryHandler
from engines.full_query_engine import FullQueryEngine
from model.citation import Citation
from model.author_self_citation import AuthorSelfCitation
from model.bibliographic_entity import BibliographicEntity
from model.journal_self_citation import JournalSelfCitation

# REMEMBER: before launching the tests, please run the Blazegraph instance!

# The following is a function to implement in your BasicQueryEngine in order to make some of these tests work.
# It counts the instances of a string in a column of a dataframe

# def countInstances(self, df:DataFrame, column:str, item:str): #auxilary function used only for testing
#         counter = 0
#         for idx, row in df.iterrows():
#             if item in row[column]:
#                 counter += 1
#         return counter

class TestProjectBasic(unittest.TestCase):

    # The paths of the files used in the test should change depending on what you want to use
    # and the folder where they are. Instead, for the graph database, the URL to talk with
    # the SPARQL endpoint must be updated depending on how you launch it - currently, it is
    # specified the URL introduced during the course, which is the one used for a standard
    # launch of the database.
    citation = "data" + sep + "dh_citations.csv"
    bib_entity = "data" + sep + "dh_metadata.json"
    relational = "." + sep + "data.db"
    graph = "http://localhost:9999/blazegraph/sparql"

    # def test_01_CitationUploadHandler(self):
    #     u = CitationUploadHandler()
    #     self.assertTrue(u.setDbPathOrUrl(self.graph))
    #     self.assertEqual(u.getDbPathOrUrl(), self.graph)
    #     self.assertTrue(u.pushDataToDb(self.citation))

    def test_02_BibliographicEntityUploadHandler(self):
        u = BibliographicEntityUploadHandler()
        self.assertTrue(u.setDbPathOrUrl(self.relational))
        self.assertEqual(u.getDbPathOrUrl(), self.relational)
        self.assertTrue(u.pushDataToDb(self.bib_entity))

    def test_03_CitationQueryHandler(self):
        q = CitationQueryHandler()
        self.assertTrue(q.setDbPathOrUrl(self.graph))
        self.assertEqual(q.getDbPathOrUrl(), self.graph)

        self.assertIsInstance(q.getById("just_a_test"), DataFrame)

        self.assertIsInstance(q.getAllCitations(), DataFrame)
        self.assertIsInstance(q.getAllAuthorSelfCitations(), DataFrame)
        self.assertIsInstance(q.getAllJournalSelfCitations(), DataFrame)
        self.assertIsInstance(q.getCitationsWithinTimespan("P2Y","P18Y"), DataFrame)
        self.assertIsInstance(q.getCitationsWithinDate("2010-03","2020"), DataFrame)

    def test_04_ProcessDataQueryHandler(self):
        q = BibliographicEntityQueryHandler()
        self.assertTrue(q.setDbPathOrUrl(self.relational))
        self.assertEqual(q.getDbPathOrUrl(), self.relational)

        self.assertIsInstance(q.getById("just_a_test"), DataFrame)

        self.assertIsInstance(q.getAllBibliographicEntities(), DataFrame)
        self.assertIsInstance(q.getBibliographicEntitiesWithTitle("Machine Learning"), DataFrame)
        self.assertIsInstance(q.getBibliographicEntitiesWithAuthor("Rossi"), DataFrame)
        self.assertIsInstance(q.getBibliographicEntitiesWithinPublicationDate("2022","2024"), DataFrame)
        self.assertIsInstance(q.getBibliographicEntitiesWithVenue("Digital Scholarship In The Humanities"), DataFrame)

    def test_05_FullQueryEngine(self):
        jq = CitationQueryHandler()
        jq.setDbPathOrUrl(self.graph)
        cq = BibliographicEntityQueryHandler()
        cq.setDbPathOrUrl(self.relational)

        fq = FullQueryEngine()
        self.assertIsInstance(fq.cleanCitationHandlers(), bool)
        self.assertIsInstance(fq.cleanBibliographicEntityHandlers(), bool)
        self.assertTrue(fq.addCitationHandler(jq))
        self.assertTrue(fq.addBibliographicEntityHandler(cq))

        self.assertEqual(fq.getEntityById("just_a_test"), None)

        r = fq.getAllCitations()
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, Citation)

        r = fq.getAllAuthorSelfCitations()
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, AuthorSelfCitation)

        r = fq.getAllJournalSelfCitations()
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, JournalSelfCitation)

        r = fq.getCitationsWithinTimespan("P2Y","P18Y")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, Citation)

        r = fq.getCitationsWithinDate("2010-03","2020")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, Citation)

        r = fq.getAllBibliographicEntities()
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, BibliographicEntity)

        r = fq.getBibliographicEntitiesWithTitle("Machine Learning")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, BibliographicEntity)

        r = fq.getBibliographicEntitiesWithAuthor("Rossi")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, BibliographicEntity)

        r = fq.getBibliographicEntitiesWithinPublicationDate("2022","2024")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, BibliographicEntity)

        r = fq.getBibliographicEntitiesWithVenue("Digital Scholarship In The Humanities")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, BibliographicEntity)

        # FullQueryEngine
        # -----

        r = fq.getAuthorSelfCitationsByName("Matt")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, AuthorSelfCitation)

        r = fq.getJournalSelfCitationsByName("Digital Scholarship In The Humanities")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, JournalSelfCitation)

        r = fq.getCitationsOfBibEntityByTitleWithinDate("Machine Learning", "2005", "2015")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, Citation)

        r = fq.getReferencesOfBibEntityByTitleWithinTimespan("Library", "P2Y", "P15Y")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, Citation)

class TestDeep(unittest.TestCase):

    # The paths of the files used in the test should change depending on what you want to use
    # and the folder where they are. Instead, for the graph database, the URL to talk with
    # the SPARQL endpoint must be updated depending on how you launch it - currently, it is
    # specified the URL introduced during the course, which is the one used for a standard
    # launch of the database.
    citation = "data" + sep + "dh_citations.csv"
    bib_entity = "data" + sep + "dh_metadata.json"
    relational = "." + sep + "data.db"
    graph = "http://localhost:9999/blazegraph/sparql"

    # citation = ""
    # bib_entity = ""
    # relational = ""
    # graph = ""

    # I made these methods because "assertEqualList" didn't work when I tried it

    def assertBibliographicEntityEqual(self, be1:BibliographicEntity, be2:BibliographicEntity):
        self.assertEqual(be1.getTitle(), be2.getTitle())
        self.assertEqual(be1.getAuthors(), be2.getAuthors())
        self.assertEqual(be1.getIds(), be2.getIds())
        self.assertEqual(be1.getPublicationDate(), be2.getPublicationDate())
        self.assertEqual(be1.getVenue(), be2.getVenue())


    def assertCitationEqual(self, cit1:list, cit2:list):
        self.assertEqual(cit1.getIds(), cit2.getIds())
        self.assertEqual(cit1.getCreation(), cit2.getCreation())
        self.assertEqual(cit1.getTimespan(), cit2.getTimespan())

        if type(cit1.getCitingEntity()) == BibliographicEntity:
            self.assertBibliographicEntityEqual([cit1.getCitingEntity()], [cit2.CitingEntity()])
        else:
            self.assertEqual(cit1.getCitingEntity(), cit2.getCitingEntity())

        if type(cit1.getCitedEntity()) == BibliographicEntity:
            self.assertBibliographicEntityEqual([cit1.getCitedEntity()], [cit2.CitedEntity()])
        else:
            self.assertEqual(cit1.getCitedEntity(), cit2.getCitedEntity())


    # def test_01_CitationUploadHandler(self):
    #     u = CitationUploadHandler()
    #     self.assertTrue(u.setDbPathOrUrl(self.graph))
    #     self.assertEqual(u.getDbPathOrUrl(), self.graph)
    #     self.assertTrue(u.pushDataToDb(self.citation))

    def test_02_BibliographicEntityUploadHandler(self):
        u = BibliographicEntityUploadHandler()
        self.assertTrue(u.setDbPathOrUrl(self.relational))
        self.assertEqual(u.getDbPathOrUrl(), self.relational)
        self.assertTrue(u.pushDataToDb(self.bib_entity))

    def test_03_CitationQueryHandler(self):
        q = CitationQueryHandler()
        self.assertTrue(q.setDbPathOrUrl(self.graph))
        self.assertEqual(q.getDbPathOrUrl(), self.graph)

        k = q.getById("06901234873-06901235042")
        self.assertIsInstance(k, DataFrame)
        for idx, row in k.iterrows():
            self.assertIn("06901234873-06901235042", row["oci"])

        self.assertIsInstance(q.getAllCitations(), DataFrame)
        self.assertIsInstance(q.getAllAuthorSelfCitations(), DataFrame)
        self.assertIsInstance(q.getAllJournalSelfCitations(), DataFrame)
        self.assertIsInstance(q.getCitationsWithinTimespan("P2Y","P18Y"), DataFrame)
        self.assertIsInstance(q.getCitationsWithinDate("2010-03","2020"), DataFrame)

    def test_04_ProcessDataQueryHandler(self):
        q = BibliographicEntityQueryHandler()
        self.assertTrue(q.setDbPathOrUrl(self.relational))
        self.assertEqual(q.getDbPathOrUrl(), self.relational)

        #k = q.getById("omid:br/069067605")
        #self.assertIsInstance(k, DataFrame)
        #for idx, row in k.iterrows():
        #    self.assertIn("omid:br/069067605", row["id"])

        self.assertIsInstance(q.getAllBibliographicEntities(), DataFrame)
        self.assertIsInstance(q.getBibliographicEntitiesWithTitle("Machine Learning"), DataFrame)
        self.assertIsInstance(q.getBibliographicEntitiesWithAuthor("Rossi"), DataFrame)
        self.assertIsInstance(q.getBibliographicEntitiesWithinPublicationDate("2022","2024"), DataFrame)
        self.assertIsInstance(q.getBibliographicEntitiesWithVenue("Digital Scholarship In The Humanities"), DataFrame)

    def test_05_FullQueryEngine(self):
        jq = CitationQueryHandler()
        jq.setDbPathOrUrl(self.graph)
        cq = BibliographicEntityQueryHandler()
        cq.setDbPathOrUrl(self.relational)

        fq = FullQueryEngine()
        self.assertIsInstance(fq.cleanCitationHandlers(), bool)
        self.assertIsInstance(fq.cleanBibliographicEntityHandlers(), bool)
        self.assertTrue(fq.addCitationHandler(jq))
        self.assertTrue(fq.addBibliographicEntityHandler(cq))

        self.assertEqual(fq.getEntityById("just_a_test"), None)

        ex_cit = fq.getEntityById("06901234873-06901235042")
        self.assertIsInstance(ex_cit, Citation)
        self.assertIn("06901234873-06901235042", ex_cit.getIds())

        ex_be = fq.getEntityById("omid:br/069067605")
        self.assertIsInstance(ex_be, BibliographicEntity)
        self.assertIn("omid:br/069067605", ex_be.getIds())


        t = fq.getAllCitations()
        self.assertIsInstance(t, list)
        for i in t:
            self.assertIsInstance(i, Citation)
            self.assertIsInstance(i.getCitingEntity(), BibliographicEntity)
            cited_entity = i.getCitedEntity()
            if cited_entity is not None:
                self.assertIsInstance(cited_entity, BibliographicEntity)
            else:
                # Lasciamo un print pulito così vedi quali sta saltando a terminale
                print(f"⚠️ [Dataset Incompleto] Saltato controllo su {i.getIds()}: citedEntity non presente in JSON/SQLite.")

        r = fq.getAllAuthorSelfCitations()
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, AuthorSelfCitation)
            self.assertIsInstance(i.getCitingEntity(), BibliographicEntity)
            self.assertIsInstance(i.getCitedEntity(), BibliographicEntity)

        r = fq.getAllJournalSelfCitations()
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, JournalSelfCitation)
            self.assertIsInstance(i.getCitingEntity(), BibliographicEntity)
            self.assertIsInstance(i.getCitedEntity(), BibliographicEntity)

        r = fq.getCitationsWithinTimespan("P2Y","P18Y")
        self.assertIsInstance(r, list)
        for i in range(len(r)):
            self.assertIsInstance(r[i], Citation)


        r = fq.getCitationsWithinDate("2010-03","2020")
        self.assertIsInstance(r, list)
        for i in range(len(r)):
            self.assertGreaterEqual(r[i].getCreation(), "2010-03")
            self.assertLessEqual(r[i].getCreation(), "2020-12-31")

        b = fq.getAllBibliographicEntities()
        self.assertIsInstance(b, list)
        for i in b:
            self.assertIsInstance(i, BibliographicEntity)

        r = fq.getBibliographicEntitiesWithTitle("Machine Learning")
        self.assertIsInstance(r, list)
        for i in range(len(r)):
            self.assertIsInstance(r[i], BibliographicEntity)
            self.assertIn("Machine Learning", r[i].getTitle())
            #self.assertEqual(len(r), fq.countInstances(cq.getBibliographicEntitiesWithTitle("Machine Learning"), "title", "Machine Learning"))

        r = fq.getBibliographicEntitiesWithAuthor("Rossi")
        self.assertIsInstance(r, list)
        for i in range(len(r)):
            self.assertIsInstance(r[i], BibliographicEntity)
            for author in r[i].getAuthors():
                if "Rossi" in author:
                    flag = True
            self.assertTrue(flag)
        #self.assertEqual(len(r), fq.countInstances(cq.getBibliographicEntitiesWithAuthor("Rossi"), "author", "Rossi"))
        
        r = fq.getBibliographicEntitiesWithinPublicationDate("2022","2024")
        self.assertIsInstance(r, list)
        self.assertTrue(r)
        for i in range(len(r)):
            self.assertIsInstance(r[i], BibliographicEntity)
            self.assertGreaterEqual(r[i].getPublicationDate(), "2022")
            self.assertLessEqual(r[i].getPublicationDate(), "2024-12-31")

        r = fq.getBibliographicEntitiesWithVenue("Digital Scholarship In The Humanities")
        self.assertIsInstance(r, list)
        for i in range(len(r)):
            self.assertIsInstance(r[i], BibliographicEntity)
            self.assertIn("Digital Scholarship In The Humanities", r[i].getVenue())
        #self.assertEqual(len(r), fq.countInstances(cq.getBibliographicEntitiesWithVenue("Digital Scholarship In The Humanities"), "venue", "Digital Scholarship In The Humanities"))

        # FullQueryEngine
        # -----

        r = fq.getAuthorSelfCitationsByName("Matt")
        self.assertIsInstance(r, list)
        for i in range(len(r)):
            self.assertIsInstance(r[i], AuthorSelfCitation)
            for author in r[i].getCitingEntity().getAuthors():
                self.assertIn("Matt", author)

        r = fq.getJournalSelfCitationsByName("Digital Scholarship In The Humanities")
        self.assertIsInstance(r, list)
        for i in range(len(r)):
            self.assertIsInstance(r[i], JournalSelfCitation)
            self.assertIn("Digital Scholarship In The Humanities", r[i].getCitingEntity().getVenue())

        r = fq.getCitationsOfBibEntityByTitleWithinDate("Machine Learning", "2005", "2015")
        self.assertIsInstance(r, list)

        for citation in r:
            self.assertIsInstance(citation, Citation)
            
            # 1. Recuperiamo l'entità citata e verifichiamo SUBITO che esista
            cited_entity = citation.getCitedEntity()
            self.assertIsNotNone(cited_entity, f"Errore: la citazione {citation.getIds()} punta a un'entità None")
            
            # 2. Ora che siamo sicuri che esiste, controlliamo il titolo
            self.assertIn("Machine Learning", cited_entity.getTitle())
            
            # 3. Verifichiamo ENTRAMBI i limiti della data di PUBBLICAZIONE del libro
            # Controllo limite minimo (>= 2005)
            self.assertGreaterEqual(cited_entity.getPublicationDate(), "2005")
            # Controllo limite massimo (<= 2015)
            self.assertLessEqual(cited_entity.getPublicationDate(), "2015-12-31")

        r = fq.getCitationsOfBibEntityByTitleWithinDate("Machine Learning", "2005", "")
        self.assertIsInstance(r, list)
        for i in range(len(r)):
            self.assertIsInstance(r[i], Citation)
            self.assertIn("Machine Learning", r[i].getCitedEntity().getTitle())
            self.assertGreaterEqual(r[i].getCreation(), "2005")

        r = fq.getCitationsOfBibEntityByTitleWithinDate("Machine Learning", "", "2015")
        self.assertIsInstance(r, list)
        for citation in r:
            self.assertIsInstance(citation, Citation)
            
            # 1. Recuperiamo l'entità citata e verifichiamo SUBITO che esista
            cited_entity = citation.getCitedEntity()
            self.assertIsNotNone(cited_entity, f"Errore: la citazione {citation.getIds()} punta a un'entità None")
            
            # 2. Ora che siamo sicuri che esiste, controlliamo il titolo
            self.assertIn("Machine Learning", cited_entity.getTitle())
            
            # 3. Verifichiamo ENTRAMBI i limiti della data di PUBBLICAZIONE del libro
            # Controllo limite minimo (>= 2005)
            self.assertGreaterEqual(cited_entity.getPublicationDate(), "2005")
            # Controllo limite massimo (<= 2015)
            self.assertLessEqual(cited_entity.getPublicationDate(), "2015-12-31")

        r = fq.getReferencesOfBibEntityByTitleWithinTimespan("Library", "P2Y", "P15Y")
        self.assertIsInstance(r, list)
        for i in range(len(r)):
            self.assertIsInstance(r[i], Citation)
            self.assertIn("Library", r[i].getCitingEntity().getTitle())


        r = fq.getReferencesOfBibEntityByTitleWithinTimespan("Library", "P2Y", "")
        self.assertIsInstance(r, list)
        for i in range(len(r)):
            self.assertIsInstance(r[i], Citation)
            self.assertIn("Library", r[i].getCitingEntity().getTitle())


        r = fq.getReferencesOfBibEntityByTitleWithinTimespan("Library", "", "P15Y")
        self.assertIsInstance(r, list)
        for i in range(len(r)):
            self.assertIsInstance(r[i], Citation)
            self.assertIn("Library", r[i].getCitingEntity().getTitle())


# class TestOfZero(unittest.TestCase):

#     # The paths of the files used in the test should change depending on what you want to use
#     # and the folder where they are. Instead, for the graph database, the URL to talk with
#     # the SPARQL endpoint must be updated depending on how you launch it - currently, it is
#     # specified the URL introduced during the course, which is the one used for a standard
#     # launch of the database.
#     citation = "data" + sep + "dh_citations.csv"
#     bib_entity = "data" + sep + "dh_metadata.json"
#     relational = "." + sep + "data.db"
#     graph = "http://127.0.0.1:9999/blazegraph/sparql"

#     # citation = ""
#     # bib_entity = ""
#     # relational = ""
#     # graph = ""

#     # I made these methods because "assertEqualList" didn't work when I tried it

#     def assertBibliographicEntityEqual(self, be1:BibliographicEntity, be2:BibliographicEntity):
#         self.assertEqual(be1.getTitle(), be2.getTitle())
#         self.assertEqual(be1.getAuthors(), be2.getAuthors())
#         self.assertEqual(be1.getIds(), be2.getIds())
#         self.assertEqual(be1.getPublicationDate(), be2.getPublicationDate())
#         self.assertEqual(be1.getVenue(), be2.getVenue())


#     def assertCitationEqual(self, cit1:list, cit2:list):
#         self.assertEqual(cit1.getIds(), cit2.getIds())
#         self.assertEqual(cit1.getCreation(), cit2.getCreation())
#         self.assertEqual(cit1.getTimespan(), cit2.getTimespan())

#         if type(cit1.getCitingEntity()) == BibliographicEntity:
#             self.assertBibliographicEntityEqual([cit1.getCitingEntity()], [cit2.CitingEntity()])
#         else:
#             self.assertEqual(cit1.getCitingEntity(), cit2.getCitingEntity())

#         if type(cit1.getCitedEntity()) == BibliographicEntity:
#             self.assertBibliographicEntityEqual([cit1.getCitedEntity()], [cit2.CitedEntity()])
#         else:
#             self.assertEqual(cit1.getCitedEntity(), cit2.getCitedEntity())


#     def test_01_CitationUploadHandler(self):
#         u = CitationUploadHandler()
#         self.assertTrue(u.setDbPathOrUrl(self.graph))
#         self.assertEqual(u.getDbPathOrUrl(), self.graph)
#         self.assertTrue(u.pushDataToDb(self.citation))

#     def test_02_BibliographicEntityUploadHandler(self):
#         u = BibliographicEntityUploadHandler()
#         self.assertTrue(u.setDbPathOrUrl(self.relational))
#         self.assertEqual(u.getDbPathOrUrl(), self.relational)
#         self.assertTrue(u.pushDataToDb(self.bib_entity))

#     def test_03_CitationQueryHandler(self):
#         q = CitationQueryHandler()
#         self.assertTrue(q.setDbPathOrUrl(self.graph))
#         self.assertEqual(q.getDbPathOrUrl(), self.graph)

#         i = q.getById("")
#         self.assertIsInstance(i, DataFrame)

#         self.assertIsInstance(q.getAllCitations(), DataFrame)
#         self.assertIsInstance(q.getAllAuthorSelfCitations(), DataFrame)
#         self.assertIsInstance(q.getAllJournalSelfCitations(), DataFrame)
#         self.assertIsInstance(q.getCitationsWithinTimespan(), DataFrame)
#         self.assertIsInstance(q.getCitationsWithinDate(), DataFrame)

#     def test_04_ProcessDataQueryHandler(self):
#         q = BibliographicEntityQueryHandler()
#         self.assertTrue(q.setDbPathOrUrl(self.relational))
#         self.assertEqual(q.getDbPathOrUrl(), self.relational)

#         i = q.getById("")
#         self.assertIsInstance(i, DataFrame)

#         self.assertIsInstance(q.getAllBibliographicEntities(), DataFrame)
#         self.assertIsInstance(q.getBibliographicEntitiesWithTitle(""), DataFrame)
#         self.assertIsInstance(q.getBibliographicEntitiesWithAuthor(""), DataFrame)
#         self.assertIsInstance(q.getBibliographicEntitiesWithinPublicationDate(), DataFrame)
#         self.assertIsInstance(q.getBibliographicEntitiesWithVenue(""), DataFrame)

#     def test_05_FullQueryEngine(self):
#         jq = CitationQueryHandler()
#         jq.setDbPathOrUrl(self.graph)
#         cq = BibliographicEntityQueryHandler()
#         cq.setDbPathOrUrl(self.relational)

#         fq = FullQueryEngine()
#         self.assertIsInstance(fq.cleanCitationHandlers(), bool)
#         self.assertIsInstance(fq.cleanBibliographicEntityHandlers(), bool)
#         self.assertTrue(fq.addCitationHandler(jq))
#         self.assertTrue(fq.addBibliographicEntityHandler(cq))

#         self.assertEqual(fq.getEntityById(""), None)

#         t = fq.getAllCitations()
#         self.assertIsInstance(t, list)
#         for i in t:
#             self.assertIsInstance(i, Citation)
#             self.assertIsInstance(i.getCitingEntity(), BibliographicEntity)
#             self.assertIsInstance(i.getCitedEntity(), BibliographicEntity)

#         r = fq.getAllAuthorSelfCitations()
#         self.assertIsInstance(r, list)
#         for i in r:
#             self.assertIsInstance(i, AuthorSelfCitation)

#         r = fq.getAllJournalSelfCitations()
#         self.assertIsInstance(r, list)
#         for i in r:
#             self.assertIsInstance(i, JournalSelfCitation)

#         r = fq.getCitationsWithinTimespan()
#         self.assertIsInstance(r, list)
#         for i in range(len(r)):
#             self.assertIsInstance(r[i], Citation)
#             self.assertCitationEqual(r[i], t[i])

#         r = fq.getCitationsWithinTimespan("P2Y","")
#         self.assertIsInstance(r, list)
#         for i in range(len(r)):
#             self.assertIsInstance(r[i], Citation)


#         r = fq.getCitationsWithinTimespan("","P18Y")
#         self.assertIsInstance(r, list)
#         for i in range(len(r)):
#             self.assertIsInstance(r[i], Citation)


#         r = fq.getCitationsWithinDate()
#         self.assertIsInstance(r, list)
#         for i in range(len(r)):
#             self.assertCitationEqual(r[i], t[i])

#         r = fq.getCitationsWithinDate("2010-03", "")
#         self.assertIsInstance(r, list)
#         for i in range(len(r)):
#             self.assertIsInstance(r[i], Citation)
#             self.assertGreaterEqual(r[i].getDate(), "2010-03")

#         r = fq.getCitationsWithinDate("", "2020")
#         self.assertIsInstance(r, list)
#         for i in range(len(r)):
#             self.assertIsInstance(r[i], Citation)
#             self.assertLessEqual(r[i].getDate(), "2020-12-31")


#         b = fq.getAllBibliographicEntities()
#         self.assertIsInstance(b, list)
#         for i in b:
#             self.assertIsInstance(i, BibliographicEntity)

#         r = fq.getBibliographicEntitiesWithTitle("")
#         self.assertIsInstance(r, list)
#         for i in range(len(r)):
#             self.assertIsInstance(r[i], BibliographicEntity)
#             self.assertBibliographicEntityEqual(r[i], b[i])
#             self.assertIn("", r[i].getTitle())

#         r = fq.getBibliographicEntitiesWithAuthor("")
#         self.assertIsInstance(r, list)
#         for i in range(len(r)):
#             self.assertIsInstance(r[i], BibliographicEntity)
#             self.assertBibliographicEntityEqual(r[i], b[i])
#             for author in r[i].getAuthors():
#                 if "" in author:
#                     flag = True
#             self.assertTrue(flag)

#         r = fq.getBibliographicEntitiesWithinPublicationDate()
#         self.assertIsInstance(r, list)
#         for i in range(len(r)):
#             self.assertIsInstance(r[i], BibliographicEntity)
#             self.assertBibliographicEntityEqual(r[i], b[i])
        
#         r = fq.getBibliographicEntitiesWithinPublicationDate("2022","")
#         self.assertIsInstance(r, list)
#         self.assertTrue(r)
#         for i in r:
#             self.assertIsInstance(i, BibliographicEntity)
#             self.assertGreaterEqual(i.getPublicationDate(), "2022")
        
#         r = fq.getBibliographicEntitiesWithinPublicationDate("","2024")
#         self.assertIsInstance(r, list)
#         self.assertTrue(r)
#         for i in r:
#             self.assertIsInstance(i, BibliographicEntity)
#             self.assertLessEqual(i.getPublicationDate(), "2024-12-31")

#         r = fq.getBibliographicEntitiesWithVenue("")
#         self.assertIsInstance(r, list)
#         for i in range(len(r)):
#             self.assertIsInstance(r[i], BibliographicEntity)
#             self.assertBibliographicEntityEqual(r[i], b[i])
#             self.assertIn("", r[i].getVenue())

#         # FullQueryEngine
#         # -----

#         r = fq.getAuthorSelfCitationsByName("")
#         self.assertIsInstance(r, list)
#         for i in range(len(r)):
#             self.assertIsInstance(r[i], AuthorSelfCitation)
#             for author in r[i].getCitingEntity().getAuthors():
#                 self.assertIn("", author)

#         r = fq.getJournalSelfCitationsByName("")
#         self.assertIsInstance(r, list)
#         for i in range(len(r)):
#             self.assertIsInstance(r[i], JournalSelfCitation)
#             self.assertIn("", r[i].getCitingEntity().getVenue())

#         r = fq.getCitationsOfBibEntityByTitleWithinDate("")
#         self.assertIsInstance(r, list)
#         for i in range(len(r)):
#             self.assertIsInstance(r[i], Citation)
#             self.assertCitationEqual(r[i], t[i])
#             self.assertIn("", r[i].getCitedEntity().getTitle())
#             self.assertGreaterEqual(r[i].getCreation(), "")
#             self.assertLessEqual(r[i].getCreation(), "")

#         r = fq.getCitationsOfBibEntityByTitleWithinDate("", "2005", "")
#         self.assertIsInstance(r, list)
#         for i in range(len(r)):
#             self.assertIsInstance(r[i], Citation)
#             self.assertCitationEqual(r[i], t[i])
#             self.assertIn("", r[i].getCitedEntity().getTitle())
#             self.assertGreaterEqual(r[i].getCreation(), "2005")

#         r = fq.getCitationsOfBibEntityByTitleWithinDate("", "", "2015")
#         self.assertIsInstance(r, list)
#         for i in range(len(r)):
#             self.assertIsInstance(r[i], Citation)
#             self.assertIn("", r[i].getCitedEntity().getTitle())
#             self.assertLessEqual(r[i].getCreation(), "2015")

#         r = fq.getReferencesOfBibEntityByTitleWithinTimespan("")
#         self.assertIsInstance(r, list)
#         for i in range(len(r)):
#             self.assertIsInstance(r[i], Citation)
#             self.assertCitationEqual(r[i], t[i])
#             self.assertIn("", r[i].getCitingEntity().getTitle())


#         r = fq.getReferencesOfBibEntityByTitleWithinTimespan("", "P2Y", "")
#         self.assertIsInstance(r, list)
#         for i in range(len(r)):
#             self.assertIsInstance(r[i], Citation)
#             self.assertIn("", r[i].getCitingEntity().getTitle())


#         r = fq.getReferencesOfBibEntityByTitleWithinTimespan("", "", "P15Y")
#         self.assertIsInstance(r, list)
#         for i in range(len(r)):
#             self.assertIsInstance(r[i], Citation)
#             self.assertIn("", r[i].getCitingEntity().getTitle())


class TestSingle(unittest.TestCase):

    citation = "data" + sep + "dh_citations.csv"
    bib_entity = "data" + sep + "dh_metadata.json"
    relational = "." + sep + "data.db"
    graph = "http://localhost:9999/blazegraph/sparql"

    def assertBibliographicEntityEqual(self, be1:BibliographicEntity, be2:BibliographicEntity):
        self.assertEqual(be1.getTitle(), be2.getTitle())
        self.assertEqual(be1.getAuthors(), be2.getAuthors())
        self.assertEqual(be1.getIds(), be2.getIds())
        self.assertEqual(be1.getPublicationDate(), be2.getPublicationDate())
        self.assertEqual(be1.getVenue(), be2.getVenue())


    def assertCitationEqual(self, cit1:list, cit2:list):
        self.assertEqual(cit1.getIds(), cit2.getIds())
        self.assertEqual(cit1.getCreation(), cit2.getCreation())
        self.assertEqual(cit1.getTimespan(), cit2.getTimespan())

        if type(cit1.getCitingEntity()) == BibliographicEntity:
            self.assertBibliographicEntityEqual([cit1.getCitingEntity()], [cit2.CitingEntity()])
        else:
            self.assertEqual(cit1.getCitingEntity(), cit2.getCitingEntity())

        if type(cit1.getCitedEntity()) == BibliographicEntity:
            self.assertBibliographicEntityEqual([cit1.getCitedEntity()], [cit2.CitedEntity()])
        else:
            self.assertEqual(cit1.getCitedEntity(), cit2.getCitedEntity())

    def test_01(self):
        jq = CitationQueryHandler()
        jq.setDbPathOrUrl(self.graph)
        cq = BibliographicEntityQueryHandler()
        cq.setDbPathOrUrl(self.relational)

        fq = FullQueryEngine()
        self.assertIsInstance(fq.cleanCitationHandlers(), bool)
        self.assertIsInstance(fq.cleanBibliographicEntityHandlers(), bool)
        self.assertTrue(fq.addCitationHandler(jq))
        self.assertTrue(fq.addBibliographicEntityHandler(cq))
