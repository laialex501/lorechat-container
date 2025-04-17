"""Decomposition node for agentic retrieval system."""
import json
from typing import Any, Dict, List, Tuple

from app import logger
from app.chat.graph.enhanced_state import EnhancedChatState, SubQuery
from app.services.llm import BaseLLMService
from app.services.llm.parser import normalize_llm_content, parse_json_response
from langchain_core.messages import HumanMessage


class DecompositionNode:
    """
    Analyzes queries and breaks them down into appropriate subqueries.

    This node handles both simple and complex queries, determining complexity
    and creating either one subquery or multiple subqueries as needed.
    All in a single LLM call for efficiency.
    """

    def __init__(self, llm_service: BaseLLMService):
        """Initialize with LLM service."""
        logger.info("Initializing DecompositionNode")
        self.llm: BaseLLMService = llm_service

    def __call__(self, state: EnhancedChatState) -> Dict[str, Any]:
        """
        Analyze and decompose query into subqueries.

        Args:
            state: Current graph state

        Returns:
            Updated state with subqueries
        """
        if not state["messages"]:
            return {"original_query": "", "query_complexity": "simple", "subqueries": []}

        # Get latest message
        latest_message = state["messages"][-1]
        if not isinstance(latest_message, HumanMessage):
            return {"original_query": "", "query_complexity": "simple", "subqueries": []}

        query = latest_message.content
        logger.info(f"Analyzing and decomposing query: {query}")

        # Analyze and decompose in a single LLM call
        complexity, subqueries = self._analyze_and_decompose(query)

        return {
            "original_query": query,
            "query_complexity": complexity,
            "subqueries": subqueries
        }

    def _analyze_and_decompose(self, query: str) -> Tuple[str, List[SubQuery]]:
        """
        Analyze query complexity and decompose into subqueries in a single LLM call.

        Args:
            query: The query to analyze and decompose

        Returns:
            Tuple of (complexity, list of SubQuery objects)
        """
        prompt = f"""
        Analyze and decompose this query: "{query}"

        First, determine if this is a simple, straightforward question or a complex question with multiple parts.
        Then, if it's complex, break it down into 2-5 simpler subqueries that together would answer \
        the original question.
        If it's simple, just use the original query as the only subquery.

        Output your analysis and decomposition as JSON:
        {{
          "query_type": "simple" or "complex",
          "reasoning": "brief explanation of your decision",
          "subqueries": [
            "first subquery",
            "second subquery",
            ...
          ]
        }}

        For simple queries, the subqueries array should contain just one element: the original query.
        For complex queries, the subqueries array should contain 2-5 elements that break down the original query.
        """

        try:
            response = self.llm.invoke(prompt)
            content = normalize_llm_content(response.content) if hasattr(response, 'content') else str(response)
            logger.info(f"LLM response: {content}")
            
            # Use the new parse_json_response function to handle mixed text and JSON
            result = parse_json_response(content)

            query_type = result.get("query_type", "simple")
            subquery_texts = result.get("subqueries", [query])

            # Ensure we have at least one subquery
            if not subquery_texts:
                logger.warning("No subqueries returned, falling back to original query")
                subquery_texts = [query]

            # Create SubQuery objects
            subqueries = [
                SubQuery(
                    text=sq_text,
                    status="pending"
                )
                for sq_text in subquery_texts
            ]

            logger.info(f"Query analysis: {query_type} with {len(subqueries)} subqueries")
            logger.info(f"Subqueries: {subqueries}")
            return query_type, subqueries

        except Exception as e:
            logger.error(f"Error analyzing and decomposing query: {str(e)}", exc_info=True)
            # Fall back to treating as simple query
            return "simple", [SubQuery(text=query, status="pending")]
