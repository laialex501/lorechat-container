"""
SiteChat - A Streamlit-based chatbot for website content interaction.
"""

__version__ = "0.1.0"

import os

from app.config import settings
from app.monitoring.logging import setup_logging

# Ensure log directory exists
if settings.LOG_FILE:
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)

# Initialize logging
logger = setup_logging(
    log_level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE
)
