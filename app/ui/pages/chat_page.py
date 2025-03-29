"""Main chat interface page for LoreChat."""
import uuid

import streamlit as st
from app import logger
from app.chat.service import ChatMessage, ChatService
from app.services.llm import ClaudeModel, LLMFactory, LLMProvider, OpenAIModel
from app.services.prompts import PersonaType, PromptFactory
from app.services.vectorstore import VectorStoreFactory
from app.ui.components.theme import FANTASY_THEME, get_thinking_html


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
    if "persona" not in st.session_state:
        st.session_state.persona = PersonaType.SCRIBE
    if "chat_service" not in st.session_state:
        st.session_state.chat_service = None


def create_chat_service():
    """Create or update chat service with current settings."""
    st.session_state.chat_service = ChatService(
        llm_service=LLMFactory.create_llm_service(
            provider=st.session_state.provider,
            model_name=st.session_state.model_name
        ),
        vector_store=VectorStoreFactory.get_vector_store(),
        persona_type=st.session_state.persona
    )


def on_persona_change():
    """Handle persona change."""
    st.session_state.messages = []  # Clear messages
    create_chat_service()  # Recreate chat service with new persona


def on_provider_change():
    """Handle provider change."""
    # Update model to first available for new provider
    st.session_state.model_name = next(iter(get_available_models()))
    create_chat_service()  # Recreate chat service with new provider


def on_model_change():
    """Handle model change."""
    create_chat_service()  # Recreate chat service with new model


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

    # Apply fantasy theme with debug logging
    logger.info("Applying fantasy theme...")
    st.markdown("""
        <style>
            /* Debug marker to verify theme injection */
            #debug-theme-marker { display: none; }
        </style>
    """, unsafe_allow_html=True)
    st.markdown(FANTASY_THEME, unsafe_allow_html=True)
    logger.info("Fantasy theme applied")
    
    initialize_session_state()
    
    # Get current persona configuration
    persona = PromptFactory.create_prompt(st.session_state.persona)
    ui_config = persona.get_ui_config()
    
    st.title(f"Welcome to LoreChat {ui_config['icon']}")
    
    # Persona selection in sidebar
    with st.sidebar:
        st.selectbox(
            "Choose Your Guide",
            options=[PersonaType.SCRIBE, PersonaType.DEVIL],
            format_func=lambda x: PromptFactory.create_prompt(x).get_ui_config()["name"],
            key="persona",
            on_change=on_persona_change
        )
    
    # Show welcome message if no messages exist
    if not st.session_state.messages:
        with st.chat_message("assistant", avatar=ui_config["icon"]):
            st.markdown(ui_config["greeting"])

    # Model selection in sidebar
    with st.sidebar:
        st.selectbox(
            "Provider",
            options=LLMProvider,
            format_func=lambda x: x.title(),
            key="provider",
            on_change=on_provider_change
        )
        
        models = get_available_models()
        st.selectbox(
            "Model",
            options=list(models.keys()),
            format_func=lambda x: models[x],
            key="model_name",
            on_change=on_model_change
        )

    # Chat messages
    for message in st.session_state.messages:
        avatar = ui_config["icon"] if message.role == "assistant" else None
        with st.chat_message(message.role, avatar=avatar):
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
            # Create chat service if not exists
            if not st.session_state.chat_service:
                create_chat_service()

            logger.info(
                f"Processing message with {st.session_state.provider} - "
                f"{st.session_state.model_name}"
            )
            
            # Show thinking animation
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown(
                get_thinking_html(ui_config["thinking_text"]),
                unsafe_allow_html=True
            )
            
            # Process message and stream response
            with st.chat_message("assistant", avatar=ui_config["icon"]):
                response = st.write_stream(
                    st.session_state.chat_service.process_message(
                        prompt,
                        st.session_state.messages,
                        thread_id=st.session_state.thread_id
                    )
                )
                st.session_state.messages.append(
                    ChatMessage(role="assistant", content=response)
                )
            
            # Clear thinking animation
            thinking_placeholder.empty()

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            st.error(f"Error: {str(e)}")

    # Instructions
    with st.sidebar:
        with st.expander("How to use LoreChat"):
            st.markdown("""
            1. Choose your preferred guide:
               - Wizard Scribe: Mystical and whimsical
               - Devil's Advocate: Sharp and precise
            2. Select your preferred AI model
            3. Ask questions about the website
            4. Get persona-flavored answers with context
            """)


if __name__ == "__main__":
    render_chat_page()
