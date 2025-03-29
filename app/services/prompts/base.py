"""Prompt and persona templates"""
from typing import Any, List

from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               MessagesPlaceholder,
                               SystemMessagePromptTemplate)
from langchain.prompts.base import BasePromptTemplate
from langchain.schema.messages import BaseMessage
from langchain_core.prompt_values import ChatPromptValue, PromptValue
from pydantic import Field


class BasePrompt(BasePromptTemplate):
    """Base class for persona prompts."""
    
    input_variables: List[str] = Field(default=["input", "context", "chat_history"])
    system_template: str = Field(default="")
    
    def format(self, **kwargs: Any) -> str:
        """Format the prompt template into a string."""
        messages = self.format_messages(**kwargs)
        return str(ChatPromptValue(messages=messages))
    
    def format_prompt(self, **kwargs: Any) -> PromptValue:
        """Format the prompt into a PromptValue."""
        messages = self.format_messages(**kwargs)
        return ChatPromptValue(messages=messages)
    
    def format_messages(self, **kwargs) -> List[BaseMessage]:
        """Format the prompt template into a list of messages."""
        return self.prompt_template.format_messages(**kwargs)
    
    @property
    def prompt_template(self) -> ChatPromptTemplate:
        """Creates a ChatPromptTemplate with system message, chat history, and human input."""
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.system_template),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template(
                "Context: {context}\nQuestion: {input}"
            )
        ])


class ScribePrompt(BasePrompt):
    """Wizard scribe persona for whimsical documentation explanations."""
    system_template: str = Field(default="""You are an eccentric Wizard scribe,\
        known for your quirky and unconventional approach to sharing knowledge.
When answering questions:
1. Use ONLY the provided context to answer
2. Incorporate whimsical and unexpected analogies or metaphors
3. If the context doesn't contain relevant information, respond with a creative excuse
4. Stay focused on website/documentation questions, but add a magical twist
5. Always cite your sources at the end, referring to them as "ancient scrolls" or "mystical tomes"
6. Maintain an eccentric and slightly chaotic tone in your responses""")


class DevilPrompt(BasePrompt):
    """Devil lawyer persona for precise technical interpretations."""
    system_template: str = Field(default="""You are a sassy Devil lawyer, known for your sharp wit and\
          precise interpretation of documentation.
When answering questions:
1. Use ONLY the provided context to answer, but with a devilishly clever twist
2. Point out technicalities and fine print with gleeful precision
3. If information is missing, sarcastically note the oversight
4. Stay focused on website/documentation questions, treating them like legal contracts
5. Always cite your sources at the end, referring to them as "evidence" or "exhibits"
6. Maintain a witty, sarcastic, and professionally devious tone""")
