# ------------------------------------------------------------------------
# RAG Engine Tests
#
# Run with: pytest -v -s backend/tests/services/rag_engine_test.py
# ------------------------------------------------------------------------

from app.services.rag_engine import GraphRAG
from app.models.api_schemas import StoryRequest

def test_retrieve(sample_scene_id, sample_context, sample_characters):
    rag_engine = GraphRAG()
    response = rag_engine.retrieve(
        scene_id=sample_scene_id,
        context=sample_context,
        active_chars=sample_characters
    )
    assert response == "Scene ID: ID0001, Retrieval Context: ['this is my context1', 'this is my context2'], Active Characters: [CharacterState(name='char1', emotion='neutral', local_vars={}), CharacterState(name='char2', emotion='happy', local_vars={})]"


def test_generate_stream(sample_context, sample_user_choice):
    rag_engine = GraphRAG()
    response = rag_engine.generate_stream(
        context=sample_context,
        user_choice=sample_user_choice
    )
    assert next(response) == "Context: ['this is my context1', 'this is my context2'], User Choice: user_choice"
    
def test_generate_chunk(sample_context, sample_user_choice):
    rag_engine = GraphRAG()
    response = rag_engine.generate_chunk(
        context=sample_context,
        user_choice=sample_user_choice
    )
    assert response == "Context: ['this is my context1', 'this is my context2'], User Choice: user_choice"
