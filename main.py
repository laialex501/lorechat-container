"""
SiteChat - Main application entry point.
"""

import streamlit as st
from app.config import settings
from app.monitoring.logging import get_logger

logger = get_logger(__name__)


# Configure Streamlit page
st.set_page_config(
    page_title=settings.APP_NAME,
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def main():
    """Main application entry point."""
    try:
        # Set up the page header
        st.title(f"{settings.APP_NAME} 💬")
        st.markdown(
            "Welcome to SiteChat! Ask questions about the website content."
        )
        
        # Initialize session state for chat history if not exists
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input(
            "Ask a question about the website..."
        ):
            # Add user message to chat history
            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Display assistant response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                # TODO: Implement chat logic with LangChain
                response = (
                    "This is a placeholder response. "
                    "Chat functionality coming soon!"
                )
                message_placeholder.markdown(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        st.error("An error occurred. Please try again later.")


if __name__ == "__main__":
    main()
