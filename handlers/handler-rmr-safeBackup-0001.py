class Handler:
    """
    Attributes
    ----------
    dbPathOrUrl : str
        The path or URL of the database, initially set as an empty string.
        Updated via setDbPathOrUrl.

    Methods
    -------
    getDbPathOrUrl()
        Returns the path or URL of the database.
    setDbPathOrUrl(pathOrUrl)
        Sets a new path or URL for the database.
    """

    def __init__(self) -> str:
        self.dbPathOrUrl: str = ""

    def getDbPathOrUrl(self) -> str:
        return self.dbPathOrUrl
    
    def setDbPathOrUrl(self, pathOrUrl: str) -> None:
        self.dbPathOrUrl = pathOrUrl
