class IdentifiableEntity:
    def __init__(self, identifiers: list[str]) -> None:
        self.id = set()

        for identifier in identifiers:

            clean_id = identifier.replace("https://w3id.org/oc/index/ci/", "")
            self.id.add(clean_id)

        #for identifier in identifiers:
        #    self.id.add(identifier)

    def getIds(self) -> list[str]:
        return list(self.id)