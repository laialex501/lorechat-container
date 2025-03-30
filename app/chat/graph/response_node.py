"""Node implementations for chat graph."""
from typing import Any, Dict

from app.chat.graph.state import ChatState
from app.services.llm import BaseLLMService
from app.services.prompts import BasePrompt
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class ResponseNode:
    """A node that generates a response using a language model."""
    def __init__(self, llm_service: BaseLLMService, prompt: BasePrompt):
        self.llm_service = llm_service
        self.prompt = prompt

    def __call__(self, state: ChatState) -> Dict[str, Any]:
        """Generate response using context and history."""
        # Create prompt with persona and context
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", self.prompt.system_template),
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
        response = self.llm_service.invoke(messages)

        # Handle potential streaming response
        if hasattr(response, "content"):
            # Regular response with sources
            content = response.content
            #  if sources:
            #    content = f"{content}\n\nSources: {', '.join(sources)}"
            return {"messages": [AIMessage(content=content)]}
        else:
            # Streaming response
            return {"messages": [response]}
