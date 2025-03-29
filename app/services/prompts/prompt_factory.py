"""Prompt factory and persona templates."""
from enum import Enum

from app import logger
from app.services.prompts.base import BasePrompt, DevilPrompt, ScribePrompt


class PersonaType(Enum):
    SCRIBE = "scribe"
    DEVIL = "devil"
    ADVENTURER = "adventurer"


class PromptFactory:
    """Factory class for prompts."""

    @staticmethod
    def create_prompt(persona: PersonaType) -> BasePrompt:
        """Factory function to get vector store service."""
        logger.info(f"Getting prompt for persona {persona.value}...")
        if (persona == PersonaType.SCRIBE):
            return ScribePrompt()
        elif (persona == PersonaType.DEVIL):
            return DevilPrompt()
        else:
            raise ValueError("Persona type is not recognized")