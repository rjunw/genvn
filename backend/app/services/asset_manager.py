# ------------------------------------------------------------------------
# Asset Manager
#
# Handles asset loading, embedding, and indexing.
# ------------------------------------------------------------------------

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import json
from app.models.embeddings import ImageTextEmbedder, AudioTextEmbedder
from app.database import get_db
from app.config import settings
from pathlib import Path
from PIL import Image
from tqdm import tqdm

class AssetManager:
    def __init__(self, db_path: Path = settings.KUZU_DB_PATH / "vdb.kuzu", asset_path: Path = settings.ASSET_PATH):
        self.image_text_embedder = ImageTextEmbedder(
            model_id=settings.IMAGE_TEXT_MODEL_ID, 
            device=settings.DEVICE
        )
        self.db = get_db(db_type="kuzu", db_path=db_path)
        self.asset_path = asset_path
        self.conn = self.db.conn
        
        # TODO: check if db is empty

    def load_assets(self):
        """
        Parse asset directory, embed assets, and index them in the database.
        This should be called once if db is empty, or if existing asset file 
        structure has changed.

        TODO: implement schema (asset_path, asset_name, asset_type, asset_embedding)
        """
        # initialize database
        self.initialize_db()

        # check if db is empty
        response = self.conn.execute("MATCH (n:Image) RETURN COUNT(*)")
        for row in response:
            db_rows = row[0]
        
        # fill db if empty
        if db_rows == 0:
            # parse assets
            image_assets = self.parse_image_assets()

            # embed assets
            image_assets = self.embed_image_assets(image_assets)

            print(f"Adding {len(image_assets)} images to database...")
            for asset in tqdm(image_assets):
                self.conn.execute(
                    """
                    CREATE (n:Image {
                        image_path: $image_path,
                        image_name: $image_name,
                        image_type: $image_type,
                        image_embedding: $image_embedding
                    })
                    """,
                    {
                        "image_path": asset['image_path'],
                        "image_name": asset['image_name'],
                        "image_type": asset['image_type'],
                        "image_embedding": asset['image_embedding']
                    }
                )

            # create HNSW index
            print("Creating HNSW index...")
            self.conn.execute(
                """
                CALL CREATE_VECTOR_INDEX(
                    'Image',
                    'image_index',
                    'image_embedding',
                    metric := 'l2'
                );
                """
            )

            print('Vector database initialized successfully!')
        else:
            print('Vector database already initialized!')

    def initialize_db(self):
        """
        Initialize database schema, if it doesn't exist.
        """
        
        print("Initializing database...")
        
        # define schemas
        image_schema = {
            "table_name": "Image",
            "image_id": "SERIAL PRIMARY KEY",
            "image_path": "STRING",
            "image_name": "STRING",
            "image_type": "STRING",
            "image_embedding": f"DOUBLE[{settings.IMAGE_TEXT_DIM}]"
        }
        self.db.create_schema(image_schema)

        # audio_schema = {
        #     "table_name": "Audio",
        #     "audio_id": "SERIAL PRIMARY KEY",
        #     "audio_path": "STRING",
        #     "audio_name": "STRING",
        #     "audio_type": "STRING",
        #     "audio_embedding": f"FLOAT[{settings.AUDIO_TEXT_DIM}]"
        # }
        # self.db.create_schema(audio_schema)

    def parse_image_assets(self):
        """
        Return a json list of valid image asset file paths.

        TODO: do i want to filter out portraits? only keeping bg assets? 
        - skip pngs for now
        """
        extensions = {'.jpg', '.jpeg', '.webp'}
        files = [p for p in Path(self.asset_path).rglob("*") if p.suffix.lower() in extensions]
        assets = []
        for file in files:

            # convert png to jpg
            # if '.png' in str(file) and not os.path.exists(str(file).replace('.png', '.jpg')):
            #     im = Image.open(str(file)).convert('RGB')
            #     im.save(str(file).replace('.png', '.jpg'))
            #     file = Path(str(file).replace('.png', '.jpg')) 
            
            # if jpg for png already exists, continue
            # if '.png' in str(file):
            #     continue

            assets.append({
                "image_path": str(file),
                "image_name": file.name,
                "image_type": file.suffix.lower()
            })
        
        return assets

    def parse_audio_assets(self):
        """
        Return a json list of valid audio asset file paths.
        """
        pass

    def embed_image_assets(self, image_assets: list):
        """
        Embed image assets and index them in the database.

        TODO: push embeddings to database or return embeddings
        """
        failed = 0
        for asset in tqdm(image_assets):
            # try:
            image = Image.open(asset['image_path']).convert('RGB')

            embedding = self.image_text_embedder.embed_image(image)
            asset['image_embedding'] = embedding.cpu().tolist()[0]
            # except Exception as e:
            #     print(f"Failed to embed asset {asset['image_path']}: {e}")
            #     failed += 1
        
        print(f"Failed to embed {failed} assets")
        return image_assets

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

    def reindex_assets(self):
        """
        Reindex assets in the database, if user rearranges directory structure.
        """
        pass

    def search_image_assets(self, query: str, k: int = 5):
        """
        Search image assets in the database.
        """
        embedding = self.image_text_embedder.embed_text(query)
        embedding = embedding.cpu().tolist()[0]
        response = self.conn.execute(
            """
            CALL QUERY_VECTOR_INDEX(
                'Image',
                'image_index',
                $embedding,
                $k,
                efs:=10000
            )
            RETURN node.image_path, distance
            ORDER BY distance;
            """,
            {"embedding": embedding, "k": k}
        )
        
        res = response.get_all()
        return res

if __name__ == "__main__":
    asset_manager = AssetManager()
    # asset_manager.initialize_db()
    # assets = asset_manager.parse_image_assets()
    # print(assets[:5])
    # embeddings = asset_manager.embed_image_assets(assets[:5])
    # print(embeddings[:5])
    asset_manager.load_assets()
    query_assets = asset_manager.search_image_assets(query="airport", k=20)
    for asset in query_assets:
        print(asset)