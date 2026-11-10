"""Offline prototype. See README.md for scope and limitations."""
from abc import ABC, abstractmethod
class LLMProvider(ABC):
    @abstractmethod
    def reply(self, system_prompt, history):
        pass
class MockLLM(LLMProvider):
    def reply(self, system_prompt, history):
        return "Demo mein aapki baat note hui hai. Human review required; no payment action taken."
