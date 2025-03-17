"""
SiteChat - A Streamlit-based chatbot for website content interaction.
"""

__version__ = "0.1.0"

from app.config import settings
from app.monitoring.logging import setup_logging

# Initialize logging
logger = setup_logging(
    log_level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE
)
