# ------------------------------------------------------------------------
# Asset Manager
#
# Handles asset loading, embedding, and indexing.
# ------------------------------------------------------------------------

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import json
import base64
from app.models.embeddings import ImageTextEmbedder, AudioTextEmbedder
from app.models.llm_wrapper import OllamaAdapter
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
        self.llm_adapter = OllamaAdapter(
            url=settings.OLLAMA_URL,
            model=settings.OLLAMA_VLM_MODEL
        )

        self.asset_path = asset_path

        # want to keep db methods private
        self._db = get_db(db_type="kuzu", db_path=db_path)
        self._conn = self._db.conn
        
        # TODO: check if db is empty

    def load_assets(self, infer_metadata: bool = True):
        """
        Parse asset directory, embed assets, and index them in the database.
        This should be called once if db is empty, or if existing asset file 
        structure has changed.

        TODO: implement schema (asset_path, asset_name, asset_type, asset_embedding)
        """
        # initialize database
        self.initialize_db()

        # check if db is empty
        response = self._conn.execute("MATCH (n:Image) RETURN COUNT(*)")
        for row in response:
            db_rows = row[0]
        
        # fill db if empty
        if db_rows == 0:
            # parse assets
            image_assets = self.parse_image_assets()

            # embed assets
            image_assets = self.embed_image_assets(image_assets, infer_metadata=infer_metadata)

            print(f"Adding {len(image_assets)} images to database...")
            for asset in tqdm(image_assets):
                self._conn.execute(
                    """
                    CREATE (n:Image {
                        image_path: $image_path,
                        image_name: $image_name,
                        image_type: $image_type,
                        image_embedding: $image_embedding,
                        image_metadata: $image_metadata
                    })
                    """,
                    {
                        "image_path": asset['image_path'],
                        "image_name": asset['image_name'],
                        "image_type": asset['image_type'],
                        "image_embedding": asset['image_embedding'],
                        "image_metadata": asset['image_metadata']
                    }
                )

            # create HNSW index
            print("Creating HNSW index...")
            self._conn.execute(
                """
                CALL CREATE_VECTOR_INDEX(
                    'Image',
                    'image_index',
                    'image_embedding',
                    metric := 'cosine'
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
            "image_embedding": f"DOUBLE[{settings.IMAGE_TEXT_DIM}]",
            "image_metadata": "STRING"
        }
        self._db.create_schema(image_schema)

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

    def embed_image_assets(self, image_assets: list, infer_metadata: bool = True):
        """
        Embed image assets and index them in the database.

        TODO: Figure out how to reduce latency of metadata extraction - quantize vlm?
        """
        failed = 0
        if infer_metadata:
            print("Inferring metadata for image assets...")
        for asset in tqdm(image_assets):
            # try:
            image = Image.open(asset['image_path']).convert('RGB')

            embedding = self.image_text_embedder.embed_image(image)
            metadata_extracted = "No extracted metadata"
            if infer_metadata:
                # use llm to infer metadata
                metadata_extraction_prompt = """
                You are an expert metadata and keyword captioner. Explain this photo in 1 sentence, with as little filler as possible. Do not write anything other than your most important keyword metadata.
                """
                with open(asset['image_path'], 'rb') as f:
                    image_b64 = base64.b64encode(f.read()).decode('utf-8')
                
                metadata = self.llm_adapter.chat_chunk(messages=[
                    {
                        "role": "user", 
                        "content": metadata_extraction_prompt,
                        'images': [image_b64]
                    }
                ])
                # print(metadata)
                metadata_extracted = metadata['message']['content']
                # print(metadata_extracted)
                # embed metadata
                metadata_embedding = self.image_text_embedder.embed_text(metadata_extracted)

                # hybrid embedding
                embedding = 0.3*embedding + 0.7*metadata_embedding
                embedding = metadata_embedding

            asset['image_embedding'] = embedding.cpu().tolist()[0]
            asset['image_metadata'] = metadata_extracted
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

    def search_image_assets(self, query: str, rewrite: bool = False, k: int = 5):
        """
        Search image assets in the database.
        """
        if rewrite:
            # use llm to rewrite query
            metadata_extraction_prompt = """
            You are an expert metadata and keyword captioner. Rewrite the query in 1 sentence, with as little filler as possible. Do not write anything other than your most important keyword metadata.

            Query: {query}
            """
            response = self.llm_adapter.chat_chunk(messages=[
                {
                    "role": "user", 
                    "content": metadata_extraction_prompt.format(query=query)
                }
            ])
            query = response['message']['content']

        embedding = self.image_text_embedder.embed_text(query)
        embedding = embedding.cpu().tolist()[0]

        response = self._conn.execute(
            f"""
            CALL QUERY_VECTOR_INDEX(
                'Image',
                'image_index',
                $embedding,
                $k,
                efs:=550
            )
            RETURN node.image_path, node.image_metadata, distance
            ORDER BY distance;
            """,
            {"embedding": embedding, "k": k}
        )
        res = []
        for row in response.rows_as_dict():
            row['query'] = query
            res.append(row)
        return res

if __name__ == "__main__":
    asset_manager = AssetManager()
    # asset_manager.initialize_db()
    # assets = asset_manager.parse_image_assets()
    # print(assets[:5])
    # embeddings = asset_manager.embed_image_assets(assets[:5])
    # print(embeddings[:5])
    asset_manager.load_assets(infer_metadata=True)
    response = asset_manager._db.conn.execute("MATCH (n:Image) RETURN *")
    # for row in response.rows_as_dict():
    #     print(row)
    query_assets = asset_manager.search_image_assets(query="a messy kitchen", rewrite=True, k=5)
    print("ASC")
    for asset in query_assets:
        print(asset)