# ------------------------------------------------------------------------
# Asset API Router
#
# Define API endpoints for asset retrieval.
# ------------------------------------------------------------------------

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.asset_manager import AssetManager
from app.models.api_schemas import AssetRequest

router = APIRouter()
asset_manager = AssetManager()

@router.post("/load_assets")
def load_assets():
    asset_manager.load_assets()
    return JSONResponse(content={"message": "Assets loaded successfully"})

@router.post("/retrieve_image_candidates")
def retrieve_image_candidates(request: AssetRequest, k: int = 5):
    """
    Example: 

        test_ar = AssetRequest(
            query="messy red kitchen",
            asset_type="image"
        )

        requests.post("http://localhost:8000/api/asset/retrieve_image_candidates", json=test_ar.model_dump(), params={'k':1}).json()
    """
    image_assets = asset_manager.search_image_assets(asset_request=request, k=k)
    return JSONResponse(content={"image_assets": image_assets})

@router.post("/retrieve_audio_candidates")
def retrieve_audio_candidates(request: AssetRequest, k: int = 5):
    audio_assets = asset_manager.search_audio_assets(asset_request=request, k=k)
    return JSONResponse(content={"audio_assets": audio_assets})