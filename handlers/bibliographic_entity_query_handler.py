from .query_handler import QueryHandler
from sqlite3 import connect
from pandas import DataFrame, Series, read_sql

class BibliographicEntityQueryHandler(QueryHandler):

    def getById(self, id: str) -> DataFrame:

        with connect(self.getDbPathOrUrl()) as con:
            query_id = f"""
                SELECT *
                FROM BibliographicEntity
                JOIN BibliographicEntityIDs ON BibliographicEntity.bib_item_id = BibliographicEntityIDs.bibitem_id
                WHERE id = "{id}"
            """
            df_sql = read_sql(query_id, con)
            bib_item_id = df_sql.at[0, "bib_item_id"]

            print(df_sql)
            print(bib_item_id)

            query_ids = f"""
                SELECT *
                FROM BibliographicEntityIDs
                WHERE bibitem_id = "{bib_item_id}"
            """

            df_ids = read_sql(query_ids, con)
            ids = []
            for i, row in df_ids.iterrows():
                ids.append(row["id"])
            
            df_sql["id"] = df_sql["id"].astype('object')
            df_sql.at[0, "id"] = ids

            query_authors = f"""
                SELECT name, pos
                FROM BibliographicEntityAuthors
                JOIN Author ON BibliographicEntityAuthors.author_id = Author.author_id
                WHERE bibitem_id = "{bib_item_id}"
            """

            df_authors = read_sql(query_authors, con)
            authors = []
            for i, row in df_authors.iterrows():
                authors.append((row["name"], row["pos"]))
            authors = sorted(authors, key=lambda x: x[1])
            authors_list = []
            for author, pos in authors:
                authors_list.append(author)
            df_sql["authors"] = Series(dtype="object")
            df_sql.at[0, "authors"] = authors_list
            
            print(df_sql)

        return df_sql

    def getAllBibliographicEntities(self) -> DataFrame:

        with connect(self.getDbPathOrUrl()) as con:
            query_id = f"""
                SELECT *
                FROM BibliographicEntity
                JOIN BibliographicEntityIDs ON BibliographicEntity.bib_item_id = BibliographicEntityIDs.bibitem_id
            """
            df_id = read_sql(query_id, con)
            print(df_id)

            ids = {}

            for idx, row in df_id.iterrows():
                if row["bibitem_id"] not in ids:
                    ids[row["bibitem_id"]] = []
                ids[row["bibitem_id"]].append(row["id"])
            
            df_ids = DataFrame(ids.items(), columns=["bibitem_id", "ids"])
            print(df_ids)

            query_bibentity = f"""
                SELECT *
                FROM BibliographicEntity
            """
            df_entities = read_sql(query_bibentity, con)
            print(df_entities)
            new_df = df_entities.merge(df_ids, left_on="bib_item_id", right_on="bibitem_id").drop(columns="bibitem_id")

            print(new_df)

            query_authors = """
                SELECT *
                FROM BibliographicEntityAuthors
                JOIN Author ON BibliographicEntityAuthors.author_id = Author.author_id
            """
            df_authors = read_sql(query_authors, con)
            print(df_authors)

            authors = {}

            for idx, row in df_authors.iterrows():
                if row["bibitem_id"] not in authors:
                    authors[row["bibitem_id"]] = []
                authors[row["bibitem_id"]].append((row["name"], row["pos"]))
            
            for key in authors:
                ordered_pos = sorted(authors[key], key=lambda x: x[1])
                ordered = []
                for author, pos in ordered_pos:
                    ordered.append(author)
                authors[key] = ordered
            
            df_autori = DataFrame(authors.items(), columns=["bibitem_id", "authors"])
            print(df_autori)

            final_df = new_df.merge(df_autori, left_on="bib_item_id", right_on="bibitem_id").drop(columns="bib_item_id")

            print(final_df)

        return final_df

    def getBibliographicEntitiesWithTitle(self, title: str) -> DataFrame:
        return DataFrame()

    def getBibliographicEntitiesWithAuthor(self, author: str) -> DataFrame:
        return DataFrame()

    def getBibliographicEntitiesWithinPublicationDate(self, start_date: str, end_date: str) -> DataFrame:
        return DataFrame()

    def getBibliographicEntitiesWithVenue(self, venue: str) -> DataFrame:
        return DataFrame()

if __name__ == "__main__":
    handler = BibliographicEntityQueryHandler()
    handler.setDbPathOrUrl("relational.db")
    #handler.getById("openalex:W3193297707")
    handler.getAllBibliographicEntities()