"""Node implementations for chat graph."""
import time
from typing import Any, Dict, List, Union

from app import logger
from app.chat.graph.state import ChatState
from app.services.llm import BaseLLMService
from app.services.prompts import BasePrompt
from langchain_core.messages import AIMessage


class ResponseNode:
    """A node that generates a response using a language model."""
    def __init__(self, llm_service: BaseLLMService, prompt: BasePrompt):
        logger.info("Initializing ResponseNode")
        self.llm_service = llm_service
        self.prompt = prompt

    def __call__(self, state: ChatState) -> Dict[str, Any]:
        """Generate response using context and history."""
        # Create prompt with persona and context
        qa_prompt = self.prompt.prompt_template

        # Get retrieved docs
        retrieved_docs = state.get("retrieved_docs", [])

        # Format context from retrieved docs
        context = "\n\n".join(doc.page_content for doc in retrieved_docs)

        # Extract and format sources
        sources = []
        for doc in retrieved_docs:
            if doc.metadata and doc.metadata.get('url'):
                sources.append(doc.metadata['url'])
        sources = list(set(sources))  # Remove duplicates
        sources_text = f"\n\nSources: {', '.join(sources)}" if sources else ""
        logger.info(f"Sources found: {len(sources)}")

        # Get latest message
        latest_message = state["messages"][-1]

        # Generate response with streaming
        messages = qa_prompt.format_messages(
            chat_history=state["messages"][:-1],
            context=f"{context}{sources_text}",
            input=latest_message.content
        )

        # Use invoke to get response
        start_time = time.time()
        response = self.llm_service.invoke(messages)
        logger.info(f"Generated response in {time.time() - start_time} seconds")

        return {"messages": [AIMessage(content=self.normalize_content(response.content))]}

    def normalize_content(self, response_content: Union[str, List[Dict[str, Any]], Any]) -> str:
        """Normalize different response content formats into a string.
        
        Args:
            response_content: Content from LLM response, could be:
                - string: direct text response
                - list of dicts: structured format with type/text fields
                - other: fallback to string conversion
                
        Returns:
            Normalized string content
        """
        if isinstance(response_content, str):
            return response_content
        elif isinstance(response_content, list) and response_content:
            # Handle structured format
            text_chunks = []
            for chunk in response_content:
                if isinstance(chunk, dict) and 'text' in chunk:
                    text_chunks.append(chunk['text'])
            if text_chunks:
                return ''.join(text_chunks)
        # Fallback for any other format
        return str(response_content)
