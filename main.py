"""SiteChat main application entry point."""
from app.config.settings import settings
from app.ui.pages.chat_page import render_chat_page
from scripts.init_vectorstore import init_dev_vectorstore

if __name__ == "__main__":
    # In development mode, ensure vector store is initialized with sample data
    if settings.ENV == "development":
        init_dev_vectorstore()
    
    # Render the chat interface
    render_chat_page()
