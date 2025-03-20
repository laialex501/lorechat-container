"""Main chat interface page for SiteChat."""
import streamlit as st
from app.chat.service import ChatMessage, ChatService
from app.services.llm import (ClaudeModel, LLMProvider, OpenAIModel,
                              get_llm_service)
from app.services.vectorstore import get_vector_store


def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "provider" not in st.session_state:
        st.session_state.provider = LLMProvider.Anthropic
    if "model_name" not in st.session_state:
        st.session_state.model_name = ClaudeModel.CLAUDE3_HAIKU


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
    st.set_page_config(
        page_title="SiteChat",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("Welcome to SiteChat 💬")
    initialize_session_state()

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
                llm_service=get_llm_service(
                    st.session_state.provider,
                    st.session_state.model_name
                ),
                vector_store=get_vector_store()
            )

            # Process message and stream response
            with st.chat_message("assistant"):
                response = st.write_stream(
                    chat_service.process_message(
                        prompt,
                        st.session_state.messages
                    )
                )
                st.session_state.messages.append(
                    ChatMessage(role="assistant", content=response)
                )

        except Exception as e:
            st.error(f"Error: {str(e)}")

    # Instructions
    with st.expander("How to use SiteChat"):
        st.markdown("""
        1. Select your preferred AI model:
           - Bedrock: Claude 3 Sonnet or Haiku
           - OpenAI: GPT-3.5 Turbo variants
        2. Ask a question about the website
        3. Get AI-powered answers with relevant context
        """)


if __name__ == "__main__":
    render_chat_page()
