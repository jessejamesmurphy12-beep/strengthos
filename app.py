import streamlit as st
from database import init_db
from auth import login_page
from coach_dashboard import coach_dashboard
from athlete_dashboard import athlete_dashboard

st.set_page_config(
    page_title="StrengthOS | Athlete Performance",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# StrengthOS visual system: navy surfaces, restrained gold accents,
# consistent controls, and responsive spacing.
st.markdown(
    """
    <style>
    :root {
        --sos-bg: #08111f;
        --sos-sidebar: #060d18;
        --sos-panel: #101d30;
        --sos-panel-raised: #152640;
        --sos-border: #263852;
        --sos-gold: #d2b15c;
        --sos-gold-soft: #f0d98d;
        --sos-text: #f3f6fb;
        --sos-muted: #a7b4c7;
        --sos-radius: 14px;
    }

    /* App canvas and main content */
    .stApp {
        background:
            radial-gradient(ellipse at 50% -20%, rgba(34, 69, 115, .22), transparent 55%),
            var(--sos-bg);
        color: var(--sos-text);
    }
    [data-testid="stAppViewContainer"] > .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }
    [data-testid="stHeader"] {
        background: rgba(8, 17, 31, .88);
    }
    [data-testid="stMainBlockContainer"] {
        color: var(--sos-text);
    }

    /* Typography: avoid forcing colors on every div/span so widgets remain legible */
    h1, h2, h3, h4 {
        color: var(--sos-text);
        letter-spacing: -0.025em;
    }
    p, li, .stMarkdown, [data-testid="stCaptionContainer"] {
        color: var(--sos-text);
    }
    [data-testid="stCaptionContainer"] {
        color: var(--sos-muted);
    }
    hr {
        border-color: var(--sos-border);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #070f1c 0%, var(--sos-sidebar) 100%);
        border-right: 1px solid #1c2b40;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.1rem;
    }
    [data-testid="stSidebar"] * {
        color: var(--sos-text);
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        border-radius: 9px;
        padding: .35rem .5rem;
    }

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        min-height: 2.55rem;
        border-radius: 9px;
        border: 1px solid #3b5270;
        background: #172944;
        color: var(--sos-text);
        font-weight: 650;
        transition: border-color .15s ease, background .15s ease, transform .15s ease;
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover,
    .stFormSubmitButton > button:hover {
