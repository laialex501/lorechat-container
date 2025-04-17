"""Processing node for agentic retrieval system."""
import asyncio
import json
from typing import Any, Dict, List

from app import logger
from app.chat.graph.enhanced_state import EnhancedChatState, SubQuery
from app.services.llm import BaseLLMService
from app.services.llm.parser import normalize_llm_content
from app.services.vectorstore import BaseVectorStoreService
from langchain.schema import Document


class ProcessingNode:
    """
    Processes all subqueries in parallel.

    This node handles the retrieval, evaluation, and refinement steps
    for each subquery concurrently using asyncio for better concurrency
    management and thread safety.
    """

    def __init__(
        self, 
        vector_store: BaseVectorStoreService, 
        retrieval_llm_service: BaseLLMService,
        evaluation_llm_service: BaseLLMService = None,
        refinement_llm_service: BaseLLMService = None,
        answer_llm_service: BaseLLMService = None
    ):
        """
        Initialize with vector store and LLM services.

        Args:
            vector_store: Vector store for document retrieval
            retrieval_llm_service: Primary LLM service
            evaluation_llm_service: LLM service for evaluation (optional)
            refinement_llm_service: LLM service for query refinement (optional)
            answer_llm_service: LLM service for answer generation (optional)
        """
        logger.info("Initializing ProcessingNode")
        self.vector_store = vector_store
        self.retrieval_llm = retrieval_llm_service

        # Use provided LLMs or fall back to the primary LLM
        self.evaluation_llm = evaluation_llm_service or retrieval_llm_service
        self.refinement_llm = refinement_llm_service or retrieval_llm_service
        self.answer_llm = answer_llm_service or retrieval_llm_service

    async def __call__(self, state: EnhancedChatState) -> Dict[str, Any]:
        """
        Process all subqueries in parallel using asyncio.

        Args:
            state: Current graph state

        Returns:
            Updated state with processed subqueries
        """
        subqueries = state.get("subqueries", [])
        if not subqueries:
            logger.warning("No subqueries to process")
            return {"subqueries": []}
 
        logger.info(f"Processing {len(subqueries)} subqueries in parallel")

        # Process all subqueries in parallel using asyncio
        tasks = [self._process_subquery(sq) for sq in subqueries]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        # Update subqueries with results
        updated_subqueries = []
        for sq, result in zip(subqueries, results_list):
            if isinstance(result, Exception):
                # Handle exceptions
                logger.error(f"Error processing subquery: {str(result)}", exc_info=True)
                sq.status = "failed"
                sq.result = f"Error: {str(result)}"
            else:
                # Update with successful result
                sq.status = "complete"
                sq.retrieved_docs = result.get("retrieved_docs", [])
                sq.refinement_count = result.get("refinement_count", 0)
                sq.result = result.get("answer", "No answer found")
                sq.sources = result.get("sources", [])

            updated_subqueries.append(sq)

        return {"subqueries": updated_subqueries}

    async def _process_subquery(self, subquery: SubQuery) -> Dict[str, Any]:
        """
        Process a single subquery through retrieval, evaluation, and refinement.

        Args:
            subquery: The subquery to process

        Returns:
            Dictionary with processing results
        """
        logger.info(f"Processing subquery: {subquery.text}")

        try:
            # Initial retrieval
            docs = await self._retrieve_documents(subquery.text)

            # Evaluate if documents are sufficient
            evaluation = await self._evaluate_results(subquery.text, docs)

            # Refine if needed (only once to avoid loops)
            refinement_count = 0
            if not evaluation["sufficient"] and refinement_count < 1:
                # Refine query
                refined_query = await self._refine_query(subquery.text, docs)
                refinement_count += 1

                # Retry with refined query
                docs = await self._retrieve_documents(refined_query)

            # Generate answer
            answer = await self._generate_answer(subquery.text, docs)

            # Extract sources
            sources = []
            for doc in docs:
                if doc.metadata and doc.metadata.get("source"):
                    sources.append(doc.metadata["source"])
                elif doc.metadata and doc.metadata.get("url"):
                    sources.append(doc.metadata["url"])

            result = {
                "retrieved_docs": docs,
                "refinement_count": refinement_count,
                "answer": answer,
                "sources": list(set(sources))  # Remove duplicates
            }

            return result

        except Exception as e:
            logger.error(f"Error processing subquery: {str(e)}", exc_info=True)
            raise
    
    async def _retrieve_documents(self, query: str) -> List[Document]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: The query to search for
            
        Returns:
            List of retrieved documents
        """
        logger.info(f"Retrieving documents for: {query}")
        try:
            # Use the vector store's retriever
            docs = self.vector_store.as_retriever().invoke(query)
            logger.info(f"Retrieved {len(docs)} documents")
            return docs
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}", exc_info=True)
            return []
    
    async def _evaluate_results(self, query: str, docs: List[Document]) -> Dict[str, Any]:
        """
        Evaluate if retrieved documents are sufficient to answer the query.
        
        Args:
            query: The original query
            docs: Retrieved documents
            
        Returns:
            Evaluation result with sufficient flag and reasoning
        """
        if not docs:
            logger.info("No documents retrieved, marking as insufficient")
            return {"sufficient": False, "reasoning": "No documents retrieved"}
        
        # Format context from retrieved docs
        context = "\n\n".join(
            f"Document {i+1}:\n{doc.page_content}" 
            for i, doc in enumerate(docs)
        )
        
        # Create prompt for evaluation
        prompt = f"""
        Evaluate if the following documents contain sufficient information to answer the query.
        
        Query: {query}
        
        Documents:
        {context}
        
        Output your evaluation as JSON:
        {{
          "sufficient": true or false,
          "reasoning": "explanation of your decision",
          "missing_information": "description of what information is missing (if insufficient)"
        }}
        
        IMPORTANT: Provide ONLY the JSON object, with no additional text before or after.
        """
        
        try:
            # Use the evaluation LLM
            response = self.evaluation_llm.invoke(prompt)
            response_text = normalize_llm_content(response.content) if hasattr(response, 'content') \
                else str(response)
            
            # Extract JSON using regex to handle potential extra text
            import re
            json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                result = json.loads(json_str)
            else:
                # Fallback if regex fails
                result = json.loads(response_text)
            
            sufficient = result.get("sufficient", False)
            reasoning = result.get("reasoning", "")
            
            logger.info(f"Document evaluation: sufficient={sufficient}, reasoning={reasoning}")
            
            return {
                "sufficient": sufficient,
                "reasoning": reasoning,
                "missing_information": result.get("missing_information", "")
            }
        except Exception as e:
            logger.error(f"Error evaluating results: {str(e)}", exc_info=True)
            # Default to insufficient if evaluation fails
            return {"sufficient": False, "reasoning": f"Evaluation error: {str(e)}"}

    async def _refine_query(self, query: str, docs: List[Document]) -> str:
        """
        Refine query based on retrieved documents.

        Args:
            query: The original query
            docs: Retrieved documents that were insufficient

        Returns:
            Refined query
        """
        logger.info(f"Refining query: {query}")

        # Format context from retrieved docs
        context = "\n\n".join(
            f"Document {i+1}:\n{doc.page_content}" 
            for i, doc in enumerate(docs)
        )

        # Create prompt for query refinement
        prompt = f"""
        The following query needs to be refined because the retrieved documents don't contain sufficient \
        information to answer it.

        Original query: "{query}"

        Retrieved documents:
        {context}

        Please create a refined version of the query that might retrieve more relevant information.
        Focus on clarifying ambiguities, adding specific keywords, or reformulating the question.

        Output only the refined query text, without any explanations or additional formatting.
        """

        try:
            # Use the refinement LLM
            response = self.refinement_llm.invoke(prompt)
            refined_query = normalize_llm_content(response.content) if hasattr(response, 'content') else str(response)

            # Clean up the response
            refined_query = refined_query.strip().strip('"')

            logger.info(f"Refined query: {refined_query}")
            return refined_query
        except Exception as e:
            logger.error(f"Error refining query: {str(e)}", exc_info=True)
            # Fall back to original query with a marker
            return f"{query} (refinement failed)"

    async def _generate_answer(self, query: str, docs: List[Document]) -> str:
        """
        Generate answer for a query using retrieved documents.

        Args:
            query: The query to answer
            docs: Retrieved documents to use as context

        Returns:
            Generated answer
        """
        logger.info(f"Generating answer for: {query}")

        if not docs:
            return "I couldn't find any relevant information to answer your question."

        # Format context from retrieved docs
        context = "\n\n".join(
            f"Document {i+1}:\n{doc.page_content}" 
            for i, doc in enumerate(docs)
        )

        # Create prompt for answer generation
        prompt = f"""
        Answer the following question using only the provided context. If the context doesn't contain
        relevant information to answer the question, say "I don't have enough information to answer this question."

        Question: {query}

        Context:
        {context}

        Provide a comprehensive, accurate answer based solely on the information in the context.
        Do not include information that isn't supported by the context.
        If different documents contain conflicting information, acknowledge this in your answer.

        Answer:
        """

        # Generate answer
        try:
            # Use the answer LLM
            response = self.answer_llm.invoke(prompt)
            answer = normalize_llm_content(response.content) if hasattr(response, 'content') else str(response)
            return answer.strip()
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}", exc_info=True)
            return "An error occurred while generating the answer."
