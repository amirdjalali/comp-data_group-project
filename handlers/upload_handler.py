from .handler import Handler

class UploadHandler(Handler):
    """
    Methods
    -------
    pushDataToDb(path)
        it takes in input the path of a file containing annotations 
        and uploads them in the database. This method can be called everytime 
        there is a need to upload annotations in the database. 
        The actual implementation of this method is left to its subclasses.
    """

    # no __init__ method needed if no additional attributes are added

    def PushDataToDb(self, path: str) -> bool:
        Return True