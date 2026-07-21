class IdentifiableEntity:
    def __init__(self, identifiers: list[str]) -> None:
        self.id = set()

        for identifier in identifiers:
            #Since Blazegraph returns full URIs for citations, we remove the base URL prefix
            # to isolate the short ID, while keeping OMID strings intact.
            clean_id = identifier.replace("https://w3id.org/oc/index/ci/", "")
            self.id.add(clean_id)


    def getIds(self) -> list[str]:
        return list(self.id)