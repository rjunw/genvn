# ------------------------------------------------------------------------
# GraphRAG Engine
# 
# Define retrieval capabilities for more consistent story-telling.
# ------------------------------------------------------------------------

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.models.llm_wrapper import LLMAdapter
from typing import List, Dict

class GraphRAG:
    """
    Use GraphRAG to provide memory/lore for story generation.
    """
    def __init__(self, llm_adapter: LLMAdapter):
        self.llm_adapter = llm_adapter
        # initialize graphdb connection


    def retrieve(self, scene_id: str, context: str, user_choice: str, active_chars: List[str]):
        """
        Retrieve relevant memory/lore for story generation, based on scene, context, and user choice.

        Args:
            scene_id: ID of the scene
            context: Context for the story to find relevant memory/lore
            user_choice: User's choice for the story to find relevant visual/audio content
            active_chars: List of active characters to find relevant memory/lore
        """
        return [{"role": "Sky", "content": "The sky is blue because of I, the lord, the sky, was born that way."}, {"role": "Sky", "content": "I was born under the sea, and so the sky reflects me."}]

    def generate_stream(self, scene_id: str, context: str, active_chars: List[str], history: List[str], user_choice: str, options: Dict[str, str]):
        """
        Yield streamed response with context retrieved from RAG.
        """

        retrieved_context = self.retrieve(scene_id, context, user_choice, active_chars)
        system_prompt = self._build_system_prompt(retrieved_context)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"History: \n{history}\nUser: {user_choice}"}
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

        TODO: Express all timeline options or maybe return json and decode in frontend timeline
        """

        system_prompt = f"""
        You are a magnificent story-teller.

        Your goal is to generate the next chunk of text for the story based on the Player's chosen action. 
        
        Choose ONE of the following:
        - Create one character's dialogue
        - Create one piece of narration
        - Create one set of choices for the player to choose from

        STRICT OUTPUT FORMAT (Dialogic 2.0's "Timeline Text Syntax"):
        1. Use "CharacterName: Dialogue" for speech. e.g. "John: Lovely to see you!"
        2. Replace "CharacterName" with "CharacterName (CharacterEmotion)" to express emotion. e.g. "John (happy): Lovely to see you!"
        3. Use "narrator: Description" for narration. e.g. "narrator: John looks around, noticing the sky in the distance."
        4. To create choices for the player to choose from, use "- UserChoice". Create at least two choices, and no more than four choices. e.g. "- I don't know\n- This is why...\n- I give up"
        5. Do NOT use any other form of formatting, purely raw text.
        6. Keep descriptions concise.

        The context for the story is as follows:
        {retrieved_context}
        """
        
        return system_prompt

if __name__ == "__main__":
    from app.models.llm_wrapper import OllamaAdapter
    user_choice = "But Why?"
    history = [
        {"role": "user", "content": "Are you sure the sky is blue?"},
        {"role": "Sky", "content": "Yes I'm sure."}
    ]
    rag_engine = GraphRAG(llm_adapter=OllamaAdapter(url="http://localhost:11434", model="gemma3"))

    context = "Why do you think the sky is blue?"
    retrieved_context = rag_engine.retrieve(scene_id="ID0001", context=context, active_chars=[], user_choice=user_choice)
    print(retrieved_context)

    print(rag_engine._build_system_prompt(retrieved_context))


    for chunk in rag_engine.generate_stream(scene_id="ID0001", context=context, active_chars=[], history=history, user_choice=user_choice, options={}):
        print(chunk)

    chunk = rag_engine.generate_chunk(scene_id="ID0001", context=context, active_chars=[], history=history, user_choice=user_choice, options={})
    print(chunk)
    print('\n' + chunk['message']['content'])