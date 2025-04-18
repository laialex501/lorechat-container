"""Combination node for agentic retrieval system."""
from typing import Any, Dict

from app import logger
from app.chat.graph.enhanced_state import EnhancedChatState
from app.services.llm import BaseLLMService
from app.services.llm.parser import normalize_llm_content


class CombinationNode:
    """
    Combines results from multiple subqueries.

    For simple queries (one subquery), this node passes through the result.
    For complex queries, it combines the results into a coherent answer.
    """

    def __init__(self, llm_service: BaseLLMService):
        """Initialize with LLM service."""
        logger.info("Initializing CombinationNode")
        self.llm = llm_service

    def __call__(self, state: EnhancedChatState) -> Dict[str, Any]:
        """
        Combine subquery results if needed.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with combined answer
        """
        original_query = state.get("original_query", "")
        subqueries = state.get("subqueries", [])
        
        if not subqueries:
            logger.warning("No subqueries to combine")
            return {"combined_answer": "I don't have enough information to answer your question."}
        
        # For simple queries (just one subquery), no combination needed
        if len(subqueries) == 1:
            logger.info("Single subquery, passing through result")
            # Check if the subquery failed
            if not subqueries[0].result:
                return {"combined_answer": "I couldn't find the information to answer your question."}
            return {"combined_answer": subqueries[0].result}
        
        # For complex queries, combine results
        logger.info("Combining results from {} subqueries".format(len(subqueries)))
        
        # Format subquery results for the prompt
        subquery_results = []
        for i, sq in enumerate(subqueries, 1):
            subquery_results.append(f"Subquery {i}: {sq.text}\nAnswer: {sq.result}")
        
        # Combine results
        subquery_text = "\n\n".join(subquery_results)
        prompt = f"""
        Combine the following subquery results into a coherent answer to the original question.
        
        ORIGINAL QUESTION: "{original_query}"
        
        SUBQUERY RESULTS:
        {subquery_text}
        
        Provide a comprehensive answer that addresses all aspects of the original question.
        Ensure the answer is well-structured, coherent, and flows naturally.
        If there are contradictions between subquery results, acknowledge them in your answer.
        If some subqueries failed to provide useful information, focus on the successful ones.
        
        Your combined answer:
        """
        
        try:
            combined_answer = self.llm.invoke(prompt)
            result = normalize_llm_content(combined_answer.content) if hasattr(combined_answer, 'content') \
                else str(combined_answer)
            logger.info("Successfully combined subquery results")
            return {"combined_answer": result.strip()}
        except Exception as e:
            logger.error(f"Error combining results: {str(e)}", exc_info=True)
            # Fall back to concatenating results
            fallback = "I found multiple pieces of information:\n\n" + "\n\n".join(subquery_results)
            return {"combined_answer": fallback}
