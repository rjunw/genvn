# ------------------------------------------------------------------------
# Asset Manager
#
# Handles asset loading, embedding, and indexing.
# ------------------------------------------------------------------------

from app.models.embeddings import ImageTextEmbedder, AudioTextEmbedder
from app.database import get_db
from app.config import settings
from pathlib import Path

class AssetManager:
    def __init__(self, db_path: Path = settings.KUZU_DB_PATH / "vdb.kuzu"):
        self.image_text_embedder = ImageTextEmbedder(
            model_id=settings.IMAGE_TEXT_MODEL_ID, 
            device=settings.DEVICE
        )
        self.db = get_db(db_type="kuzu", db_path=db_path)
        self.asset_path = settings.ASSET_PATH
        self.conn = self.db.conn
        
        # TODO: check if db is empty

    def load_assets(self):
        """
        Parse asset directory, embed assets, and index them in the database.
        This should be called once if db is empty, or if existing asset file 
        structure has changed.

        TODO: implement schema (asset_path, asset_name, asset_type, asset_embedding)
        """

        # define schemas
        image_schema = {
            "image_id": "SERIAL PRIMARY KEY",
            "image_path": "TEXT",
            "image_name": "TEXT",
            "image_type": "TEXT",
            "image_embedding": f"FLOAT[{settings.IMAGE_TEXT_DIM}]"
        }
        self.db.create_schema(image_schema)

        audio_schema = {
            "audio_id": "SERIAL PRIMARY KEY",
            "audio_path": "TEXT",
            "audio_name": "TEXT",
            "audio_type": "TEXT",
            "audio_embedding": f"FLOAT[{settings.AUDIO_TEXT_DIM}]"
        }
        self.db.create_schema(audio_schema)

        # parse assets
        image_assets = self.parse_image_assets()
        audio_assets = self.parse_audio_assets()

        # embed assets
        self.embed_image_assets(image_assets)
        self.embed_audio_assets(audio_assets)

    def parse_image_assets(self):
        """
        Return a list of valid image asset file paths.
        """
        pass

    def parse_audio_assets(self):
        """
        Return a list of valid audio asset file paths.
        """
        pass

    def embed_image_assets(self):
        """
        Embed image assets and index them in the database.
        """
        pass

    def embed_audio_assets(self):
        """
        Embed audio assets and index them in the database.
        """
        pass

    def add_assets(self, asset_path: Path):
        """
        Add new assets to the database, if user provides new assets.
        """
        pass 