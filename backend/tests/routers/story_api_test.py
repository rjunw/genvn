# ------------------------------------------------------------------------
# Story API Tests
#
# Run with: pytest -v -s backend/tests/routers/story_api_test.py
# ------------------------------------------------------------------------

import requests
from app.models.api_schemas import StoryRequest

def test_generate_stream(sample_story_request):
    url = "http://localhost:8000/api/story/generate_stream"
    story_request = sample_story_request
    response = requests.post(url, json=story_request.model_dump())
    print(response.text)

    assert response.status_code == 200

def test_generate_chunk(sample_story_request):
    url = "http://localhost:8000/api/story/generate_chunk"
    story_request = sample_story_request
    response = requests.post(url, json=story_request.model_dump())
    print(response.text)

    assert response.status_code == 200