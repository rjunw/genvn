# ------------------------------------------------------------------------
# Kuzu Database
#
# VectorDB will live on the disk, dynamic story graph will be in memory.
# - Kuzu as opposed to Neo4j or Memgraph which require server-client setup
# - Kuzu runs without server overhead, so it's better suited for game logic
# ------------------------------------------------------------------------
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from pathlib import Path
import kuzu
from app.config import settings
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

        columns = ""
        for column in schema:
            if column == "table_name":
                continue
            columns += f"{column} {schema[column]}, "
        columns = columns[:-2]
        q = f"""
        CREATE NODE TABLE IF NOT EXISTS {schema["table_name"]}({columns});
        """
        # print(q)
        self.conn.execute(q)


def get_db(db_type: str = "kuzu", db_path: Path = settings.KUZU_DB_PATH / "vdb.kuzu"):
    if db_type == "kuzu":
        return KuzuDB(db_path)
    else:
        raise NotImplementedError(f"Unknown database type: {db_type}")

if __name__ == "__main__":
    db = get_db()
    print(db.conn)

    image_schema = {
        "table_name": "Image",
        "image_id": "SERIAL PRIMARY KEY",
        "image_path": "STRING",
        "image_name": "STRING",
        "image_type": "STRING",
        "image_embedding": f"FLOAT[{settings.IMAGE_TEXT_DIM}]"
    }
    db.create_schema(image_schema)
    response = db.conn.execute("CALL show_tables() RETURN *;")
    for row in response:
        print(row)

    response = db.conn.execute("MATCH (n:Image) RETURN COUNT(*)")
    for row in response:
        print(row)