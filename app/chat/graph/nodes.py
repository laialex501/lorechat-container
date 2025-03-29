"""Node implementations for chat graph."""
from typing import Any, Dict

from app.chat.graph.state import ChatState
from app.services.llm import BaseLLMService
from app.services.prompts import PersonaType, PromptFactory
from app.services.vectorstore import BaseVectorStoreService
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_nodes(
    llm_service: BaseLLMService,
    vector_store: BaseVectorStoreService,
    persona_type: PersonaType = PersonaType.SCRIBE
) -> Dict[str, Any]:
    """
    Create graph nodes for chat workflow.

    Args:
        llm_service: LLM service for response generation
        vector_store: Vector store for document retrieval
        persona_type: Type of chat persona to use

    Returns:
        Dictionary of node functions
    """
    # Initialize prompt
    prompt = PromptFactory.create_prompt(persona_type)

    def retrieve_context(state: ChatState) -> Dict[str, Any]:
        """Retrieve relevant documents based on latest message."""
        if not state["messages"]:
            return {"retrieved_docs": []}

        # Get latest message
        latest_message = state["messages"][-1]
        if not isinstance(latest_message, HumanMessage):
            return {"retrieved_docs": []}
     
        # Search vector store
        docs = vector_store.as_retriever().get_relevant_documents(
            latest_message.content
        )
        return {"retrieved_docs": docs}

    def generate_response(state: ChatState) -> Dict[str, Any]:
        """Generate response using context and history."""
        # Create prompt with persona and context
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", prompt.system_template),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "Context: {context}\nQuestion: {input}")
        ])

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

        # Get latest message
        latest_message = state["messages"][-1]

        # Generate response with streaming
        messages = qa_prompt.format_messages(
            chat_history=state["messages"][:-1],
            context=f"{context}{sources_text}",
            input=latest_message.content
        )

        # Use invoke to get response
        response = llm_service.invoke(messages)

        # Handle potential streaming response
        if hasattr(response, "content"):
            # Regular response with sources
            content = response.content
            if sources:
                content = f"{content}\n\nSources: {', '.join(sources)}"
            return {"messages": [AIMessage(content=content)]}
        else:
            # Streaming response with sources
            content = str(response)
            if sources:
                content = f"{content}\n\nSources: {', '.join(sources)}"
            return {"messages": [AIMessage(content=content)]}
        
    return {
        "retrieve": retrieve_context,
        "respond": generate_response
    }
