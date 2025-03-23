"""LoreChat main application entry point."""
import os

import streamlit as st
from app.monitoring.logging import get_logger
from app.ui.pages.chat_page import render_chat_page

if __name__ == "__main__":
    logger = get_logger()
    logger.info("Starting LoreChat application...")

    logger.info(f"Streamlit version: {st.__version__}")

    logger.info("Current Streamlit Settings...")
    logger.info(f"Server port: {st.get_option('server.port')}")
    logger.info("Browser server address: "
                + f"{st.get_option('browser.serverAddress')}")
    logger.info("XSRF Protection: "
                + f"{st.get_option('server.enableXsrfProtection')}")
    logger.info("Allow CORS: "
                + f"{st.get_option('server.enableCORS')}")
    logger.info(f"Headless: {st.get_option('server.headless')}")
    logger.info("Client Max Message Size: "
                + f"{st.get_option('server.maxMessageSize')}")
    logger.info(f"Max Upload Size: {st.get_option('server.maxUploadSize')}")

    # Check for environment override
    if os.environ.get('STREAMLIT_CONFIG_FILE'):
        logger.info(f"Config file override found in environment: \
                    {os.environ['STREAMLIT_CONFIG_FILE']}")
    
    # Render the chat interface
    render_chat_page()
