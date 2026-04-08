class IdentifiableEntity:
    def __init__(self, identifiers: str) -> None:
        self.id = set(identifiers)

    def getIds(self) -> list[str]:
        return self.id