"""Main chat interface page for LoreChat."""
import uuid

import streamlit as st
from app import logger
from app.chat.service import ChatMessage, ChatService
from app.services.llm import ClaudeModel, LLMFactory, LLMProvider, OpenAIModel
from app.services.vectorstore import VectorStoreFactory


def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "provider" not in st.session_state:
        st.session_state.provider = LLMProvider.Anthropic
    if "model_name" not in st.session_state:
        st.session_state.model_name = ClaudeModel.CLAUDE3_HAIKU
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())


def get_available_models():
    """Get available models based on selected provider."""
    if st.session_state.provider == LLMProvider.Anthropic:
        return {m: m.name.replace('_', ' ').title() for m in ClaudeModel}
    elif st.session_state.provider == LLMProvider.OPENAI:
        return {m: m.name.replace('_', ' ').title() for m in OpenAIModel}
    else:
        return {}


def render_chat_page():
    """Render the main chat interface."""
    logger.info("Rendering chat page")
    st.set_page_config(
        page_title="LoreChat",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("Welcome to LoreChat 💬")
    initialize_session_state()
    
    # Show welcome message if no messages exist
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown(
                "Greetings, seeker of knowledge! I am a humble wizard scribe in service "
                "to Nethys, the All-Seeing Eye, god of magic and knowledge. Within these "
                "halls of wisdom, I tend to the sacred scrolls and tomes, preserving and "
                "sharing their insights with those who seek understanding. How may I "
                "illuminate your path today?"
            )

    # Model selection
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox(
            "Provider",
            options=LLMProvider,
            format_func=lambda x: x.title(),
            key="provider",
            on_change=lambda: setattr(
                st.session_state,
                "model_name",
                next(iter(get_available_models()))
            )
        )
    
    with col2:
        models = get_available_models()
        st.selectbox(
            "Model",
            options=list(models.keys()),
            format_func=lambda x: models[x],
            key="model_name"
        )

    # Chat messages
    for message in st.session_state.messages:
        with st.chat_message(message.role):
            st.markdown(message.content)

    # Chat input
    if prompt := st.chat_input("Ask a question about the website"):
        # Add user message
        st.session_state.messages.append(
            ChatMessage(role="user", content=prompt)
        )
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            # Setup services
            chat_service = ChatService(
                llm_service=LLMFactory.create_llm_service(
                    provider=st.session_state.provider,
                    model_name=st.session_state.model_name
                ),
                vector_store=VectorStoreFactory.get_vector_store()
            )

            logger.info(
                f"Processing message with {st.session_state.provider} - "
                f"{st.session_state.model_name}"
            )
            # Process message and stream response
            with st.chat_message("assistant"):
                response = st.write_stream(
                    chat_service.process_message(
                        prompt,
                        st.session_state.messages,
                        thread_id=st.session_state.thread_id
                    )
                )
                st.session_state.messages.append(
                    ChatMessage(role="assistant", content=response)
                )

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            st.error(f"Error: {str(e)}")

    # Instructions
    with st.expander("How to use LoreChat"):
        st.markdown("""
        1. Select your preferred AI model:
           - Bedrock: Claude 3 Sonnet or Haiku
           - OpenAI: GPT-3.5 Turbo variants
        2. Ask a question about the website
        3. Get AI-powered answers with relevant context
        """)


if __name__ == "__main__":
    render_chat_page()
