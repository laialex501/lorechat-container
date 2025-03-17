"""
SiteChat - Main application entry point.

This module serves as the entry point for the Streamlit-based chat interface.
We use Streamlit for rapid development of the UI and real-time updates,
making it ideal for prototyping and testing the chat functionality.
"""

import streamlit as st
from app.config import settings
from app.monitoring.logging import get_logger

# Initialize logger for error tracking and debugging
logger = get_logger(__name__)


# Configure Streamlit page with optimal settings for chat interface
st.set_page_config(
    page_title=settings.APP_NAME,
    page_icon="💬",
    layout="wide",  # Wide layout for better chat message visibility
    initial_sidebar_state="collapsed"  # Focus on chat interface
)


def main():
    """
    Main application entry point that sets up the chat interface.
    Uses Streamlit's chat components for a familiar messaging experience
    and session state for persistent chat history during the session.
    """
    try:
        # Set up the page header with branding
        st.title(f"{settings.APP_NAME} 💬")
        st.markdown(
            "Welcome to SiteChat! Ask questions about the website content."
        )
        
        # Initialize session state for chat history
        # This persists messages during page reloads
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display existing chat messages
        # Using Streamlit's chat_message for consistent UI/UX
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input using Streamlit's native chat interface
        if prompt := st.chat_input(
            "Ask a question about the website..."
        ):
            # Add user message to chat history immediately
            # This provides instant feedback to the user
            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Display user message in real-time
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process and display assistant response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                # TODO: Implement chat logic with LangChain
                # This will be replaced with actual LLM integration
                response = (
                    "This is a placeholder response. "
                    "Chat functionality coming soon!"
                )
                message_placeholder.markdown(response)
            
            # Store assistant response in chat history
            # This maintains conversation context
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })
        
    except Exception as e:
        # Log detailed error information for debugging
        logger.error(f"Application error: {str(e)}", exc_info=True)
        # Show user-friendly error message
        st.error("An error occurred. Please try again later.")


if __name__ == "__main__":
    main()
