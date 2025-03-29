"""Theme configuration for LoreChat UI."""

# Fantasy theme CSS with custom fonts and magical styling
FANTASY_THEME = """
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=MedievalSharp&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap');
    
    /* Archives of Nethys Theme Colors */
    :root {
        --background: #1A1A1A;  /* Dark background */
        --header-bg: #8B8B5A;   /* Olive/bronze headers */
        --timestamp: #4A2F2F;   /* Burgundy timestamp */
        --text: #E0E0E0;        /* Light text */
        --link: #FFD700;        /* Gold links */
        --section-bg: #2A2A2A;  /* Slightly lighter background */
        --accent: #C0C0A8;      /* Light olive accent */
        --border: #4A4A4A;      /* Dark border */
        --shadow: rgba(139, 139, 90, 0.2);  /* Olive glow */
    }
    
    /* Main Container and Global Styles */
    div.stApp {
        background: linear-gradient(180deg, #1F1F1F 0%, var(--background) 100%) !important;
        color: var(--text) !important;
        font-family: 'Roboto', sans-serif !important;
    }

    div.stApp > .main .block-container {
        padding: 2rem !important;
        max-width: 1000px !important;
        margin: 0 auto !important;
        background: transparent !important;
    }

    /* Override Streamlit's base theme */
    .stApp [data-testid="stAppViewContainer"] {
        background: transparent !important;
    }

    .stApp [data-testid="stToolbar"] {
        background: var(--section-bg) !important;
        border-bottom: 1px solid var(--border) !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(90deg, var(--section-bg) 0%, #1F1F1F 100%) !important;
        border-right: 1px solid var(--border) !important;
        box-shadow: 2px 0 5px rgba(0, 0, 0, 0.2) !important;
    }

    section[data-testid="stSidebar"] .css-1d391kg,
    section[data-testid="stSidebar"] .css-1544g2n {
        background: transparent !important;
    }

    .css-1629p8f h1 {  /* Sidebar title */
        font-family: 'MedievalSharp', cursive;
        color: var(--header-bg);
        text-shadow: 0 0 10px var(--shadow);
        margin-bottom: 2rem;
        padding: 1rem;
        border-bottom: 1px solid var(--accent);
        background: linear-gradient(180deg, var(--section-bg) 0%, transparent 100%);
    }

    .css-1629p8f .block-container {  /* Sidebar content */
        padding: 2rem 1rem;
    }

    /* Selectbox Containers */
    .css-1x8cf1d {  /* Selectbox label */
        color: var(--accent) !important;
        font-size: 1.1em;
        margin-bottom: 0.5rem;
        padding: 0.5rem 0;
        font-family: 'MedievalSharp', cursive;
    }

    .stSelectbox > div {
        background: var(--section-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 4px !important;
        color: var(--text) !important;
        margin: 0.5rem 0 1.5rem 0;
    }

    .stSelectbox > div:hover {
        border-color: var(--header-bg) !important;
        box-shadow: 0 0 10px var(--shadow) !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, var(--header-bg) 0%, #6B6B3A 100%) !important;
        border: 1px solid var(--accent) !important;
        border-radius: 4px !important;
        color: var(--text) !important;
        font-family: 'MedievalSharp', cursive;
        padding: 0.75rem 1rem !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
    }

    .streamlit-expanderContent {
        background: var(--section-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 0 0 4px 4px !important;
        padding: 1rem !important;
    }
    
    /* Headers and Text */
    h1, h2, h3 {
        font-family: 'MedievalSharp', cursive;
        color: var(--header-bg);
        text-shadow: 0 0 10px var(--shadow);
        margin-bottom: 1.5rem;
        padding: 0.75rem 1rem;
        border: 1px solid var(--accent);
        border-radius: 4px;
        background: linear-gradient(180deg, var(--section-bg) 0%, var(--background) 100%);
    }

    h1::before, h1::after {
        content: '✧';
        color: var(--accent);
        margin: 0 1rem;
        opacity: 0.7;
    }

    p, li {
        color: var(--text);
        line-height: 1.6;
    }

    a {
        color: var(--link);
        text-decoration: none;
        transition: all 0.2s ease;
    }

    a:hover {
        color: var(--accent);
        text-decoration: underline;
    }
    
    /* Chat Messages */
    div[data-testid="stChatMessageContainer"] [data-testid="stChatMessage"] {
        background: linear-gradient(180deg, var(--section-bg) 0%, var(--background) 100%) !important;
        border: 1px solid var(--border) !important;
        border-radius: 4px !important;
        margin: 1rem 0 !important;
        padding: 1.5rem !important;
        position: relative !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
    }

    /* Message decorative borders */
    div[data-testid="stChatMessageContainer"] [data-testid="stChatMessage"]::after {
        content: '';
        position: absolute;
        top: 4px;
        left: 4px;
        right: 4px;
        bottom: 4px;
        border: 1px solid rgba(139, 139, 90, 0.1);
        border-radius: 2px;
        pointer-events: none;
    }
    
    [data-testid="stChatMessage"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        opacity: 0.02;
        pointer-events: none;
    }
    
    /* User Message */
    [data-testid="stChatMessage"].user {
        background: linear-gradient(180deg, var(--timestamp) 0%, #3A2525 100%) !important;
        border-left: 4px solid var(--link) !important;
        margin-left: 2rem !important;
    }
    
    /* Assistant Message */
    [data-testid="stChatMessage"].assistant {
        background: linear-gradient(180deg, var(--header-bg) 0%, #6B6B3A 100%) !important;
        border-left: 4px solid var(--accent) !important;
        margin-right: 2rem !important;
    }

    /* Message Avatars */
    [data-testid="stChatMessage"] img {
        padding: 0.25rem;
        background: var(--section-bg);
        border: 1px solid var(--accent);
        border-radius: 4px;
        box-shadow: 0 0 10px var(--shadow);
    }
    
    /* Chat Input */
    div.stChatInputContainer {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        padding: 1rem 2rem !important;
        background: linear-gradient(0deg, var(--background) 0%, transparent 100%) !important;
        backdrop-filter: blur(10px) !important;
        z-index: 100 !important;
        border-top: 1px solid var(--border) !important;
    }

    /* Override any Streamlit default backgrounds */
    .stApp > div:not([class]), 
    .stApp > div[class=""], 
    .stApp div[data-testid="stDecoration"] {
        background: transparent !important;
    }

    .stTextInput input {
        background: var(--section-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 4px !important;
        color: var(--text) !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.2s ease;
    }

    .stTextInput input:focus {
        border-color: var(--header-bg) !important;
        box-shadow: 0 0 10px var(--shadow) !important;
    }

    .stTextInput input::placeholder {
        color: rgba(224, 224, 224, 0.5) !important;
    }
    
    /* Buttons and Interactive Elements */
    .stButton button {
        background: linear-gradient(90deg, var(--header-bg) 0%, #6B6B3A 100%) !important;
        border: 1px solid var(--accent) !important;
        border-radius: 4px !important;
        color: var(--text) !important;
        font-family: 'MedievalSharp', cursive !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        padding: 0.75rem 1.25rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stButton button:hover {
        background: linear-gradient(90deg, var(--accent) 0%, #D4D4BC 100%) !important;
        color: var(--background) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3) !important;
    }

    .stButton button:active {
        transform: translateY(0) !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Selectbox */
    .stSelectbox {
        background: var(--section-bg);
        border: 1px solid var(--border);
        border-radius: 4px;
        padding: 0.75rem 1.25rem !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--background);
        border-left: 1px solid var(--border);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--header-bg) 0%, #6B6B3A 100%);
        border: 1px solid var(--accent);
        border-radius: 4px;
    }
    
    /* Loading Animation */
    @keyframes thinking {
        0% { opacity: 0.5; }
        50% { opacity: 1; }
        100% { opacity: 0.5; }
    }
    
    .thinking-dots {
        padding: 12px 16px;
        margin: 10px 0;
        background: linear-gradient(180deg, var(--timestamp) 0%, #3A2525 100%);
        border: 1px solid var(--accent);
        border-radius: 4px;
        font-family: 'MedievalSharp', cursive;
        color: var(--text);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .thinking-dots span {
        animation: thinking 1.4s infinite;
        display: inline-block;
        margin: 0 2px;
        color: var(--link);
    }
    
    .thinking-dots span:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .thinking-dots span:nth-child(3) {
        animation-delay: 0.4s;
    }
</style>
"""


def get_thinking_html(thinking_text: str) -> str:
    """Get thinking animation HTML with custom text."""
    return f"""
    <div class="thinking-dots">
        {thinking_text}
        <span>.</span><span>.</span><span>.</span>
    </div>
    """
