# GenVN

## Overview

TODO: Summarize project + goals

## Components

### Story-Telling Engine

Modular LLM framework running on a FastAPI backend to separate heavy-lifting from the lightweight Ren'Py frontend. Will start on ollama/HF for local dev, but extend to other popular APIs like Gemini/OpenAI if time permits.

- Can add option for VLM capabilities, so user can upload an image along with text to prompt next story responses (i.e. inputting an image to setup the premise of a custom scenario)

### Automated Retrieval Engine

Will keep this portion modular, but currently enstating paired text embeddings for Image-Text features and Audio-Text features.

- SigLIP2 (or other) for Image-Text retrieval, enforcing visual consistency
- CLAP (or other) for Audio-Text retrieval

Search will run via FAISS on locally built indices, allowing for easy serialization.

Retrieved objects will be incorporated into both story-telling engine context and displayed in the Ren'Py frontend.

### Dynamic Story Graphs

Starting a new scenario will instance a root node, that will extend during user choice and consequence selection. Still considering whether to use JSON or a specific graph class for efficient traversal, or just use both.

- Each request to the story-telling engine will return a structured response representing a new node that can be inserted into the story graph
- While in a scene, we traverse backwards through user choice DAG and when we enter a new scene, we pull longer-term memory into the context
- Encoding and decoding graph through JSON (if I decide to build a graph object) can be used for save states, but will likely need two states, one for vector database and one for story graph time-travel
- Also planning on implementing functionality for sharing stories between different users
