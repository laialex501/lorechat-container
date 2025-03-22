"""SiteChat main application entry point."""
from app.monitoring.logging import get_logger
from app.ui.pages.chat_page import render_chat_page

if __name__ == "__main__":
    logger = get_logger()
    logger.info("Starting SiteChat application...")
    
    # Render the chat interface
    render_chat_page()
