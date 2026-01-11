# ------------------------------------------------------------------------
# Kuzu Database
#
# VectorDB will live on the disk, dynamic story graph will be in memory.
# - Kuzu as opposed to Neo4j or Memgraph which require server-client setup
# - Kuzu runs without server overhead, so it's better suited for game logic
# ------------------------------------------------------------------------

from pathlib import Path
import kuzu
from config import settings
from abc import ABC, abstractmethod

# kuzu is discontinued, so defining interface to allow for easy switching in case
# of a different vector database
class DB(ABC):
    def __init__(self, db_path: Path):
        self.db_path = db_path

    @abstractmethod
    def create_schema(self):
        """
        Create schema for the database.
        """
        pass

class KuzuDB(DB):
    """
    Kuzu Database Connection Manager

    Based on https://stackoverflow.com/questions/37408081/write-a-database-class-in-python
    """
    # _instance = None
    # def __new__(cls):
    #     """
    #     Enforce one instance of the database connection.
    #     """
    #     if cls._instance is None:
    #         cls._instance = super().__new__(cls)
    #     return cls._instance

    def __init__(self, db_path: Path = settings.KUZU_DB_PATH / "vdb.kuzu"):
        self.db = kuzu.Database(db_path)
        self.conn = kuzu.Connection(self.db)

        # install vectordb extension
        self.conn.execute("INSTALL vector; LOAD vector;")

    def create_schema(self, schema: dict):
        """
        Create schema for the database.
        """
        pass

def get_db(db_type: str = "kuzu", db_path: Path = settings.KUZU_DB_PATH / "vdb.kuzu"):
    if db_type == "kuzu":
        return KuzuDB(db_path)
    else:
        raise NotImplementedError(f"Unknown database type: {db_type}")

if __name__ == "__main__":
    db = get_db()
    print(db.conn)
    