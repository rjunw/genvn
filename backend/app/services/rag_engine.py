# ------------------------------------------------------------------------
# GraphRAG Engine
# 
# Define retrieval capabilities for more consistent story-telling.
# ------------------------------------------------------------------------

from app.models.llm_wrapper import LLMAdapter
from typing import List, Dict

class GraphRAG:
    """
    Use GraphRAG to provide memory/lore for story generation.
    """
    def __init__(self, llm_adapter: LLMAdapter):
        self.llm_adapter = llm_adapter
        # initialize graphdb connection
        pass

    def retrieve(self, scene_id: str, context: str, user_choice: str, active_chars: List[str]):
        """
        Retrieve relevant memory/lore for story generation, based on scene, context, and user choice.

        Args:
            scene_id: ID of the scene
            context: Context for the story to find relevant memory/lore
            user_choice: User's choice for the story to find relevant visual/audio content
            active_chars: List of active characters to find relevant memory/lore
        """
        return "retrieved_context"

    def generate_stream(self, scene_id: str, context: str, active_chars: List[str], history: List[str], user_choice: str, options: Dict[str, str]):
        """
        Yield streamed response with context retrieved from RAG.
        """

        retrieved_context = self.retrieve(scene_id, context, user_choice, active_chars)
        system_prompt = self._build_system_prompt(retrieved_context)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"History: \n{history}\nUser Choice: {user_choice}"}
        ]
        for chunk in self.llm_adapter.chat_stream(messages):
            yield chunk

    def generate_chunk(self, scene_id: str, context: str, active_chars: List[str], history: List[str], user_choice: str, options: Dict[str, str]):
        """
        Return single chunk response with context retrieved from RAG.
        """
        retrieved_context = self.retrieve(scene_id, context, user_choice, active_chars)
        system_prompt = self._build_system_prompt(retrieved_context)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"History: \n{history}\nUser Choice: {user_choice}"}
        ]
        return self.llm_adapter.chat_chunk(messages)

    def _build_system_prompt(self, retrieved_context: List[str]):
        """
        Return system prompt for story generation, using RAG-retrieved context.

        Should follow Dialogic 2's 'timeline text syntax': https://docs.dialogic.pro/timeline-text-syntax.html
        """

        system_prompt = f"""
        You are a magnificent story-teller.

        Your goal is to generate the next chunk of text for the story based on the Player's chosen action.
        STRICTLY OUTPUT IN DIALOGIC 2.0'S "Timeline Text Syntax":
        1. Use "<CharacterName>: <Dialogue>" for speech.
        2. Use "narrator: Description" for narration.
        3. To create choices, use "- <Option Text>".
        4. Do NOT use any other form of formatting, purely raw text.
        5. Keep descriptions concise.

        The context for the story is as follows:
        {retrieved_context}
        """
        
        return system_prompt

if __name__ == "__main__":
    rag_engine = GraphRAG(llm_adapter=OllamaAdapter(url="http://localhost:11434", model="gemma3"))
    for chunk in rag_engine.generate_stream(scene_id="ID0001", context=["Why is the sky blue?"], active_chars=[], history=["History1", "History2"], user_choice="user_choice", options={}):
        print(chunk)

    chunk = rag_engine.generate_chunk(scene_id="ID0001", context=["Why is the sky blue?"], active_chars=[], history=["History1", "History2"], user_choice="user_choice", options={})
    print(chunk)