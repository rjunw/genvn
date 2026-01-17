# ------------------------------------------------------------------------
# Pydantic Schemas for FastAPI API Requests/Responses
# 
# Enforce schema for incoming requests and outgoing responses.
# ------------------------------------------------------------------------

from pydantic import BaseModel, Field
from typing import List, Union, Dict # Union instead of Optional for clarity

# ---------------------- Incoming Story Requests -------------------------

class CharacterState(BaseModel):
    """
    Current character state in story scene.
    """
    name: str
    emotion: Union[str, None] = "neutral" # default to neutral face
    local_vars: Dict[str, str | int | float | bool] = {} # any passed vars

class StoryRequest(BaseModel):
    """
    Incoming request from frontend engine to story-telling engine.
    """
    active_chars: List[CharacterState] # characters currently in scene
    scene_id: str # ID of current scene, identify scene in story graph

    # default_factory=list to prevent all requests sharing same instance
    context: List[str] = Field(default_factory=list) # rollback context
    user_choice: str # user's choice from previous scene

# ------------------------ Outgoing Story Responses -------------------------

class Chunk(BaseModel):
    """
    Chunk-generated text from the LLM response.
    """
    text: str # chunk-generated text
    is_final: bool = False # whether this is the final chunk
    fx: Union[Dict[str, str], None] = None # any events to trigger
    
# ------------------------ Incoming Asset Requests -------------------------

class AssetRequest(BaseModel):
    """
    Incoming request from frontend engine to asset manager.
    """
    asset_type: str # type of asset to retrieve
    asset_category: Union[str, None] = None # category of asset to retrieve
    query: str # query to retrieve assets