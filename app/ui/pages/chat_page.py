"""Main chat interface page for SiteChat."""
import asyncio

import streamlit as st
from app.chat.service import ChatMessage, ChatService
from app.services.llm import get_llm_service
from app.services.vectorstore import get_vector_store

# Custom CSS for styling
custom_css = """
<style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    .chat-container {
        height: 75vh;
        overflow-y: auto;
        padding: 1rem;
        background-color: #f9f9f9;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #007bff;
        align-items: flex-end;
        color: white;
    }
    .assistant-message {
        background-color: #f0f0f0;
        align-items: flex-start;
        color: #000000;
    }
    .message-content {
        max-width: 80%;
        white-space: pre-wrap;
    }
    .avatar {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .stButton > button {
        height: 2.75rem;
        margin-top: 0px;
        width: 100%;
    }
    .stTextInput div {
        height: 2.75rem;
    }
    .stream-content {
        opacity: 0.7;
    }
</style>
"""


def get_chat_service() -> ChatService:
    """Get initialized chat service instance."""
    if "chat_service" not in st.session_state:
        st.session_state.chat_service = ChatService(
            llm_service=get_llm_service(),
            vector_store=get_vector_store()
        )
    return st.session_state.chat_service


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""
    if 'thinking' not in st.session_state:
        st.session_state.thinking = False
    if 'current_response' not in st.session_state:
        st.session_state.current_response = ""


def display_message(
    message: ChatMessage,
    is_streaming: bool = False
):
    """Display a single chat message."""
    is_user = message.role == "user"
    message_class = "user-message" if is_user else "assistant-message"
    if is_streaming:
        message_class += " stream-content"
    avatar = "👤" if is_user else "🤖"

    message_html = f"""
    <div class="chat-message {message_class}">
        <div class="avatar">{avatar}</div>
        <div class="message-content">{message.content}</div>
    </div>
    """
    st.markdown(message_html, unsafe_allow_html=True)


def display_chat_messages():
    """Display all messages in the chat history."""
    # Display all completed messages
    for message in st.session_state.messages:
        display_message(message)
    
    # Display current streaming response if any
    if st.session_state.current_response:
        display_message(
            ChatMessage(
                role="assistant",
                content=st.session_state.current_response
            ),
            is_streaming=True
        )


async def handle_user_input_async():
    """Async handler for user input."""
    if st.session_state.user_input and st.session_state.user_input.strip():
        user_input = st.session_state.user_input
        st.session_state.user_input = ""  # Clear input immediately
        
        try:
            # Add user message immediately
            st.session_state.messages.append(
                ChatMessage(role="user", content=user_input)
            )
            
            # Set thinking state and clear current response
            st.session_state.thinking = True
            st.session_state.current_response = ""
            
            # Get chat service and process message
            chat_service = get_chat_service()
            generator = await chat_service.process_message(
                message=user_input,
                history=st.session_state.messages[:-1],  # Exclude last message
                stream=True
            )
            
            # Process streaming response
            full_response = []
            async for chunk in generator:
                full_response.append(chunk)
                st.session_state.current_response = "".join(full_response)
                st.rerun()
            
            # Add completed response to messages
            final_response = "".join(full_response)
            st.session_state.messages.append(
                ChatMessage(role="assistant", content=final_response)
            )
            st.session_state.current_response = ""
            
        except Exception as e:
            import logging
            logging.error(
                "Error processing message: %s",
                str(e),
                exc_info=True
            )
            error_message = (
                "I apologize, but I encountered an error processing your "
                "message. Please try again or contact support if the "
                "issue persists."
            )
            st.session_state.messages.append(
                ChatMessage(role="assistant", content=error_message)
            )
        
        finally:
            # Always clear thinking state
            st.session_state.thinking = False


def handle_user_input():
    """Synchronous wrapper for async handler."""
    asyncio.run(handle_user_input_async())


def render_chat_page():
    """Render the main chat interface."""
    st.set_page_config(page_title="SiteChat", page_icon="💬", layout="wide")
    st.markdown(custom_css, unsafe_allow_html=True)

    st.title("Welcome to SiteChat 💬")
    st.markdown("Ask me anything about our website!")

    initialize_session_state()

    # Chat message display area
    chat_container = st.container()
    with chat_container:
        display_chat_messages()

    # User input area
    st.markdown("---")
    col1, col2 = st.columns([6, 1])
    with col1:
        st.text_input(
            "Type your message here",
            key="user_input",
            placeholder="Ask a question about the website...",
            label_visibility="collapsed",  # This hides the label
            on_change=handle_user_input,  # This triggers on Enter key
        )
    with col2:
        st.button(
            "Send",
            on_click=handle_user_input,
            use_container_width=True
        )

    # Auto-scroll to bottom of chat
    if st.session_state.messages:
        js = """
        <script>
            function scroll() {
                var container = document.querySelector('.chat-container');
                container.scrollTop = container.scrollHeight;
            }
            scroll();
        </script>
        """
        st.markdown(js, unsafe_allow_html=True)

    # Placeholder for thinking animation
    thinking_placeholder = st.empty()
    if st.session_state.get('thinking', False):
        with thinking_placeholder:
            st.markdown("Thinking... 🤔")

    # Instructions or help text
    with st.expander("How to use SiteChat"):
        st.markdown("""
        1. Type your question in the input box below.
        2. Click the 'Send' button or press Enter to send your message.
        3. Wait for the AI to respond with relevant information.
        4. You can ask follow-up questions to get more details.

        SiteChat is here to help you find information quickly and easily!
        """)


if __name__ == "__main__":
    render_chat_page()
