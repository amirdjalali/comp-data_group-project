from citation import Citation
from bibliographic_entity import BibliographicEntity

class JournalSelfCitation(Citation):
    def __init__(self, identifiers: list[str], creation: str, timespan: str, citing_entity: BibliographicEntity, cited_entity: BibliographicEntity) -> None:
        super().__init__(identifiers, creation, timespan, citing_entity, cited_entity)