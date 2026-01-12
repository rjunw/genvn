# ------------------------------------------------------------------------
# Config
#
# Handles configuration for the application, i.e. paths, models, etc.
# TODO: should i split the settings into their own subsetting classes?
#   - i.e. DatabaseSettings, LLMSettings, EmbeddingSettings, etc.
# ------------------------------------------------------------------------

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    BASE_PATH: Path = Path('./backend')
    KUZU_DB_PATH: Path = BASE_PATH / "data" / "kuzu"
    ASSET_PATH: Path = BASE_PATH / "data" / "assets"

    DEVICE: str = "cpu"

    # ollama settings
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma3"

    # embedding models
    IMAGE_TEXT_MODEL_ID: str = "google/siglip2-so400m-patch16-naflex"
    IMAGE_TEXT_DIM: int = 1152 # siglip2-large-patch16-256
    AUDIO_TEXT_MODEL_ID: str = ""
    AUDIO_TEXT_DIM: int = 0

    # override defaults if .env provided
    model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore"
        )

    def _ensure_dirs(self):
        self.KUZU_DB_PATH.mkdir(exist_ok=True)
        self.ASSET_PATH.mkdir(exist_ok=True)

settings = Settings()
# settings._ensure_dirs() # create directories if they don't exist

if __name__ == "__main__":
    print(settings.BASE_PATH)
    print(settings.KUZU_DB_PATH)
    print(settings.ASSET_PATH)
    print(settings.OLLAMA_URL, settings.OLLAMA_MODEL)
    print(settings.IMAGE_TEXT_MODEL_ID, settings.IMAGE_TEXT_DIM)
    print(settings.AUDIO_TEXT_MODEL_ID, settings.AUDIO_TEXT_DIM)