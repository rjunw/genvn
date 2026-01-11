# ------------------------------------------------------------------------
# Story API Router
#
# Define API endpoints for story-telling engine.
# ------------------------------------------------------------------------

from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from app.models.api_schemas import StoryRequest, Chunk 
from app.services.rag_engine import GraphRAG

router = APIRouter() 
rag_engine = GraphRAG()

@router.post("/generate_stream")
async def generate_stream(request: StoryRequest):
    """
    Endpoint to generate the next story dialogue as a stream.
    """
    context = rag_engine.retrieve(
        scene_id=request.scene_id,
        context=request.context, 
        active_chars=request.active_chars
    )
    response_generator = rag_engine.generate_stream(
        context=context,
        user_choice=request.user_choice
    )
    return StreamingResponse(response_generator, media_type="text/event-stream")

@router.post("/generate_chunk")
async def generate_chunk(request: StoryRequest):
    """
    Endpoint to generate the next story dialogue as a chunk.
    """
    context = rag_engine.retrieve(
        scene_id=request.scene_id,
        context=request.context,
        active_chars=request.active_chars
    )
    response = rag_engine.generate_chunk(
        context=context,
        user_choice=request.user_choice
    )
    return JSONResponse(content=response)

@router.get("/save_story")
async def save_story():
    """
    Endpoint to save in-memory kuzu db (dynamic story graph)

    TODO: save as json or parquet... thinking...
    """
    pass