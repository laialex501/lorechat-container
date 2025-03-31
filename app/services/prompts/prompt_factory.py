"""Prompt factory and persona templates."""
from enum import Enum
from typing import Union

from app import logger
from app.services.prompts.base import BasePrompt, DevilPrompt, ScribePrompt


class PersonaType(Enum):
    SCRIBE = "scribe"
    DEVIL = "devil"
    ADVENTURER = "adventurer"


class PromptFactory:
    """Factory class for prompts."""

    @staticmethod
    def create_prompt(persona: Union[PersonaType, str]) -> BasePrompt:
        """Factory function to create prompt based on persona type.
        
        Args:
            persona: Either a PersonaType enum or a string matching an enum value
            
        Returns:
            BasePrompt: The configured prompt for the persona
            
        Raises:
            ValueError: If persona type is invalid or not recognized
        """
        # Convert string to enum if needed
        if isinstance(persona, str):
            try:
                persona = PersonaType(persona)
            except ValueError:
                raise ValueError(f"Invalid persona type: {persona}")
        
        if not isinstance(persona, PersonaType):
            raise ValueError(f"Persona must be a PersonaType enum or valid string value: {persona}")

        # Get persona value for logging
        persona_value = persona.value if isinstance(persona, PersonaType) else persona
        logger.info(f"Getting prompt for persona {persona_value}...")

        if (persona == PersonaType.SCRIBE):
            return ScribePrompt()
        elif (persona == PersonaType.DEVIL):
            return DevilPrompt()
        else:
            raise ValueError(f"Persona type is not recognized: {persona}")
