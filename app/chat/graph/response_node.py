"""Response node for agentic retrieval system."""
from typing import Any, Dict

from app import logger
from app.chat.graph.enhanced_state import EnhancedChatState
from app.services.llm import BaseLLMService
from app.services.llm.parser import normalize_llm_content
from app.services.prompts import BasePrompt
from langchain_core.messages import AIMessage


class ResponseNode:
    """
    Formats the final response using LLM and user prompt.

    This node uses the user's prompt template and the LLM to generate
    a properly formatted response with appropriate attribution.
    """

    def __init__(self, llm_service: BaseLLMService, prompt_template: BasePrompt):
        """
        Initialize with LLM service and prompt template.

        Args:
            llm_service: LLM service for response generation
            prompt_template: Prompt template for formatting
        """
        logger.info("Initializing ResponseNode")
        self.llm_service = llm_service
        self.prompt_template = prompt_template

    async def __call__(self, state: EnhancedChatState) -> Dict[str, Any]:
        """
        Generate response using LLM and prompt template.

        Args:
            state: Current graph state

        Returns:
            Updated state with response message
        """
        original_query = state.get("original_query", "")
        subqueries = state.get("subqueries", [])
        combined_answer = state.get("combined_answer", "")

        if not combined_answer:
            logger.warning("No combined answer available")
            combined_answer = "I don't have enough information to answer that question."

        # Format context with subquery information
        context_parts = []

        # For simple queries (just one subquery)
        if len(subqueries) == 1:
            sq = subqueries[0]
            context = "Answer: {}".format(sq.result)
            if sq.sources:
                context += "\nSources: {}".format(", ".join(sq.sources))
            context_parts.append(context)
        else:
            # For complex queries, include the combined answer and subquery details
            context_parts.append("Combined Answer: {}".format(combined_answer))

            # Then add details for each subquery
            for i, sq in enumerate(subqueries, 1):
                part = "Subquery {}: {}\nAnswer: {}".format(i, sq.text, sq.result)
                if sq.sources:
                    part += "\nSources: {}".format(", ".join(sq.sources))
                context_parts.append(part)

        # Join all context parts
        full_context = "\n\n".join(context_parts)

        # Use prompt template to format messages for LLM
        formatted_messages = self.prompt_template.format_messages(
            chat_history=state["messages"][:-1],  # Exclude the latest user message
            context=full_context,
            input=original_query
        )

        # Generate response using LLM with streaming
        try:
            logger.info("Generating streaming response")
            
            # TODO: Fix streaming implementation in ResponseNode
            # Current implementation accumulates all chunks and only returns the complete response
            # at the end, which prevents true streaming to the user interface.
            #
            # To fix this, we need to modify the ResponseNode to yield intermediate state updates
            # after each chunk is received. This would require:
            #
            # 1. Modifying the StateGraph node to support yielding intermediate state updates
            # 2. For each chunk received, yield a partial message update
            # 3. Ensure the workflow and chat service can handle these partial updates
            #
            # Example implementation:
            # async for chunk in self.llm_service.astream(formatted_messages):
            #     if hasattr(chunk, 'content'):
            #         content = normalize_llm_content(chunk.content)
            #     else:
            #         content = str(chunk)
            #     
            #     # Create a partial message and yield it
            #     partial_messages = state["messages"].copy()
            #     partial_messages.append(AIMessage(content=content))
            #     yield {"messages": partial_messages}
            #
            # Note: This would require changes to how LangGraph StateGraph nodes work with streaming.
            
            # Current implementation: Use streaming to get response but accumulate all chunks
            response_content = ""
            async for chunk in self.llm_service.astream(formatted_messages):
                # Accumulate chunks for the final message
                if hasattr(chunk, 'content'):
                    response_content += normalize_llm_content(chunk.content)
                else:
                    response_content += str(chunk)
            
            # Log the final accumulated response content
            logger.info(f"Final response content: {response_content}")
            
            # Add response to messages
            messages = state["messages"].copy()
            messages.append(AIMessage(content=response_content))
            
            logger.info("Generated final response")
            return {"messages": messages}
        except Exception as e:
            logger.error("Error generating response: {}".format(str(e)), exc_info=True)

            # Fall back to combined answer
            messages = state["messages"].copy()
            messages.append(AIMessage(content=combined_answer))

            return {"messages": messages}
