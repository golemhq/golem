import pymongo
import tinymongo


class Mongo(object):
    """
    Creating Connection object for Mongo DB.
    """

    db = None

    def __init__(self, **kwargs):
        db_string = kwargs["db_string"]
        db_name = kwargs["db_name"]
        connection = pymongo.MongoClient(db_string)
        self.db = connection[db_name]

class Tinydb(object):
    """
    Creating Connection object for Tiny DB.
    """

    db = None

    def __init__(self, **kwargs):
        db_name = kwargs["db_name"]
        connection = tinymongo.TinyMongoClient()
        self.db = connection[db_name]