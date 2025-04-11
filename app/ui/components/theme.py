"""Theme configuration for LoreChat UI."""

# Custom theme CSS overlay for Streamlit's dark theme
MODERN_THEME = """
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    /* CSS Variables for theme colors */
    :root {
        /* Persona-specific colors - default to wizard */
        --persona-primary: #6C63FF;
        --persona-secondary: #4ECDC4;
        --persona-accent: #FF6B6B;
    }

    /* Devil's Advocate theme */
    .devil-theme {
        --persona-primary: #FF5757;
        --persona-secondary: #FF9966;
        --persona-accent: #FFCC33;
    }

    /* Apply custom fonts */
    h1, h2, h3, h4, h5, h6, .streamlit-expanderHeader {
        font-family: 'Quicksand', sans-serif !important;
        font-weight: 600 !important;
    }

    body, p, div, span, li, .stSelectbox, .stTextInput {
        font-family: 'Inter', sans-serif !important;
    }

    /* Headers styling */
    h1 {
        position: relative;
        text-align: center;
        padding: 1rem 0;
    }

    h1::before, h1::after {
        content: '✦';
        color: var(--persona-accent);
        margin: 0 1rem;
        font-weight: normal;
    }

    /* Chat Messages */
    div[data-testid="stChatMessageContainer"] [data-testid="stChatMessage"] {
        border-radius: 12px !important;
        margin: 1.5rem 0 !important;
        padding: 1.5rem !important;
        position: relative !important;
        transition: all 0.3s ease;
    }

    /* User Message */
    [data-testid="stChatMessage"].user {
        border-right: 4px solid var(--persona-accent) !important;
        margin-left: 3rem !important;
        margin-right: 1rem !important;
    }

    /* User message tail */
    [data-testid="stChatMessage"].user::before {
        content: '';
        position: absolute;
        bottom: 15px;
        right: -10px;
        width: 20px;
        height: 20px;
        transform: rotate(45deg);
        border-right: 4px solid var(--persona-accent);
        border-top: 4px solid var(--persona-accent);
        border-radius: 0 5px 0 0;
        z-index: -1;
    }

    /* Assistant Message */
    [data-testid="stChatMessage"].assistant {
        border-left: 4px solid var(--persona-primary) !important;
        margin-right: 3rem !important;
        margin-left: 1rem !important;
    }

    /* Assistant message tail */
    [data-testid="stChatMessage"].assistant::before {
        content: '';
        position: absolute;
        bottom: 15px;
        left: -10px;
        width: 20px;
        height: 20px;
        transform: rotate(45deg);
        border-left: 4px solid var(--persona-primary);
        border-bottom: 4px solid var(--persona-primary);
        border-radius: 0 0 0 5px;
        z-index: -1;
    }

    /* Message Avatars */
    [data-testid="stChatMessage"] img {
        padding: 0.25rem;
        border: 2px solid var(--persona-primary);
        border-radius: 50%;
    }

    /* Buttons and Interactive Elements */
    .stButton button {
        background: linear-gradient(135deg, var(--persona-primary) 0%, var(--persona-secondary) 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: 'Quicksand', sans-serif !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: all 0.3s ease !important;
    }

    .stButton button:hover {
        background: linear-gradient(135deg, var(--persona-secondary) 0%, var(--persona-primary) 100%) !important;
        transform: translateY(-2px) !important;
    }

    /* Loading Animation */
    @keyframes thinking {
        0% { opacity: 0.5; transform: scale(0.8); }
        50% { opacity: 1; transform: scale(1.2); }
        100% { opacity: 0.5; transform: scale(0.8); }
    }

    .thinking-dots {
        padding: 16px 20px;
        margin: 15px 0;
        border-radius: 12px;
        font-family: 'Quicksand', sans-serif;
        display: flex;
        align-items: center;
        justify-content: flex-start;
    }

    .thinking-dots span {
        animation: thinking 1.4s infinite;
        display: inline-block;
        margin: 0 3px;
        color: var(--persona-primary);
        font-size: 1.5rem;
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
        <span>•</span><span>•</span><span>•</span>
    </div>
    """
