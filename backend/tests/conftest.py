import sys
import os
import pytest

# add backend directory to sys.path so that modules can be imported for testing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.api_schemas import StoryRequest, CharacterState

@pytest.fixture
def sample_character():
    return CharacterState(name="char1", emotion="neutral", local_vars={})

@pytest.fixture
def sample_characters():
    return [
        CharacterState(name="char1", emotion="neutral", local_vars={}), 
        CharacterState(name="char2", emotion="happy", local_vars={})
    ]

@pytest.fixture
def sample_context():
    return ["this is my context1", "this is my context2"]

@pytest.fixture
def sample_user_choice():
    return "user_choice"

@pytest.fixture
def sample_scene_id():
    return "ID0001"

@pytest.fixture
def sample_story_request():
    sample_scene_id = "ID0001"
    sample_context = ["this is my context1", "this is my context2"]
    sample_characters = [
        CharacterState(name="char1", emotion="neutral", local_vars={}), 
        CharacterState(name="char2", emotion="happy", local_vars={})
    ]
    sample_user_choice = "user_choice"
    return StoryRequest(
        scene_id=sample_scene_id,
        context=sample_context,
        active_chars=sample_characters,
        user_choice=sample_user_choice
    )