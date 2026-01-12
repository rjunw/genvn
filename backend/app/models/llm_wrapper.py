# ------------------------------------------------------------------------
# LLM Wrapper
# 
# Interface for LLM adapters. Currently implemented adapters:
# - OllamaAdapter
# ------------------------------------------------------------------------

import abc 
import requests
from typing import Generator, List, Dict

class LLMAdapter(abc.ABC):
    """
    Abstract base class for LLM adapters. 
    """
    # TODO: think about whether we want a shared constructor
    # def __init__(self):
    #     pass

    @abc.abstractmethod
    def chat_stream(self, messages: List[Dict[str, str]]):
        """
        Yield streamed response.
        """
        pass

    @abc.abstractmethod
    def chat_chunk(self, messages: List[Dict[str, str]]):
        """
        Return single chunk response.
        """
        pass


class OllamaAdapter(LLMAdapter):
    """
    Ollama LLM adapter for local inference. 

    Use chat endpoint to allow for message history context.
    """
    def __init__(self, url: str, model: str):
        self.url = url # ollama api url
        self.model = model # ollama model name
        self.chat_url = f"{self.url}/api/chat" # natural language chat

    # for now, just use messages, rather than allowing kwargs
    def chat_stream(self, messages: List[Dict[str, str]], options: Dict[str, str] = {}):
        """
        Args:
            messages: List of messages to send to LLM, defined by 'role' and 'content'
            options: Additional inference options
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": options 
        }

        # stream response https://stackoverflow.com/questions/57497833/python-requests-stream-data-from-api
        with requests.post(self.chat_url, json=payload, stream=True) as resp:
            for line in resp.iter_lines(): # streams word by word
                if line:
                    yield line

    def chat_chunk(self, messages: List[Dict[str, str]], options: Dict[str, str] = {}):
        """
        Args:
            messages: List of messages to send to LLM, defined by 'role' and 'content'
            options: Additional inference options
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": options
        }
        response = requests.post(self.chat_url, json=payload)
        return response.json()

    def list_models(self):
        response = requests.get(f"{self.url}/api/tags")
        return response.json()



if __name__ == "__main__":
    adapter = OllamaAdapter(url="http://localhost:11434", model="gemma3")
    print(adapter.list_models())
    
    # treat chat_stream as a generator
    for chunk in adapter.chat_stream(messages=[
        {
            "role": "user", 
            "content": "Hello, how are you?"
        }
    ]):
        print(chunk)

    chunk = adapter.chat_chunk(messages=[
        {
            "role": "user", 
            "content": "Hello, how are you?"
        }
    ])
    print(chunk)
    

    